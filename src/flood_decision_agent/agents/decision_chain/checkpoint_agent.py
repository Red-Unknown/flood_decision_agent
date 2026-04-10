"""断点接续 Agent 模块.

提供任务状态保存与恢复功能，支持网络断联、手动取消、Token 超限等场景的恢复。
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from flood_decision_agent.agents.base.agent import BaseAgent
from flood_decision_agent.core.message import BaseMessage
from flood_decision_agent.infrastructure.logging import get_logger


class CheckpointStatus(enum.Enum):
    """断点状态枚举."""

    ACTIVE = "active"  # 活跃状态，可恢复
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    EXPIRED = "expired"  # 已过期


class InterruptionReason(enum.Enum):
    """中断原因枚举."""

    NETWORK_DISCONNECT = "network_disconnect"  # 网络断联
    MANUAL_CANCEL = "manual_cancel"  # 手动取消
    TOKEN_LIMIT_EXCEEDED = "token_limit_exceeded"  # Token 超限
    TIMEOUT = "timeout"  # 超时
    SYSTEM_ERROR = "system_error"  # 系统错误
    UNKNOWN = "unknown"  # 未知原因


@dataclass
class Checkpoint:
    """断点数据类.

    Attributes:
        session_id: 会话唯一标识
        state: 会话状态数据
        status: 断点状态
        interruption_reason: 中断原因
        created_at: 创建时间戳
        updated_at: 更新时间戳
        expires_at: 过期时间戳（可选）
        metadata: 额外元数据
    """

    session_id: str
    state: Dict[str, Any] = field(default_factory=dict)
    status: CheckpointStatus = CheckpointStatus.ACTIVE
    interruption_reason: Optional[InterruptionReason] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """检查断点是否已过期."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式."""
        return {
            "session_id": self.session_id,
            "state": self.state,
            "status": self.status.value,
            "interruption_reason": (
                self.interruption_reason.value if self.interruption_reason else None
            ),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """从字典创建 Checkpoint 实例."""
        return cls(
            session_id=data["session_id"],
            state=data.get("state", {}),
            status=CheckpointStatus(data.get("status", "active")),
            interruption_reason=InterruptionReason(data["interruption_reason"])
            if data.get("interruption_reason")
            else None,
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            expires_at=data.get("expires_at"),
            metadata=data.get("metadata", {}),
        )


class CheckpointStorage:
    """断点存储基类."""

    def save(self, checkpoint: Checkpoint) -> None:
        """保存断点."""
        raise NotImplementedError

    def load(self, session_id: str) -> Optional[Checkpoint]:
        """加载断点."""
        raise NotImplementedError

    def list_all(self) -> List[Checkpoint]:
        """列出所有断点."""
        raise NotImplementedError

    def delete(self, session_id: str) -> bool:
        """删除断点."""
        raise NotImplementedError

    def clear(self) -> None:
        """清空所有断点."""
        raise NotImplementedError


class MemoryCheckpointStorage(CheckpointStorage):
    """内存断点存储实现."""

    def __init__(self):
        self._checkpoints: Dict[str, Checkpoint] = {}
        self._logger = get_logger()

    def save(self, checkpoint: Checkpoint) -> None:
        """保存断点到内存."""
        checkpoint.updated_at = time.time()
        self._checkpoints[checkpoint.session_id] = checkpoint
        self._logger.debug(f"[CheckpointStorage] 保存断点: {checkpoint.session_id}")

    def load(self, session_id: str) -> Optional[Checkpoint]:
        """从内存加载断点."""
        checkpoint = self._checkpoints.get(session_id)
        if checkpoint is None:
            self._logger.warning(f"[CheckpointStorage] 断点不存在: {session_id}")
            return None

        # 检查是否过期
        if checkpoint.is_expired():
            self._logger.warning(f"[CheckpointStorage] 断点已过期: {session_id}")
            checkpoint.status = CheckpointStatus.EXPIRED
            return None

        return checkpoint

    def list_all(self) -> List[Checkpoint]:
        """列出内存中所有断点."""
        # 过滤掉过期的断点
        active_checkpoints = []
        for cp in self._checkpoints.values():
            if cp.is_expired():
                cp.status = CheckpointStatus.EXPIRED
            else:
                active_checkpoints.append(cp)
        return active_checkpoints

    def delete(self, session_id: str) -> bool:
        """删除指定断点."""
        if session_id in self._checkpoints:
            del self._checkpoints[session_id]
            self._logger.debug(f"[CheckpointStorage] 删除断点: {session_id}")
            return True
        return False

    def clear(self) -> None:
        """清空所有断点."""
        self._checkpoints.clear()
        self._logger.debug("[CheckpointStorage] 清空所有断点")


class CheckpointResumptionAgent(BaseAgent):
    """断点接续 Agent.

    用于处理任务恢复，支持以下场景的恢复：
    - 网络断联 (NETWORK_DISCONNECT)
    - 手动取消 (MANUAL_CANCEL)
    - Token 超限 (TOKEN_LIMIT_EXCEEDED)
    - 超时 (TIMEOUT)
    - 系统错误 (SYSTEM_ERROR)

    Attributes:
        storage: 断点存储后端（默认使用内存存储）
        default_ttl: 默认断点过期时间（秒）
    """

    def __init__(
        self,
        agent_id: str = "checkpoint_resumption_agent",
        storage: Optional[CheckpointStorage] = None,
        default_ttl: Optional[int] = 3600,  # 默认1小时过期
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(agent_id=agent_id, metadata=metadata)
        self.storage = storage or MemoryCheckpointStorage()
        self.default_ttl = default_ttl
        self._logger = get_logger()

    def save_checkpoint(
        self,
        session_id: str,
        state: Dict[str, Any],
        interruption_reason: Optional[str] = None,
        expires_at: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Checkpoint:
        """保存会话状态.

        Args:
            session_id: 会话唯一标识
            state: 会话状态数据
            interruption_reason: 中断原因（字符串或 InterruptionReason 枚举）
            expires_at: 过期时间戳（可选，默认使用 default_ttl）
            metadata: 额外元数据

        Returns:
            保存的 Checkpoint 对象
        """
        # 解析中断原因
        reason = self._parse_interruption_reason(interruption_reason)

        # 计算过期时间
        if expires_at is None and self.default_ttl is not None:
            expires_at = time.time() + self.default_ttl

        # 创建或更新断点
        existing = self.storage.load(session_id)
        if existing:
            # 更新现有断点
            existing.state = state
            existing.status = CheckpointStatus.ACTIVE
            existing.interruption_reason = reason
            existing.updated_at = time.time()
            existing.expires_at = expires_at
            if metadata:
                existing.metadata.update(metadata)
            checkpoint = existing
        else:
            # 创建新断点
            checkpoint = Checkpoint(
                session_id=session_id,
                state=state,
                status=CheckpointStatus.ACTIVE,
                interruption_reason=reason,
                expires_at=expires_at,
                metadata=metadata or {},
            )

        # 保存到存储
        self.storage.save(checkpoint)

        self._logger.info(
            f"[CheckpointResumptionAgent] 保存断点: {session_id}, "
            f"原因: {reason.value if reason else 'none'}"
        )

        return checkpoint

    def resume_checkpoint(
        self,
        session_id: str,
        validate_state: bool = True,
    ) -> Dict[str, Any]:
        """恢复会话状态.

        Args:
            session_id: 会话唯一标识
            validate_state: 是否验证状态完整性

        Returns:
            恢复的状态数据

        Raises:
            CheckpointNotFoundError: 断点不存在或已过期
            CheckpointInvalidError: 断点状态无效
        """
        from flood_decision_agent.shared.exceptions.checkpoint_exceptions import (
            CheckpointInvalidError,
            CheckpointNotFoundError,
        )

        checkpoint = self.storage.load(session_id)

        if checkpoint is None:
            raise CheckpointNotFoundError(f"断点不存在或已过期: {session_id}")

        if checkpoint.status == CheckpointStatus.COMPLETED:
            raise CheckpointInvalidError(f"断点已完成，无法恢复: {session_id}")

        if checkpoint.status == CheckpointStatus.FAILED:
            self._logger.warning(
                f"[CheckpointResumptionAgent] 恢复失败的断点: {session_id}"
            )

        # 验证状态完整性
        if validate_state and not self._validate_state(checkpoint.state):
            raise CheckpointInvalidError(f"断点状态无效: {session_id}")

        # 更新断点状态
        checkpoint.updated_at = time.time()
        self.storage.save(checkpoint)

        self._logger.info(f"[CheckpointResumptionAgent] 恢复断点: {session_id}")

        return {
            "session_id": checkpoint.session_id,
            "state": checkpoint.state,
            "interruption_reason": (
                checkpoint.interruption_reason.value
                if checkpoint.interruption_reason
                else None
            ),
            "created_at": checkpoint.created_at,
            "updated_at": checkpoint.updated_at,
            "metadata": checkpoint.metadata,
        }

    def list_checkpoints(
        self,
        status: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """列出所有断点.

        Args:
            status: 按状态过滤（可选）
            reason: 按中断原因过滤（可选）

        Returns:
            断点信息列表
        """
        checkpoints = self.storage.list_all()

        # 应用过滤条件
        if status:
            try:
                status_enum = CheckpointStatus(status)
                checkpoints = [cp for cp in checkpoints if cp.status == status_enum]
            except ValueError:
                self._logger.warning(f"[CheckpointResumptionAgent] 无效的状态过滤: {status}")

        if reason:
            try:
                reason_enum = InterruptionReason(reason)
                checkpoints = [
                    cp
                    for cp in checkpoints
                    if cp.interruption_reason == reason_enum
                ]
            except ValueError:
                self._logger.warning(
                    f"[CheckpointResumptionAgent] 无效的原因过滤: {reason}"
                )

        # 转换为字典列表
        return [cp.to_dict() for cp in checkpoints]

    def complete_checkpoint(self, session_id: str) -> bool:
        """标记断点为已完成.

        Args:
            session_id: 会话唯一标识

        Returns:
            是否成功标记
        """
        checkpoint = self.storage.load(session_id)
        if checkpoint is None:
            return False

        checkpoint.status = CheckpointStatus.COMPLETED
        checkpoint.updated_at = time.time()
        self.storage.save(checkpoint)

        self._logger.info(
            f"[CheckpointResumptionAgent] 标记断点为已完成: {session_id}"
        )
        return True

    def fail_checkpoint(
        self,
        session_id: str,
        error_message: Optional[str] = None,
    ) -> bool:
        """标记断点为失败.

        Args:
            session_id: 会话唯一标识
            error_message: 错误信息

        Returns:
            是否成功标记
        """
        checkpoint = self.storage.load(session_id)
        if checkpoint is None:
            return False

        checkpoint.status = CheckpointStatus.FAILED
        checkpoint.updated_at = time.time()
        if error_message:
            checkpoint.metadata["error_message"] = error_message
        self.storage.save(checkpoint)

        self._logger.info(f"[CheckpointResumptionAgent] 标记断点为失败: {session_id}")
        return True

    def delete_checkpoint(self, session_id: str) -> bool:
        """删除断点.

        Args:
            session_id: 会话唯一标识

        Returns:
            是否成功删除
        """
        return self.storage.delete(session_id)

    def clear_checkpoints(self) -> None:
        """清空所有断点."""
        self.storage.clear()
        self._logger.info("[CheckpointResumptionAgent] 清空所有断点")

    def _parse_interruption_reason(
        self, reason: Optional[str]
    ) -> Optional[InterruptionReason]:
        """解析中断原因字符串为枚举值."""
        if reason is None:
            return None

        try:
            return InterruptionReason(reason)
        except ValueError:
            # 尝试映射常见错误描述
            reason_map = {
                "network": InterruptionReason.NETWORK_DISCONNECT,
                "disconnect": InterruptionReason.NETWORK_DISCONNECT,
                "cancel": InterruptionReason.MANUAL_CANCEL,
                "token": InterruptionReason.TOKEN_LIMIT_EXCEEDED,
                "timeout": InterruptionReason.TIMEOUT,
                "error": InterruptionReason.SYSTEM_ERROR,
            }
            mapped = reason_map.get(reason.lower())
            if mapped:
                return mapped
            return InterruptionReason.UNKNOWN

    def _validate_state(self, state: Dict[str, Any]) -> bool:
        """验证状态数据完整性.

        Args:
            state: 状态数据

        Returns:
            是否有效
        """
        if not isinstance(state, dict):
            return False

        # 检查必需字段（可根据业务需求扩展）
        required_fields = state.get("_required_fields", [])
        for field in required_fields:
            if field not in state:
                return False

        return True

    def _process(self, message: BaseMessage) -> Any:
        """处理消息（基类要求实现）.

        当前实现主要用于接收断点相关命令消息。
        """
        payload = message.payload

        if not isinstance(payload, dict):
            return {"error": "消息payload必须是字典类型"}

        command = payload.get("command")

        if command == "save":
            checkpoint = self.save_checkpoint(
                session_id=payload["session_id"],
                state=payload["state"],
                interruption_reason=payload.get("interruption_reason"),
                metadata=payload.get("metadata"),
            )
            return checkpoint.to_dict()

        elif command == "resume":
            return self.resume_checkpoint(
                session_id=payload["session_id"],
                validate_state=payload.get("validate_state", True),
            )

        elif command == "list":
            return self.list_checkpoints(
                status=payload.get("status"),
                reason=payload.get("reason"),
            )

        elif command == "complete":
            success = self.complete_checkpoint(payload["session_id"])
            return {"success": success}

        elif command == "fail":
            success = self.fail_checkpoint(
                session_id=payload["session_id"],
                error_message=payload.get("error_message"),
            )
            return {"success": success}

        elif command == "delete":
            success = self.delete_checkpoint(payload["session_id"])
            return {"success": success}

        elif command == "clear":
            self.clear_checkpoints()
            return {"success": True}

        else:
            return {"error": f"未知命令: {command}"}
