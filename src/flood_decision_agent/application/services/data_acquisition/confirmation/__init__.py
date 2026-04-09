"""数据确认交互流程模块

提供数据确认相关的模型定义和管理功能，支持：
- 确认视图创建与管理
- 字段级别状态标识（缺失、异常、正常）
- 用户确认/修改/拒绝操作处理
- 可视化数据结构转换
"""

from .models import (
    ConfirmationStatus,
    DataFieldStatus,
    DataFieldDisplay,
    ConfirmationAction,
    ConfirmationView,
    ConfirmationResult,
    FieldModification,
    ConfirmationSession,
)

from .manager import ConfirmationManager


__all__ = [
    "ConfirmationStatus",
    "DataFieldStatus",
    "DataFieldDisplay",
    "ConfirmationAction",
    "ConfirmationView",
    "ConfirmationResult",
    "FieldModification",
    "ConfirmationSession",
    "ConfirmationManager",
]
