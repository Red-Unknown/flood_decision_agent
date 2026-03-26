"""决策仓储"""
from typing import List, Optional
from flood_decision_agent.domain.entities.decision import Decision


class DecisionRepository:
    """决策仓储"""
    
    def __init__(self):
        self._decisions: dict = {}
    
    def get(self, decision_id: str) -> Optional[Decision]:
        """获取决策"""
        return self._decisions.get(decision_id)
    
    def save(self, decision: Decision) -> None:
        """保存决策"""
        self._decisions[decision.id] = decision
    
    def list_all(self) -> List[Decision]:
        """列出所有决策"""
        return list(self._decisions.values())
