"""对话上下文管理 - 保持和维护对话上下文."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai import OpenAI

from flood_decision_agent.conversation.state import ConversationState, ConversationTurn
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key


class ConversationContext:
    """对话上下文管理类.
    
    负责维护对话上下文，包括：
    - 历史对话记录
    - 累积的数据和知识
    - 用户偏好和意图
    """
    
    def __init__(self, max_history: int = 5):
        """初始化上下文管理器.
        
        Args:
            max_history: 最大保留历史轮数
        """
        self.max_history = max_history
        self._client: Optional[OpenAI] = None
        self._init_llm_client()
    
    def _init_llm_client(self) -> None:
        """初始化LLM客户端."""
        try:
            api_key = require_kimi_api_key()
            self._client = OpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.cn/v1",
            )
        except Exception:
            self._client = None
    
    def build_system_prompt(self, state: ConversationState) -> str:
        """构建系统提示词，包含上下文信息.
        
        Args:
            state: 对话状态
            
        Returns:
            系统提示词
        """
        base_prompt = """你是"水利智脑"——专业的水利调度领域AI助手。

【你的职责】
1. 理解用户的水利调度相关需求
2. 基于上下文提供连贯的回答
3. 在多轮对话中保持逻辑一致性
4. 根据累积信息调整回答策略

【上下文感知原则】
- 如果用户问题涉及前文内容，主动关联
- 如果用户补充或修正前文，及时响应
- 如果用户转换话题，灵活切换
- 累积用户提供的信息，用于后续分析"""
        
        # 添加上下文信息
        context_parts = [base_prompt]
        
        # 添加当前任务类型
        if state.current_task_type:
            context_parts.append(f"\n【当前任务类型】\n{state.current_task_type}")
        
        # 添加累积数据摘要
        if state.accumulated_data:
            context_parts.append("\n【已累积信息】")
            for key, value in state.accumulated_data.items():
                if isinstance(value, list) and len(value) > 0:
                    context_parts.append(f"- {key}: {len(value)} 条记录")
                else:
                    context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts)
    
    def build_conversation_prompt(
        self, 
        state: ConversationState, 
        current_input: str
    ) -> str:
        """构建包含历史对话的提示词.
        
        Args:
            state: 对话状态
            current_input: 当前用户输入
            
        Returns:
            格式化的提示词
        """
        prompt_parts = []
        
        # 添加历史对话（最近几轮）
        recent_turns = state.get_recent_turns(self.max_history)
        if recent_turns:
            prompt_parts.append("【历史对话】")
            for turn in recent_turns[:-1]:  # 不包括当前轮
                prompt_parts.append(f"用户: {turn.user_input}")
                if turn.agent_response:
                    # 截取回答的前200字符
                    response_summary = turn.agent_response[:200]
                    if len(turn.agent_response) > 200:
                        response_summary += "..."
                    prompt_parts.append(f"助手: {response_summary}")
                prompt_parts.append("")
        
        # 添加当前输入
        prompt_parts.append(f"【当前输入】\n用户: {current_input}")
        prompt_parts.append("\n请基于以上上下文，理解用户意图并给出回答。")
        
        return "\n".join(prompt_parts)
    
    def analyze_context_change(
        self, 
        state: ConversationState, 
        current_input: str
    ) -> Dict[str, Any]:
        """分析上下文变化，判断用户意图变化.
        
        Args:
            state: 对话状态
            current_input: 当前用户输入
            
        Returns:
            分析结果
        """
        if not state.turns:
            return {
                "is_new_topic": True,
                "is_follow_up": False,
                "related_turns": [],
                "suggested_action": "start_new",
            }
        
        # 使用LLM分析上下文关系
        if self._client:
            return self._llm_analyze_context(state, current_input)
        else:
            # 简单规则判断
            return self._rule_based_analyze(state, current_input)
    
    def _llm_analyze_context(
        self, 
        state: ConversationState, 
        current_input: str
    ) -> Dict[str, Any]:
        """使用LLM分析上下文.
        
        Args:
            state: 对话状态
            current_input: 当前用户输入
            
        Returns:
            分析结果
        """
        recent_turns = state.get_recent_turns(3)
        history = "\n".join([
            f"用户: {t.user_input}\n助手: {t.agent_response[:100]}..."
            for t in recent_turns
        ])
        
        prompt = f"""分析以下对话上下文，判断当前输入的性质：

【历史对话】
{history}

【当前输入】
{current_input}

请判断：
1. 当前输入是否是新话题？（是/否）
2. 当前输入是否是对前文的追问/补充？（是/否）
3. 建议采取什么行动？（continue/expand/correct/start_new）

以JSON格式输出：
{{"is_new_topic": true/false, "is_follow_up": true/false, "suggested_action": "action"}}"""
        
        try:
            response = self._client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "你是一个对话分析助手。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=200,
            )
            
            import json
            result_text = response.choices[0].message.content
            # 提取JSON
            if "{" in result_text and "}" in result_text:
                json_str = result_text[result_text.find("{"):result_text.rfind("}")+1]
                return json.loads(json_str)
        except Exception:
            pass
        
        # 失败时返回默认结果
        return self._rule_based_analyze(state, current_input)
    
    def _rule_based_analyze(
        self, 
        state: ConversationState, 
        current_input: str
    ) -> Dict[str, Any]:
        """基于规则分析上下文.
        
        Args:
            state: 对话状态
            current_input: 当前用户输入
            
        Returns:
            分析结果
        """
        current_input_lower = current_input.lower()
        
        # 追问关键词
        follow_up_keywords = ["那", "还有", "另外", "补充", "再问", "继续", "详细"]
        is_follow_up = any(kw in current_input_lower for kw in follow_up_keywords)
        
        # 新话题关键词
        new_topic_keywords = ["换个话题", "另外问", "新问题", "先不说"]
        is_new_topic = any(kw in current_input_lower for kw in new_topic_keywords)
        
        # 确定建议行动
        if is_new_topic:
            suggested_action = "start_new"
        elif is_follow_up:
            suggested_action = "expand"
        else:
            suggested_action = "continue"
        
        return {
            "is_new_topic": is_new_topic,
            "is_follow_up": is_follow_up,
            "related_turns": list(range(max(0, len(state.turns)-2), len(state.turns))),
            "suggested_action": suggested_action,
        }
    
    def extract_key_info(self, user_input: str, agent_response: str) -> Dict[str, Any]:
        """从对话中提取关键信息.
        
        Args:
            user_input: 用户输入
            agent_response: Agent回答
            
        Returns:
            提取的关键信息
        """
        info = {
            "mentioned_stations": [],
            "mentioned_dates": [],
            "task_types": [],
            "user_preferences": [],
        }
        
        # 简单规则提取站点名
        import re
        station_pattern = r"(三峡|葛洲坝|丹江口|宜昌|武汉|重庆|南京|上海)[站|市|大坝]?"
        stations = re.findall(station_pattern, user_input + agent_response)
        info["mentioned_stations"] = list(set(stations))
        
        # 提取日期
        date_pattern = r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?|\d{1,2}[-/月]\d{1,2}[日]?)"
        dates = re.findall(date_pattern, user_input)
        info["mentioned_dates"] = dates
        
        return info
    
    def should_clear_context(
        self, 
        state: ConversationState, 
        current_input: str
    ) -> bool:
        """判断是否应该清空上下文.
        
        Args:
            state: 对话状态
            current_input: 当前用户输入
            
        Returns:
            是否清空
        """
        # 检查是否明确要求清空
        clear_keywords = ["重新开始", "清空", "重置", "新对话", "换个话题"]
        if any(kw in current_input for kw in clear_keywords):
            return True
        
        # 检查是否过期
        if state.is_expired(timeout_seconds=1800):  # 30分钟
            return True
        
        # 检查轮数是否过多
        if len(state.turns) >= state.max_turns:
            return True
        
        return False
