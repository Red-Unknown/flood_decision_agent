"""单元任务执行 Agent - 支持动态工具选择和自主选用"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from flood_decision_agent.core.agent import BaseAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.fusion.decision_fusion import DecisionFusion
from flood_decision_agent.tools.registry import ToolMetadata, ToolRegistry, get_tool_registry
from flood_decision_agent.tools.common_tools import CommonTools


class UnitTaskExecutionAgent(BaseAgent):
    """单元任务执行 Agent
    
    特性：
    1. 优先使用上游Agent指定的工具列表
    2. 上游未指定时，可从常用工具库自主选用
    3. 支持多种执行策略：single/parallel/fallback/auto
    """

    def __init__(
        self,
        agent_id: str = "UnitTaskExecutor",
        fusion: Optional[DecisionFusion] = None,
        tool_registry: Optional[ToolRegistry] = None,
        enable_common_tools: bool = True,
        handlers: Optional[Dict[str, Any]] = None,  # 向后兼容参数
    ):
        super().__init__(agent_id)
        self.fusion = fusion or DecisionFusion()
        self.tool_registry = tool_registry or get_tool_registry()
        self.tool_registry.set_logger(self.logger)
        
        # 向后兼容：注册旧式 handlers 为工具
        if handlers:
            self._register_legacy_handlers(handlers)
        
        # 注册常用工具（使用当前注册表）
        if enable_common_tools:
            CommonTools.register_all(self.tool_registry)
            self.logger.info(f"常用工具已注册，共 {len(self.tool_registry.list_tools())} 个")
    
    def _register_legacy_handlers(self, handlers: Dict[str, Any]) -> None:
        """注册旧式 handlers 为工具（向后兼容）"""
        from flood_decision_agent.tools.registry import ToolMetadata
        
        for name, handler in handlers.items():
            # 包装旧式 handler 为新式 tool
            def wrapper(data_pool, config, handler=handler):
                return handler(data_pool)
            
            self.tool_registry.register(
                name,
                wrapper,
                ToolMetadata(
                    name=name,
                    description=f"Legacy handler: {name}",
                    task_types={"legacy"},
                    priority=50,
                )
            )
            self.logger.debug(f"注册旧式 handler: {name}")

    def _process(self, message: BaseMessage) -> Dict[str, Any]:
        """处理单元任务执行请求"""
        payload = message.payload
        
        # 1. 解析消息
        node_id = payload.get("node_id", "unknown")
        task_type = payload.get("task_type", "default")
        tools_spec = payload.get("tools", [])  # 上游指定的工具列表
        execution_strategy = payload.get("execution_strategy", "auto")
        data_pool = payload.get("data_pool")
        context = payload.get("context", {})
        
        if not data_pool:
            raise ValueError("消息 payload 必须包含 'data_pool'")
        
        self.logger.info(f"[节点 {node_id}] 开始执行，任务类型: {task_type}, 策略: {execution_strategy}")
        
        # 2. 工具选择决策
        selected_tools = self._select_tools(tools_spec, task_type, context)
        
        if not selected_tools:
            raise ValueError(f"未找到适合任务类型 '{task_type}' 的工具")
        
        self.logger.info(f"选定工具: {[t['tool_name'] for t in selected_tools]}")
        
        # 3. 确定执行策略
        strategy = self._determine_strategy(execution_strategy, selected_tools, task_type)
        self.logger.info(f"执行策略: {strategy}")
        
        # 4. 执行任务
        start_time = time.time()
        results = self._execute_with_strategy(selected_tools, data_pool, strategy)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # 5. 结果处理
        if len(results) > 1 and strategy in ("parallel", "auto"):
            # 多结果融合
            fused_result = self._fuse_results(results)
        else:
            fused_result = results[0] if results else {}
        
        # 6. 构建响应
        response = {
            "node_id": node_id,
            "task_type": task_type,
            "status": "success",
            "output": fused_result,
            "metrics": {
                "elapsed_time_ms": elapsed_ms,
                "tools_used": [t['tool_name'] for t in selected_tools],
                "execution_strategy": strategy,
                "tool_count": len(selected_tools),
            }
        }
        
        self.logger.info(f"[节点 {node_id}] 执行完成，耗时: {elapsed_ms:.2f}ms")
        return response

    def _select_tools(
        self,
        tools_spec: List[Dict[str, Any]],
        task_type: str,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """工具选择决策 - 补充策略
        
        核心逻辑：
        1. 优先使用上游指定的工具
        2. 当上游工具不足（缺失或不可用）时，从常用工具库自主选用补充
        
        补充触发条件：
        - 上游未指定任何工具
        - 上游指定的工具部分不可用
        - 上游指定的工具数量不足以完成任务（根据任务类型判断）
        """
        allow_auto_select = context.get("allow_auto_select", True)
        selected_tools = []
        
        # 步骤1：验证并使用上游指定的工具
        if tools_spec:
            for tool in tools_spec:
                tool_name = tool.get("tool_name")
                if self.tool_registry.is_available(tool_name):
                    selected_tools.append(tool)
                    self.logger.debug(f"上游指定工具 '{tool_name}' 验证通过")
                else:
                    self.logger.warning(f"上游指定工具 '{tool_name}' 不可用，将从常用工具库选用补充")
        
        # 步骤2：检查是否需要自主选用补充
        need_supplement = False
        
        if not selected_tools:
            # 情况A：上游未指定，或指定的全部不可用
            self.logger.info("上游未提供可用工具，将自主选用")
            need_supplement = True
        elif len(selected_tools) < self._get_min_tools_required(task_type):
            # 情况B：工具数量不足（根据任务类型判断）
            self.logger.info(f"上游工具数量不足（{len(selected_tools)} < {self._get_min_tools_required(task_type)}），将补充选用")
            need_supplement = True
        
        # 步骤3：自主选用补充
        if need_supplement and allow_auto_select:
            supplement_tools = self._auto_select_tools(task_type, exclude_names={t["tool_name"] for t in selected_tools})
            if supplement_tools:
                self.logger.info(f"自主选用补充工具: {[t['tool_name'] for t in supplement_tools]}")
                selected_tools.extend(supplement_tools)
        
        return selected_tools
    
    def _get_min_tools_required(self, task_type: str) -> int:
        """根据任务类型判断最少需要多少工具"""
        # 简单启发式规则，可根据实际需求调整
        multi_tool_tasks = {
            "hydrological_model": 2,  # 通常需要数据获取+计算
            "reservoir_dispatch": 2,  # 通常需要计算+方案生成
            "data_query": 1,
            "format": 1,
            "compute": 1,
            "log": 1,
        }
        return multi_tool_tasks.get(task_type, 1)

    def _auto_select_tools(
        self, 
        task_type: str,
        exclude_names: Optional[set] = None
    ) -> List[Dict[str, Any]]:
        """根据任务类型从常用工具库选择工具
        
        Args:
            task_type: 任务类型
            exclude_names: 需要排除的工具名称集合（避免重复选择上游已指定的工具）
        """
        exclude_names = exclude_names or set()
        matching_tools = self.tool_registry.find_by_task_type(task_type)
        
        if not matching_tools:
            # 尝试更宽泛的任务类型匹配
            broad_types = self._get_broad_task_types(task_type)
            for broad_type in broad_types:
                matching_tools = self.tool_registry.find_by_task_type(broad_type)
                if matching_tools:
                    break
        
        if not matching_tools:
            return []
        
        # 过滤掉已排除的工具，选择优先级最高的前3个
        selected = [
            tool for tool in matching_tools 
            if tool.name not in exclude_names
        ][:3]
        
        return [
            {
                "tool_name": tool.name,
                "tool_config": {},
                "priority": tool.priority,
            }
            for tool in selected
        ]

    def _get_broad_task_types(self, task_type: str) -> List[str]:
        """获取更宽泛的任务类型"""
        # 任务类型层次结构
        hierarchy = {
            "hydrological_model": ["compute", "data_query"],
            "reservoir_dispatch": ["compute", "log"],
            "data_query": ["data_query"],
            "format": ["format"],
        }
        return hierarchy.get(task_type, ["data_query"])

    def _determine_strategy(
        self,
        execution_strategy: str,
        tools: List[Dict[str, Any]],
        task_type: str,
    ) -> str:
        """确定执行策略"""
        if execution_strategy != "auto":
            return execution_strategy
        
        # auto策略的决策逻辑
        tool_count = len(tools)
        
        if tool_count == 1:
            return "single"
        
        # 某些任务类型适合并行
        parallel_friendly = {"compute", "statistics", "data_query"}
        if task_type in parallel_friendly:
            return "parallel"
        
        # 需要可靠性的任务使用fallback
        reliability_required = {"reservoir_dispatch", "flood_warning"}
        if task_type in reliability_required:
            return "fallback"
        
        # 默认使用parallel
        return "parallel"

    def _execute_with_strategy(
        self,
        tools: List[Dict[str, Any]],
        data_pool: SharedDataPool,
        strategy: str,
    ) -> List[Dict[str, Any]]:
        """按策略执行工具"""
        if strategy == "single":
            tool = tools[0]
            result = self._execute_single_tool(tool, data_pool)
            return [result]
        
        elif strategy == "parallel":
            return self._execute_parallel(tools, data_pool)
        
        elif strategy == "fallback":
            return self._execute_fallback(tools, data_pool)
        
        elif strategy == "ensemble":
            # 集成策略：并行执行所有工具并合并结果
            return self._execute_parallel(tools, data_pool)
        
        elif strategy == "no_handler":
            # 无处理程序策略：返回空结果
            self.logger.warning(f"策略为 'no_handler'，无可用工具执行")
            return [{
                "tool_name": "none",
                "success": True,
                "data": {},
                "message": "No handler available for this task",
            }]
        
        else:
            raise ValueError(f"未知的执行策略: {strategy}")

    def _execute_single_tool(
        self,
        tool_spec: Dict[str, Any],
        data_pool: SharedDataPool,
    ) -> Dict[str, Any]:
        """执行单个工具"""
        tool_name = tool_spec["tool_name"]
        tool_config = tool_spec.get("tool_config", {})
        
        try:
            result = self.tool_registry.execute(tool_name, data_pool, tool_config)
            return {
                "tool_name": tool_name,
                "success": True,
                "data": result,
            }
        except Exception as e:
            self.logger.error(f"工具 {tool_name} 执行失败: {e}")
            return {
                "tool_name": tool_name,
                "success": False,
                "error": str(e),
            }

    def _execute_parallel(
        self,
        tools: List[Dict[str, Any]],
        data_pool: SharedDataPool,
    ) -> List[Dict[str, Any]]:
        """并行执行多个工具"""
        results = []
        
        # 使用线程池或异步执行
        # 这里简化为顺序执行，实际可优化为并发
        for tool in tools:
            result = self._execute_single_tool(tool, data_pool)
            results.append(result)
        
        return results

    def _execute_fallback(
        self,
        tools: List[Dict[str, Any]],
        data_pool: SharedDataPool,
    ) -> List[Dict[str, Any]]:
        """降级策略：按优先级依次尝试"""
        # 按优先级排序
        sorted_tools = sorted(tools, key=lambda t: t.get("priority", 100))
        
        for tool in sorted_tools:
            result = self._execute_single_tool(tool, data_pool)
            if result["success"]:
                return [result]
        
        # 全部失败，返回最后一个错误
        return [result] if result else []

    def _fuse_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """融合多个工具的执行结果"""
        successful = [r for r in results if r.get("success")]
        
        if not successful:
            # 全部失败
            return {
                "success": False,
                "errors": [r.get("error") for r in results],
            }
        
        if len(successful) == 1:
            return successful[0]["data"]
        
        # 使用决策融合模块
        candidates = [s["data"] for s in successful]
        fused = self.fusion.fuse(candidates)
        
        return fused.value if hasattr(fused, 'value') else fused

    def execute_task(
        self,
        node_id: str,
        task_type: str,
        data_pool: SharedDataPool,
        tools: Optional[List[Dict[str, Any]]] = None,
        execution_strategy: str = "auto",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """便捷方法：直接执行任务（无需构造消息）"""
        message = BaseMessage(
            type=MessageType.NODE_EXECUTE,
            payload={
                "node_id": node_id,
                "task_type": task_type,
                "tools": tools or [],
                "execution_strategy": execution_strategy,
                "data_pool": data_pool,
                "context": context or {},
            },
            sender="direct_call",
        )
        return self.execute(message)

    def list_available_tools(self) -> List[str]:
        """列出所有可用工具"""
        return self.tool_registry.list_tools()

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具信息"""
        meta = self.tool_registry.get_metadata(tool_name)
        if meta:
            return {
                "name": meta.name,
                "description": meta.description,
                "task_types": list(meta.task_types),
                "priority": meta.priority,
                "required_keys": list(meta.required_keys),
                "output_keys": list(meta.output_keys),
            }
        return None


def build_default_handlers(mock_generator: Any) -> Dict[str, HandlerFn]:
    """构建默认处理器（向后兼容）"""
    import pandas as pd

    def get_rainfall_forecast(data_pool: SharedDataPool) -> dict[str, Any]:
        rainfall = mock_generator.generate_rainfall_forecast()
        report = mock_generator.validate_rainfall_forecast(rainfall)
        if not report.ok:
            raise ValueError("; ".join(report.errors))
        return {"rainfall_forecast": rainfall}

    def get_inflow_forecast(data_pool: SharedDataPool) -> dict[str, Any]:
        rainfall: pd.DataFrame = data_pool.get("rainfall_forecast")
        inflow = mock_generator.generate_inflow_forecast(rainfall)
        report = mock_generator.validate_inflow_forecast(inflow)
        if not report.ok:
            raise ValueError("; ".join(report.errors))
        alignment = mock_generator.validate_pair_alignment(rainfall, inflow)
        if not alignment.ok:
            raise ValueError("; ".join(alignment.errors))
        return {"inflow_forecast": inflow}

    def compute_dispatch_plan(data_pool: SharedDataPool) -> dict[str, Any]:
        inflow: pd.DataFrame = data_pool.get("inflow_forecast")
        peak = float(inflow["inflow_m3s"].max())
        target_peak = 19000.0
        gate_ratio = min(1.0, target_peak / max(peak, 1.0))
        plan = {
            "strategy": "conventional",
            "peak_inflow_m3s": peak,
            "gate_ratio": gate_ratio,
        }
        return {"dispatch_plan": plan}

    def generate_dispatch_order(data_pool: SharedDataPool) -> dict[str, Any]:
        plan: dict[str, Any] = data_pool.get("dispatch_plan")
        text = (
            "调令草稿：\n"
            f"- 策略：{plan['strategy']}\n"
            f"- 预测入库洪峰：{plan['peak_inflow_m3s']:.1f} m3/s\n"
            f"- 建议闸门系数：{plan['gate_ratio']:.3f}\n"
        )
        return {"dispatch_order_text": text}

    return {
        "get_rainfall_forecast": get_rainfall_forecast,
        "get_inflow_forecast": get_inflow_forecast,
        "compute_dispatch_plan": compute_dispatch_plan,
        "generate_dispatch_order": generate_dispatch_order,
    }
