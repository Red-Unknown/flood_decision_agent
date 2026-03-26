"""对话管理模块 - 支持多轮对话和上下文保持."""

from flood_decision_agent.conversation.manager import ConversationManager
from flood_decision_agent.conversation.state import ConversationState, ConversationStatus
from flood_decision_agent.conversation.context import ConversationContext

__all__ = [
    "ConversationManager",
    "ConversationState", 
    "ConversationStatus",
    "ConversationContext",
]
