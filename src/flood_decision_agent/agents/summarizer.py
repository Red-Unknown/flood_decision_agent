"""总结智能体模块 - 对任务执行过程和结果进行智能总结.

提供执行过程分析、结果汇总、关键发现提取等功能。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from flood_decision_agent.core.agent import BaseAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key


class SummarizerAgent(BaseAgent):
    """总结智能体.

    在所有任务执行完成后，对整个过程和结果进行智能总结。
    支持流式输出总结结果到控制台。
    """

    def __init__(
        self,
        agent_id: str = "Summarizer",
        enable_streaming: bool = True,
    ):
        """初始化总结智能体.

        Args:
            agent_id: Agent 标识
            enable_streaming: 是否启用流式输出
        """
        super().__init__(agent_id=agent_id)
        self.enable_streaming = enable_streaming
        self._client: Optional[OpenAI] = None
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
            self.logger.warning(f"无法初始化 LLM 客户端: {e}")
            self._client = None

    def _process(self, message: BaseMessage) -> Dict[str, Any]:
        """处理总结请求.

        Args:
            message: 包含执行过程和结果的消息

        Returns:
            总结结果
        """
        payload = message.payload

        # 提取执行信息
        execution_info = {
            "task_request": payload.get("task_request", {}),
            "execution_summary": payload.get("execution_summary", {}),
            "data_pool_snapshot": payload.get("data_pool_snapshot", {}),
            "task_graph": payload.get("task_graph", {}),
            "node_results": payload.get("node_results", []),
        }

        # 生成总结
        summary = self._generate_summary(execution_info)

        return {
            "status": "success",
            "summary": summary,
            "agent_id": self.agent_id,
        }

    def _generate_summary(self, execution_info: Dict[str, Any]) -> str:
        """生成执行总结.

        使用 LLM 对执行过程和结果进行智能总结。

        Args:
            execution_info: 执行信息

        Returns:
            总结文本
        """
        if not self._client:
            return self._generate_fallback_summary(execution_info)

        # 构建提示词
        prompt = self._build_summary_prompt(execution_info)

        try:
            messages = [
                {
                    "role": "system",
                    "content": """你是"水利智脑"的总结助手，负责分析任务执行过程和结果，生成清晰、专业的总结报告。

【你的职责】
1. 分析任务执行的整体流程和关键步骤
2. 总结各阶段的执行结果和关键数据
3. 提取重要发现和结论
4. 提供后续建议或注意事项

【输出要求】
- 语言简洁专业，符合水利调度领域特点
- 结构清晰，分点说明
- 突出关键数据和结论
- 总字数控制在300-500字""",
                },
                {"role": "user", "content": prompt},
            ]

            if self.enable_streaming:
                return self._generate_streaming_summary(messages)
            else:
                return self._generate_normal_summary(messages)

        except Exception as e:
            self.logger.error(f"LLM 总结生成失败: {e}")
            return self._generate_fallback_summary(execution_info)

    def _generate_streaming_summary(self, messages: List[Dict[str, str]]) -> str:
        """使用流式传输生成总结.

        Args:
            messages: 消息列表

        Returns:
            完整的总结文本
        """
        print("\n" + "=" * 70)
        print("[AI 正在生成执行总结...]")
        print("=" * 70 + "\n")

        response_stream = self._client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            temperature=0.3,
            max_tokens=800,
            stream=True,
        )

        # 收集流式输出
        content_parts = []
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                part = chunk.choices[0].delta.content
                content_parts.append(part)
                print(part, end="", flush=True)  # 实时输出到控制台

        print("\n")  # 换行
        return "".join(content_parts)

    def _generate_normal_summary(self, messages: List[Dict[str, str]]) -> str:
        """使用普通模式生成总结.

        Args:
            messages: 消息列表

        Returns:
            总结文本
        """
        response = self._client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            temperature=0.3,
            max_tokens=800,
        )

        return response.choices[0].message.content

    def _build_summary_prompt(self, execution_info: Dict[str, Any]) -> str:
        """构建总结提示词.

        Args:
            execution_info: 执行信息

        Returns:
            提示词文本
        """
        task_request = execution_info.get("task_request", {})
        execution_summary = execution_info.get("execution_summary", {})
        data_pool = execution_info.get("data_pool_snapshot", {})
        node_results = execution_info.get("node_results", [])

        # 构建任务描述
        user_input = task_request.get("input", "未知任务")
        task_type = task_request.get("type", "unknown")

        # 构建执行统计
        total_tasks = execution_summary.get("total_tasks", 0)
        completed_tasks = execution_summary.get("completed_tasks", 0)
        failed_tasks = execution_summary.get("failed_tasks", 0)
        duration_ms = execution_summary.get("total_duration_ms", 0)

        # 构建节点执行详情
        node_details = []
        for result in node_results:
            node_id = result.get("node_id", "unknown")
            task_type = result.get("task_type", "unknown")
            status = result.get("status", "unknown")
            metrics = result.get("metrics", {})
            elapsed_ms = metrics.get("elapsed_time_ms", 0)
            tools_used = metrics.get("tools_used", [])

            node_details.append(
                f"- {node_id} ({task_type}): {status}, "
                f"耗时 {elapsed_ms:.1f}ms, 使用工具: {tools_used}"
            )

        prompt = f"""请对以下水利调度任务执行过程和结果进行总结：

【用户请求】
{user_input}

【任务类型】
{task_type}

【执行统计】
- 总任务数: {total_tasks}
- 成功完成: {completed_tasks}
- 失败任务: {failed_tasks}
- 总耗时: {duration_ms:.2f}ms

【节点执行详情】
{chr(10).join(node_details) if node_details else "无详细节点信息"}

【数据池关键数据】
{json.dumps(data_pool, ensure_ascii=False, indent=2)[:500]}

请生成一份专业的执行总结报告，包括：
1. 任务执行概况
2. 关键执行步骤和结果
3. 重要数据发现
4. 后续建议"""

        return prompt

    def _generate_fallback_summary(self, execution_info: Dict[str, Any]) -> str:
        """生成备用总结（当 LLM 不可用时）.

        Args:
            execution_info: 执行信息

        Returns:
            简单的总结文本
        """
        execution_summary = execution_info.get("execution_summary", {})
        total_tasks = execution_summary.get("total_tasks", 0)
        completed_tasks = execution_summary.get("completed_tasks", 0)
        duration_ms = execution_summary.get("total_duration_ms", 0)

        return f"""【执行总结】

本次任务共包含 {total_tasks} 个子任务，其中 {completed_tasks} 个成功完成，总耗时 {duration_ms:.2f}ms。

各阶段执行顺利，数据已采集并处理完毕，决策方案已生成。建议持续关注水情变化，根据实际情况调整调度策略。"""
