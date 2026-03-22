"""意图解析模块 - 使用 LLM 工具进行意图识别.

模板作为上下文 prompt 喂给 LLM，支持官方工具（web_search）和自定义工具。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from openai import OpenAI

from flood_decision_agent.core.prompts import PromptTemplates, get_system_prompt
from flood_decision_agent.core.task_types import (
    BusinessTaskType,
    get_execution_types_for_business,
    ExecutionTaskType,
)
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key
from flood_decision_agent.tools.llm_tools import LLMToolManager, create_default_tool_manager


@dataclass
class TaskIntent:
    """任务意图数据类."""

    goal: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    task_type: BusinessTaskType = BusinessTaskType.UNKNOWN
    raw_input: Optional[str] = None
    execution_steps: List[ExecutionTaskType] = field(default_factory=list)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "constraints": self.constraints,
            "context": self.context,
            "task_type": self.task_type.value,
            "raw_input": self.raw_input,
            "execution_steps": [e.value for e in self.execution_steps],
            "error_message": self.error_message,
        }


class IntentParser:
    """基于 LLM 工具的意图解析器.

    使用工具系统支持 web_search 等官方工具。
    """

    # 模板定义（作为上下文）
    _TEMPLATES = [
        {
            "name": "flood_warning",
            "task_type": "flood_warning",
            "description": "洪水预警分析",
            "keywords": ["洪水", "预警", "预报", "警戒", "水位", "超警", "洪峰", "水情"],
        },
        {
            "name": "flood_dispatch",
            "task_type": "flood_dispatch",
            "description": "洪水调度",
            "keywords": ["洪水", "泄洪", "防洪", "洪峰", "出库", "流量", "调度"],
        },
        {
            "name": "reservoir_dispatch",
            "task_type": "reservoir_dispatch",
            "description": "水库调度",
            "keywords": ["水库", "调度", "水位", "出库", "入库", "蓄水", "放水"],
        },
        {
            "name": "drought_dispatch",
            "task_type": "drought_dispatch",
            "description": "干旱调度",
            "keywords": ["干旱", "枯水", "蓄水", "保水", "供水", "抗旱"],
        },
        {
            "name": "data_query",
            "task_type": "data_query",
            "description": "数据查询",
            "keywords": ["查询", "数据", "水位", "流量", "降雨", "历史"],
        },
        {
            "name": "weather_forecast",
            "task_type": "weather_forecast",
            "description": "天气预报",
            "keywords": ["天气", "预报", "温度", "降雨", "降水", "气象"],
        },
        {
            "name": "risk_assessment",
            "task_type": "risk_assessment",
            "description": "风险评估",
            "keywords": ["风险", "评估", "安全", "危险", "隐患", "分析"],
        },
        {
            "name": "emergency_response",
            "task_type": "emergency_response",
            "description": "应急响应",
            "keywords": ["应急", "响应", "抢险", "救援", "灾情", "险情"],
        },
        {
            "name": "watershed_analysis",
            "task_type": "watershed_analysis",
            "description": "流域分析",
            "keywords": ["流域", "分析", "水文", "降雨", "产流", "汇流"],
        },
        {
            "name": "strategic_planning",
            "task_type": "strategic_planning",
            "description": "战略规划",
            "keywords": ["规划", "战略", "长期", "防洪体系", "工程"],
        },
    ]

    def __init__(self, use_tools: bool = False):
        """初始化解析器.

        Args:
            use_tools: 是否启用工具（web_search 等），默认关闭以启用流式传输
        """
        self.use_tools = use_tools
        self._client: Optional[OpenAI] = None
        self._tool_manager: Optional[LLMToolManager] = None
        self._init_llm_client()

    def _init_llm_client(self) -> None:
        """初始化 LLM 客户端和工具管理器."""
        try:
            api_key = require_kimi_api_key()
            self._client = OpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.cn/v1",
            )
            
            # 初始化工具管理器
            if self.use_tools:
                self._tool_manager = create_default_tool_manager(self._client)
                
        except Exception as e:
            print(f"警告: 无法初始化 LLM 客户端: {e}")
            self._client = None
            self._tool_manager = None

    def parse(self, user_input: str) -> TaskIntent:
        """解析用户输入.

        使用 LLM 工具进行意图识别，支持 web_search。

        Args:
            user_input: 用户输入文本

        Returns:
            解析后的任务意图
        """
        if not self._client:
            return TaskIntent(
                task_type=BusinessTaskType.UNKNOWN,
                raw_input=user_input,
                error_message="LLM 客户端未初始化",
            )

        # 使用新的提示词模板
        prompt = PromptTemplates.get_intent_parser_prompt(
            user_input=user_input,
            templates=self._TEMPLATES,
            use_template_context=True,
        )

        try:
            # 构建消息（使用新的系统提示词）
            messages = [
                {"role": "system", "content": get_system_prompt("intent_parser")},
                {"role": "user", "content": prompt},
            ]

            # 定义 prefix（预填的 JSON 开头），引导模型输出格式
            prefix = '{\n    "task_type": "'

            # 使用工具管理器进行对话（如果启用）
            if self.use_tools and self._tool_manager:
                # 工具模式下不使用 prefix
                content = self._tool_manager.chat_with_tools(
                    messages=messages,
                    model="moonshot-v1-8k",
                    temperature=0.1,
                    max_tokens=800,
                )
            else:
                # 不使用工具，使用 prefix mode + 流式传输
                print("\n[AI 思考中...]", end="", flush=True)
                
                response_stream = self._client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=800,
                    stream=True,  # 启用流式传输
                    extra_body={
                        "prefix": prefix,
                    },
                )
                
                # 收集流式输出
                content_parts = []
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        part = chunk.choices[0].delta.content
                        content_parts.append(part)
                        print(part, end="", flush=True)  # 实时输出到控制台
                
                print()  # 换行
                content = "".join(content_parts)

            # 如果使用了 prefix，需要补全开头的括号
            if not content.strip().startswith("{"):
                content = prefix + content

            # 解析 JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                task_type_str = result.get("task_type", "unknown")
                error_message = result.get("error_message")

                # 如果有错误信息，返回错误
                if error_message:
                    return TaskIntent(
                        task_type=BusinessTaskType.UNKNOWN,
                        raw_input=user_input,
                        error_message=error_message,
                    )

                try:
                    task_type = BusinessTaskType(task_type_str)
                except ValueError:
                    task_type = BusinessTaskType.UNKNOWN
                    error_message = f"未知的任务类型: {task_type_str}"

                # 置信度检查
                confidence = result.get("confidence", 0.5)
                if confidence < 0.5:
                    task_type = BusinessTaskType.UNKNOWN
                    error_message = "置信度太低，无法确定任务类型"

                # 获取执行步骤
                execution_steps = get_execution_types_for_business(task_type)

                return TaskIntent(
                    goal=result.get("goal", {"description": user_input}),
                    constraints=result.get("constraints", {}),
                    task_type=task_type,
                    raw_input=user_input,
                    execution_steps=execution_steps,
                    error_message=error_message,
                )
            else:
                return TaskIntent(
                    task_type=BusinessTaskType.UNKNOWN,
                    raw_input=user_input,
                    error_message="LLM 返回格式错误，无法解析 JSON",
                )

        except Exception as e:
            return TaskIntent(
                task_type=BusinessTaskType.UNKNOWN,
                raw_input=user_input,
                error_message=f"LLM 解析失败: {str(e)}",
            )

    def parse_structured(self, data: Dict[str, Any]) -> TaskIntent:
        """解析结构化数据."""
        task_type_str = data.get("type", "unknown")
        try:
            task_type = BusinessTaskType(task_type_str)
        except ValueError:
            task_type = BusinessTaskType.UNKNOWN

        execution_steps = get_execution_types_for_business(task_type)

        return TaskIntent(
            goal=data.get("params", {}),
            constraints={},
            task_type=task_type,
            raw_input=str(data),
            execution_steps=execution_steps,
        )

    def parse_natural_language(self, text: str) -> TaskIntent:
        """解析自然语言输入（别名）."""
        return self.parse(text)
