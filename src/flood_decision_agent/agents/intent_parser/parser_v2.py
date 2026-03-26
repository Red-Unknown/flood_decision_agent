"""意图解析模块 V2 - 支持 LLM 回退.

优先使用模板匹配，如果匹配失败则调用 LLM 进行解析。
使用统一的 TaskType 枚举。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Tuple

from openai import OpenAI

from flood_decision_agent.core.task_types import (
    BusinessTaskType,
    get_business_type_description,
)
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key


@dataclass
class TaskIntent:
    """任务意图数据类.

    Attributes:
        goal: 任务目标
        constraints: 任务约束条件
        context: 上下文信息
        task_type: 任务类型
        raw_input: 原始输入
    """

    goal: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    task_type: BusinessTaskType = BusinessTaskType.UNKNOWN
    raw_input: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return {
            "goal": self.goal,
            "constraints": self.constraints,
            "context": self.context,
            "task_type": self.task_type.value,
            "raw_input": self.raw_input,
        }


class IntentTemplate:
    """意图模板类，用于规则匹配."""

    def __init__(
        self,
        name: str,
        task_type: BusinessTaskType,
        keywords: List[str],
        patterns: List[Pattern[str]],
        extractors: Dict[str, Pattern[str]],
    ):
        self.name = name
        self.task_type = task_type
        self.keywords = keywords
        self.patterns = patterns
        self.extractors = extractors


class IntentParserV2:
    """意图解析器 V2.

    策略:
    1. 优先使用模板匹配（快速、确定性强）
    2. 模板匹配失败时，调用 LLM 解析（智能、通用性强）
    """

    # 预定义的模板
    _TEMPLATES: List[IntentTemplate] = [
        # 洪水预警模板
        IntentTemplate(
            name="flood_warning",
            task_type=BusinessTaskType.FLOOD_WARNING,
            keywords=["洪水", "预警", "预报", "警戒", "水位", "超警", "洪峰"],
            patterns=[
                re.compile(r".*?(?:洪水|洪峰).*?(?:预警|预报).*?"),
                re.compile(r".*?(?:水位|流量).*?(?:超警|超保|警戒).*?"),
            ],
            extractors={
                "station": re.compile(r"([\u4e00-\u9fa5]+(?:站|大坝|水库))"),
                "water_level": re.compile(r"(\d+(?:\.\d+)?)\s*(?:米|m)"),
                "flow_rate": re.compile(r"(\d+(?:\.\d+)?)\s*(?:立方米每秒|m³/s|方)"),
            },
        ),
        # 洪水调度模板
        IntentTemplate(
            name="flood_dispatch",
            task_type=BusinessTaskType.FLOOD_DISPATCH,
            keywords=["洪水", "泄洪", "防洪", "洪峰", "出库", "流量", "调度"],
            patterns=[
                re.compile(r".*?(?:洪水|泄洪|防洪).*?"),
                re.compile(r".*?出库.*?流量.*?"),
                re.compile(r".*?(?:三峡|葛洲坝|小浪底|丹江口).*?(?:调度|泄洪)"),
            ],
            extractors={
                "reservoir": re.compile(r"(三峡大坝|三峡|葛洲坝|小浪底|丹江口)"),
                "outflow": re.compile(r"(\d+(?:\.\d+)?)\s*(?:立方米每秒|m³/s|方每秒)"),
                "target_level": re.compile(r"(?:水位|降至|调整到)\s*(\d+(?:\.\d+)?)\s*(?:米|m)"),
            },
        ),
        # 水库调度模板
        IntentTemplate(
            name="reservoir_dispatch",
            task_type=BusinessTaskType.RESERVOIR_DISPATCH,
            keywords=["水库", "调度", "水位", "出库", "入库", "蓄水", "放水"],
            patterns=[
                re.compile(r".*?(?:水库|大坝).*?(?:调度|调整).*?"),
                re.compile(r".*?(?:出库|入库|流量).*?(?:调整|控制).*?"),
            ],
            extractors={
                "reservoir": re.compile(r"([\u4e00-\u9fa5]+(?:水库|大坝))"),
                "water_level": re.compile(r"(\d+(?:\.\d+)?)\s*(?:米|m)"),
                "flow_rate": re.compile(r"(\d+(?:\.\d+)?)\s*(?:立方米每秒|m³/s)"),
            },
        ),
        # 干旱调度模板
        IntentTemplate(
            name="drought_dispatch",
            task_type=BusinessTaskType.DROUGHT_DISPATCH,
            keywords=["干旱", "枯水", "蓄水", "保水", "供水", "抗旱"],
            patterns=[
                re.compile(r".*?(?:干旱|枯水|抗旱).*?"),
                re.compile(r".*?(?:蓄水|保水|供水).*?"),
            ],
            extractors={
                "reservoir": re.compile(r"([\u4e00-\u9fa5]+(?:水库|大坝))"),
                "water_supply": re.compile(r"(\d+(?:\.\d+)?)\s*(?:万方|万立方米)"),
            },
        ),
        # 数据查询模板
        IntentTemplate(
            name="data_query",
            task_type=BusinessTaskType.DATA_QUERY,
            keywords=["查询", "数据", "水位", "流量", "降雨", "历史"],
            patterns=[
                re.compile(r".*?查询.*?(?:数据|水位|流量|降雨).*?"),
                re.compile(r".*?(?:最近|历史).*?(?:数据|记录).*?"),
            ],
            extractors={
                "station": re.compile(r"([\u4e00-\u9fa5]+(?:站|大坝|水库))"),
                "data_type": re.compile(r"(水位|流量|降雨|雨量|含沙量)"),
                "time_range": re.compile(r"(最近\d+天|最近\d+小时|历史)"),
            },
        ),
        # 天气预报模板
        IntentTemplate(
            name="weather_forecast",
            task_type=BusinessTaskType.WEATHER_FORECAST,
            keywords=["天气", "预报", "温度", "降雨", "降水", "气象"],
            patterns=[
                re.compile(r".*?(?:天气|气象).*?(?:预报|预测|怎么样).*?"),
                re.compile(r".*?(?:明天|未来|接下来).*?(?:天气|降雨).*?"),
            ],
            extractors={
                "location": re.compile(r"([\u4e00-\u9fa5]+(?:市|县|区|镇))"),
                "days": re.compile(r"(\d+)\s*(?:天|日)"),
            },
        ),
        # 风险评估模板
        IntentTemplate(
            name="risk_assessment",
            task_type=BusinessTaskType.RISK_ASSESSMENT,
            keywords=["风险", "评估", "安全", "危险", "隐患", "分析"],
            patterns=[
                re.compile(r".*?(?:风险|安全).*?(?:评估|分析|评价).*?"),
                re.compile(r".*?(?:洪水|溃坝|险情).*?(?:风险|可能性).*?"),
            ],
            extractors={
                "area": re.compile(r"([\u4e00-\u9fa5]+(?:市|县|区|流域))"),
                "risk_type": re.compile(r"(洪水|溃坝|干旱|地质灾害)"),
            },
        ),
        # 应急响应模板
        IntentTemplate(
            name="emergency_response",
            task_type=BusinessTaskType.EMERGENCY_RESPONSE,
            keywords=["应急", "响应", "抢险", "救援", "灾情", "险情"],
            patterns=[
                re.compile(r".*?(?:应急|抢险|救援).*?(?:响应|方案|措施).*?"),
                re.compile(r".*?(?:发生|出现).*?(?:险情|灾情|溃坝).*?"),
            ],
            extractors={
                "emergency_type": re.compile(r"(洪水|溃坝|险情|灾情)"),
                "location": re.compile(r"([\u4e00-\u9fa5]+(?:市|县|区|镇))"),
            },
        ),
    ]

    def __init__(self, use_llm_fallback: bool = True):
        """初始化意图解析器.

        Args:
            use_llm_fallback: 是否使用 LLM 作为回退策略
        """
        self.use_llm_fallback = use_llm_fallback
        self._client: Optional[OpenAI] = None

        if use_llm_fallback:
            self._init_llm_client()

    def _init_llm_client(self) -> None:
        """初始化 LLM 客户端."""
        try:
            api_key = require_kimi_api_key()
            self._client = OpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.cn/v1",
            )
        except Exception as e:
            print(f"警告: 无法初始化 LLM 客户端: {e}")
            self._client = None

    def parse(self, user_input: str) -> TaskIntent:
        """解析用户输入.

        策略:
        1. 优先尝试模板匹配
        2. 模板匹配失败且允许 LLM 回退时，调用 LLM
        3. 否则返回 UNKNOWN

        Args:
            user_input: 用户输入文本

        Returns:
            解析后的任务意图
        """
        # 步骤 1: 尝试模板匹配
        intent = self._try_template_match(user_input)
        if intent.task_type != BusinessTaskType.UNKNOWN:
            return intent

        # 步骤 2: 尝试 LLM 解析
        if self.use_llm_fallback and self._client:
            intent = self._try_llm_parse(user_input)
            if intent.task_type != BusinessTaskType.UNKNOWN:
                return intent

        # 步骤 3: 返回 UNKNOWN
        return TaskIntent(
            task_type=BusinessTaskType.UNKNOWN,
            raw_input=user_input,
        )

    def _try_template_match(self, user_input: str) -> TaskIntent:
        """尝试模板匹配.

        Args:
            user_input: 用户输入

        Returns:
            匹配结果
        """
        user_input_lower = user_input.lower()

        for template in self._TEMPLATES:
            # 检查关键词匹配
            keyword_match = any(
                kw in user_input_lower for kw in template.keywords
            )

            # 检查正则模式匹配
            pattern_match = any(
                p.search(user_input) for p in template.patterns
            )

            if keyword_match or pattern_match:
                # 提取参数
                goal = {"description": user_input}
                constraints = {}

                for field_name, pattern in template.extractors.items():
                    match = pattern.search(user_input)
                    if match:
                        goal[field_name] = match.group(1)

                return TaskIntent(
                    goal=goal,
                    constraints=constraints,
                    task_type=template.task_type,
                    raw_input=user_input,
                )

        return TaskIntent(
            task_type=BusinessTaskType.UNKNOWN,
            raw_input=user_input,
        )

    def _try_llm_parse(self, user_input: str) -> TaskIntent:
        """尝试使用 LLM 解析.

        Args:
            user_input: 用户输入

        Returns:
            LLM 解析结果
        """
        if not self._client:
            return TaskIntent(
                task_type=BusinessTaskType.UNKNOWN,
                raw_input=user_input,
            )

        # 构建提示词
        task_types_str = "\n".join([
            f"- {t.value}: {get_business_type_description(t)}"
            for t in BusinessTaskType
            if t != BusinessTaskType.UNKNOWN
        ])

        prompt = f"""你是一个水利调度领域的意图解析助手。请分析用户的输入，判断其意图类型并提取关键信息。

可选的任务类型:
{task_types_str}

用户输入: {user_input}

请以 JSON 格式返回解析结果:
{{
    "task_type": "任务类型枚举值",
    "goal": {{
        "description": "任务描述",
        "关键参数1": "值1",
        "关键参数2": "值2"
    }},
    "constraints": {{
        "约束条件1": "值1"
    }},
    "confidence": 0.95  // 置信度 0-1
}}

如果无法确定任务类型，请返回 "unknown"。"""

        try:
            response = self._client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "你是一个专业的水利调度领域意图解析助手。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=500,
            )

            content = response.choices[0].message.content

            # 解析 JSON
            # 尝试提取 JSON 部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                task_type_str = result.get("task_type", "unknown")
                try:
                    task_type = BusinessTaskType(task_type_str)
                except ValueError:
                    task_type = BusinessTaskType.UNKNOWN

                # 置信度检查
                confidence = result.get("confidence", 0.5)
                if confidence < 0.6:
                    task_type = BusinessTaskType.UNKNOWN

                return TaskIntent(
                    goal=result.get("goal", {"description": user_input}),
                    constraints=result.get("constraints", {}),
                    task_type=task_type,
                    raw_input=user_input,
                )

        except Exception as e:
            print(f"LLM 解析失败: {e}")

        return TaskIntent(
            task_type=BusinessTaskType.UNKNOWN,
            raw_input=user_input,
        )

    def parse_structured(self, data: Dict[str, Any]) -> TaskIntent:
        """解析结构化数据.

        Args:
            data: 结构化数据字典

        Returns:
            解析后的任务意图
        """
        task_type_str = data.get("type", "unknown")
        try:
            task_type = BusinessTaskType(task_type_str)
        except ValueError:
            task_type = BusinessTaskType.UNKNOWN

        return TaskIntent(
            goal=data.get("params", {}),
            constraints={},
            task_type=task_type,
            raw_input=str(data),
        )
