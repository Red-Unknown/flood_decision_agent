"""提示词模板模块.

集中管理所有 Agent 的提示词，便于维护和优化。
"""

from __future__ import annotations

import json
from typing import Dict, List, Any

from flood_decision_agent.core.task_types import (
    BusinessTaskType,
    ExecutionTaskType,
    get_business_type_description,
    get_execution_type_description,
)


class PromptTemplates:
    """提示词模板类."""

    # ========== 系统角色定义 ==========

    INTENT_PARSER_SYSTEM = """你是"水利智脑"——一个专业的水利调度领域 AI 助手。

【你的职责】
1. 准确理解用户的水利调度相关需求
2. 将自然语言转化为结构化的任务意图
3. 识别任务类型、提取关键参数、判断约束条件

【你的专业领域】
- 洪水预警与预报
- 水库调度与优化
- 干旱监测与抗旱
- 水文数据分析
- 风险评估与应急响应
- 流域综合管理

【输出原则】
- 严格按 JSON 格式输出
- 不确定时明确标注 "unknown"
- 提取所有可识别的关键参数
- 置信度低于 0.5 时标记为不确定"""

    TASK_DECOMPOSER_SYSTEM = """你是"任务规划师"——负责将高层意图分解为可执行的具体步骤。

【你的职责】
1. 分析任务目标，确定所需执行步骤
2. 明确各步骤的输入输出依赖关系
3. 识别可并行执行的步骤
4. 评估任务可行性和风险点

【分解原则】
- 每个步骤必须是原子操作
- 明确标注步骤间的依赖关系
- 考虑异常处理和回退方案
- 优化执行顺序以提高效率"""

    DECISION_GENERATOR_SYSTEM = """你是"调度决策专家"——基于数据分析生成最优调度方案。

【你的职责】
1. 综合分析水情、雨情、工情数据
2. 评估不同调度方案的影响
3. 在多目标间寻求平衡（防洪、发电、航运、生态）
4. 生成可执行的调度指令

【决策原则】
- 安全第一，防洪优先
- 综合效益最大化
- 方案可操作、可验证
- 明确决策依据和风险提示"""

    # ========== 意图解析提示词 ==========

    @staticmethod
    def get_intent_parser_prompt(
        user_input: str,
        templates: List[Dict[str, Any]],
        use_template_context: bool = True,
    ) -> str:
        """获取意图解析提示词.

        Args:
            user_input: 用户输入
            templates: 模板定义列表
            use_template_context: 是否使用模板上下文

        Returns:
            完整的提示词
        """
        # 构建业务类型列表
        business_types = []
        for t in BusinessTaskType:
            if t != BusinessTaskType.UNKNOWN:
                business_types.append(f"- {t.value}: {get_business_type_description(t)}")
        business_types_str = "\n".join(business_types)

        # 构建模板上下文（可选）
        template_context = ""
        if use_template_context and templates:
            templates_json = json.dumps(templates, ensure_ascii=False, indent=2)
            template_context = f"""
【参考模板】
以下是我们预定义的任务模板供参考：
{templates_json}

请判断用户输入是否符合某个模板，或需要创建新的任务类型。"""

        prompt = f"""【任务】
请分析以下用户输入，识别其意图并提取关键信息，然后继续完成 JSON 输出。

【用户输入】
{user_input}

【可选任务类型】
{business_types_str}
{template_context}

【分析要求】
1. 判断任务类型（从可选类型中选择最合适的）
2. 提取关键参数（如站点名称、时间范围、数值等）
3. 识别约束条件（如有）
4. 评估置信度（0-1之间）

【输出要求】
请继续完成以下 JSON（我已帮你开头），不要添加其他内容：
{{
    "task_type": "<从可选类型中选择，不确定则填 unknown>",
    "goal": {{
        "description": "<任务描述>",
        "station": "<站点名称，如有>",
        "time_range": "<时间范围，如有>"
    }},
    "constraints": {{}},
    "confidence": <0-1之间的数值>,
    "error_message": <如有错误填错误信息，否则填 null>
}}

注意：
- 如果无法确定任务类型，task_type 填 "unknown"
- 如果用户问题与水利调度无关，在 error_message 中说明原因
- 置信度低于 0.5 时，task_type 填 "unknown"
"""

        return prompt

    @staticmethod
    def get_task_decomposer_prompt(
        intent: Dict[str, Any],
        execution_types: List[ExecutionTaskType],
    ) -> str:
        """获取任务分解提示词.

        Args:
            intent: 任务意图
            execution_types: 可用的执行类型列表

        Returns:
            任务分解提示词
        """
        # 构建执行类型列表
        exec_types = []
        for et in execution_types:
            exec_types.append(f"- {et.value}: {get_execution_type_description(et)}")
        exec_types_str = "\n".join(exec_types)

        intent_json = json.dumps(intent, ensure_ascii=False, indent=2)

        prompt = f"""【任务】
请将以下高层任务意图分解为具体的执行步骤。

【任务意图】
{intent_json}

【可用执行类型】
{exec_types_str}

【分解要求】
1. 将任务分解为 3-8 个执行步骤
2. 每个步骤必须是原子操作（不可再分）
3. 明确标注步骤间的依赖关系
4. 考虑数据流向和输入输出匹配

【输出格式】
请按以下 JSON 格式返回步骤列表：
{{
    "steps": [
        {{
            "step_id": "step_001",
            "execution_type": "执行类型",
            "description": "步骤描述",
            "inputs": ["输入数据项"],
            "outputs": ["输出数据项"],
            "dependencies": ["依赖的步骤ID"]
        }}
    ],
    "parallel_groups": [["可并行的步骤ID组"]],
    "estimated_duration": "预估总耗时"
}}"""

        return prompt

    @staticmethod
    def get_decision_generator_prompt(
        data_summary: Dict[str, Any],
        objectives: List[str],
        constraints: Dict[str, Any],
    ) -> str:
        """获取决策生成提示词.

        Args:
            data_summary: 数据汇总
            objectives: 决策目标列表
            constraints: 约束条件

        Returns:
            决策生成提示词
        """
        data_json = json.dumps(data_summary, ensure_ascii=False, indent=2)
        objectives_str = "\n".join([f"- {obj}" for obj in objectives])
        constraints_json = json.dumps(constraints, ensure_ascii=False, indent=2)

        prompt = f"""【任务】
基于以下数据和分析结果，生成最优的调度决策方案。

【数据汇总】
{data_json}

【决策目标】（按优先级排序）
{objectives_str}

【约束条件】
{constraints_json}

【决策原则】
1. 防洪安全是首要目标，必须满足
2. 在满足安全的前提下，优化其他目标
3. 考虑方案的可操作性和风险
4. 提供备选方案和触发条件

【输出格式】
请按以下 JSON 格式返回决策方案：
{{
    "decision": {{
        "action": "主要决策动作",
        "target_outflow": 20000,
        "target_level": 165.5,
        "timing": "执行时机"
    }},
    "reasoning": "决策理由和分析过程",
    "expected_outcomes": {{
        "flood_control": "防洪效果评估",
        "power_generation": "发电效益评估",
        "navigation": "航运影响评估"
    }},
    "risks": [
        {{
            "risk": "风险描述",
            "probability": "可能性（高/中/低）",
            "mitigation": "缓解措施"
        }}
    ],
    "alternatives": [
        {{
            "option": "备选方案",
            "trigger_condition": "触发条件"
        }}
    ],
    "monitoring_points": ["需要重点监测的指标"]
}}"""

        return prompt

    @staticmethod
    def get_risk_assessment_prompt(
        scenario: Dict[str, Any],
        risk_factors: List[str],
    ) -> str:
        """获取风险评估提示词.

        Args:
            scenario: 场景信息
            risk_factors: 风险因素列表

        Returns:
            风险评估提示词
        """
        scenario_json = json.dumps(scenario, ensure_ascii=False, indent=2)
        factors_str = "\n".join([f"- {f}" for f in risk_factors])

        prompt = f"""【任务】
对以下场景进行全面的风险评估。

【场景信息】
{scenario_json}

【评估维度】
{factors_str}

【评估要求】
1. 识别主要风险点和触发条件
2. 评估风险概率和影响程度
3. 划分风险等级（红/橙/黄/蓝）
4. 提出预警建议和应对措施

【输出格式】
{{
    "overall_risk_level": "总体风险等级",
    "risk_items": [
        {{
            "risk": "风险描述",
            "level": "风险等级",
            "probability": 0.3,
            "impact": "影响描述",
            "indicators": ["监测指标"],
            "threshold": "预警阈值"
        }}
    ],
    "warning_advice": "预警建议",
    "emergency_measures": ["应急措施"],
    "monitoring_requirements": "监测要求"
}}"""

        return prompt

    @staticmethod
    def get_report_generator_prompt(
        task_results: List[Dict[str, Any]],
        report_type: str = "综合分析报告",
    ) -> str:
        """获取报告生成提示词.

        Args:
            task_results: 任务执行结果列表
            report_type: 报告类型

        Returns:
            报告生成提示词
        """
        results_json = json.dumps(task_results, ensure_ascii=False, indent=2)

        prompt = f"""【任务】
基于以下任务执行结果，生成一份专业的{report_type}。

【执行结果】
{results_json}

【报告要求】
1. 结构清晰，包含执行摘要、详细分析、结论建议
2. 数据准确，引用具体的执行结果
3. 语言专业，符合水利行业规范
4. 重点突出，强调关键发现和风险点

【输出格式】
{{
    "title": "报告标题",
    "summary": "执行摘要（200字以内）",
    "sections": [
        {{
            "title": "章节标题",
            "content": "章节内容"
        }}
    ],
    "key_findings": ["关键发现"],
    "recommendations": ["建议措施"],
    "appendix": {{
        "data_sources": "数据来源",
        "methodology": "分析方法"
    }}
}}"""

        return prompt


# 便捷函数
def get_system_prompt(agent_type: str) -> str:
    """获取系统提示词.

    Args:
        agent_type: Agent 类型

    Returns:
        系统提示词
    """
    prompts = {
        "intent_parser": PromptTemplates.INTENT_PARSER_SYSTEM,
        "task_decomposer": PromptTemplates.TASK_DECOMPOSER_SYSTEM,
        "decision_generator": PromptTemplates.DECISION_GENERATOR_SYSTEM,
    }
    return prompts.get(agent_type, "你是一个专业的 AI 助手。")
