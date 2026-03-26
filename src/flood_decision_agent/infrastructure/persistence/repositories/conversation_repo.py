"""对话仓储"""
from typing import List, Optional
from flood_decision_agent.domain.entities.conversation import Conversation


class ConversationRepository:
    """对话仓储"""
    
    def __init__(self):
        self._conversations: dict = {}
    
    def get(self, conversation_id: str) -> Optional[Conversation]:
        """获取对话"""
        return self._conversations.get(conversation_id)
    
    def save(self, conversation: Conversation) -> None:
        """保存对话"""
        self._conversations[conversation.id] = conversation
    
    def list_all(self) -> List[Conversation]:
        """列出所有对话"""
        return list(self._conversations.values())
    
    def delete(self, conversation_id: str) -> bool:
        """删除对话"""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False
