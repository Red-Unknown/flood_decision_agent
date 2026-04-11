from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from flood_decision_agent.core.parameter_types import ParameterRequirement


class ParameterPlannerState(str, Enum):
    """ParameterPlanner 状态机
    
    表示参数规划器在不同阶段的状态。
    """

    INITIALIZING = "initializing"
    EXTRACTING_FROM_INPUT = "extracting_from_input"
    EXTRACTING_FROM_CONTEXT = "extracting_from_context"
    EXTRACTING_FROM_EXPERIENCE = "extracting_from_experience"
    WAITING_FOR_CLARIFICATION = "waiting_for_clarification"
    VALIDATING = "validating"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ClarificationRequest:
    """参数澄清请求
    
    当 ParameterPlanner 发现缺少必需参数时，向用户发送的澄清请求。
    
    Attributes:
        request_id: 请求唯一标识
        node_id: 关联的节点ID
        task_type: 任务类型
        missing_params: 缺失的参数需求列表
        context: 上下文信息
        generated_questions: LLM生成的自然语言问题
        created_at: 创建时间
    """

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str = ""
    task_type: str = ""
    missing_params: List[ParameterRequirement] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    generated_questions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "request_id": self.request_id,
            "node_id": self.node_id,
            "task_type": self.task_type,
            "missing_params": [p.to_dict() for p in self.missing_params],
            "context": self.context,
            "generated_questions": self.generated_questions,
            "created_at": self.created_at,
        }


@dataclass
class ClarificationResponse:
    """用户澄清响应
    
    用户针对 ClarificationRequest 提交的答案。
    
    Attributes:
        request_id: 关联的请求ID
        answers: 参数名到答案的映射
        submitted_at: 提交时间
    """

    request_id: str
    answers: Dict[str, Any]
    submitted_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "request_id": self.request_id,
            "answers": self.answers,
            "submitted_at": self.submitted_at,
        }


@dataclass
class ClarificationSession:
    """澄清会话
    
    管理一次完整的参数澄清过程。
    
    Attributes:
        session_id: 会话ID
        node_id: 关联的节点ID
        request: 澄清请求
        response: 用户响应
        status: 会话状态
        created_at: 创建时间
        completed_at: 完成时间
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str = ""
    request: Optional[ClarificationRequest] = None
    response: Optional[ClarificationResponse] = None
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def mark_completed(self, response: ClarificationResponse) -> None:
        """标记会话完成"""
        self.response = response
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "node_id": self.node_id,
            "request": self.request.to_dict() if self.request else None,
            "response": self.response.to_dict() if self.response else None,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
