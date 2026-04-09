"""渐进式澄清机制模块

该模块实现了数据获取过程中的渐进式澄清机制，用于处理任务执行时
所需数据的依赖检查、默认值提供、暂停/恢复等功能。
"""

from .models import (
    ClarificationStatus,
    DataRequestType,
    PendingDataRequest,
    ClarificationSession,
    DefaultValueSuggestion,
)
from .manager import ClarificationManager

__all__ = [
    "ClarificationStatus",
    "DataRequestType",
    "PendingDataRequest",
    "ClarificationSession",
    "DefaultValueSuggestion",
    "ClarificationManager",
]
