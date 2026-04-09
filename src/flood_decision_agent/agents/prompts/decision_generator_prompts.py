"""决策生成提示词模块

提供决策生成相关的提示词模板
"""

import json
from typing import Dict, List, Any


class DecisionGeneratorPrompts:
    """决策生成提示词类"""

    @staticmethod
    def get_decision_generator_prompt(
        data_summary: Dict[str, Any],
        objectives: List[str],
        constraints: Dict[str, Any],
    ) -> str:
        """获取决策生成提示词

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
        """获取风险评估提示词

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
        """获取报告生成提示词

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
