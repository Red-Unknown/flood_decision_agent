"""
WebSocket 消息处理器模块

提供各种消息类型的处理逻辑：
- 聊天消息处理（普通模式）
- Plan/Spec 模式确认与执行
- LLM 流式生成
- 心跳检测
- 取消操作

集成 ChainGenerator 和 StreamingTaskExecutor 实现完整的决策链生成与执行流程。
"""

from __future__ import annotations

import asyncio
import json
from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps, fast_json_loads
import time
import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional
from loguru import logger

if TYPE_CHECKING:
    from web.backend.websocket.chat_ws import ConnectionManager

from flood_decision_agent.agents.decision_chain.chain_generator import (
    ChainGenerator,
    GenerationStage,
)
from flood_decision_agent.agents.decision_chain.task_extractor import (
    TaskExtractor,
    DocumentType,
)
from flood_decision_agent.agents.summarizer import SummarizerAgent
from flood_decision_agent.agents.task_executor.streaming_executor import (
    StreamingTaskExecutor,
    TaskStatus,
)
from flood_decision_agent.agents.task_executor.executor import (
    TASK_TYPE_FRIENDLY_NAMES,
    MCP_TOOL_FRIENDLY_NAMES,
)
from flood_decision_agent.agents.prompts import PlanSpecPrompts, PromptContext
from flood_decision_agent.core.message import BaseMessage
from flood_decision_agent.infrastructure.llm.kimi_client import KimiClient
from flood_decision_agent.infrastructure.persistence.file_storage import get_file_storage


class MessageHandler(ABC):
    """消息处理器基类"""

    def __init__(self, manager: "ConnectionManager"):
        self.manager = manager

    @abstractmethod
    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        """处理消息"""
        pass

    async def send_message(self, conversation_id: str, data: Dict[str, Any]) -> bool:
        """发送消息到客户端"""
        logger.info(f"[WebSocket] 发送消息: type={data.get('type')}, conversation_id={conversation_id}")
        return await self.manager.send_message(conversation_id, data)


class PingHandler(MessageHandler):
    """心跳请求处理器"""

    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        await self.send_message(
            conversation_id,
            {
                "type": "pong",
                "timestamp": time.time(),
            },
        )


class ChatMessageHandler(MessageHandler):
    """聊天消息处理器 - 普通模式
    
    使用 ChainGenerator 进行流式决策链生成，
    使用 StreamingTaskExecutor 进行流式任务执行。
    """

    def __init__(self, manager: "ConnectionManager"):
        super().__init__(manager)
        self._chain_generator: Optional[ChainGenerator] = None
        self._task_executor: Optional[StreamingTaskExecutor] = None
        self._summarizer: Optional[SummarizerAgent] = None
        self._user_input: str = ""
        self._task_type: str = ""
        self._task_graph: Dict[str, Any] = {}
        self._node_results: List[Dict[str, Any]] = []
        self._data_pool: Dict[str, Any] = {}
        self._execution_total_tasks: int = 0
        self._execution_completed_tasks: int = 0
        self._execution_task_results: Dict[str, Any] = {}
        self._summarizer: Optional[SummarizerAgent] = None
        self._user_input: str = ""
        self._task_type: str = ""
        self._task_graph: Dict[str, Any] = {}
        self._node_results: List[Dict[str, Any]] = []
        self._data_pool: Dict[str, Any] = {}
        # 跟踪执行过程中的数据
        self._execution_total_tasks: int = 0
        self._execution_completed_tasks: int = 0
        self._execution_task_results: Dict[str, Any] = {}

    def _get_chain_generator(self) -> ChainGenerator:
        if self._chain_generator is None:
            self._chain_generator = ChainGenerator()
        return self._chain_generator

    def _get_task_executor(self) -> StreamingTaskExecutor:
        if self._task_executor is None:
            self._task_executor = StreamingTaskExecutor()
        return self._task_executor

    def _get_summarizer(self) -> SummarizerAgent:
        """获取或创建总结智能体"""
        if self._summarizer is None:
            self._summarizer = SummarizerAgent(enable_streaming=False)
        return self._summarizer

    def _get_data_pool_snapshot(self) -> Dict[str, Any]:
        """获取数据池快照"""
        if hasattr(self._task_executor, '_data_pool'):
            try:
                return self._task_executor._data_pool.snapshot()
            except:
                pass
        return self._data_pool

    def _get_friendly_task_name(self, task_id: str, task_type: str = "") -> str:
        """获取友好的任务名称
        
        Args:
            task_id: 任务 ID（如 data_query_001）
            task_type: 任务类型
            
        Returns:
            友好的任务名称
        """
        # 如果 task_type 为空，尝试从 task_id 提取
        if not task_type and task_id:
            if "_" in task_id:
                # 从 task_id 提取任务类型（如 data_query）
                task_type = "_".join(task_id.split("_")[:-1])
        
        # 从 task_id 提取任务编号
        task_num = ""
        if "_" in task_id:
            parts = task_id.split("_")
            if len(parts) >= 2:
                task_num = parts[-1]  # 获取最后的数字部分
        
        # 获取任务类型的中文名称
        type_name = TASK_TYPE_FRIENDLY_NAMES.get(task_type, task_type or "任务")
        
        # 构建友好名称
        if task_num:
            return f"{type_name} #{task_num}"
        else:
            return type_name
    
    def _get_friendly_tool_name(self, tool_name: str) -> str:
        """获取友好的工具名称
        
        Args:
            tool_name: 工具名称
            
        Returns:
            友好的工具名称
        """
        return MCP_TOOL_FRIENDLY_NAMES.get(tool_name, tool_name)

    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        """处理聊天消息 - 普通模式完整流程"""
        content = message.get("content", "")
        if not content:
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "EMPTY_MESSAGE",
                    "message": "消息内容不能为空",
                    "timestamp": time.time(),
                },
            )
            return

        # 保存用户输入
        self._user_input = content

        # 1. 发送用户消息确认
        await self.send_message(
            conversation_id,
            {
                "type": "user_message_confirm",
                "content": content,
                "timestamp": time.time(),
            },
        )

        try:
            # 2. 流式决策链生成
            generator = self._get_chain_generator()
            task_graph = None
            generation_metadata = {}

            async for event in generator.generate(content, input_type="natural_language"):
                # 根据事件类型发送不同的消息
                if event.stage == GenerationStage.INTENT_PARSING:
                    if event.progress == 0.2 and event.data and "intent" in event.data:
                        # 发送意图解析结果
                        await self.send_message(
                            conversation_id,
                            {
                                "type": "intent_parsed",
                                "intent": event.data["intent"],
                                "confidence": 0.8,
                            },
                        )
                    else:
                        # 发送意图解析阶段
                        await self.send_message(
                            conversation_id,
                            {
                                "type": "chain_generation_stage",
                                "stage": "intent_parsing",
                                "stage_name": "意图解析",
                                "progress": event.progress,
                                "message": event.message,
                            },
                        )

                elif event.stage == GenerationStage.TASK_DECOMPOSITION:
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "chain_generation_stage",
                            "stage": "task_decomposition",
                            "stage_name": "任务分解",
                            "progress": event.progress,
                            "message": event.message,
                            "data": event.data,
                        },
                    )

                elif event.stage == GenerationStage.CHAIN_OPTIMIZATION:
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "chain_generation_stage",
                            "stage": "chain_optimization",
                            "stage_name": "决策链优化",
                            "progress": event.progress,
                            "message": event.message,
                            "data": event.data,
                        },
                    )

                elif event.stage == GenerationStage.TASK_GRAPH_BUILDING:
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "chain_generation_stage",
                            "stage": "task_graph_building",
                            "stage_name": "任务图构建",
                            "progress": event.progress,
                            "message": event.message,
                            "data": event.data,
                        },
                    )

                elif event.stage == GenerationStage.COMPLETED:
                    # 生成完成，获取结果
                    result = generator.get_last_result()
                    if result and result.success:
                        task_graph = result.task_graph
                        generation_metadata = result.metadata

                        # 发送任务图生成完成
                        nodes = task_graph.get_all_nodes()
                        tasks = []
                        for node_id, node in nodes.items():
                            task_type = getattr(node, 'task_type', 'unknown')
                            if hasattr(task_type, 'value'):
                                task_type = task_type.value

                            tasks.append({
                                "task_id": node_id,
                                "task_name": getattr(node, 'description', node_id),
                                "task_type": task_type,
                                "dependencies": list(getattr(node, 'dependencies', [])),
                                "status": "pending",
                            })

                        await self.send_message(
                            conversation_id,
                            {
                                "type": "task_graph_generated",
                                "tasks": tasks,
                                "total_count": len(tasks),
                                "reliability_score": generation_metadata.get("optimization", {}).get("reliability_score", 0),
                            },
                        )

                        # 保存任务图信息用于总结
                        self._task_graph = {
                            "total_tasks": len(tasks),
                            "reliability_score": generation_metadata.get("optimization", {}).get("reliability_score", 0),
                            "tasks": tasks,
                        }

                        # 发送决策链生成完成
                        generation_id = f"gen_{conversation_id}_{int(time.time())}"
                        
                        # 构建 nodes 和 edges
                        nodes_list = []
                        for node_id, node in nodes.items():
                            task_type = getattr(node, 'task_type', 'unknown')
                            if hasattr(task_type, 'value'):
                                task_type = task_type.value
                            
                            nodes_list.append({
                                "task_id": node_id,
                                "task_name": getattr(node, 'description', node_id),
                                "task_type": task_type,
                                "dependencies": list(getattr(node, 'dependencies', [])),
                                "status": "pending",
                            })
                        
                        edges_list = []
                        for from_node, to_nodes in task_graph._edges.items():
                            for to_node in to_nodes:
                                edges_list.append({
                                    "from": from_node,
                                    "to": to_node,
                                })
                        
                        await self.send_message(
                            conversation_id,
                            {
                                "type": "chain_generated",
                                "generation_id": generation_id,
                                "mode": "normal",
                                "task_graph": {
                                    "tasks": nodes_list,
                                    "nodes": nodes_list,
                                    "edges": edges_list,
                                },
                                "reliability_score": generation_metadata.get("optimization", {}).get("reliability_score", 0),
                                "metadata": generation_metadata,
                                "timestamp": time.time(),
                            },
                        )

                elif event.stage == GenerationStage.ERROR:
                    # 生成失败
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "error",
                            "code": "GENERATION_FAILED",
                            "message": event.message,
                            "data": event.data,
                        },
                    )
                    return

            # 检查是否成功生成任务图
            if task_graph is None:
                await self.send_message(
                    conversation_id,
                    {
                        "type": "error",
                        "code": "GENERATION_FAILED",
                        "message": "决策链生成失败",
                    },
                )
                return

            # 3. 流式任务执行
            executor = self._get_task_executor()
            
            # 初始化执行跟踪变量
            self._execution_total_tasks = 0
            self._execution_completed_tasks = 0
            self._execution_task_results = {}

            async for event in executor.execute(task_graph):
                if event.event_type == "execution_started":
                    # 跟踪任务数
                    self._execution_total_tasks = event.total_count
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_started",
                            "execution_id": f"exec_{conversation_id}_{int(time.time())}",
                            "total_tasks": event.total_count,
                        },
                    )

                elif event.event_type == "task_update":
                    # 收集任务结果
                    if event.result and isinstance(event.result, dict):
                        self._execution_task_results[event.task_id] = event.result
                        if event.status and event.status.value == "completed":
                            self._execution_completed_tasks += 1
                    
                    # 从 result 中提取 duration_ms 和 MCP 数据
                    duration_ms = None
                    mcp_data = {}
                    if event.result and isinstance(event.result, dict):
                        duration_ms = event.result.get("metrics", {}).get("elapsed_time_ms")
                        # 从 output 中提取 MCP 工具返回的数据
                        output = event.result.get("output", {})
                        if output and isinstance(output, dict):
                            # 检查是否有 MCP 工具返回的数据
                            for key, value in output.items():
                                if isinstance(value, dict) and "data" in value:
                                    mcp_data[key] = value.get("data")
                                elif key not in ("success", "status", "error"):
                                    mcp_data[key] = value
                    
                    # 合并 MCP 数据到数据池
                    if mcp_data:
                        self._data_pool.update(mcp_data)
                        debug_msg = f"[DEBUG] 更新后 data_pool keys: {list(self._data_pool.keys())}, mcp_data: {mcp_data}"
                        logger.debug(debug_msg)
                    
                    # 获取任务类型和友好名称
                    task_type = event.result.get("task_type", "") if event.result else ""
                    friendly_task_name = self._get_friendly_task_name(event.task_id, task_type)
                    
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "task_update",
                            "task_id": event.task_id,
                            "friendly_task_name": friendly_task_name,
                            "task_type": task_type,
                            "friendly_task_type": TASK_TYPE_FRIENDLY_NAMES.get(task_type, task_type),
                            "status": event.status.value if event.status else "unknown",
                            "result": event.result,
                            "error": event.error,
                            "duration_ms": duration_ms,
                            "detail": {
                                "stage": event.detail.stage if event.detail else "",
                                "message": event.detail.message if event.detail else "",
                                "progress": event.detail.progress if event.detail else 0,
                                "modalities": event.detail.modalities if event.detail else None,
                            } if event.detail else None,
                        },
                    )

                elif event.event_type == "execution_progress":
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_progress",
                            "completed_tasks": event.completed_count,
                            "total_tasks": event.total_count,
                            "progress": event.progress,
                        },
                    )

                elif event.event_type == "execution_complete":
                    # 执行完成，使用跟踪的变量构建 summary
                    summary = {
                        "total_tasks": self._execution_total_tasks,
                        "completed_tasks": self._execution_completed_tasks,
                        "failed_tasks": self._execution_total_tasks - self._execution_completed_tasks,
                    }
                    
                    # 收集节点结果 - 从跟踪的字典转换为列表
                    self._node_results = list(self._execution_task_results.values())
                    summary["task_results"] = self._node_results
                    
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_complete",
                            "success": event.success,
                            "summary": summary,
                            "results": self._node_results,
                            "timestamp": time.time(),
                        },
                    )
                    
                    # 调用总结智能体生成专业总结
                    response_content = await self._generate_summary_with_ai(summary, event.success)

                    await self.send_message(
                        conversation_id,
                        {
                            "type": "assistant_message",
                            "content": response_content,
                        },
                    )

                elif event.event_type == "execution_error":
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "error",
                            "code": "EXECUTION_FAILED",
                            "message": event.error,
                        },
                    )

        except Exception as e:
            import traceback
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "PROCESSING_FAILED",
                    "message": f"处理失败: {str(e)}",
                    "traceback": traceback.format_exc(),
                    "timestamp": time.time(),
                },
            )

    async def _generate_summary_with_ai(self, summary: Dict[str, Any], success: bool) -> str:
        """使用总结智能体生成专业总结"""
        if not success:
            return f"任务执行失败。错误信息：{summary.get('error', '未知错误')}"

        try:
            # 获取总结智能体
            summarizer = self._get_summarizer()
            
            # 获取数据池快照
            data_pool_snapshot = self._get_data_pool_snapshot()
            
            # 构建总结请求 - BaseMessage 需要 type 和 sender 参数
            from flood_decision_agent.core.message import MessageType
            summary_message = BaseMessage(
                type=MessageType.EVENT,
                sender="websocket_handler",
                payload={
                    "task_request": {
                        "input": self._user_input,
                        "type": self._task_type,
                    },
                    "execution_summary": summary,
                    "data_pool_snapshot": data_pool_snapshot,
                    "task_graph": self._task_graph,
                    "node_results": self._node_results,
                }
            )
            
            # 调用总结智能体
            summary_result = summarizer._process(summary_message)
            summary_text = summary_result.get("summary", "")
            
            # 如果总结智能体成功生成，使用其输出
            if summary_text:
                return summary_text
            
        except Exception as e:
            import traceback
            logger.error(f"[ChatMessageHandler] 生成总结失败: {e}")
            logger.error(f"[ChatMessageHandler] traceback: {traceback.format_exc()}")
            pass
        
        # 降级到简单统计回复
        return self._generate_fallback_response(summary)

    def _generate_fallback_response(self, summary: Dict[str, Any]) -> str:
        """生成备用回复（当总结智能体失败时）"""
        total = summary.get('total_tasks', 0)
        completed = summary.get('completed_tasks', 0)
        failed = summary.get('failed_tasks', 0)

        return (
            f"任务执行完成！\n\n"
            f"📊 执行统计：\n"
            f"- 总任务数：{total}\n"
            f"- 成功任务：{completed}\n"
            f"- 失败任务：{failed}"
        )


class ConfirmPlanHandler(MessageHandler):
    """Plan 模式确认处理器
    
    使用 ChainGenerator 从 Plan 文档生成决策链，
    使用 StreamingTaskExecutor 进行流式任务执行。
    """

    def __init__(self, manager: "ConnectionManager"):
        super().__init__(manager)
        self._chain_generator: Optional[ChainGenerator] = None
        self._task_extractor: Optional[TaskExtractor] = None
        self._task_executor: Optional[StreamingTaskExecutor] = None
        self._summarizer: Optional[SummarizerAgent] = None
        self._user_input: str = ""
        self._task_type: str = ""
        self._task_graph: Dict[str, Any] = {}
        self._node_results: List[Dict[str, Any]] = []
        self._data_pool: Dict[str, Any] = {}
        self._execution_total_tasks: int = 0
        self._execution_completed_tasks: int = 0
        self._execution_task_results: Dict[str, Any] = {}

    def _get_chain_generator(self) -> ChainGenerator:
        if self._chain_generator is None:
            self._chain_generator = ChainGenerator()
        return self._chain_generator

    def _get_task_extractor(self) -> TaskExtractor:
        if self._task_extractor is None:
            self._task_extractor = TaskExtractor()
        return self._task_extractor

    def _get_task_executor(self) -> StreamingTaskExecutor:
        if self._task_executor is None:
            self._task_executor = StreamingTaskExecutor()
        return self._task_executor

    def _get_summarizer(self) -> SummarizerAgent:
        if self._summarizer is None:
            self._summarizer = SummarizerAgent(enable_streaming=False)
        return self._summarizer

    def _get_data_pool_snapshot(self) -> Dict[str, Any]:
        if hasattr(self._task_executor, '_data_pool'):
            try:
                return self._task_executor._data_pool.snapshot()
            except:
                pass
        return self._data_pool

    def _get_friendly_task_name(self, task_id: str, task_type: str = "") -> str:
        if not task_type and task_id:
            if "_" in task_id:
                task_type = "_".join(task_id.split("_")[:-1])
        
        task_num = ""
        if "_" in task_id:
            parts = task_id.split("_")
            if len(parts) >= 2:
                task_num = parts[-1]
        
        type_name = TASK_TYPE_FRIENDLY_NAMES.get(task_type, task_type or "任务")
        
        if task_num:
            return f"{type_name} #{task_num}"
        else:
            return type_name
    
    def _get_friendly_tool_name(self, tool_name: str) -> str:
        return MCP_TOOL_FRIENDLY_NAMES.get(tool_name, tool_name)

    async def _generate_summary_with_ai(self, summary: Dict[str, Any], success: bool) -> str:
        """使用总结智能体生成专业总结"""
        if not success:
            return f"任务执行失败。错误信息：{summary.get('error', '未知错误')}"

        try:
            summarizer = self._get_summarizer()
            data_pool_snapshot = self._get_data_pool_snapshot()
            
            from flood_decision_agent.core.message import MessageType
            summary_message = BaseMessage(
                type=MessageType.EVENT,
                sender="plan_handler",
                payload={
                    "task_request": {
                        "input": self._user_input,
                        "type": self._task_type,
                    },
                    "execution_summary": summary,
                    "data_pool_snapshot": data_pool_snapshot,
                    "task_graph": self._task_graph,
                    "node_results": self._node_results,
                }
            )
            
            summary_result = summarizer._process(summary_message)
            summary_text = summary_result.get("summary", "")
            
            if summary_text:
                return summary_text
            
        except Exception as e:
            pass
        
        return self._generate_fallback_response(summary)

    def _generate_fallback_response(self, summary: Dict[str, Any]) -> str:
        total = summary.get('total_tasks', 0)
        completed = summary.get('completed_tasks', 0)
        return f"任务执行完成！总任务数：{total}，成功任务：{completed}"

    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        """处理 Plan 确认消息"""
        plan_id = message.get("plan_id", "")
        action = message.get("action", "confirm")

        if not plan_id:
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "MISSING_PLAN_ID",
                    "message": "缺少 Plan ID",
                },
            )
            return

        if action == "cancel":
            await self.send_message(
                conversation_id,
                {
                    "type": "operation_cancelled",
                    "operation_type": "plan",
                    "reason": "用户取消",
                },
            )
            return

        try:
            # 1. 发送 Plan 确认成功
            await self.send_message(
                conversation_id,
                {
                    "type": "plan_confirmed",
                    "plan_id": plan_id,
                    "action": action,
                },
            )

            # 2. 加载 Plan 文档
            storage = get_file_storage()
            doc = storage.load_document(plan_id)

            if not doc:
                await self.send_message(
                    conversation_id,
                    {
                        "type": "error",
                        "code": "PLAN_NOT_FOUND",
                        "message": f"Plan 文档不存在: {plan_id}",
                    },
                )
                return

            plan_document = doc.get("content", "")
            user_input = doc.get("metadata", {}).get("user_input", "")

            # 3. 任务提取阶段
            await self.send_message(
                conversation_id,
                {
                    "type": "task_extracting",
                    "source": "plan",
                    "progress": 0.2,
                    "message": "正在从 Plan 文档提取任务...",
                },
            )

            # 4. 流式决策链生成（从 Plan）
            generator = self._get_chain_generator()
            task_graph = None
            generation_metadata = {}

            async for event in generator.generate_from_plan(plan_document, user_input):
                if event.stage == GenerationStage.INTENT_PARSING:
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "chain_generation_stage",
                            "stage": "task_extracting",
                            "stage_name": "任务提取",
                            "progress": event.progress,
                            "message": event.message,
                            "data": event.data,
                        },
                    )

                elif event.stage in [GenerationStage.TASK_DECOMPOSITION, GenerationStage.CHAIN_OPTIMIZATION, GenerationStage.TASK_GRAPH_BUILDING]:
                    stage_name_map = {
                        "task_decomposition": "任务分解",
                        "chain_optimization": "决策链优化",
                        "task_graph_building": "任务图构建",
                    }
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "chain_generation_stage",
                            "stage": event.stage.value,
                            "stage_name": stage_name_map.get(event.stage.value, event.stage.value),
                            "progress": event.progress,
                            "message": event.message,
                            "data": event.data,
                        },
                    )

                elif event.stage == GenerationStage.COMPLETED:
                    result = generator.get_last_result()
                    if result and result.success:
                        task_graph = result.task_graph
                        generation_metadata = result.metadata

                        # 发送任务图生成完成
                        nodes = task_graph.get_all_nodes()
                        tasks = []
                        for node_id, node in nodes.items():
                            task_type = getattr(node, 'task_type', 'unknown')
                            if hasattr(task_type, 'value'):
                                task_type = task_type.value

                            tasks.append({
                                "task_id": node_id,
                                "task_name": getattr(node, 'description', node_id),
                                "task_type": task_type,
                                "dependencies": list(getattr(node, 'dependencies', [])),
                                "status": "pending",
                            })

                        await self.send_message(
                            conversation_id,
                            {
                                "type": "task_graph_generated",
                                "tasks": tasks,
                                "total_count": len(tasks),
                                "reliability_score": generation_metadata.get("reliability_score", 0),
                            },
                        )

                        # 发送决策链生成完成
                        generation_id = f"gen_plan_{conversation_id}_{int(time.time())}"
                        
                        # 构建 edges
                        edges_list = []
                        for from_node, to_nodes in task_graph._edges.items():
                            for to_node in to_nodes:
                                edges_list.append({
                                    "from": from_node,
                                    "to": to_node,
                                })
                        
                        await self.send_message(
                            conversation_id,
                            {
                                "type": "chain_generated",
                                "generation_id": generation_id,
                                "mode": "plan",
                                "task_graph": {
                                    "tasks": tasks,
                                    "nodes": tasks,
                                    "edges": edges_list,
                                },
                                "reliability_score": generation_metadata.get("reliability_score", 0),
                                "metadata": generation_metadata,
                                "timestamp": time.time(),
                            },
                        )

                elif event.stage == GenerationStage.ERROR:
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "error",
                            "code": "GENERATION_FAILED",
                            "message": event.message,
                        },
                    )
                    return

            # 检查是否成功生成任务图
            if task_graph is None:
                await self.send_message(
                    conversation_id,
                    {
                        "type": "error",
                        "code": "GENERATION_FAILED",
                        "message": "决策链生成失败",
                    },
                )
                return

            # 5. 流式任务执行
            executor = self._get_task_executor()
            
            # 初始化执行跟踪变量
            self._execution_total_tasks = 0
            self._execution_completed_tasks = 0
            self._execution_task_results = {}
            self._user_input = plan_document[:100] if plan_document else ""  # 保存用户输入用于总结
            self._task_type = "plan_execution"
            self._task_graph = {"tasks": tasks}

            async for event in executor.execute(task_graph):
                if event.event_type == "execution_started":
                    # 初始化总任务数
                    self._execution_total_tasks = event.total_count
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_started",
                            "execution_id": f"exec_plan_{conversation_id}_{int(time.time())}",
                            "total_tasks": event.total_count,
                        },
                    )

                elif event.event_type == "task_update":
                    # 收集任务结果和 MCP 数据
                    if event.result and isinstance(event.result, dict):
                        self._execution_task_results[event.task_id] = event.result
                        if event.status and event.status.value == "completed":
                            self._execution_completed_tasks += 1
                        
                        # 从 output 中提取 MCP 工具返回的数据
                        output = event.result.get("output", {})
                        if output and isinstance(output, dict):
                            for key, value in output.items():
                                if isinstance(value, dict) and "data" in value:
                                    self._data_pool[key] = value.get("data")
                                elif key not in ("success", "status", "error"):
                                    self._data_pool[key] = value
                    
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "task_update",
                            "task_id": event.task_id,
                            "status": event.status.value if event.status else "unknown",
                            "result": event.result,
                            "error": event.error,
                            "detail": {
                                "stage": event.detail.stage if event.detail else "",
                                "message": event.detail.message if event.detail else "",
                                "progress": event.detail.progress if event.detail else 0,
                            } if event.detail else None,
                        },
                    )

                elif event.event_type == "execution_progress":
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_progress",
                            "completed_tasks": event.completed_count,
                            "total_tasks": event.total_count,
                            "progress": event.progress,
                        },
                    )

                elif event.event_type == "execution_complete":
                    result = executor.get_last_result()
                    
                    # 使用跟踪的变量构建 summary
                    summary = {
                        "total_tasks": self._execution_total_tasks,
                        "completed_tasks": self._execution_completed_tasks,
                        "failed_tasks": self._execution_total_tasks - self._execution_completed_tasks,
                    }
                    
                    # 收集节点结果
                    self._node_results = list(self._execution_task_results.values())
                    summary["task_results"] = self._node_results
                    
                    # 先发送 execution_complete 事件
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_complete",
                            "success": event.success,
                            "summary": summary,
                            "results": self._node_results,
                            "timestamp": time.time(),
                        },
                    )
                    
                    # 调用总结智能体生成专业总结
                    response_content = await self._generate_summary_with_ai(summary, event.success)

                    await self.send_message(
                        conversation_id,
                        {
                            "type": "assistant_message",
                            "content": response_content,
                        },
                    )

                elif event.event_type == "execution_error":
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "error",
                            "code": "EXECUTION_FAILED",
                            "message": event.error,
                        },
                    )

        except Exception as e:
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "PLAN_EXECUTION_FAILED",
                    "message": f"Plan 执行失败: {str(e)}",
                },
            )

    def _generate_plan_response(self, summary: Dict[str, Any], success: bool, plan_id: str) -> str:
        """生成 Plan 模式回复"""
        if not success:
            return f"Plan 执行失败。错误信息：{summary.get('error', '未知错误')}"

        total = summary.get('total_tasks', 0)
        completed = summary.get('completed_tasks', 0)

        return (
            f"✅ Plan 执行完成！\n\n"
            f"📋 Plan ID: {plan_id}\n"
            f"📊 执行统计：\n"
            f"- 总任务数：{total}\n"
            f"- 成功任务：{completed}"
        )


class ConfirmSpecHandler(MessageHandler):
    """Spec 模式确认处理器
    
    使用 ChainGenerator 从 Spec 文档生成决策链，
    使用 StreamingTaskExecutor 进行流式任务执行。
    """

    def __init__(self, manager: "ConnectionManager"):
        super().__init__(manager)
        self._chain_generator: Optional[ChainGenerator] = None
        self._task_executor: Optional[StreamingTaskExecutor] = None
        self._summarizer: Optional[SummarizerAgent] = None
        self._user_input: str = ""
        self._task_type: str = ""
        self._task_graph: Dict[str, Any] = {}
        self._node_results: List[Dict[str, Any]] = []
        self._data_pool: Dict[str, Any] = {}
        self._execution_total_tasks: int = 0
        self._execution_completed_tasks: int = 0
        self._execution_task_results: Dict[str, Any] = {}

    def _get_chain_generator(self) -> ChainGenerator:
        if self._chain_generator is None:
            self._chain_generator = ChainGenerator()
        return self._chain_generator

    def _get_task_executor(self) -> StreamingTaskExecutor:
        if self._task_executor is None:
            self._task_executor = StreamingTaskExecutor()
        return self._task_executor

    def _get_summarizer(self) -> SummarizerAgent:
        if self._summarizer is None:
            self._summarizer = SummarizerAgent(enable_streaming=False)
        return self._summarizer

    def _get_data_pool_snapshot(self) -> Dict[str, Any]:
        if hasattr(self._task_executor, '_data_pool'):
            try:
                return self._task_executor._data_pool.snapshot()
            except:
                pass
        return self._data_pool

    def _get_friendly_task_name(self, task_id: str, task_type: str = "") -> str:
        if not task_type and task_id:
            if "_" in task_id:
                task_type = "_".join(task_id.split("_")[:-1])
        
        task_num = ""
        if "_" in task_id:
            parts = task_id.split("_")
            if len(parts) >= 2:
                task_num = parts[-1]
        
        type_name = TASK_TYPE_FRIENDLY_NAMES.get(task_type, task_type or "任务")
        
        if task_num:
            return f"{type_name} #{task_num}"
        else:
            return type_name
    
    def _get_friendly_tool_name(self, tool_name: str) -> str:
        return MCP_TOOL_FRIENDLY_NAMES.get(tool_name, tool_name)

    async def _generate_summary_with_ai(self, summary: Dict[str, Any], success: bool) -> str:
        """使用总结智能体生成专业总结"""
        if not success:
            return f"任务执行失败。错误信息：{summary.get('error', '未知错误')}"

        try:
            summarizer = self._get_summarizer()
            data_pool_snapshot = self._get_data_pool_snapshot()
            
            from flood_decision_agent.core.message import MessageType
            summary_message = BaseMessage(
                type=MessageType.EVENT,
                sender="spec_handler",
                payload={
                    "task_request": {
                        "input": self._user_input,
                        "type": self._task_type,
                    },
                    "execution_summary": summary,
                    "data_pool_snapshot": data_pool_snapshot,
                    "task_graph": self._task_graph,
                    "node_results": self._node_results,
                }
            )
            
            summary_result = summarizer._process(summary_message)
            summary_text = summary_result.get("summary", "")
            
            if summary_text:
                return summary_text
            
        except Exception as e:
            pass
        
        return self._generate_fallback_response(summary)

    def _generate_fallback_response(self, summary: Dict[str, Any]) -> str:
        total = summary.get('total_tasks', 0)
        completed = summary.get('completed_tasks', 0)
        return f"任务执行完成！总任务数：{total}，成功任务：{completed}"

    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        """处理 Spec 确认消息"""
        feature_name = message.get("feature_name", "")
        action = message.get("action", "confirm")

        if not feature_name:
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "MISSING_FEATURE_NAME",
                    "message": "缺少功能名称",
                },
            )
            return

        if action == "cancel":
            await self.send_message(
                conversation_id,
                {
                    "type": "operation_cancelled",
                    "operation_type": "spec",
                    "reason": "用户取消",
                },
            )
            return

        try:
            # 1. 发送 Spec 确认成功
            await self.send_message(
                conversation_id,
                {
                    "type": "spec_confirmed",
                    "feature_name": feature_name,
                    "action": action,
                },
            )

            # 2. 加载 Spec 文档
            storage = get_file_storage()
            doc = storage.load_document(feature_name)

            if not doc:
                await self.send_message(
                    conversation_id,
                    {
                        "type": "error",
                        "code": "SPEC_NOT_FOUND",
                        "message": f"Spec 文档不存在: {feature_name}",
                    },
                )
                return

            spec_document = doc.get("content", "")
            user_input = doc.get("metadata", {}).get("user_input", "")

            # 3. 任务提取阶段
            await self.send_message(
                conversation_id,
                {
                    "type": "task_extracting",
                    "source": "spec",
                    "progress": 0.2,
                    "message": "正在从 Spec 文档提取任务...",
                },
            )

            # 4. 流式决策链生成（从 Spec）
            generator = self._get_chain_generator()
            task_graph = None
            generation_metadata = {}

            async for event in generator.generate_from_spec(spec_document, user_input):
                if event.stage == GenerationStage.INTENT_PARSING:
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "chain_generation_stage",
                            "stage": "task_extracting",
                            "stage_name": "任务提取",
                            "progress": event.progress,
                            "message": event.message,
                            "data": event.data,
                        },
                    )

                elif event.stage in [GenerationStage.TASK_DECOMPOSITION, GenerationStage.CHAIN_OPTIMIZATION, GenerationStage.TASK_GRAPH_BUILDING]:
                    stage_name_map = {
                        "task_decomposition": "任务分解",
                        "chain_optimization": "决策链优化",
                        "task_graph_building": "任务图构建",
                    }
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "chain_generation_stage",
                            "stage": event.stage.value,
                            "stage_name": stage_name_map.get(event.stage.value, event.stage.value),
                            "progress": event.progress,
                            "message": event.message,
                            "data": event.data,
                        },
                    )

                elif event.stage == GenerationStage.COMPLETED:
                    result = generator.get_last_result()
                    if result and result.success:
                        task_graph = result.task_graph
                        generation_metadata = result.metadata

                        # 发送任务图生成完成
                        nodes = task_graph.get_all_nodes()
                        tasks = []
                        for node_id, node in nodes.items():
                            task_type = getattr(node, 'task_type', 'unknown')
                            if hasattr(task_type, 'value'):
                                task_type = task_type.value

                            tasks.append({
                                "task_id": node_id,
                                "task_name": getattr(node, 'description', node_id),
                                "task_type": task_type,
                                "dependencies": list(getattr(node, 'dependencies', [])),
                                "status": "pending",
                            })

                        await self.send_message(
                            conversation_id,
                            {
                                "type": "task_graph_generated",
                                "tasks": tasks,
                                "total_count": len(tasks),
                                "reliability_score": generation_metadata.get("reliability_score", 0),
                            },
                        )

                        # 发送决策链生成完成
                        generation_id = f"gen_spec_{conversation_id}_{int(time.time())}"
                        
                        # 构建 edges
                        edges_list = []
                        for from_node, to_nodes in task_graph._edges.items():
                            for to_node in to_nodes:
                                edges_list.append({
                                    "from": from_node,
                                    "to": to_node,
                                })
                        
                        await self.send_message(
                            conversation_id,
                            {
                                "type": "chain_generated",
                                "generation_id": generation_id,
                                "mode": "spec",
                                "task_graph": {
                                    "tasks": tasks,
                                    "nodes": tasks,
                                    "edges": edges_list,
                                },
                                "reliability_score": generation_metadata.get("reliability_score", 0),
                                "metadata": generation_metadata,
                                "timestamp": time.time(),
                            },
                        )

                elif event.stage == GenerationStage.ERROR:
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "error",
                            "code": "GENERATION_FAILED",
                            "message": event.message,
                        },
                    )
                    return

            # 检查是否成功生成任务图
            if task_graph is None:
                await self.send_message(
                    conversation_id,
                    {
                        "type": "error",
                        "code": "GENERATION_FAILED",
                        "message": "决策链生成失败",
                    },
                )
                return

            # 5. 流式任务执行
            executor = self._get_task_executor()
            
            # 初始化执行跟踪变量
            self._execution_total_tasks = 0
            self._execution_completed_tasks = 0
            self._execution_task_results = {}
            self._user_input = spec_content[:100] if spec_content else ""
            self._task_type = "spec_execution"
            self._task_graph = {"tasks": tasks}

            async for event in executor.execute(task_graph):
                if event.event_type == "execution_started":
                    # 初始化总任务数
                    self._execution_total_tasks = event.total_count
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_started",
                            "execution_id": f"exec_spec_{conversation_id}_{int(time.time())}",
                            "total_tasks": event.total_count,
                        },
                    )

                elif event.event_type == "task_update":
                    # 收集任务结果和 MCP 数据
                    if event.result and isinstance(event.result, dict):
                        self._execution_task_results[event.task_id] = event.result
                        
                        # 从 output 中提取 MCP 工具返回的数据
                        output = event.result.get("output", {})
                        if output and isinstance(output, dict):
                            for key, value in output.items():
                                if isinstance(value, dict) and "data" in value:
                                    self._data_pool[key] = value.get("data")
                                elif key not in ("success", "status", "error"):
                                    self._data_pool[key] = value
                    
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "task_update",
                            "task_id": event.task_id,
                            "status": event.status.value if event.status else "unknown",
                            "result": event.result,
                            "error": event.error,
                            "detail": {
                                "stage": event.detail.stage if event.detail else "",
                                "message": event.detail.message if event.detail else "",
                                "progress": event.detail.progress if event.detail else 0,
                            } if event.detail else None,
                        },
                    )

                elif event.event_type == "execution_progress":
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_progress",
                            "completed_tasks": event.completed_count,
                            "total_tasks": event.total_count,
                            "progress": event.progress,
                        },
                    )

                elif event.event_type == "execution_complete":
                    result = executor.get_last_result()
                    
                    # 使用跟踪的变量构建 summary
                    summary = {
                        "total_tasks": self._execution_total_tasks,
                        "completed_tasks": self._execution_completed_tasks,
                        "failed_tasks": self._execution_total_tasks - self._execution_completed_tasks,
                    }
                    
                    # 收集节点结果
                    self._node_results = list(self._execution_task_results.values())
                    summary["task_results"] = self._node_results
                    
                    # 先发送 execution_complete 事件
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "execution_complete",
                            "success": event.success,
                            "summary": summary,
                            "results": self._node_results,
                            "timestamp": time.time(),
                        },
                    )
                    
                    # 调用总结智能体生成专业总结
                    response_content = await self._generate_summary_with_ai(summary, event.success)

                    await self.send_message(
                        conversation_id,
                        {
                            "type": "assistant_message",
                            "content": response_content,
                        },
                    )

                elif event.event_type == "execution_error":
                    await self.send_message(
                        conversation_id,
                        {
                            "type": "error",
                            "code": "EXECUTION_FAILED",
                            "message": event.error,
                        },
                    )

        except Exception as e:
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "SPEC_EXECUTION_FAILED",
                    "message": f"Spec 执行失败: {str(e)}",
                },
            )

    def _generate_spec_response(self, summary: Dict[str, Any], success: bool, feature_name: str) -> str:
        """生成 Spec 模式回复"""
        if not success:
            return f"Spec 执行失败。错误信息：{summary.get('error', '未知错误')}"

        total = summary.get('total_tasks', 0)
        completed = summary.get('completed_tasks', 0)

        return (
            f"✅ Spec 执行完成！\n\n"
            f"📋 功能名称: {feature_name}\n"
            f"📊 执行统计：\n"
            f"- 总任务数：{total}\n"
            f"- 成功任务：{completed}"
        )


class CancelOperationHandler(MessageHandler):
    """取消操作处理器"""

    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        """处理取消操作请求"""
        operation_type = message.get("operation_type", "")
        operation_id = message.get("operation_id", "")
        reason = message.get("reason", "用户请求")

        # 发送取消确认
        await self.send_message(
            conversation_id,
            {
                "type": "operation_cancelled",
                "operation_type": operation_type,
                "operation_id": operation_id,
                "reason": reason,
            },
        )

        # TODO: 实现实际的中断逻辑
        # 目前只是发送取消确认，实际的中断需要在执行器中实现


class StartPlanHandler(MessageHandler):
    """启动 Plan 模式处理器 - 生成 Plan 文档"""

    def __init__(self, manager: "ConnectionManager"):
        super().__init__(manager)
        self._llm_client: Optional[KimiClient] = None

    def _get_llm_client(self) -> KimiClient:
        if self._llm_client is None:
            self._llm_client = KimiClient()
        return self._llm_client

    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        """处理 Plan 模式启动请求 - 生成 Plan 文档"""
        user_input = message.get("user_input", "")
        plan_id = message.get("plan_id") or f"plan_{conversation_id}_{int(time.time())}"

        if not user_input:
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "EMPTY_INPUT",
                    "message": "用户输入不能为空",
                    "timestamp": time.time(),
                },
            )
            return

        # 发送开始标记
        await self.send_message(
            conversation_id,
            {
                "type": "generation_started",
                "document_id": plan_id,
                "document_type": "plan",
                "timestamp": time.time(),
            },
        )

        try:
            # 构建提示词上下文
            context = PromptContext(
                user_input=user_input,
                domain="水利调度",
            )

            # 获取规划生成提示词
            prompt = PlanSpecPrompts.get_plan_single_generation_prompt(context)
            system_prompt = PlanSpecPrompts.PLAN_GENERATOR_SYSTEM

            # 流式生成规划文档
            client = self._get_llm_client()
            accumulated_content = ""

            response_stream = client._client.chat.completions.create(
                model="moonshot-v1-32k",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=6000,
                stream=True,
            )

            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    part = chunk.choices[0].delta.content
                    accumulated_content += part

                    # 计算进度（简化处理）
                    progress = min(0.95, len(accumulated_content) / 3000)

                    await self.send_message(
                        conversation_id,
                        {
                            "type": "document_chunk",
                            "document_id": plan_id,
                            "document_type": "plan",
                            "content": part,
                            "accumulated": accumulated_content,
                            "progress": progress,
                            "timestamp": time.time(),
                        },
                    )
                    await asyncio.sleep(0.01)

            # 保存规划文档
            storage = get_file_storage()
            metadata = {
                "plan_id": plan_id,
                "created_at": time.time(),
                "status": "generated",
                "user_input": user_input,
            }
            storage.save_document(plan_id, accumulated_content, metadata)

            # 发送完成标记
            await self.send_message(
                conversation_id,
                {
                    "type": "document_complete",
                    "document_id": plan_id,
                    "document_type": "plan",
                    "content": accumulated_content,
                    "files": {
                        "plan": {
                            "title": "规划文档",
                            "content": accumulated_content,
                        }
                    },
                    "timestamp": time.time(),
                },
            )

        except Exception as e:
            await self.send_message(
                conversation_id,
                {
                    "type": "generation_error",
                    "code": "GENERATION_FAILED",
                    "message": f"生成规划失败: {str(e)}",
                    "timestamp": time.time(),
                },
            )


class StartSpecHandler(MessageHandler):
    """启动 Spec 模式处理器 - 生成 Spec 文档套组"""

    def __init__(self, manager: "ConnectionManager"):
        super().__init__(manager)
        self._llm_client: Optional[KimiClient] = None

    def _get_llm_client(self) -> KimiClient:
        if self._llm_client is None:
            self._llm_client = KimiClient()
        return self._llm_client

    async def handle(self, message: Dict[str, Any], conversation_id: str) -> None:
        """处理 Spec 模式启动请求 - 生成完整 Spec 套组"""
        user_input = message.get("user_input", "")
        feature_name = message.get("feature_name") or f"spec_{conversation_id}_{int(time.time())}"

        if not user_input:
            await self.send_message(
                conversation_id,
                {
                    "type": "error",
                    "code": "EMPTY_INPUT",
                    "message": "用户输入不能为空",
                    "timestamp": time.time(),
                },
            )
            return

        # 发送开始标记
        await self.send_message(
            conversation_id,
            {
                "type": "generation_started",
                "document_id": feature_name,
                "document_type": "spec",
                "timestamp": time.time(),
            },
        )

        try:
            # 使用 LLM 生成完整 Spec 套组
            client = self._get_llm_client()
            
            # 构建提示词
            system_prompt = """你是一个专业的软件规格说明书编写专家。
请根据用户需求生成完整的规格说明文档，包含以下部分：
1. 功能概述
2. 详细规格
3. 任务分解
4. 验收标准"""

            prompt = f"""请为以下需求生成完整的规格说明文档：

{user_input}

请按照以下格式输出：

# 功能概述
...

# 详细规格
...

# 任务分解
1. **任务名称**（预计耗时）
   - 具体内容：...
   - 交付物：...
   
# 验收标准
...
"""

            # 流式生成
            accumulated_content = ""
            response_stream = client._client.chat.completions.create(
                model="moonshot-v1-32k",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=6000,
                stream=True,
            )

            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    part = chunk.choices[0].delta.content
                    accumulated_content += part

                    progress = min(0.95, len(accumulated_content) / 3000)

                    await self.send_message(
                        conversation_id,
                        {
                            "type": "document_chunk",
                            "document_id": feature_name,
                            "document_type": "spec",
                            "content": part,
                            "accumulated": accumulated_content,
                            "progress": progress,
                            "timestamp": time.time(),
                        },
                    )
                    await asyncio.sleep(0.01)

            # 保存规格文档
            storage = get_file_storage()
            metadata = {
                "feature_name": feature_name,
                "created_at": time.time(),
                "status": "generated",
                "user_input": user_input,
            }
            storage.save_document(feature_name, accumulated_content, metadata)

            # 发送完成标记
            await self.send_message(
                conversation_id,
                {
                    "type": "document_complete",
                    "document_id": feature_name,
                    "document_type": "spec",
                    "content": accumulated_content,
                    "files": {
                        "spec": {
                            "title": "规格说明",
                            "content": accumulated_content,
                        }
                    },
                    "timestamp": time.time(),
                },
            )

        except Exception as e:
            await self.send_message(
                conversation_id,
                {
                    "type": "generation_error",
                    "code": "GENERATION_FAILED",
                    "message": f"生成规格失败: {str(e)}",
                    "timestamp": time.time(),
                },
            )


# ==================== 处理器注册表 ====================

HANDLER_MAP: Dict[str, type[MessageHandler]] = {
    # 基础消息
    "ping": PingHandler,
    "chat_message": ChatMessageHandler,
    
    # Plan/Spec 模式启动（生成文档）
    "start_plan": StartPlanHandler,
    "start_spec": StartSpecHandler,
    
    # Plan/Spec 确认（生成并执行决策链）
    "confirm_plan": ConfirmPlanHandler,
    "confirm_spec": ConfirmSpecHandler,
    
    # 操作控制
    "cancel_operation": CancelOperationHandler,
}


def get_handler(message_type: str, manager: "ConnectionManager") -> Optional[MessageHandler]:
    """
    获取消息处理器

    Args:
        message_type: 消息类型
        manager: 连接管理器

    Returns:
        对应的消息处理器实例，如果没有找到则返回 None
    """
    handler_class = HANDLER_MAP.get(message_type)
    if handler_class:
        return handler_class(manager)
    return None
