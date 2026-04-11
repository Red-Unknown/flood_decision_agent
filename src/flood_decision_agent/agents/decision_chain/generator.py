"""决策链生成 Agent - 系统入口，负责决策链的生成和优化.

该模块提供DecisionChainGeneratorAgent类，作为系统的入口Agent，
负责理解用户意图、分解任务、优化链路并生成可执行的任务图。
支持MCP工具自动选择功能。
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, List, Optional, Tuple

from flood_decision_agent.agents.base import BaseAgent
from flood_decision_agent.agents.decision_chain.chain_optimizer import ChainAlternative, ChainOptimizer
from flood_decision_agent.agents.decision_chain.checkpoint_agent import (
    CheckpointResumptionAgent,
    InterruptionReason,
)
from flood_decision_agent.agents.decision_chain.mode_detector import ModeDetector
from flood_decision_agent.agents.prompts import PromptContext, PlanSpecPrompts, WaterDomainPrompts
from flood_decision_agent.agents.decision_chain.task_decomposer import TaskDecomposer, TaskNodeInfo
from flood_decision_agent.agents.intent_parser.parser import IntentParser, TaskIntent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.core.task_graph_builder import TaskChainItem, TaskGraphBuilder
from flood_decision_agent.core.task_types import (
    BusinessTaskType,
    ExecutionTaskType,
    get_execution_types_for_business,
    get_business_type_description,
)
from flood_decision_agent.infrastructure.logging import get_logger
from flood_decision_agent.infrastructure.llm.kimi_client import KimiClient

# MCP客户端集成
from flood_decision_agent.mcp.clients.base import MCPClientManager


class DecisionChainGeneratorAgent(BaseAgent):
    """决策链生成 Agent：系统入口，负责决策链的生成和优化.

    核心功能：
    1. 意图理解：解析自然语言或结构化输入
    2. 任务分解：逆向分解 + 正向验证
    3. 链路优化：生成备选链 + 可靠性评估 + 迭代优化
    4. TaskGraph生成：构建可执行的任务图

    3阶段处理流程：
    意图理解 → 任务分解 → 链路优化 → TaskGraph

    Attributes:
        intent_parser: 意图解析器
        task_decomposer: 任务分解器
        chain_optimizer: 链路优化器
        task_graph_builder: 任务图构建器
    """

    def __init__(
        self,
        agent_id: str = "DecisionChainGenerator",
        intent_parser: Optional[IntentParser] = None,
        task_decomposer: Optional[TaskDecomposer] = None,
        chain_optimizer: Optional[ChainOptimizer] = None,
        task_graph_builder: Optional[TaskGraphBuilder] = None,
        checkpoint_agent: Optional[CheckpointResumptionAgent] = None,
        mode_detector: Optional[ModeDetector] = None,
        enable_mcp: bool = True,
        mcp_config_path: Optional[str] = None,
    ):
        """初始化决策链生成Agent.

        Args:
            agent_id: Agent唯一标识
            intent_parser: 意图解析器，为None时自动创建
            task_decomposer: 任务分解器，为None时自动创建
            chain_optimizer: 链路优化器，为None时自动创建
            task_graph_builder: 任务图构建器，为None时自动创建
            checkpoint_agent: 断点续传Agent，为None时自动创建
            mode_detector: 模式检测器，为None时自动创建
            enable_mcp: 是否启用MCP工具自动选择
            mcp_config_path: MCP配置文件路径
        """
        super().__init__(agent_id=agent_id)
        self._logger = get_logger().bind(name=self.__class__.__name__)

        # 初始化各模块
        self.intent_parser = intent_parser or IntentParser()
        self.task_decomposer = task_decomposer or TaskDecomposer()
        self.chain_optimizer = chain_optimizer or ChainOptimizer()
        self.task_graph_builder = task_graph_builder or TaskGraphBuilder()
        self.checkpoint_agent = checkpoint_agent or CheckpointResumptionAgent()
        self.mode_detector = mode_detector or ModeDetector()

        # MCP客户端管理器
        self._mcp_manager: Optional[MCPClientManager] = None
        self._mcp_enabled = enable_mcp
        self._mcp_config_path = mcp_config_path or "configs/mcp/servers.yaml"
        self._mcp_tools_cache: Dict[str, Dict[str, Any]] = {}

        self._logger.info("DecisionChainGeneratorAgent 初始化完成")

    async def initialize_mcp(self) -> bool:
        """初始化MCP客户端管理器并连接所有服务

        Returns:
            是否成功初始化
        """
        if not self._mcp_enabled:
            self._logger.debug("MCP集成已禁用")
            return False

        if self._mcp_manager is not None:
            self._logger.debug("MCP管理器已初始化")
            return True

        try:
            self._logger.info("初始化MCP客户端管理器...")
            self._mcp_manager = MCPClientManager(auto_load_config=False)

            # 从配置加载服务器
            self._mcp_manager.load_from_config(self._mcp_config_path)

            # 连接所有服务器
            connected = await self._mcp_manager.connect_all()
            self._logger.info(f"MCP服务器连接完成: {connected} 个")

            # 缓存所有可用工具
            await self._cache_mcp_tools()

            return connected > 0

        except Exception as e:
            self._logger.error(f"MCP初始化失败: {e}")
            self._mcp_manager = None
            return False

    async def _cache_mcp_tools(self) -> None:
        """缓存所有MCP服务器的工具信息"""
        if not self._mcp_manager:
            return

        self._mcp_tools_cache = {}

        for server_name, client in self._mcp_manager.clients.items():
            if not client._connected:
                continue

            tools = client.tools if hasattr(client, 'tools') else []
            for tool in tools:
                # 处理 MCPToolInfo 对象（使用属性访问）或字典（使用 get 方法）
                if hasattr(tool, 'name'):
                    # MCPToolInfo 对象
                    tool_name = tool.name
                    tool_info = {
                        'name': tool.name,
                        'description': tool.description,
                        'input_schema': tool.input_schema,
                    }
                else:
                    # 字典格式
                    tool_name = tool.get('name', '')
                    tool_info = tool

                if tool_name:
                    self._mcp_tools_cache[tool_name] = {
                        'server_name': server_name,
                        'tool_info': tool_info,
                    }

        self._logger.info(f"已缓存 {len(self._mcp_tools_cache)} 个MCP工具")

    def _find_mcp_tools_for_task(
        self,
        task_type: ExecutionTaskType,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """根据任务类型查找相关的MCP工具

        Args:
            task_type: 执行任务类型
            context: 上下文信息

        Returns:
            匹配的MCP工具列表
        """
        if not self._mcp_tools_cache:
            return []

        # 任务类型到工具关键词的映射
        task_tool_mapping = {
            ExecutionTaskType.DATA_COLLECTION: ['data', 'query', 'get', 'read', 'fetch'],
            ExecutionTaskType.DATA_PROCESSING: ['process', 'transform', 'clean'],
            ExecutionTaskType.PREDICTION: ['forecast', 'predict', 'model'],
            ExecutionTaskType.CALCULATION: ['calc', 'compute', 'analysis'],
            ExecutionTaskType.SIMULATION: ['simulation', 'model', 'flood', 'hydro'],
            ExecutionTaskType.OPTIMIZATION: ['optimize', 'plan', 'dispatch'],
            ExecutionTaskType.DECISION: ['decision', 'plan', 'dispatch'],
            ExecutionTaskType.EXECUTION: ['execute', 'control', 'operate'],
            ExecutionTaskType.VERIFICATION: ['verify', 'check', 'validate'],
            ExecutionTaskType.REPORTING: ['report', 'doc', 'write', 'markdown'],
            ExecutionTaskType.UNIVERSAL_QUERY: ['query', 'data', 'get'],
        }

        # 从上下文中提取额外关键词
        context_text = context.get('description', '') + ' ' + context.get('user_input', '')

        # 获取匹配关键词
        keywords = task_tool_mapping.get(task_type, [task_type.value.lower()])

        # 在上下文中查找额外关键词
        additional_keywords = []
        if 'rain' in context_text.lower() or '降雨' in context_text:
            additional_keywords.append('rain')
        if 'flood' in context_text.lower() or '洪水' in context_text:
            additional_keywords.append('flood')
        if 'dispatch' in context_text.lower() or '调度' in context_text:
            additional_keywords.append('dispatch')
        if 'inflow' in context_text.lower() or '入库' in context_text:
            additional_keywords.append('inflow')
        if 'data' in context_text.lower() or '数据' in context_text:
            additional_keywords.append('data')
        if 'report' in context_text.lower() or '报告' in context_text:
            additional_keywords.append('report')

        keywords.extend(additional_keywords)

        # 查找匹配的工具
        matched_tools = []
        for tool_name, tool_cache in self._mcp_tools_cache.items():
            tool_info = tool_cache['tool_info']
            # 统一使用字典方式访问工具信息
            if isinstance(tool_info, dict):
                tool_desc = tool_info.get('description', '').lower()
            else:
                # MCPToolInfo 对象
                tool_desc = getattr(tool_info, 'description', '').lower()
            tool_name_lower = tool_name.lower()

            # 检查是否匹配任何关键词
            for keyword in keywords:
                if keyword in tool_name_lower or keyword in tool_desc:
                    matched_tools.append({
                        'tool_name': tool_name,
                        'server_name': tool_cache['server_name'],
                        'tool_info': tool_info,
                        'matched_keyword': keyword,
                    })
                    break

        return matched_tools

    def _process(self, message: BaseMessage) -> BaseMessage:
        """执行决策链生成.

        这是Agent的主要入口方法，接收用户输入消息，
        经过3阶段处理后返回生成的TaskGraph。

        Args:
            message: 输入消息，包含用户请求

        Returns:
            输出消息，包含生成的TaskGraph
        """
        self._logger.info(f"开始执行决策链生成，消息类型: {message.type}")

        # 初始化MCP（如果启用）
        if self._mcp_enabled and not self._mcp_manager:
            try:
                import traceback
                import concurrent.futures
                self._logger.info("开始MCP初始化（在线程池中）...")
                # 使用线程池来避免嵌套事件循环问题
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.initialize_mcp())
                    mcp_result = future.result(timeout=60)
                    self._logger.info(f"MCP初始化结果: {mcp_result}")
            except Exception as e:
                self._logger.warning(f"MCP初始化失败（将继续使用本地工具）: {e}\n{traceback.format_exc()}")

        # 解析输入
        user_input = message.payload.get("input", "")
        input_type = message.payload.get("input_type", "natural_language")
        session_id = message.payload.get("session_id")

        # 生成决策链（带异常处理和断点保存）
        task_graph, metadata = self._generate_chain_with_checkpoint(
            user_input, input_type, session_id
        )

        # 构建响应消息
        response = BaseMessage(
            type=MessageType.TASK_RESPONSE,
            sender=self.agent_id,
            receiver="NodeSchedulerAgent",
            payload={
                "task_graph": task_graph,
                "metadata": metadata,
            },
        )

        self._logger.info("决策链生成完成")
        return response

    def _generate_chain_with_checkpoint(
        self,
        user_input: str,
        input_type: str,
        session_id: Optional[str] = None,
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """带断点保护的决策链生成.

        Args:
            user_input: 用户输入
            input_type: 输入类型
            session_id: 会话ID（可选，自动生成）

        Returns:
            (TaskGraph, 元数据)
        """
        # 生成或复用会话ID
        self._current_session_id = session_id or str(uuid.uuid4())
        metadata: Dict[str, Any] = {
            "session_id": self._current_session_id,
            "input": user_input,
            "input_type": input_type,
        }

        try:
            # 尝试生成决策链
            task_graph, gen_metadata = self.generate_chain(user_input, input_type)
            metadata.update(gen_metadata)
            return task_graph, metadata

        except BaseException as e:
            # 捕获异常并保存断点（使用 BaseException 以捕获 KeyboardInterrupt）
            interruption_reason = self._classify_exception(e)
            self._logger.error(
                f"决策链生成异常: {type(e).__name__}: {e}, "
                f"原因: {interruption_reason.value}"
            )

            # 保存断点
            checkpoint_state = {
                "user_input": user_input,
                "input_type": input_type,
                "current_phase": metadata.get("current_phase", "unknown"),
                "partial_result": metadata.get("partial_result", {}),
            }

            self.checkpoint_agent.save_checkpoint(
                session_id=self._current_session_id,
                state=checkpoint_state,
                interruption_reason=interruption_reason.value,
                metadata={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "agent_id": self.agent_id,
                },
            )

            # 重新抛出异常，让上层处理
            raise

    def _classify_exception(self, exception: Exception) -> InterruptionReason:
        """分类异常为中断原因.

        Args:
            exception: 异常对象

        Returns:
            中断原因枚举
        """
        error_name = type(exception).__name__.lower()
        error_msg = str(exception).lower()

        # 网络异常
        if any(
            keyword in error_name or keyword in error_msg
            for keyword in [
                "connection",
                "network",
                "timeout",
                "disconnect",
                "refused",
                "unreachable",
            ]
        ):
            return InterruptionReason.NETWORK_DISCONNECT

        # Token 超限
        if any(
            keyword in error_name or keyword in error_msg
            for keyword in [
                "token",
                "rate limit",
                "quota",
                "limit exceeded",
                "context length",
            ]
        ):
            return InterruptionReason.TOKEN_LIMIT_EXCEEDED

        # 手动取消
        if any(
            keyword in error_name or keyword in error_msg
            for keyword in ["cancel", "abort", "interrupted", "keyboardinterrupt"]
        ):
            return InterruptionReason.MANUAL_CANCEL

        # 默认系统错误
        return InterruptionReason.SYSTEM_ERROR

    def resume_session(self, session_id: str) -> Tuple[TaskGraph, Dict[str, Any]]:
        """恢复会话并继续生成决策链.

        Args:
            session_id: 会话ID

        Returns:
            (TaskGraph, 元数据)

        Raises:
            CheckpointNotFoundError: 断点不存在
        """
        self._logger.info(f"恢复会话: {session_id}")

        # 恢复断点
        checkpoint_data = self.checkpoint_agent.resume_checkpoint(session_id)
        state = checkpoint_data["state"]

        user_input = state.get("user_input", "")
        input_type = state.get("input_type", "natural_language")

        self._logger.info(
            f"断点恢复成功，继续生成决策链，中断原因: {checkpoint_data.get('interruption_reason')}"
        )

        # 使用保存的状态重新生成
        task_graph, metadata = self.generate_chain(user_input, input_type)
        metadata["resumed_from_checkpoint"] = True
        metadata["session_id"] = session_id
        metadata["original_interruption_reason"] = checkpoint_data.get(
            "interruption_reason"
        )

        # 标记断点为已完成
        self.checkpoint_agent.complete_checkpoint(session_id)

        return task_graph, metadata

    def generate_chain(
        self,
        user_input: str,
        input_type: str = "natural_language",
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """生成决策链的主方法.

        3阶段处理流程：
        1. 意图理解：解析用户输入
        2. 任务分解：逆向分解 + 正向验证
        3. 链路优化：生成备选链 + 选择最优
        4. 图生成：构建TaskGraph

        Args:
            user_input: 用户输入（自然语言或结构化数据）
            input_type: 输入类型，"natural_language" 或 "structured"

        Returns:
            (生成的TaskGraph, 元数据)
        """
        return self.generate_with_mode(user_input, preferred_mode="auto", input_type=input_type)

    def generate_with_mode(
        self,
        user_input: str,
        preferred_mode: str = "auto",
        input_type: str = "natural_language",
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """根据指定模式生成决策链.

        支持自动检测模式或强制指定模式：
        - "auto": 调用 ModeDetector.detect() 自动判断
        - "simple": 简单模式，直接回答
        - "plan": 计划模式，生成执行计划
        - "spec": 规范模式，生成详细规范文档

        Args:
            user_input: 用户输入（自然语言或结构化数据）
            preferred_mode: 首选模式，"auto" | "simple" | "plan" | "spec"
            input_type: 输入类型，"natural_language" 或 "structured"

        Returns:
            (生成的TaskGraph, 元数据)
        """
        # 确定处理模式
        if preferred_mode == "auto":
            detected_mode = self.mode_detector.detect(user_input)
            self._logger.info(f"自动检测模式: {detected_mode}")
        elif preferred_mode in ["simple", "plan", "spec"]:
            detected_mode = preferred_mode
            self._logger.info(f"使用指定模式: {detected_mode}")
        else:
            self._logger.warning(f"未知模式 '{preferred_mode}'，使用 auto 模式")
            detected_mode = self.mode_detector.detect(user_input)

        metadata: Dict[str, Any] = {
            "input": user_input,
            "input_type": input_type,
            "mode": detected_mode,
            "mode_source": "auto" if preferred_mode == "auto" else "specified",
        }

        # 根据模式选择不同的处理流程
        if detected_mode == "simple":
            return self._generate_simple_mode(user_input, input_type, metadata)
        elif detected_mode == "plan":
            return self._generate_plan_mode(user_input, input_type, metadata)
        elif detected_mode == "spec":
            return self._generate_spec_mode(user_input, input_type, metadata)
        else:
            # 默认使用标准流程
            return self._generate_standard_mode(user_input, input_type, metadata)

    def _generate_simple_mode(
        self,
        user_input: str,
        input_type: str,
        metadata: Dict[str, Any],
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """简单模式：直接回答，最小化处理流程.

        Args:
            user_input: 用户输入
            input_type: 输入类型
            metadata: 元数据字典

        Returns:
            (生成的TaskGraph, 元数据)
        """
        self._logger.info("使用 Simple 模式生成决策链")

        # 阶段1: 意图理解（简化）
        self._logger.info("阶段1: 意图理解（简化）")
        intent = self._parse_intent(user_input, input_type)

        if intent.error_message:
            self._logger.error(f"意图解析失败: {intent.error_message}")
            metadata["error"] = intent.error_message
            return TaskGraph(), metadata

        metadata["intent"] = {
            "task_type": intent.task_type.value if intent.task_type else None,
            "goal": intent.goal,
            "constraints": intent.constraints,
        }

        # 阶段2: 简化的任务分解
        self._logger.info("阶段2: 简化的任务分解")
        task_nodes = self._decompose_tasks_simple(intent)
        metadata["decomposition"] = {
            "node_count": len(task_nodes),
            "nodes": [{"id": n.task_id, "type": n.task_type.value} for n in task_nodes],
            "mode": "simple",
        }

        # 阶段3: 跳过复杂优化
        self._logger.info("阶段3: 跳过链路优化（Simple模式）")
        metadata["optimization"] = {
            "reliability_score": 1.0,
            "log": ["Simple模式：跳过复杂优化"],
            "mode": "simple",
        }

        # 阶段4: TaskGraph生成（带MCP工具选择）
        self._logger.info("阶段4: TaskGraph生成")
        context = {"description": intent.goal.get("description", ""), "user_input": user_input}
        task_graph = self._build_task_graph(task_nodes, context)
        metadata["task_graph"] = {
            "node_count": len(task_graph.get_all_nodes()),
            "edge_count": sum(len(edges) for edges in task_graph._edges.values()),
        }

        return task_graph, metadata

    def _generate_plan_mode(
        self,
        user_input: str,
        input_type: str,
        metadata: Dict[str, Any],
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """计划模式：生成详细的执行计划.

        Args:
            user_input: 用户输入
            input_type: 输入类型
            metadata: 元数据字典

        Returns:
            (生成的TaskGraph, 元数据)
        """
        self._logger.info("使用 Plan 模式生成决策链")

        # 使用标准流程，但标记为 plan 模式
        task_graph, meta = self._generate_standard_mode(user_input, input_type, metadata)
        meta["mode"] = "plan"
        meta["optimization"]["mode"] = "plan"

        return task_graph, meta

    def _generate_spec_mode(
        self,
        user_input: str,
        input_type: str,
        metadata: Dict[str, Any],
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """规范模式：生成详细规范文档.

        Args:
            user_input: 用户输入
            input_type: 输入类型
            metadata: 元数据字典

        Returns:
            (生成的TaskGraph, 元数据)
        """
        self._logger.info("使用 Spec 模式生成决策链")

        # 使用标准流程，但启用更多备选链和详细分析
        metadata["spec_mode"] = True

        # 阶段1: 意图理解
        self._logger.info("阶段1: 意图理解")
        intent = self._parse_intent(user_input, input_type)

        if intent.error_message:
            self._logger.error(f"意图解析失败: {intent.error_message}")
            metadata["error"] = intent.error_message
            return TaskGraph(), metadata

        metadata["intent"] = {
            "task_type": intent.task_type.value if intent.task_type else None,
            "goal": intent.goal,
            "constraints": intent.constraints,
        }

        # 阶段2: 详细的任务分解
        self._logger.info("阶段2: 详细的任务分解（Spec模式）")
        task_nodes = self._decompose_tasks(intent)
        metadata["decomposition"] = {
            "node_count": len(task_nodes),
            "nodes": [{"id": n.task_id, "type": n.task_type.value} for n in task_nodes],
            "mode": "spec",
        }

        # 阶段3: 生成更多备选链并详细评估
        self._logger.info("阶段3: 详细的链路优化（Spec模式）")
        alternatives = self.chain_optimizer.generate_alternatives(
            task_nodes, strategies=["default", "parallel", "granular", "fallback"]
        )

        # 评估所有备选链
        for alt in alternatives:
            reliability, issues, details = self.chain_optimizer.evaluate_reliability(alt.nodes)
            alt.reliability_score = reliability
            alt.metadata["issues"] = issues
            alt.metadata["evaluation_details"] = details

        # 选择最优链
        best_chain = self.chain_optimizer.select_best_chain(alternatives)

        if best_chain:
            optimized_nodes, final_reliability, log = self.chain_optimizer.optimize_iteratively(
                best_chain.nodes
            )
        else:
            optimized_nodes = task_nodes
            final_reliability, _, _ = self.chain_optimizer.evaluate_reliability(task_nodes)
            log = ["使用原始链"]

        metadata["optimization"] = {
            "reliability_score": final_reliability,
            "log": log,
            "alternatives_count": len(alternatives),
            "selected_chain": best_chain.chain_id if best_chain else None,
            "mode": "spec",
        }

        # 阶段4: TaskGraph生成（带MCP工具选择）
        self._logger.info("阶段4: TaskGraph生成")
        context = {"description": intent.goal.get("description", ""), "user_input": user_input}
        task_graph = self._build_task_graph(optimized_nodes, context)
        metadata["task_graph"] = {
            "node_count": len(task_graph.get_all_nodes()),
            "edge_count": sum(len(edges) for edges in task_graph._edges.values()),
        }

        return task_graph, metadata

    def _generate_standard_mode(
        self,
        user_input: str,
        input_type: str,
        metadata: Dict[str, Any],
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """标准模式生成决策链.

        Args:
            user_input: 用户输入
            input_type: 输入类型
            metadata: 元数据字典

        Returns:
            (生成的TaskGraph, 元数据)
        """
        # ========== 阶段1: 意图理解 ==========
        self._logger.info("阶段1: 意图理解")
        intent = self._parse_intent(user_input, input_type)

        # 检查意图解析是否出错
        if intent.error_message:
            self._logger.error(f"意图解析失败: {intent.error_message}")
            metadata["error"] = intent.error_message
            return TaskGraph(), metadata

        metadata["intent"] = {
            "task_type": intent.task_type.value if intent.task_type else None,
            "goal": intent.goal,
            "constraints": intent.constraints,
        }

        # ========== 阶段2: 任务分解 ==========
        self._logger.info("阶段2: 任务分解")
        task_nodes = self._decompose_tasks(intent)
        metadata["decomposition"] = {
            "node_count": len(task_nodes),
            "nodes": [{"id": n.task_id, "type": n.task_type.value} for n in task_nodes],
        }

        # ========== 阶段3: 链路优化 ==========
        self._logger.info("阶段3: 链路优化")
        optimized_nodes, reliability, optimization_log = self._optimize_chain(task_nodes)
        metadata["optimization"] = {
            "reliability_score": reliability,
            "log": optimization_log,
        }

        # ========== 阶段4: TaskGraph生成（带MCP工具选择） ==========
        self._logger.info("阶段4: TaskGraph生成")
        context = {"description": intent.goal.get("description", ""), "user_input": user_input}
        task_graph = self._build_task_graph(optimized_nodes, context)
        metadata["task_graph"] = {
            "node_count": len(task_graph.get_all_nodes()),
            "edge_count": sum(len(edges) for edges in task_graph._edges.values()),
        }

        return task_graph, metadata

    def _parse_intent(self, user_input: str, input_type: str) -> TaskIntent:
        """解析用户意图.

        Args:
            user_input: 用户输入
            input_type: 输入类型

        Returns:
            解析后的意图对象
        """
        if input_type == "natural_language":
            intent = self.intent_parser.parse_natural_language(user_input)
        elif input_type == "structured":
            # 将字符串解析为字典
            import json

            try:
                structured_data = json.loads(user_input)
            except json.JSONDecodeError:
                structured_data = {"task_type": "unknown", "description": user_input}
            intent = self.intent_parser.parse_structured(structured_data)
        else:
            # 默认尝试自然语言解析
            intent = self.intent_parser.parse_natural_language(user_input)

        self._logger.info(
            f"意图解析完成: 任务类型={intent.task_type.value if intent.task_type else 'unknown'}, "
            f"目标={intent.goal}"
        )
        return intent

    def _decompose_tasks(self, intent: TaskIntent) -> List[TaskNodeInfo]:
        """分解任务.

        使用新的类型系统，基于业务类型获取执行步骤。

        Args:
            intent: 用户意图

        Returns:
            任务节点列表
        """
        # 获取业务类型和执行步骤
        business_type = intent.task_type
        execution_steps = intent.execution_steps

        # 如果没有执行步骤，使用默认步骤
        if not execution_steps:
            execution_steps = get_execution_types_for_business(business_type)

        # 提取目标描述
        goal_description = intent.goal.get("description", "")
        if not goal_description and intent.raw_input:
            goal_description = intent.raw_input

        # 构建任务节点列表
        task_nodes: List[TaskNodeInfo] = []
        prev_node_id = None

        for idx, exec_type in enumerate(execution_steps):
            node_id = f"{business_type.value}_{idx:03d}"

            # 构建依赖关系
            dependencies = []
            if prev_node_id:
                dependencies.append(prev_node_id)

            node = TaskNodeInfo(
                task_id=node_id,
                task_type=exec_type,
                description=f"{get_business_type_description(business_type)} - {exec_type.value}",
                inputs=[],
                outputs=[f"output_{node_id}"],
                dependencies=dependencies,
                metadata={
                    "business_type": business_type.value,
                    "execution_type": exec_type.value,
                    "step_index": idx,
                },
            )
            task_nodes.append(node)
            prev_node_id = node_id

        self._logger.info(f"任务分解完成: {len(task_nodes)} 个节点 (业务类型: {business_type.value})")
        return task_nodes

    def _decompose_tasks_simple(self, intent: TaskIntent) -> List[TaskNodeInfo]:
        """简化的任务分解（Simple模式使用）.

        Args:
            intent: 用户意图

        Returns:
            简化的任务节点列表
        """
        from flood_decision_agent.core.task_types import ExecutionTaskType

        business_type = intent.task_type

        # 只创建一个简单的执行节点
        node = TaskNodeInfo(
            task_id=f"{business_type.value}_simple",
            task_type=ExecutionTaskType.UNIVERSAL_QUERY,
            description=intent.goal.get("description", intent.raw_input or "简单任务"),
            inputs=[],
            outputs=[f"output_{business_type.value}_simple"],
            dependencies=[],
            metadata={
                "business_type": business_type.value,
                "execution_type": ExecutionTaskType.UNIVERSAL_QUERY.value,
                "mode": "simple",
            },
        )

        self._logger.info(f"简单模式任务分解: 1 个节点")
        return [node]

    def _optimize_chain(
        self, task_nodes: List[TaskNodeInfo]
    ) -> Tuple[List[TaskNodeInfo], float, List[str]]:
        """优化任务链.

        Args:
            task_nodes: 初始任务节点列表

        Returns:
            (优化后的节点列表, 可靠性评分, 优化日志)
        """
        # 生成备选链
        alternatives = self.chain_optimizer.generate_alternatives(task_nodes)
        self._logger.info(f"生成 {len(alternatives)} 条备选链")

        # 评估每条链的可靠性
        for alt in alternatives:
            reliability, issues, _ = self.chain_optimizer.evaluate_reliability(alt.nodes)
            alt.reliability_score = reliability
            alt.metadata["issues"] = issues

        # 选择最优链
        best_chain = self.chain_optimizer.select_best_chain(alternatives)

        if best_chain:
            self._logger.info(
                f"选择最优链: {best_chain.chain_id}, 可靠性={best_chain.reliability_score:.2f}"
            )
            # 对最优链进行迭代优化
            optimized_nodes, final_reliability, log = self.chain_optimizer.optimize_iteratively(
                best_chain.nodes
            )
            return optimized_nodes, final_reliability, log
        else:
            # 如果没有找到合适的链，返回原始节点
            self._logger.warning("未找到合适的备选链，使用原始链")
            reliability, _, _ = self.chain_optimizer.evaluate_reliability(task_nodes)
            return task_nodes, reliability, ["使用原始链"]

    def _build_task_graph(
        self,
        task_nodes: List[TaskNodeInfo],
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskGraph:
        """构建任务图.

        Args:
            task_nodes: 任务节点列表
            context: 上下文信息，用于MCP工具选择

        Returns:
            构建的TaskGraph
        """
        context = context or {}

        # 转换为TaskChainItem，并添加MCP工具信息
        chain_items = []
        for node in task_nodes:
            # 查找该节点可用的MCP工具
            mcp_tools = []
            if self._mcp_enabled and self._mcp_tools_cache:
                matched_tools = self._find_mcp_tools_for_task(node.task_type, context)
                # 最多选择2个MCP工具
                for tool in matched_tools[:2]:
                    mcp_tools.append({
                        "tool_name": tool["tool_name"],
                        "server_name": tool["server_name"],
                        "is_mcp_tool": True,
                    })

            # 构建节点元数据
            node_metadata = dict(node.metadata) if node.metadata else {}
            if mcp_tools:
                node_metadata["mcp_tools"] = mcp_tools
                self._logger.debug(f"节点 {node.task_id} 分配了 {len(mcp_tools)} 个MCP工具")

            item = TaskChainItem(
                task_id=node.task_id,
                task_type=node.task_type.value,
                description=node.description,
                inputs=node.inputs,
                outputs=node.outputs,
                dependencies=node.dependencies,
                metadata=node_metadata,
            )
            chain_items.append(item)

        # 构建任务图
        task_graph = self.task_graph_builder.build_from_chain(chain_items)

        # 将MCP工具信息添加到TaskGraph的节点中
        for item in chain_items:
            if item.metadata and "mcp_tools" in item.metadata:
                node = task_graph.get_node(item.task_id)
                if node:
                    node.metadata = node.metadata or {}
                    node.metadata["mcp_tools"] = item.metadata["mcp_tools"]

        mcp_enabled_count = sum(
            1 for item in chain_items if item.metadata and "mcp_tools" in item.metadata
        )
        self._logger.info(
            f"TaskGraph构建完成: {len(task_graph.get_all_nodes())} 个节点, "
            f"{sum(len(edges) for edges in task_graph._edges.values())} 条边, "
            f"{mcp_enabled_count} 个节点启用了MCP工具"
        )
        return task_graph

    def generate_chain_with_alternatives(
        self,
        user_input: str,
        input_type: str = "natural_language",
        num_alternatives: int = 3,
    ) -> Tuple[TaskGraph, List[ChainAlternative], Dict[str, Any]]:
        """生成决策链并返回所有备选方案.

        用于需要查看所有备选链的场景。

        Args:
            user_input: 用户输入
            input_type: 输入类型
            num_alternatives: 备选链数量

        Returns:
            (最优TaskGraph, 所有备选链, 元数据)
        """
        # 意图理解
        intent = self._parse_intent(user_input, input_type)

        # 任务分解
        task_nodes = self._decompose_tasks(intent)

        # 生成备选链
        alternatives = self.chain_optimizer.generate_alternatives(
            task_nodes, strategies=["default", "parallel", "granular"][:num_alternatives]
        )

        # 评估所有备选链
        for alt in alternatives:
            reliability, issues, _ = self.chain_optimizer.evaluate_reliability(alt.nodes)
            alt.reliability_score = reliability
            alt.metadata["issues"] = issues

        # 选择最优链并构建TaskGraph（带MCP工具选择）
        context = {"description": intent.goal.get("description", ""), "user_input": user_input}
        best_chain = self.chain_optimizer.select_best_chain(alternatives)
        if best_chain:
            optimized_nodes, _, _ = self.chain_optimizer.optimize_iteratively(best_chain.nodes)
            task_graph = self._build_task_graph(optimized_nodes, context)
        else:
            task_graph = self._build_task_graph(task_nodes, context)

        metadata = {
            "intent": {
                "task_type": intent.task_type.value if intent.task_type else None,
                "goal": intent.goal,
            },
            "alternatives_count": len(alternatives),
            "selected_chain": best_chain.chain_id if best_chain else None,
        }

        return task_graph, alternatives, metadata

    def generate_plan_single(
        self,
        user_input: str,
        domain: str = "水利调度",
        constraints: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """生成单一规划文档（可编辑版本）.

        使用更新后的提示词生成单一规划方案，强调可编辑性和章节结构。

        Args:
            user_input: 用户输入的需求描述
            domain: 领域背景，默认为"水利调度"
            constraints: 约束条件（可选）
            references: 参考资料列表（可选）

        Returns:
            包含规划文档和元数据的字典
            {
                "plan_document": str,  # Markdown格式的规划文档
                "metadata": {
                    "user_input": str,
                    "domain": str,
                    "sections": List[str],  # 章节列表
                    "editable": True,
                }
            }
        """
        self._logger.info(f"开始生成单一规划文档，用户输入: {user_input[:50]}...")

        # 构建提示词上下文
        context = PromptContext(
            user_input=user_input,
            domain=domain,
            constraints=constraints,
            references=references,
        )

        # 获取单一规划生成提示词
        prompt = PlanSpecPrompts.get_plan_single_generation_prompt(context)

        # 调用LLM生成规划文档
        try:
            llm_client = LLMClient()
            response = llm_client.complete(
                prompt=prompt,
                system_message=PlanSpecPrompts.PLAN_GENERATOR_SYSTEM,
                temperature=0.7,
            )

            plan_document = response.strip()

            # 解析章节结构
            sections = self._extract_plan_sections(plan_document)

            metadata = {
                "user_input": user_input,
                "domain": domain,
                "sections": sections,
                "editable": True,
                "section_count": len(sections),
            }

            self._logger.info(f"单一规划文档生成完成，包含 {len(sections)} 个章节")

            return {
                "plan_document": plan_document,
                "metadata": metadata,
            }

        except Exception as e:
            self._logger.error(f"生成规划文档失败: {e}")
            return {
                "plan_document": "",
                "metadata": {
                    "user_input": user_input,
                    "domain": domain,
                    "error": str(e),
                    "editable": False,
                },
            }

    def _extract_plan_sections(self, plan_document: str) -> List[str]:
        """提取规划文档的章节结构.

        Args:
            plan_document: 规划文档内容

        Returns:
            章节标题列表
        """
        sections = []
        for line in plan_document.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                section_name = line[3:].strip()
                sections.append(section_name)
        return sections

    def generate_water_plan(
        self,
        user_input: str,
        water_business_type: str = "flood_warning",
        constraints: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """生成水利项目专用规划文档.

        使用水利领域知识生成符合行业规范的水利项目规划文档。

        Args:
            user_input: 用户输入的需求描述
            water_business_type: 水利业务类型，如 flood_warning/reservoir_dispatch
            constraints: 约束条件（可选）
            references: 参考资料列表（可选）

        Returns:
            包含规划文档和元数据的字典
            {
                "plan_document": str,  # Markdown格式的规划文档
                "metadata": {
                    "user_input": str,
                    "water_business_type": str,
                    "sections": List[str],
                    "domain_knowledge_used": True,
                }
            }
        """
        self._logger.info(f"开始生成水利项目规划文档，业务类型: {water_business_type}")

        # 构建提示词上下文（使用水利领域知识）
        context = PromptContext(
            user_input=user_input,
            domain="水利调度",
            constraints=constraints,
            references=references,
            water_business_type=water_business_type,
            use_water_domain_knowledge=True,
        )

        # 获取水利专用规划生成提示词
        prompt = PlanSpecPrompts.get_water_plan_generation_prompt(context)

        # 调用LLM生成规划文档
        try:
            llm_client = KimiClient()
            response = llm_client.complete(
                prompt=prompt,
                system_message=PlanSpecPrompts.PLAN_GENERATOR_SYSTEM,
                temperature=0.7,
                max_tokens=4000,
            )

            plan_document = response.strip()

            # 解析章节结构
            sections = self._extract_plan_sections(plan_document)

            metadata = {
                "user_input": user_input,
                "water_business_type": water_business_type,
                "sections": sections,
                "domain_knowledge_used": True,
                "section_count": len(sections),
            }

            self._logger.info(f"水利项目规划文档生成完成，包含 {len(sections)} 个章节")

            return {
                "plan_document": plan_document,
                "metadata": metadata,
            }

        except Exception as e:
            self._logger.error(f"生成水利项目规划文档失败: {e}")
            return {
                "plan_document": "",
                "metadata": {
                    "user_input": user_input,
                    "water_business_type": water_business_type,
                    "error": str(e),
                    "domain_knowledge_used": False,
                },
            }

    def generate_chain_from_plan(
        self,
        plan_document: str,
        user_input: str = "",
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """从规划文档生成决策链.

        解析规划文档中的实施步骤，转换为可执行的任务链。

        Args:
            plan_document: 规划文档内容
            user_input: 原始用户输入（可选）

        Returns:
            (TaskGraph, 元数据)
        """
        self._logger.info("开始从规划文档生成决策链")

        # 解析规划文档中的实施步骤
        steps = self._extract_implementation_steps(plan_document)

        if not steps:
            self._logger.warning("规划文档中未找到实施步骤，使用默认任务分解")
            # 回退到标准流程
            return self.generate_chain(user_input or "执行规划任务")

        # 将步骤转换为任务节点
        task_nodes = self._steps_to_task_nodes(steps)

        # 优化任务链
        optimized_nodes, reliability, optimization_log = self._optimize_chain(task_nodes)

        # 构建任务图
        context = {"description": user_input, "source": "plan_document"}
        task_graph = self._build_task_graph(optimized_nodes, context)

        metadata = {
            "source": "plan_document",
            "steps_extracted": len(steps),
            "node_count": len(task_graph.get_all_nodes()),
            "reliability_score": reliability,
            "optimization_log": optimization_log,
        }

        self._logger.info(f"从规划文档生成决策链完成，包含 {len(task_nodes)} 个节点")

        return task_graph, metadata

    def _extract_implementation_steps(self, plan_document: str) -> List[Dict[str, Any]]:
        """从规划文档中提取实施步骤.

        Args:
            plan_document: 规划文档内容

        Returns:
            步骤列表，每个步骤包含名称、描述、交付物等
        """
        steps = []
        lines = plan_document.split("\n")
        current_step = None

        for line in lines:
            line = line.strip()

            # 识别步骤标题（如 "1. **步骤名称**（预计耗时）"）
            if line.startswith("1. **") or line.startswith("2. **") or \
               line.startswith("3. **") or line.startswith("4. **") or \
               line.startswith("5. **") or line.startswith("6. **"):
                if current_step:
                    steps.append(current_step)

                # 解析步骤标题
                title_start = line.find("**") + 2
                title_end = line.find("**", title_start)
                title = line[title_start:title_end] if title_end > title_start else "未命名步骤"

                current_step = {
                    "name": title,
                    "description": "",
                    "deliverables": "",
                    "responsible": "",
                }

            # 识别步骤内容
            elif current_step and line.startswith("-"):
                if "具体内容" in line:
                    current_step["description"] = line.split("：", 1)[-1].strip()
                elif "交付物" in line:
                    current_step["deliverables"] = line.split("：", 1)[-1].strip()
                elif "负责人" in line:
                    current_step["responsible"] = line.split("：", 1)[-1].strip()

        # 添加最后一个步骤
        if current_step:
            steps.append(current_step)

        return steps

    def _steps_to_task_nodes(self, steps: List[Dict[str, Any]]) -> List[TaskNodeInfo]:
        """将实施步骤转换为任务节点.

        Args:
            steps: 实施步骤列表

        Returns:
            任务节点列表
        """
        from flood_decision_agent.agents.decision_chain.task_decomposer import TaskType

        task_nodes = []
        prev_node_id = None

        for idx, step in enumerate(steps):
            node_id = f"plan_step_{idx:03d}"

            # 根据步骤内容推断任务类型
            task_type = self._infer_task_type(step["name"], step["description"])

            # 构建依赖关系
            dependencies = []
            if prev_node_id:
                dependencies.append(prev_node_id)

            node = TaskNodeInfo(
                task_id=node_id,
                task_type=task_type,
                description=f"{step['name']}: {step['description']}",
                inputs=[],
                outputs=[f"output_{node_id}"],
                dependencies=dependencies,
                metadata={
                    "step_name": step["name"],
                    "deliverables": step.get("deliverables", ""),
                    "responsible": step.get("responsible", ""),
                    "step_index": idx,
                    "source": "plan_document",
                },
            )
            task_nodes.append(node)
            prev_node_id = node_id

        return task_nodes

    def _infer_task_type(self, step_name: str, step_description: str) -> Any:
        """根据步骤内容推断任务类型.

        Args:
            step_name: 步骤名称
            step_description: 步骤描述

        Returns:
            任务类型
        """
        from flood_decision_agent.agents.decision_chain.task_decomposer import TaskType

        text = (step_name + " " + step_description).lower()

        # 关键词匹配
        if any(kw in text for kw in ["数据", "采集", "接入", "获取"]):
            return TaskType.DATA_COLLECTION
        elif any(kw in text for kw in ["设计", "开发", "实现", "编码"]):
            return TaskType.EXECUTION
        elif any(kw in text for kw in ["测试", "验证", "检验"]):
            return TaskType.VERIFICATION
        elif any(kw in text for kw in ["模型", "训练", "算法", "预报"]):
            return TaskType.PREDICTION
        elif any(kw in text for kw in ["分析", "计算", "评估"]):
            return TaskType.CALCULATION
        elif any(kw in text for kw in ["决策", "方案", "调度"]):
            return TaskType.DECISION
        else:
            return TaskType.EXECUTION

    def generate_complete_workflow(
        self,
        user_input: str,
        water_business_type: str = "flood_warning",
        constraints: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """生成完整工作流：输入 -> 规划文档 -> 决策链.

        这是集成水利提示词的完整流程，包括：
        1. 生成水利项目规划文档（使用水利领域知识）
        2. 从规划文档生成决策链
        3. 返回完整结果

        Args:
            user_input: 用户输入的需求描述
            water_business_type: 水利业务类型
            constraints: 约束条件
            references: 参考资料

        Returns:
            完整工作流结果
            {
                "plan_result": {...},      # 规划文档生成结果
                "task_graph": TaskGraph,    # 决策链任务图
                "chain_metadata": {...},    # 决策链元数据
                "workflow_summary": {...},  # 工作流摘要
            }
        """
        self._logger.info("=" * 60)
        self._logger.info("开始生成完整工作流")
        self._logger.info("=" * 60)

        # 阶段1：生成水利项目规划文档
        self._logger.info("\n【阶段1】生成水利项目规划文档")
        plan_result = self.generate_water_plan(
            user_input=user_input,
            water_business_type=water_business_type,
            constraints=constraints,
            references=references,
        )

        if not plan_result["plan_document"]:
            self._logger.error("规划文档生成失败，中断工作流")
            return {
                "success": False,
                "error": "规划文档生成失败",
                "plan_result": plan_result,
            }

        plan_document = plan_result["plan_document"]

        # 阶段2：从规划文档生成决策链
        self._logger.info("\n【阶段2】从规划文档生成决策链")
        task_graph, chain_metadata = self.generate_chain_from_plan(
            plan_document=plan_document,
            user_input=user_input,
        )

        # 构建工作流摘要
        workflow_summary = {
            "user_input": user_input,
            "water_business_type": water_business_type,
            "plan_sections": plan_result["metadata"].get("section_count", 0),
            "chain_nodes": len(task_graph.get_all_nodes()),
            "chain_edges": sum(len(edges) for edges in task_graph._edges.values()),
            "reliability_score": chain_metadata.get("reliability_score", 0),
        }

        self._logger.info("=" * 60)
        self._logger.info("完整工作流生成完成")
        self._logger.info(f"规划章节数: {workflow_summary['plan_sections']}")
        self._logger.info(f"决策链节点数: {workflow_summary['chain_nodes']}")
        self._logger.info(f"可靠性评分: {workflow_summary['reliability_score']:.2f}")
        self._logger.info("=" * 60)

        return {
            "success": True,
            "plan_result": plan_result,
            "task_graph": task_graph,
            "chain_metadata": chain_metadata,
            "workflow_summary": workflow_summary,
        }

    def generate_water_spec(
        self,
        plan_document: str,
        user_input: str = "",
        water_business_type: str = "flood_warning",
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """生成水利项目专用规格文档.

        基于规划文档生成详细的技术规格文档，包含系统架构、接口设计、
        数据模型、算法方案等水利行业特有的技术规范。

        Args:
            plan_document: 规划文档内容
            user_input: 原始用户输入（可选）
            water_business_type: 水利业务类型
            constraints: 约束条件（可选）

        Returns:
            包含规格文档和元数据的字典
            {
                "spec_document": str,  # Markdown格式的规格文档
                "metadata": {
                    "plan_sections": int,
                    "spec_sections": int,
                    "domain_knowledge_used": True,
                }
            }
        """
        self._logger.info(f"开始生成水利项目规格文档，业务类型: {water_business_type}")

        # 构建提示词上下文
        context = PromptContext(
            user_input=user_input or "基于规划文档生成技术规格",
            domain="水利调度",
            existing_content=plan_document,
            constraints=constraints,
            water_business_type=water_business_type,
            use_water_domain_knowledge=True,
        )

        # 获取水利专用规格生成提示词
        prompt = PlanSpecPrompts.get_water_spec_generation_prompt(context)

        # 调用LLM生成规格文档
        try:
            llm_client = KimiClient()
            response = llm_client.complete(
                prompt=prompt,
                system_message=PlanSpecPrompts.SPEC_GENERATOR_SYSTEM,
                temperature=0.7,
                max_tokens=6000,
            )

            spec_document = response.strip()

            # 解析章节结构
            plan_sections = self._extract_plan_sections(plan_document)
            spec_sections = self._extract_plan_sections(spec_document)

            metadata = {
                "user_input": user_input,
                "water_business_type": water_business_type,
                "plan_sections": len(plan_sections),
                "spec_sections": len(spec_sections),
                "domain_knowledge_used": True,
            }

            self._logger.info(f"水利项目规格文档生成完成，包含 {len(spec_sections)} 个章节")

            return {
                "spec_document": spec_document,
                "metadata": metadata,
            }

        except Exception as e:
            self._logger.error(f"生成水利项目规格文档失败: {e}")
            return {
                "spec_document": "",
                "metadata": {
                    "user_input": user_input,
                    "water_business_type": water_business_type,
                    "error": str(e),
                    "domain_knowledge_used": False,
                },
            }

    def generate_complete_spec_workflow(
        self,
        user_input: str,
        water_business_type: str = "flood_warning",
        constraints: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """生成完整Spec工作流：输入 -> 规划文档 -> 规格文档.

        这是集成水利提示词的完整Spec流程，包括：
        1. 生成水利项目规划文档（使用水利领域知识）
        2. 基于规划文档生成技术规格文档
        3. 返回完整结果

        Args:
            user_input: 用户输入的需求描述
            water_business_type: 水利业务类型
            constraints: 约束条件
            references: 参考资料

        Returns:
            完整工作流结果
            {
                "plan_result": {...},      # 规划文档生成结果
                "spec_result": {...},      # 规格文档生成结果
                "workflow_summary": {...}, # 工作流摘要
            }
        """
        self._logger.info("=" * 60)
        self._logger.info("开始生成完整Spec工作流")
        self._logger.info("=" * 60)

        # 阶段1：生成水利项目规划文档
        self._logger.info("\n【阶段1】生成水利项目规划文档")
        plan_result = self.generate_water_plan(
            user_input=user_input,
            water_business_type=water_business_type,
            constraints=constraints,
            references=references,
        )

        if not plan_result["plan_document"]:
            self._logger.error("规划文档生成失败，中断工作流")
            return {
                "success": False,
                "error": "规划文档生成失败",
                "plan_result": plan_result,
            }

        plan_document = plan_result["plan_document"]

        # 阶段2：基于规划文档生成规格文档
        self._logger.info("\n【阶段2】基于规划文档生成规格文档")
        spec_result = self.generate_water_spec(
            plan_document=plan_document,
            user_input=user_input,
            water_business_type=water_business_type,
            constraints=constraints,
        )

        if not spec_result["spec_document"]:
            self._logger.error("规格文档生成失败")
            return {
                "success": False,
                "error": "规格文档生成失败",
                "plan_result": plan_result,
                "spec_result": spec_result,
            }

        # 构建工作流摘要
        workflow_summary = {
            "user_input": user_input,
            "water_business_type": water_business_type,
            "plan_sections": plan_result["metadata"].get("section_count", 0),
            "spec_sections": spec_result["metadata"].get("spec_sections", 0),
        }

        self._logger.info("=" * 60)
        self._logger.info("完整Spec工作流生成完成")
        self._logger.info(f"规划章节数: {workflow_summary['plan_sections']}")
        self._logger.info(f"规格章节数: {workflow_summary['spec_sections']}")
        self._logger.info("=" * 60)

        return {
            "success": True,
            "plan_result": plan_result,
            "spec_result": spec_result,
            "workflow_summary": workflow_summary,
        }

    def generate_water_tasks(
        self,
        spec_document: str,
        user_input: str = "",
        water_business_type: str = "flood_warning",
    ) -> Dict[str, Any]:
        """生成水利项目任务分解文档.

        基于规格文档生成详细的任务分解列表（tasks.md）。

        Args:
            spec_document: 规格文档内容
            user_input: 原始用户输入（可选）
            water_business_type: 水利业务类型

        Returns:
            包含任务分解文档和元数据的字典
        """
        self._logger.info(f"开始生成水利项目任务分解文档，业务类型: {water_business_type}")

        # 构建提示词上下文
        context = PromptContext(
            user_input=user_input or "基于规格文档生成任务分解",
            domain="水利调度",
            existing_content=spec_document,
            water_business_type=water_business_type,
            use_water_domain_knowledge=True,
        )

        # 获取任务分解生成提示词
        prompt = PlanSpecPrompts.get_water_tasks_generation_prompt(context)

        # 调用LLM生成任务分解文档
        try:
            llm_client = KimiClient()
            response = llm_client.complete(
                prompt=prompt,
                system_message=PlanSpecPrompts.SPEC_GENERATOR_SYSTEM,
                temperature=0.7,
                max_tokens=4000,
            )

            tasks_document = response.strip()

            metadata = {
                "user_input": user_input,
                "water_business_type": water_business_type,
                "domain_knowledge_used": True,
            }

            self._logger.info("水利项目任务分解文档生成完成")

            return {
                "tasks_document": tasks_document,
                "metadata": metadata,
            }

        except Exception as e:
            self._logger.error(f"生成水利项目任务分解文档失败: {e}")
            return {
                "tasks_document": "",
                "metadata": {
                    "user_input": user_input,
                    "water_business_type": water_business_type,
                    "error": str(e),
                    "domain_knowledge_used": False,
                },
            }

    def generate_water_checklist(
        self,
        spec_document: str,
        user_input: str = "",
        water_business_type: str = "flood_warning",
    ) -> Dict[str, Any]:
        """生成水利项目检查清单文档.

        基于规格文档生成详细的验收检查清单（checklist.md）。

        Args:
            spec_document: 规格文档内容
            user_input: 原始用户输入（可选）
            water_business_type: 水利业务类型

        Returns:
            包含检查清单文档和元数据的字典
        """
        self._logger.info(f"开始生成水利项目检查清单文档，业务类型: {water_business_type}")

        # 构建提示词上下文
        context = PromptContext(
            user_input=user_input or "基于规格文档生成检查清单",
            domain="水利调度",
            existing_content=spec_document,
            water_business_type=water_business_type,
            use_water_domain_knowledge=True,
        )

        # 获取检查清单生成提示词
        prompt = PlanSpecPrompts.get_water_checklist_generation_prompt(context)

        # 调用LLM生成检查清单文档
        try:
            llm_client = KimiClient()
            response = llm_client.complete(
                prompt=prompt,
                system_message=PlanSpecPrompts.SPEC_GENERATOR_SYSTEM,
                temperature=0.7,
                max_tokens=4000,
            )

            checklist_document = response.strip()

            metadata = {
                "user_input": user_input,
                "water_business_type": water_business_type,
                "domain_knowledge_used": True,
            }

            self._logger.info("水利项目检查清单文档生成完成")

            return {
                "checklist_document": checklist_document,
                "metadata": metadata,
            }

        except Exception as e:
            self._logger.error(f"生成水利项目检查清单文档失败: {e}")
            return {
                "checklist_document": "",
                "metadata": {
                    "user_input": user_input,
                    "water_business_type": water_business_type,
                    "error": str(e),
                    "domain_knowledge_used": False,
                },
            }

    def generate_complete_spec_suite(
        self,
        user_input: str,
        water_business_type: str = "flood_warning",
        constraints: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """生成完整Spec文档套组：spec.md + tasks.md + checklist.md.

        这是集成水利提示词的完整Spec流程，包括：
        1. 生成水利项目规划文档
        2. 基于规划文档生成规格文档（spec.md）
        3. 基于规格文档生成任务分解（tasks.md）
        4. 基于规格文档生成检查清单（checklist.md）

        Args:
            user_input: 用户输入的需求描述
            water_business_type: 水利业务类型
            constraints: 约束条件
            references: 参考资料

        Returns:
            完整Spec文档套组
            {
                "plan_result": {...},
                "spec_result": {...},
                "tasks_result": {...},
                "checklist_result": {...},
                "workflow_summary": {...},
            }
        """
        self._logger.info("=" * 60)
        self._logger.info("开始生成完整Spec文档套组")
        self._logger.info("=" * 60)

        # 阶段1：生成规划文档
        self._logger.info("\n【阶段1】生成水利项目规划文档")
        plan_result = self.generate_water_plan(
            user_input=user_input,
            water_business_type=water_business_type,
            constraints=constraints,
            references=references,
        )

        if not plan_result["plan_document"]:
            self._logger.error("规划文档生成失败，中断工作流")
            return {
                "success": False,
                "error": "规划文档生成失败",
                "plan_result": plan_result,
            }

        plan_document = plan_result["plan_document"]

        # 阶段2：生成规格文档
        self._logger.info("\n【阶段2】生成规格文档（spec.md）")
        spec_result = self.generate_water_spec(
            plan_document=plan_document,
            user_input=user_input,
            water_business_type=water_business_type,
            constraints=constraints,
        )

        if not spec_result["spec_document"]:
            self._logger.error("规格文档生成失败")
            return {
                "success": False,
                "error": "规格文档生成失败",
                "plan_result": plan_result,
                "spec_result": spec_result,
            }

        spec_document = spec_result["spec_document"]

        # 阶段3：生成任务分解
        self._logger.info("\n【阶段3】生成任务分解（tasks.md）")
        tasks_result = self.generate_water_tasks(
            spec_document=spec_document,
            user_input=user_input,
            water_business_type=water_business_type,
        )

        # 阶段4：生成检查清单
        self._logger.info("\n【阶段4】生成检查清单（checklist.md）")
        checklist_result = self.generate_water_checklist(
            spec_document=spec_document,
            user_input=user_input,
            water_business_type=water_business_type,
        )

        # 构建工作流摘要
        workflow_summary = {
            "user_input": user_input,
            "water_business_type": water_business_type,
            "plan_sections": plan_result["metadata"].get("section_count", 0),
            "spec_sections": spec_result["metadata"].get("spec_sections", 0),
            "has_tasks": bool(tasks_result.get("tasks_document")),
            "has_checklist": bool(checklist_result.get("checklist_document")),
        }

        self._logger.info("=" * 60)
        self._logger.info("完整Spec文档套组生成完成")
        self._logger.info(f"规划章节数: {workflow_summary['plan_sections']}")
        self._logger.info(f"规格章节数: {workflow_summary['spec_sections']}")
        self._logger.info(f"任务分解: {'已生成' if workflow_summary['has_tasks'] else '失败'}")
        self._logger.info(f"检查清单: {'已生成' if workflow_summary['has_checklist'] else '失败'}")
        self._logger.info("=" * 60)

        return {
            "success": True,
            "plan_result": plan_result,
            "spec_result": spec_result,
            "tasks_result": tasks_result,
            "checklist_result": checklist_result,
            "workflow_summary": workflow_summary,
        }


class DecisionPipeline:
    """决策流程管道.

    整合 DecisionChainGeneratorAgent 和 NodeSchedulerAgent，
    提供端到端的决策执行流程。
    """

    def __init__(
        self,
        chain_generator: Optional[DecisionChainGeneratorAgent] = None,
        node_scheduler: Optional[Any] = None,
    ):
        """初始化决策管道.

        Args:
            chain_generator: 决策链生成Agent
            node_scheduler: 节点调度Agent
        """
        self._logger = get_logger().bind(name=self.__class__.__name__)

        self.chain_generator = chain_generator or DecisionChainGeneratorAgent()
        self.node_scheduler = node_scheduler

        self._logger.info("DecisionPipeline 初始化完成")

    def execute(
        self,
        user_input: str,
        input_type: str = "natural_language",
        data_pool: Optional[SharedDataPool] = None,
    ) -> Dict[str, Any]:
        """执行完整决策流程.

        Args:
            user_input: 用户输入
            input_type: 输入类型
            data_pool: 共享数据池

        Returns:
            执行结果
        """
        if data_pool is None:
            data_pool = SharedDataPool()

        # 保存用户原始输入到数据池，供后续工具使用
        data_pool.set("raw_user_input", user_input)
        data_pool.set("input_type", input_type)

        # 阶段1: 生成决策链
        self._logger.info("=" * 50)
        self._logger.info("阶段1: 生成决策链")
        self._logger.info("=" * 50)

        task_graph, metadata = self.chain_generator.generate_chain(user_input, input_type)

        # 从意图解析结果中提取城市参数，写入数据池供后续工具使用
        intent_goal = metadata.get("intent", {}).get("goal", {})
        self._logger.debug(f"[Generator] intent_goal: {intent_goal}")
        if intent_goal.get("city"):
            data_pool.set("city", intent_goal["city"])
            self._logger.info(f"从意图解析中提取城市参数: {intent_goal['city']}")
            self._logger.debug(f"[Generator] 写入data_pool: city={intent_goal['city']}")

        # 阶段2: 执行决策链（如果有NodeScheduler）
        if self.node_scheduler:
            self._logger.info("=" * 50)
            self._logger.info("阶段2: 执行决策链")
            self._logger.info("=" * 50)

            execution_result = self.node_scheduler.execute_task_graph(
                task_graph, data_pool
            )

            return {
                "task_graph": task_graph,
                "generation_metadata": metadata,
                "execution_result": execution_result,
            }
        else:
            return {
                "task_graph": task_graph,
                "generation_metadata": metadata,
                "execution_result": None,
            }
