"""断点接续 Agent 单元测试."""

import time
from unittest.mock import MagicMock, patch

import pytest

from flood_decision_agent.agents.decision_chain.checkpoint_agent import (
    Checkpoint,
    CheckpointResumptionAgent,
    CheckpointStatus,
    CheckpointStorage,
    InterruptionReason,
    MemoryCheckpointStorage,
)
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.shared.exceptions.checkpoint_exceptions import (
    CheckpointInvalidError,
    CheckpointNotFoundError,
)


class TestCheckpoint:
    """Checkpoint 数据类测试."""

    def test_checkpoint_creation(self):
        """测试创建 Checkpoint."""
        cp = Checkpoint(
            session_id="test-session-1",
            state={"key": "value"},
            status=CheckpointStatus.ACTIVE,
        )
        assert cp.session_id == "test-session-1"
        assert cp.state == {"key": "value"}
        assert cp.status == CheckpointStatus.ACTIVE
        assert cp.created_at > 0
        assert cp.updated_at > 0

    def test_checkpoint_is_expired(self):
        """测试过期检查."""
        # 未设置过期时间
        cp1 = Checkpoint(session_id="test-1")
        assert not cp1.is_expired()

        # 已过期
        cp2 = Checkpoint(session_id="test-2", expires_at=time.time() - 1)
        assert cp2.is_expired()

        # 未过期
        cp3 = Checkpoint(session_id="test-3", expires_at=time.time() + 3600)
        assert not cp3.is_expired()

    def test_checkpoint_to_dict(self):
        """测试转换为字典."""
        cp = Checkpoint(
            session_id="test-1",
            state={"data": "value"},
            status=CheckpointStatus.ACTIVE,
            interruption_reason=InterruptionReason.NETWORK_DISCONNECT,
        )
        data = cp.to_dict()
        assert data["session_id"] == "test-1"
        assert data["state"] == {"data": "value"}
        assert data["status"] == "active"
        assert data["interruption_reason"] == "network_disconnect"

    def test_checkpoint_from_dict(self):
        """测试从字典创建."""
        data = {
            "session_id": "test-1",
            "state": {"data": "value"},
            "status": "active",
            "interruption_reason": "network_disconnect",
            "created_at": 1234567890,
            "updated_at": 1234567890,
            "metadata": {"key": "value"},
        }
        cp = Checkpoint.from_dict(data)
        assert cp.session_id == "test-1"
        assert cp.state == {"data": "value"}
        assert cp.status == CheckpointStatus.ACTIVE
        assert cp.interruption_reason == InterruptionReason.NETWORK_DISCONNECT
        assert cp.metadata == {"key": "value"}


class TestMemoryCheckpointStorage:
    """内存存储测试."""

    def test_save_and_load(self):
        """测试保存和加载."""
        storage = MemoryCheckpointStorage()
        cp = Checkpoint(session_id="test-1", state={"data": "value"})

        storage.save(cp)
        loaded = storage.load("test-1")

        assert loaded is not None
        assert loaded.session_id == "test-1"
        assert loaded.state == {"data": "value"}

    def test_load_nonexistent(self):
        """测试加载不存在的断点."""
        storage = MemoryCheckpointStorage()
        loaded = storage.load("nonexistent")
        assert loaded is None

    def test_load_expired(self):
        """测试加载已过期的断点."""
        storage = MemoryCheckpointStorage()
        cp = Checkpoint(
            session_id="test-1",
            state={"data": "value"},
            expires_at=time.time() - 1,
        )
        storage.save(cp)

        loaded = storage.load("test-1")
        assert loaded is None

    def test_list_all(self):
        """测试列出所有断点."""
        storage = MemoryCheckpointStorage()
        cp1 = Checkpoint(session_id="test-1", state={"data": "1"})
        cp2 = Checkpoint(session_id="test-2", state={"data": "2"})

        storage.save(cp1)
        storage.save(cp2)

        checkpoints = storage.list_all()
        assert len(checkpoints) == 2
        assert {cp.session_id for cp in checkpoints} == {"test-1", "test-2"}

    def test_list_all_filters_expired(self):
        """测试列出时过滤过期断点."""
        storage = MemoryCheckpointStorage()
        cp1 = Checkpoint(session_id="test-1", state={"data": "1"})
        cp2 = Checkpoint(
            session_id="test-2",
            state={"data": "2"},
            expires_at=time.time() - 1,
        )

        storage.save(cp1)
        storage.save(cp2)

        checkpoints = storage.list_all()
        assert len(checkpoints) == 1
        assert checkpoints[0].session_id == "test-1"

    def test_delete(self):
        """测试删除断点."""
        storage = MemoryCheckpointStorage()
        cp = Checkpoint(session_id="test-1", state={"data": "value"})
        storage.save(cp)

        assert storage.delete("test-1") is True
        assert storage.load("test-1") is None
        assert storage.delete("test-1") is False

    def test_clear(self):
        """测试清空所有断点."""
        storage = MemoryCheckpointStorage()
        storage.save(Checkpoint(session_id="test-1"))
        storage.save(Checkpoint(session_id="test-2"))

        storage.clear()
        assert storage.load("test-1") is None
        assert storage.load("test-2") is None
        assert len(storage.list_all()) == 0


class TestCheckpointResumptionAgent:
    """断点接续 Agent 测试."""

    @pytest.fixture
    def agent(self):
        """创建测试用的 Agent."""
        return CheckpointResumptionAgent(agent_id="test-checkpoint-agent")

    def test_agent_initialization(self, agent):
        """测试 Agent 初始化."""
        assert agent.agent_id == "test-checkpoint-agent"
        assert agent.default_ttl == 3600
        assert isinstance(agent.storage, CheckpointStorage)

    def test_save_checkpoint(self, agent):
        """测试保存断点."""
        checkpoint = agent.save_checkpoint(
            session_id="session-1",
            state={"step": 5, "data": "test"},
            interruption_reason="network_disconnect",
        )

        assert checkpoint.session_id == "session-1"
        assert checkpoint.state == {"step": 5, "data": "test"}
        assert checkpoint.interruption_reason == InterruptionReason.NETWORK_DISCONNECT
        assert checkpoint.status == CheckpointStatus.ACTIVE

    def test_save_checkpoint_update_existing(self, agent):
        """测试更新现有断点."""
        agent.save_checkpoint(
            session_id="session-1",
            state={"step": 1},
            interruption_reason="network_disconnect",
        )

        checkpoint = agent.save_checkpoint(
            session_id="session-1",
            state={"step": 2},
            interruption_reason="manual_cancel",
        )

        assert checkpoint.state == {"step": 2}
        assert checkpoint.interruption_reason == InterruptionReason.MANUAL_CANCEL

    def test_save_checkpoint_with_custom_expiry(self, agent):
        """测试保存带自定义过期时间的断点."""
        expires = time.time() + 7200
        checkpoint = agent.save_checkpoint(
            session_id="session-1",
            state={"data": "test"},
            expires_at=expires,
        )

        assert checkpoint.expires_at == expires

    def test_resume_checkpoint(self, agent):
        """测试恢复断点."""
        agent.save_checkpoint(
            session_id="session-1",
            state={"step": 5, "data": "test"},
            interruption_reason="token_limit_exceeded",
        )

        result = agent.resume_checkpoint("session-1")

        assert result["session_id"] == "session-1"
        assert result["state"] == {"step": 5, "data": "test"}
        assert result["interruption_reason"] == "token_limit_exceeded"

    def test_resume_checkpoint_not_found(self, agent):
        """测试恢复不存在的断点."""
        with pytest.raises(CheckpointNotFoundError):
            agent.resume_checkpoint("nonexistent")

    def test_resume_checkpoint_completed(self, agent):
        """测试恢复已完成的断点."""
        agent.save_checkpoint(
            session_id="session-1",
            state={"data": "test"},
        )
        agent.complete_checkpoint("session-1")

        with pytest.raises(CheckpointInvalidError):
            agent.resume_checkpoint("session-1")

    def test_resume_checkpoint_invalid_state(self, agent):
        """测试恢复状态无效的断点."""
        agent.save_checkpoint(
            session_id="session-1",
            state={"_required_fields": ["missing_field"]},
        )

        with pytest.raises(CheckpointInvalidError):
            agent.resume_checkpoint("session-1", validate_state=True)

    def test_list_checkpoints(self, agent):
        """测试列出断点."""
        agent.save_checkpoint(
            session_id="session-1",
            state={"data": "1"},
            interruption_reason="network_disconnect",
        )
        agent.save_checkpoint(
            session_id="session-2",
            state={"data": "2"},
            interruption_reason="manual_cancel",
        )

        checkpoints = agent.list_checkpoints()
        assert len(checkpoints) == 2

    def test_list_checkpoints_filter_by_status(self, agent):
        """测试按状态过滤."""
        agent.save_checkpoint("session-1", {"data": "1"})
        agent.save_checkpoint("session-2", {"data": "2"})
        agent.complete_checkpoint("session-1")

        checkpoints = agent.list_checkpoints(status="active")
        assert len(checkpoints) == 1
        assert checkpoints[0]["session_id"] == "session-2"

    def test_list_checkpoints_filter_by_reason(self, agent):
        """测试按原因过滤."""
        agent.save_checkpoint(
            "session-1",
            {"data": "1"},
            interruption_reason="network_disconnect",
        )
        agent.save_checkpoint(
            "session-2",
            {"data": "2"},
            interruption_reason="manual_cancel",
        )

        checkpoints = agent.list_checkpoints(reason="network_disconnect")
        assert len(checkpoints) == 1
        assert checkpoints[0]["session_id"] == "session-1"

    def test_complete_checkpoint(self, agent):
        """测试标记断点为已完成."""
        agent.save_checkpoint("session-1", {"data": "test"})

        success = agent.complete_checkpoint("session-1")
        assert success is True

        checkpoint = agent.storage.load("session-1")
        assert checkpoint.status == CheckpointStatus.COMPLETED

    def test_complete_checkpoint_not_found(self, agent):
        """测试标记不存在的断点为已完成."""
        success = agent.complete_checkpoint("nonexistent")
        assert success is False

    def test_fail_checkpoint(self, agent):
        """测试标记断点为失败."""
        agent.save_checkpoint("session-1", {"data": "test"})

        success = agent.fail_checkpoint("session-1", error_message="Something went wrong")
        assert success is True

        checkpoint = agent.storage.load("session-1")
        assert checkpoint.status == CheckpointStatus.FAILED
        assert checkpoint.metadata["error_message"] == "Something went wrong"

    def test_delete_checkpoint(self, agent):
        """测试删除断点."""
        agent.save_checkpoint("session-1", {"data": "test"})

        success = agent.delete_checkpoint("session-1")
        assert success is True
        assert agent.storage.load("session-1") is None

    def test_clear_checkpoints(self, agent):
        """测试清空所有断点."""
        agent.save_checkpoint("session-1", {"data": "1"})
        agent.save_checkpoint("session-2", {"data": "2"})

        agent.clear_checkpoints()
        assert len(agent.list_checkpoints()) == 0

    def test_parse_interruption_reason(self, agent):
        """测试解析中断原因."""
        # 标准枚举值
        assert agent._parse_interruption_reason("network_disconnect") == InterruptionReason.NETWORK_DISCONNECT
        assert agent._parse_interruption_reason("manual_cancel") == InterruptionReason.MANUAL_CANCEL
        assert agent._parse_interruption_reason("token_limit_exceeded") == InterruptionReason.TOKEN_LIMIT_EXCEEDED

        # 简写形式
        assert agent._parse_interruption_reason("network") == InterruptionReason.NETWORK_DISCONNECT
        assert agent._parse_interruption_reason("cancel") == InterruptionReason.MANUAL_CANCEL
        assert agent._parse_interruption_reason("token") == InterruptionReason.TOKEN_LIMIT_EXCEEDED
        assert agent._parse_interruption_reason("timeout") == InterruptionReason.TIMEOUT
        assert agent._parse_interruption_reason("error") == InterruptionReason.SYSTEM_ERROR

        # 未知原因
        assert agent._parse_interruption_reason("unknown_reason") == InterruptionReason.UNKNOWN
        assert agent._parse_interruption_reason(None) is None

    def test_validate_state(self, agent):
        """测试状态验证."""
        # 有效状态
        assert agent._validate_state({"key": "value"}) is True
        assert agent._validate_state({}) is True

        # 无效状态（非字典）
        assert agent._validate_state("invalid") is False
        assert agent._validate_state(None) is False

        # 带必需字段验证
        assert agent._validate_state({
            "_required_fields": ["field1"],
            "field1": "value"
        }) is True
        assert agent._validate_state({
            "_required_fields": ["missing_field"]
        }) is False


class TestCheckpointResumptionAgentMessageProcessing:
    """断点接续 Agent 消息处理测试."""

    @pytest.fixture
    def agent(self):
        """创建测试用的 Agent."""
        return CheckpointResumptionAgent(agent_id="test-checkpoint-agent")

    def create_message(self, payload: dict) -> BaseMessage:
        """辅助方法：创建消息."""
        return BaseMessage(
            id="test-msg-1",
            type=MessageType.TASK_REQUEST,
            payload=payload,
            sender="test_sender",
        )

    def test_process_save_command(self, agent):
        """测试处理保存命令."""
        msg = self.create_message({
            "command": "save",
            "session_id": "session-1",
            "state": {"data": "test"},
            "interruption_reason": "network_disconnect",
        })

        result = agent.execute(msg)

        assert result["session_id"] == "session-1"
        assert result["state"] == {"data": "test"}
        assert result["interruption_reason"] == "network_disconnect"

    def test_process_resume_command(self, agent):
        """测试处理恢复命令."""
        agent.save_checkpoint("session-1", {"data": "test"})

        msg = self.create_message({
            "command": "resume",
            "session_id": "session-1",
        })

        result = agent.execute(msg)

        assert result["session_id"] == "session-1"
        assert result["state"] == {"data": "test"}

    def test_process_list_command(self, agent):
        """测试处理列出命令."""
        agent.save_checkpoint("session-1", {"data": "1"})
        agent.save_checkpoint("session-2", {"data": "2"})

        msg = self.create_message({"command": "list"})
        result = agent.execute(msg)

        assert len(result) == 2

    def test_process_complete_command(self, agent):
        """测试处理完成命令."""
        agent.save_checkpoint("session-1", {"data": "test"})

        msg = self.create_message({
            "command": "complete",
            "session_id": "session-1",
        })
        result = agent.execute(msg)

        assert result["success"] is True

    def test_process_fail_command(self, agent):
        """测试处理失败命令."""
        agent.save_checkpoint("session-1", {"data": "test"})

        msg = self.create_message({
            "command": "fail",
            "session_id": "session-1",
            "error_message": "Test error",
        })
        result = agent.execute(msg)

        assert result["success"] is True

    def test_process_delete_command(self, agent):
        """测试处理删除命令."""
        agent.save_checkpoint("session-1", {"data": "test"})

        msg = self.create_message({
            "command": "delete",
            "session_id": "session-1",
        })
        result = agent.execute(msg)

        assert result["success"] is True
        assert agent.storage.load("session-1") is None

    def test_process_clear_command(self, agent):
        """测试处理清空命令."""
        agent.save_checkpoint("session-1", {"data": "1"})

        msg = self.create_message({"command": "clear"})
        result = agent.execute(msg)

        assert result["success"] is True
        assert len(agent.list_checkpoints()) == 0

    def test_process_invalid_payload(self, agent):
        """测试处理无效 payload."""
        msg = BaseMessage(
            id="test-msg-1",
            type=MessageType.TASK_REQUEST,
            payload="invalid payload",
            sender="test_sender",
        )

        result = agent.execute(msg)
        assert "error" in result

    def test_process_unknown_command(self, agent):
        """测试处理未知命令."""
        msg = self.create_message({
            "command": "unknown_command",
            "session_id": "session-1",
        })

        result = agent.execute(msg)
        assert "error" in result
        assert "unknown_command" in result["error"]


class TestInterruptionScenarios:
    """中断场景测试."""

    @pytest.fixture
    def agent(self):
        """创建测试用的 Agent."""
        return CheckpointResumptionAgent(agent_id="test-checkpoint-agent")

    def test_network_disconnect_scenario(self, agent):
        """测试网络断联场景."""
        # 模拟任务执行中断
        checkpoint = agent.save_checkpoint(
            session_id="task-123",
            state={
                "task_id": "task-123",
                "current_step": 3,
                "total_steps": 5,
                "intermediate_results": ["result1", "result2"],
            },
            interruption_reason="network_disconnect",
        )

        assert checkpoint.interruption_reason == InterruptionReason.NETWORK_DISCONNECT

        # 恢复任务
        result = agent.resume_checkpoint("task-123")
        assert result["state"]["current_step"] == 3
        assert result["interruption_reason"] == "network_disconnect"

    def test_manual_cancel_scenario(self, agent):
        """测试手动取消场景."""
        checkpoint = agent.save_checkpoint(
            session_id="task-456",
            state={
                "task_id": "task-456",
                "current_step": 2,
                "user_input": "some input",
            },
            interruption_reason="manual_cancel",
        )

        assert checkpoint.interruption_reason == InterruptionReason.MANUAL_CANCEL

        result = agent.resume_checkpoint("task-456")
        assert result["interruption_reason"] == "manual_cancel"

    def test_token_limit_exceeded_scenario(self, agent):
        """测试 Token 超限场景."""
        checkpoint = agent.save_checkpoint(
            session_id="task-789",
            state={
                "task_id": "task-789",
                "current_step": 4,
                "tokens_used": 8000,
                "token_limit": 4096,
            },
            interruption_reason="token_limit_exceeded",
        )

        assert checkpoint.interruption_reason == InterruptionReason.TOKEN_LIMIT_EXCEEDED

        result = agent.resume_checkpoint("task-789")
        assert result["state"]["tokens_used"] == 8000

    def test_timeout_scenario(self, agent):
        """测试超时场景."""
        checkpoint = agent.save_checkpoint(
            session_id="task-timeout",
            state={
                "task_id": "task-timeout",
                "start_time": time.time() - 3600,
                "timeout": 300,
            },
            interruption_reason="timeout",
        )

        assert checkpoint.interruption_reason == InterruptionReason.TIMEOUT

    def test_system_error_scenario(self, agent):
        """测试系统错误场景."""
        checkpoint = agent.save_checkpoint(
            session_id="task-error",
            state={
                "task_id": "task-error",
                "current_step": 1,
            },
            interruption_reason="system_error",
            metadata={"error_code": "ERR_001", "error_details": "Database connection failed"},
        )

        assert checkpoint.interruption_reason == InterruptionReason.SYSTEM_ERROR
        assert checkpoint.metadata["error_code"] == "ERR_001"


class TestCheckpointStorageBase:
    """CheckpointStorage 基类测试."""

    def test_base_methods_raise_not_implemented(self):
        """测试基类方法抛出 NotImplementedError."""
        storage = CheckpointStorage()

        with pytest.raises(NotImplementedError):
            storage.save(None)

        with pytest.raises(NotImplementedError):
            storage.load("test")

        with pytest.raises(NotImplementedError):
            storage.list_all()

        with pytest.raises(NotImplementedError):
            storage.delete("test")

        with pytest.raises(NotImplementedError):
            storage.clear()


class TestCheckpointStatusAndReason:
    """CheckpointStatus 和 InterruptionReason 枚举测试."""

    def test_checkpoint_status_values(self):
        """测试 CheckpointStatus 枚举值."""
        assert CheckpointStatus.ACTIVE.value == "active"
        assert CheckpointStatus.COMPLETED.value == "completed"
        assert CheckpointStatus.FAILED.value == "failed"
        assert CheckpointStatus.EXPIRED.value == "expired"

    def test_interruption_reason_values(self):
        """测试 InterruptionReason 枚举值."""
        assert InterruptionReason.NETWORK_DISCONNECT.value == "network_disconnect"
        assert InterruptionReason.MANUAL_CANCEL.value == "manual_cancel"
        assert InterruptionReason.TOKEN_LIMIT_EXCEEDED.value == "token_limit_exceeded"
        assert InterruptionReason.TIMEOUT.value == "timeout"
        assert InterruptionReason.SYSTEM_ERROR.value == "system_error"
        assert InterruptionReason.UNKNOWN.value == "unknown"
