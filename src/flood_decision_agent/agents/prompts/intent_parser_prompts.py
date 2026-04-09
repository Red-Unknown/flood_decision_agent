"""意图解析提示词模块

提供意图解析相关的提示词模板
"""

import json
from typing import Dict, List, Any


class IntentParserPrompts:
    """意图解析提示词类"""

    @staticmethod
    def get_intent_parser_prompt(
        user_input: str,
        templates: List[Dict[str, Any]],
        use_template_context: bool = True,
    ) -> str:
        """获取意图解析提示词

        Args:
            user_input: 用户输入
            templates: 模板定义列表
            use_template_context: 是否使用模板上下文

        Returns:
            完整的提示词
        """
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
        "city": "<城市名称，如：北京、上海、金坛等>",
        "station": "<站点名称，如有>",
        "time_range": "<时间范围，如有>"
    }},
    "constraints": {{}},
    "confidence": <0-1之间的数值>,
    "error_message": <如有错误填错误信息，否则填 null>
}}

注意：
- 如果用户输入中明确提到了城市（如"金坛"、"北京"等），必须在 goal.city 中准确提取
- 如果无法确定任务类型，task_type 填 "unknown"
- 如果用户问题与水利调度无关，在 error_message 中说明原因
- 置信度低于 0.5 时，task_type 填 "unknown"
"""

        return prompt
