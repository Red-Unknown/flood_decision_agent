"""断点相关异常类"""

from flood_decision_agent.shared.exceptions.base import FloodDecisionAgentError


class CheckpointError(FloodDecisionAgentError):
    """断点基础异常"""

    def __init__(self, message: str, code: str = None, details: dict = None):
        super().__init__(
            message, code=code or "CHECKPOINT_ERROR", details=details
        )


class CheckpointNotFoundError(CheckpointError):
    """断点不存在异常"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message, code="CHECKPOINT_NOT_FOUND", details=details
        )


class CheckpointInvalidError(CheckpointError):
    """断点状态无效异常"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message, code="CHECKPOINT_INVALID", details=details
        )


class CheckpointExpiredError(CheckpointError):
    """断点已过期异常"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message, code="CHECKPOINT_EXPIRED", details=details
        )


class CheckpointStorageError(CheckpointError):
    """断点存储异常"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message, code="CHECKPOINT_STORAGE_ERROR", details=details
        )
