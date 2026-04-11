from __future__ import annotations

import json
import re
from asyncio import Future
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from flood_decision_agent.agents.prompts.water_domain_prompts import WaterDomainPrompts
from flood_decision_agent.core.parameter_types import (
    ParameterPlan,
    ParameterRequirement,
    ParameterSource,
    ParameterValue,
)
from flood_decision_agent.core.clarification_types import (
    ClarificationRequest,
    ClarificationResponse,
    ParameterPlannerState,
)
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.tools.registry import ToolRegistry, get_tool_registry

try:
    from flood_decision_agent.core.tool_types import ToolCandidate
except ImportError:
    ToolCandidate = None


class ParameterPlanner:
    """参数规划器 - 核心模块

    负责完整的参数提取、验证和用户澄清。

    5步参数规划流程：
    1. 从 user_input 提取数据 (LLM + water_domain_prompts)
    2. 从 data_pool 提取上下文数据 (前置任务输出)
    3. 从 water_domain_prompts 获取经验参数 (阈值、默认值)
    4. 使用 DataAcquisitionService 管理缺失数据 (按需)
    5. 验证数据符合工具 schema

    Attributes:
        tool_registry: 工具注册中心
        water_domain_prompts: 水利领域提示词
        on_clarification_needed: 回调函数 - 需要用户澄清时
    """

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        water_domain_prompts: Optional[WaterDomainPrompts] = None,
        on_clarification_needed: Optional[Callable[[ClarificationRequest], None]] = None,
        llm_client: Optional[Any] = None,
    ):
        self.tool_registry = tool_registry or get_tool_registry()
        self.water_domain_prompts = water_domain_prompts or WaterDomainPrompts()
        self.on_clarification_needed = on_clarification_needed
        self.llm_client = llm_client

        self._pending_requests: Dict[str, ClarificationRequest] = {}
        self._pending_futures: Dict[str, Future] = {}
        self._state: ParameterPlannerState = ParameterPlannerState.INITIALIZING

    @property
    def state(self) -> ParameterPlannerState:
        """获取当前状态"""
        return self._state

    async def plan_parameters(
        self,
        task_nodes: List[Any],
        intent: Any,
        data_pool: SharedDataPool,
    ) -> AsyncGenerator[Union[ParameterPlan, ClarificationRequest], None]:
        """异步生成参数计划

        Args:
            task_nodes: 任务节点列表 (TaskNodeInfo)
            intent: 任务意图 (TaskIntent)
            data_pool: 共享数据池

        Yields:
            - ParameterPlan: 完成的参数计划
            - ClarificationRequest: 需要用户澄清时
        """
        for node in task_nodes:
            self._state = ParameterPlannerState.EXTRACTING_FROM_INPUT

            from_input = await self._extract_from_input(
                intent.raw_input or "", node
            )

            self._state = ParameterPlannerState.EXTRACTING_FROM_CONTEXT
            from_context = await self._extract_from_context(data_pool, node)

            self._state = ParameterPlannerState.EXTRACTING_FROM_EXPERIENCE
            from_experience = await self._extract_from_experience(node)

            merged = self._merge_parameters(from_input, from_context, from_experience)

            selected_tool = self._select_tool(node.tool_candidates if hasattr(node, 'tool_candidates') else [])
            required_params = self._get_required_params(selected_tool)
            missing = self._find_missing_params(merged, required_params)

            if missing:
                self._state = ParameterPlannerState.WAITING_FOR_CLARIFICATION
                request = self._build_clarification_request(node, missing, merged)

                self._pending_requests[request.request_id] = request

                if self.on_clarification_needed:
                    self.on_clarification_needed(request)

                yield request

                user_provided = await self._wait_for_clarification(request.request_id)
                merged.extend(user_provided)

            self._state = ParameterPlannerState.VALIDATING
            validated = await self._validate_parameters(merged, required_params)

            self._state = ParameterPlannerState.COMPLETED
            plan = ParameterPlan(
                node_id=node.task_id if hasattr(node, 'task_id') else "unknown",
                task_type=node.task_type.value if hasattr(node.task_type, 'value') else str(node.task_type),
                selected_tool=selected_tool,
                parameters=validated,
            )

            yield plan

    def submit_clarification(self, response: ClarificationResponse) -> None:
        """提交用户澄清响应

        外部调用：WebSocket/API 层调用此方法将用户答案传回

        Args:
            response: 用户澄清响应
        """
        request_id = response.request_id
        if request_id not in self._pending_requests:
            return

        if request_id in self._pending_futures:
            future = self._pending_futures[request_id]
            if not future.done():
                future.set_result(response)

        del self._pending_requests[request_id]
        if request_id in self._pending_futures:
            del self._pending_futures[request_id]

    async def _extract_from_input(
        self,
        user_input: str,
        node: Any,
    ) -> List[ParameterValue]:
        """Step 1: 使用 LLM 从 user_input 提取数据"""
        if not self.llm_client or not user_input:
            return []

        try:
            domain_context = self.water_domain_prompts.get_expert_rules_prompt()

            prompt = f"""
从以下用户输入中提取任务所需的参数：

用户输入："{user_input}"

任务：{node.description if hasattr(node, 'description') else '未知任务'}

{domain_context}

请输出JSON格式的提取结果，格式：
{{
    "parameters": [
        {{
            "param_name": "参数名",
            "value": "参数值",
            "confidence": 0.95
        }}
    ]
}}
"""
            response = await self.llm_client.complete(prompt)

            extracted = self._parse_llm_extraction(response, ParameterSource.USER_INPUT)
            return extracted
        except Exception:
            return []

    async def _extract_from_context(
        self,
        data_pool: SharedDataPool,
        node: Any,
    ) -> List[ParameterValue]:
        """Step 2: 从 data_pool 提取上下文数据"""
        extracted = []

        dependencies = node.dependencies if hasattr(node, 'dependencies') else []
        for dep_id in dependencies:
            outputs = data_pool.find_by_prefix(f"tool:{dep_id}:")
            for key, value in outputs.items():
                param_name = key.split(":")[-1]
                extracted.append(ParameterValue(
                    param_name=param_name,
                    value=value,
                    source=ParameterSource.DATA_POOL,
                ))

        context_data = data_pool.find_by_prefix("context:")
        for key, value in context_data.items():
            param_name = key.split(":")[-1]
            extracted.append(ParameterValue(
                param_name=param_name,
                value=value,
                source=ParameterSource.DATA_POOL,
            ))

        return extracted

    async def _extract_from_experience(
        self,
        node: Any,
    ) -> List[ParameterValue]:
        """Step 3: 从 water_domain_prompts 获取经验参数"""
        extracted = []

        thresholds = self.water_domain_prompts.THRESHOLDS if hasattr(self.water_domain_prompts, 'THRESHOLDS') else {}

        task_type = ""
        if hasattr(node.task_type, 'value'):
            task_type = node.task_type.value
        elif hasattr(node, 'task_type'):
            task_type = str(node.task_type)

        if "reservoir" in task_type.lower() or "dispatch" in task_type.lower():
            dispatch_thresholds = thresholds.get("dispatch_control", {})
            for name, info in dispatch_thresholds.items():
                if isinstance(info, dict) and "value" in info:
                    extracted.append(ParameterValue(
                        param_name=name,
                        value=info["value"],
                        source=ParameterSource.EXPERIENCE,
                    ))

        if "rainfall" in task_type.lower() or "rain" in (node.description or "").lower():
            rainfall_thresholds = thresholds.get("rainfall", {})
            for name, info in rainfall_thresholds.items():
                if isinstance(info, dict) and "value" in info:
                    extracted.append(ParameterValue(
                        param_name=name,
                        value=info["value"],
                        source=ParameterSource.EXPERIENCE,
                    ))

        return extracted

    def _merge_parameters(
        self,
        from_input: List[ParameterValue],
        from_context: List[ParameterValue],
        from_experience: List[ParameterValue],
    ) -> List[ParameterValue]:
        """合并参数，按优先级覆盖"""
        merged: Dict[str, ParameterValue] = {}

        for param in from_experience:
            merged[param.param_name] = param

        for param in from_context:
            merged[param.param_name] = param

        for param in from_input:
            merged[param.param_name] = param

        return list(merged.values())

    def _select_tool(self, tool_candidates: List[Any]) -> str:
        """选择最终使用的工具"""
        if not tool_candidates:
            return "default_tool"

        sorted_candidates = sorted(
            tool_candidates,
            key=lambda x: getattr(x, 'priority', 50),
            reverse=True
        )
        return sorted_candidates[0].tool_name if hasattr(sorted_candidates[0], 'tool_name') else str(sorted_candidates[0])

    def _get_required_params(self, tool_name: str) -> List[ParameterRequirement]:
        """获取工具的参数需求"""
        tool_meta = self.tool_registry.get_metadata(tool_name)
        if tool_meta and hasattr(tool_meta, 'param_requirements'):
            return tool_meta.param_requirements or []
        return []

    def _find_missing_params(
        self,
        merged_params: List[ParameterValue],
        required_params: List[ParameterRequirement],
    ) -> List[ParameterRequirement]:
        """查找缺失的必需参数"""
        merged_names = {p.param_name for p in merged_params}
        missing = []

        for req in required_params:
            if req.required and req.param_name not in merged_names:
                if req.default_value is None:
                    missing.append(req)

        return missing

    def _build_clarification_request(
        self,
        node: Any,
        missing_params: List[ParameterRequirement],
        current_params: List[ParameterValue],
    ) -> ClarificationRequest:
        """构建澄清请求"""
        questions = []
        for param in missing_params:
            question = f"请提供 '{param.description or param.param_name}'"
            if param.default_value is not None:
                question += f"（默认值: {param.default_value}）"
            questions.append(question)

        return ClarificationRequest(
            node_id=node.task_id if hasattr(node, 'task_id') else "unknown",
            task_type=node.task_type.value if hasattr(node.task_type, 'value') else str(node.task_type),
            missing_params=missing_params,
            context={
                "current_params": [
                    {"name": p.param_name, "value": p.value, "source": p.source.value}
                    for p in current_params
                ],
                "task_description": node.description if hasattr(node, 'description') else "",
            },
            generated_questions=questions,
        )

    async def _validate_parameters(
        self,
        parameters: List[ParameterValue],
        required_params: List[ParameterRequirement],
    ) -> List[ParameterValue]:
        """验证参数"""
        validated = []
        param_dict = {p.param_name: p for p in parameters}

        for req in required_params:
            if req.param_name in param_dict:
                param = param_dict[req.param_name]
                validated.append(param)
            elif req.default_value is not None:
                validated.append(ParameterValue(
                    param_name=req.param_name,
                    value=req.default_value,
                    source=ParameterSource.EXPERIENCE,
                ))

        for param in parameters:
            if param.param_name not in [v.param_name for v in validated]:
                validated.append(param)

        return validated

    def _parse_llm_extraction(
        self,
        llm_response: str,
        source: ParameterSource,
    ) -> List[ParameterValue]:
        """解析 LLM 提取结果"""
        try:
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                params = result.get("parameters", [])
                return [
                    ParameterValue(
                        param_name=p.get("param_name", ""),
                        value=p.get("value"),
                        source=source,
                    )
                    for p in params
                ]
        except Exception:
            pass
        return []

    async def _wait_for_clarification(
        self,
        request_id: str,
    ) -> List[ParameterValue]:
        """等待用户澄清响应"""
        if request_id not in self._pending_requests:
            return []

        future: Future = Future()
        self._pending_futures[request_id] = future

        try:
            response = await future.result(timeout=300)
            return [
                ParameterValue(
                    param_name=param_name,
                    value=param_value,
                    source=ParameterSource.USER_PROVIDED,
                )
                for param_name, param_value in response.answers.items()
            ]
        except Exception:
            return []
        finally:
            if request_id in self._pending_futures:
                del self._pending_futures[request_id]
