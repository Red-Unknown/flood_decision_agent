"""对话管理器 - 协调多轮对话流程.

提供对话生命周期管理、流程调度和上下文维护功能。
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from flood_decision_agent.conversation.context import ConversationContext
from flood_decision_agent.conversation.state import (
    ConversationState,
    ConversationStatus,
    ConversationTurn,
)


class ConversationManager:
    """对话管理器类.
    
    负责：
    - 对话的创建、维护和销毁
    - 根据用户输入调整执行流程
    - 管理多轮对话状态
    """
    
    def __init__(
        self,
        pipeline_factory: Optional[Callable] = None,
        max_conversations: int = 100,
        conversation_timeout: float = 3600,
    ):
        """初始化对话管理器.
        
        Args:
            pipeline_factory: Pipeline工厂函数
            max_conversations: 最大并发对话数
            conversation_timeout: 对话超时时间（秒）
        """
        self.pipeline_factory = pipeline_factory
        self.max_conversations = max_conversations
        self.conversation_timeout = conversation_timeout
        
        # 存储活跃对话
        self._conversations: Dict[str, ConversationState] = {}
        self._context_manager = ConversationContext()
    
    def create_conversation(self) -> ConversationState:
        """创建新对话.
        
        Returns:
            新对话状态
        """
        # 清理过期对话
        self._cleanup_expired()
        
        # 检查是否达到上限
        if len(self._conversations) >= self.max_conversations:
            # 移除最旧的对话
            oldest_id = min(
                self._conversations.keys(),
                key=lambda k: self._conversations[k].updated_at
            )
            del self._conversations[oldest_id]
        
        state = ConversationState()
        self._conversations[state.conversation_id] = state
        state.update_status(ConversationStatus.ACTIVE)
        
        return state
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationState]:
        """获取对话状态.
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话状态，不存在返回None
        """
        state = self._conversations.get(conversation_id)
        if state and state.is_expired(self.conversation_timeout):
            state.update_status(ConversationStatus.TIMEOUT)
            return None
        return state
    
    def process_input(
        self,
        conversation_id: Optional[str],
        user_input: str,
        **kwargs
    ) -> Dict[str, Any]:
        """处理用户输入.
        
        核心方法，根据对话状态和用户输入决定执行流程。
        
        Args:
            conversation_id: 对话ID，None则创建新对话
            user_input: 用户输入
            **kwargs: 额外参数
            
        Returns:
            处理结果
        """
        # 获取或创建对话
        if conversation_id:
            state = self.get_conversation(conversation_id)
            if not state:
                # 对话不存在或已过期，创建新对话
                state = self.create_conversation()
                is_new = True
            else:
                is_new = False
        else:
            state = self.create_conversation()
            is_new = True
        
        # 检查是否需要清空上下文
        if not is_new and self._context_manager.should_clear_context(state, user_input):
            # 保存旧对话ID用于提示
            old_id = state.conversation_id
            # 创建新对话
            state = self.create_conversation()
            is_new = True
            print(f"[系统] 已开启新对话 (原对话 {old_id} 已归档)")
        
        # 分析上下文变化
        context_analysis = self._context_manager.analyze_context_change(state, user_input)
        
        # 根据分析结果调整流程
        flow_decision = self._decide_flow(state, user_input, context_analysis)
        
        # 更新对话状态
        state.update_status(ConversationStatus.PROCESSING)
        
        # 执行相应流程
        try:
            if flow_decision["action"] == "continue_task":
                result = self._continue_current_task(state, user_input, flow_decision)
            elif flow_decision["action"] == "new_task":
                result = self._start_new_task(state, user_input, flow_decision)
            elif flow_decision["action"] == "expand_task":
                result = self._expand_current_task(state, user_input, flow_decision)
            elif flow_decision["action"] == "clarify":
                result = self._request_clarification(state, user_input, flow_decision)
            else:
                result = self._start_new_task(state, user_input, flow_decision)
            
            # 记录对话轮次
            turn = state.add_turn(
                user_input=user_input,
                agent_response=result.get("response", ""),
                intent=result.get("intent"),
                execution_result=result.get("execution_result")
            )
            
            # 提取并保存关键信息
            key_info = self._context_manager.extract_key_info(
                user_input, 
                result.get("response", "")
            )
            for key, value in key_info.items():
                if value:
                    state.accumulate_data(key, value)
            
            # 更新状态
            state.update_status(ConversationStatus.WAITING_USER_INPUT)
            
            # 构建返回结果
            return {
                "conversation_id": state.conversation_id,
                "turn_id": turn.turn_id,
                "is_new_conversation": is_new,
                "flow_action": flow_decision["action"],
                "response": result.get("response", ""),
                "status": "success",
                "context_analysis": context_analysis,
            }
            
        except Exception as e:
            state.update_status(ConversationStatus.ERROR)
            state.error_count += 1
            return {
                "conversation_id": state.conversation_id,
                "error": str(e),
                "status": "error",
            }
    
    def _decide_flow(
        self,
        state: ConversationState,
        user_input: str,
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """决定执行流程.
        
        Args:
            state: 对话状态
            user_input: 用户输入
            context_analysis: 上下文分析结果
            
        Returns:
            流程决策
        """
        action = context_analysis.get("suggested_action", "continue")
        
        # 根据建议行动和当前状态决定具体流程
        if action == "start_new":
            return {
                "action": "new_task",
                "reason": "用户开启新话题",
                "use_context": False,
            }
        
        elif action == "expand":
            if state.current_task_type:
                return {
                    "action": "expand_task",
                    "reason": "用户追问或补充",
                    "use_context": True,
                    "task_type": state.current_task_type,
                }
            else:
                return {
                    "action": "new_task",
                    "reason": "无当前任务，创建新任务",
                    "use_context": True,
                }
        
        elif action == "correct":
            return {
                "action": "expand_task",
                "reason": "用户修正前文",
                "use_context": True,
                "correct_mode": True,
            }
        
        else:  # continue
            if state.current_task_type and not state.current_task_graph:
                # 有任务类型但没有任务图，可能是等待用户补充
                return {
                    "action": "expand_task",
                    "reason": "继续当前任务",
                    "use_context": True,
                }
            elif state.current_task_type:
                return {
                    "action": "continue_task",
                    "reason": "继续执行当前任务",
                    "use_context": True,
                }
            else:
                return {
                    "action": "new_task",
                    "reason": "无当前任务",
                    "use_context": False,
                }
    
    def _continue_current_task(
        self,
        state: ConversationState,
        user_input: str,
        flow_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """继续当前任务.
        
        Args:
            state: 对话状态
            user_input: 用户输入
            flow_decision: 流程决策
            
        Returns:
            执行结果
        """
        # 构建包含上下文的输入
        if flow_decision.get("use_context"):
            enhanced_input = self._context_manager.build_conversation_prompt(
                state, user_input
            )
        else:
            enhanced_input = user_input
        
        # 执行Pipeline
        if self.pipeline_factory:
            pipeline = self.pipeline_factory()
            result = pipeline.run({
                "type": "natural_language",
                "input": enhanced_input,
                "conversation_context": state.get_full_context(),
            })
            
            return {
                "response": self._format_result(result),
                "execution_result": result,
                "intent": {"type": state.current_task_type},
            }
        else:
            # 无Pipeline时的默认处理
            return {
                "response": f"继续处理任务: {state.current_task_type}\n用户输入: {user_input}",
                "intent": {"type": state.current_task_type},
            }
    
    def _start_new_task(
        self,
        state: ConversationState,
        user_input: str,
        flow_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """开始新任务.
        
        Args:
            state: 对话状态
            user_input: 用户输入
            flow_decision: 流程决策
            
        Returns:
            执行结果
        """
        # 重置当前任务
        state.current_task_type = None
        state.current_task_graph = None
        
        # 构建系统提示词（包含上下文）
        system_prompt = self._context_manager.build_system_prompt(state)
        
        # 执行Pipeline
        if self.pipeline_factory:
            pipeline = self.pipeline_factory()
            result = pipeline.run({
                "type": "natural_language",
                "input": user_input,
                "system_prompt": system_prompt,
            })
            
            # 更新当前任务类型
            if hasattr(result, 'data_pool_snapshot'):
                intent = result.data_pool_snapshot.get('intent', {})
                state.current_task_type = intent.get('task_type')
            
            return {
                "response": self._format_result(result),
                "execution_result": result,
                "intent": {"type": state.current_task_type},
            }
        else:
            return {
                "response": f"开始新任务\n用户输入: {user_input}",
                "intent": {"type": "unknown"},
            }
    
    def _expand_current_task(
        self,
        state: ConversationState,
        user_input: str,
        flow_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """扩展当前任务.
        
        Args:
            state: 对话状态
            user_input: 用户输入
            flow_decision: 流程决策
            
        Returns:
            执行结果
        """
        # 合并历史上下文
        context_summary = state.get_full_context()
        enhanced_input = f"【历史上下文】\n{context_summary}\n\n【当前补充】\n{user_input}"
        
        if self.pipeline_factory:
            pipeline = self.pipeline_factory()
            result = pipeline.run({
                "type": "natural_language",
                "input": enhanced_input,
                "is_follow_up": True,
                "original_task": state.current_task_type,
            })
            
            return {
                "response": self._format_result(result),
                "execution_result": result,
                "intent": {"type": state.current_task_type},
            }
        else:
            return {
                "response": f"扩展任务: {state.current_task_type}\n补充: {user_input}",
                "intent": {"type": state.current_task_type},
            }
    
    def _request_clarification(
        self,
        state: ConversationState,
        user_input: str,
        flow_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """请求用户澄清.
        
        Args:
            state: 对话状态
            user_input: 用户输入
            flow_decision: 流程决策
            
        Returns:
            执行结果
        """
        return {
            "response": "我需要更多信息来理解您的需求。您是想：\n1. 继续讨论之前的话题\n2. 开启一个新的话题\n3. 对之前的回答进行补充或修正",
            "intent": {"type": "clarification_needed"},
        }
    
    def _format_result(self, result: Any) -> str:
        """格式化结果为字符串.
        
        Args:
            result: 执行结果
            
        Returns:
            格式化字符串
        """
        if hasattr(result, 'data_pool_snapshot'):
            # 从数据池中提取回答
            snapshot = result.data_pool_snapshot
            if 'answer' in snapshot:
                return snapshot['answer']
            elif 'summary' in snapshot:
                return snapshot['summary']
        
        if isinstance(result, dict):
            return result.get('response', str(result))
        
        return str(result)
    
    def _cleanup_expired(self) -> None:
        """清理过期对话."""
        expired_ids = [
            cid for cid, state in self._conversations.items()
            if state.is_expired(self.conversation_timeout)
        ]
        for cid in expired_ids:
            del self._conversations[cid]
    
    def end_conversation(self, conversation_id: str) -> bool:
        """结束对话.
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            是否成功
        """
        state = self._conversations.get(conversation_id)
        if state:
            state.update_status(ConversationStatus.COMPLETED)
            return True
        return False
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """获取对话摘要.
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话摘要
        """
        state = self.get_conversation(conversation_id)
        if not state:
            return None
        
        return {
            "conversation_id": state.conversation_id,
            "status": state.status.value,
            "turn_count": len(state.turns),
            "current_task": state.current_task_type,
            "accumulated_data": state.accumulated_data,
            "duration_minutes": (time.time() - state.created_at) / 60,
        }
