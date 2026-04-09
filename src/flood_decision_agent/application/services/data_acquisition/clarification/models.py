"""澄清机制数据模型定义

定义渐进式澄清机制中使用的所有数据模型，包括状态枚举、数据请求、
澄清会话和默认值建议等。
"""

from enum import Enum, auto
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class ClarificationStatus(Enum):
    """澄清会话状态枚举
    
    Attributes:
        pending: 待处理状态，等待开始澄清流程
        waiting_for_user: 等待用户输入状态
        resolved: 已解决状态，所有数据请求已处理
        skipped: 已跳过状态，用户选择跳过澄清
    """
    pending = "pending"
    waiting_for_user = "waiting_for_user"
    resolved = "resolved"
    skipped = "skipped"


class DataRequestType(Enum):
    """数据请求类型枚举
    
    Attributes:
        required: 必需数据，没有默认值，必须用户提供
        optional_with_default: 可选数据，但有默认值可用
        optional_no_default: 可选数据，无默认值
    """
    required = "required"
    optional_with_default = "optional_with_default"
    optional_no_default = "optional_no_default"


@dataclass
class DefaultValueSuggestion:
    """默认值建议
    
    表示系统根据上下文为某个数据项提供的默认值建议。
    
    Attributes:
        value: 建议的默认值
        source: 默认值来源（如 "historical_data", "similar_case", "rule_based" 等）
        confidence: 置信度，范围 0.0-1.0
        description: 默认值描述说明
    """
    value: Any
    source: str
    confidence: float
    description: str = ""

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class PendingDataRequest:
    """待请求数据
    
    表示一个需要澄清的数据请求项。
    
    Attributes:
        request_id: 请求唯一标识符
        data_key: 数据键名，用于标识所需数据
        description: 数据描述，向用户说明需要什么数据
        request_type: 请求类型，参见 DataRequestType
        suggested_defaults: 建议的默认值列表
        resolved_value: 已解决的值（解决后填充）
        resolution_type: 解决方式（"user_input", "default", "assumed", "skipped"）
        created_at: 创建时间
        resolved_at: 解决时间
    """
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_key: str = ""
    description: str = ""
    request_type: DataRequestType = DataRequestType.required
    suggested_defaults: List[DefaultValueSuggestion] = field(default_factory=list)
    resolved_value: Optional[Any] = None
    resolution_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

    def is_resolved(self) -> bool:
        """检查该请求是否已解决"""
        return self.resolved_value is not None

    def resolve(self, value: Any, resolution_type: str) -> None:
        """解决该数据请求
        
        Args:
            value: 解决后的值
            resolution_type: 解决方式
        """
        self.resolved_value = value
        self.resolution_type = resolution_type
        self.resolved_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "request_id": self.request_id,
            "data_key": self.data_key,
            "description": self.description,
            "request_type": self.request_type.value,
            "suggested_defaults": [
                {
                    "value": s.value,
                    "source": s.source,
                    "confidence": s.confidence,
                    "description": s.description,
                }
                for s in self.suggested_defaults
            ],
            "resolved_value": self.resolved_value,
            "resolution_type": self.resolution_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_resolved": self.is_resolved(),
        }


@dataclass
class ClarificationSession:
    """澄清会话
    
    管理一次完整的澄清流程，包含多个数据请求。
    
    Attributes:
        session_id: 会话唯一标识符
        task_id: 关联的任务ID
        pending_requests: 待处理的请求列表
        status: 当前会话状态
        created_at: 创建时间
        updated_at: 更新时间
        completed_at: 完成时间
        metadata: 额外元数据
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    pending_requests: List[PendingDataRequest] = field(default_factory=list)
    status: ClarificationStatus = ClarificationStatus.pending
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._request_map: Dict[str, PendingDataRequest] = {
            req.request_id: req for req in self.pending_requests
        }

    def add_request(self, request: PendingDataRequest) -> None:
        """添加新的数据请求
        
        Args:
            request: 待添加的数据请求
        """
        self.pending_requests.append(request)
        self._request_map[request.request_id] = request
        self._update_timestamp()

    def get_request(self, request_id: str) -> Optional[PendingDataRequest]:
        """根据ID获取数据请求
        
        Args:
            request_id: 请求ID
            
        Returns:
            找到的数据请求，未找到返回 None
        """
        return self._request_map.get(request_id)

    def get_unresolved_requests(self) -> List[PendingDataRequest]:
        """获取所有未解决的请求
        
        Returns:
            未解决的数据请求列表
        """
        return [req for req in self.pending_requests if not req.is_resolved()]

    def get_next_pending_request(self) -> Optional[PendingDataRequest]:
        """获取下一个待处理的请求
        
        Returns:
            下一个未解决的请求，如果没有则返回 None
        """
        unresolved = self.get_unresolved_requests()
        return unresolved[0] if unresolved else None

    def update_status(self, status: ClarificationStatus) -> None:
        """更新会话状态
        
        Args:
            status: 新状态
        """
        self.status = status
        self._update_timestamp()
        if status in (ClarificationStatus.resolved, ClarificationStatus.skipped):
            self.completed_at = datetime.now()

    def is_complete(self) -> bool:
        """检查会话是否已完成
        
        Returns:
            如果所有请求都已解决或会话被跳过，返回 True
        """
        if self.status in (ClarificationStatus.resolved, ClarificationStatus.skipped):
            return True
        return len(self.get_unresolved_requests()) == 0

    def _update_timestamp(self) -> None:
        """更新时间戳"""
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "status": self.status.value,
            "pending_requests": [req.to_dict() for req in self.pending_requests],
            "unresolved_count": len(self.get_unresolved_requests()),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_complete": self.is_complete(),
            "metadata": self.metadata,
        }
