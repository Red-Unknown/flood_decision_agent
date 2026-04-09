"""任务分解提示词模块

提供任务分解相关的提示词模板
"""

import json
from typing import Dict, List, Any


class TaskDecomposerPrompts:
    """任务分解提示词类"""

    @staticmethod
    def get_task_decomposer_prompt(
        intent: Dict[str, Any],
        execution_types: List[str],
    ) -> str:
        """获取任务分解提示词

        Args:
            intent: 任务意图
            execution_types: 可用的执行类型列表

        Returns:
            任务分解提示词
        """
        # 构建执行类型列表
        exec_types_str = "\n".join([f"- {et}" for et in execution_types])

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
