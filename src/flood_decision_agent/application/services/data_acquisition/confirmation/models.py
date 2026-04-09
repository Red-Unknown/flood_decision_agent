"""数据确认交互流程模块 - 模型定义"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class ConfirmationStatus(str, Enum):
    """确认状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    MODIFIED = "modified"


class DataFieldStatus(str, Enum):
    """数据字段状态枚举"""
    VALID = "valid"
    MISSING = "missing"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class DataFieldDisplay:
    """字段展示模型
    
    Attributes:
        name: 字段名称
        value: 字段值
        status: 字段状态（valid/missing/invalid/warning）
        message: 状态说明信息
        editable: 是否可编辑
    """
    name: str
    value: Any = None
    status: DataFieldStatus = DataFieldStatus.VALID
    message: str = ""
    editable: bool = True


@dataclass
class ConfirmationAction:
    """确认操作模型
    
    Attributes:
        action_id: 操作标识
        label: 显示标签
        action_type: 操作类型（confirm/reject/modify）
        primary: 是否为主要操作
    """
    action_id: str
    label: str
    action_type: str
    primary: bool = False


@dataclass
class ConfirmationView:
    """确认视图模型
    
    Attributes:
        confirmation_id: 确认会话ID
        title: 确认视图标题
        fields: 字段展示列表
        summary: 数据摘要说明
        actions: 可用操作列表
        status: 当前确认状态
        created_at: 创建时间戳
        expires_at: 过期时间戳（可选）
    """
    confirmation_id: str
    title: str
    fields: List[DataFieldDisplay] = field(default_factory=list)
    summary: str = ""
    actions: List[ConfirmationAction] = field(default_factory=list)
    status: ConfirmationStatus = ConfirmationStatus.PENDING
    created_at: Optional[float] = None
    expires_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "confirmation_id": self.confirmation_id,
            "title": self.title,
            "fields": [
                {
                    "name": f.name,
                    "value": f.value,
                    "status": f.status.value,
                    "message": f.message,
                    "editable": f.editable
                }
                for f in self.fields
            ],
            "summary": self.summary,
            "actions": [
                {
                    "action_id": a.action_id,
                    "label": a.label,
                    "action_type": a.action_type,
                    "primary": a.primary
                }
                for a in self.actions
            ],
            "status": self.status.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }


@dataclass
class ConfirmationResult:
    """确认结果模型
    
    Attributes:
        confirmation_id: 确认会话ID
        status: 确认结果状态
        original_data: 原始数据
        modified_data: 修改后的数据
        user_notes: 用户备注
        confirmed_at: 确认时间戳
    """
    confirmation_id: str
    status: ConfirmationStatus
    original_data: Dict[str, Any] = field(default_factory=dict)
    modified_data: Dict[str, Any] = field(default_factory=dict)
    user_notes: str = ""
    confirmed_at: Optional[float] = None

    def has_modifications(self) -> bool:
        """检查是否有数据修改"""
        return self.original_data != self.modified_data

    def get_final_data(self) -> Dict[str, Any]:
        """获取最终确认的数据"""
        if self.status == ConfirmationStatus.CONFIRMED:
            return self.original_data
        elif self.status == ConfirmationStatus.MODIFIED:
            return self.modified_data
        else:
            return {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "confirmation_id": self.confirmation_id,
            "status": self.status.value,
            "original_data": self.original_data,
            "modified_data": self.modified_data,
            "user_notes": self.user_notes,
            "confirmed_at": self.confirmed_at,
            "has_modifications": self.has_modifications(),
            "final_data": self.get_final_data()
        }


@dataclass
class FieldModification:
    """字段修改记录"""
    field_name: str
    old_value: Any
    new_value: Any
    modified_at: float


@dataclass
class ConfirmationSession:
    """确认会话内部模型"""
    confirmation_id: str
    view: ConfirmationView
    result: Optional[ConfirmationResult] = None
    modifications: List[FieldModification] = field(default_factory=list)
    schema: Optional[Any] = None
