"""决策实体"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class DecisionStatus(Enum):
    """决策状态"""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class Decision:
    """决策实体"""
    id: str
    query: str
    status: DecisionStatus = DecisionStatus.PENDING
    result: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def complete(self, result: str):
        """完成决策"""
        self.result = result
        self.status = DecisionStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def fail(self, error: str):
        """标记决策失败"""
        self.status = DecisionStatus.FAILED
        self.context["error"] = error
        self.updated_at = datetime.now()
