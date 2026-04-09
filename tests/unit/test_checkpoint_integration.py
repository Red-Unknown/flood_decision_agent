"""CheckpointResumptionAgent 集成测试.

测试 CheckpointResumptionAgent 与 DecisionChainGeneratorAgent 的集成功能。
"""

import pytest
import uuid
from unittest.mock import Mock, patch

from flood_decision_agent.agents.decision_chain import (
    CheckpointResumptionAgent,
    DecisionChainGeneratorAgent,
    InterruptionReason,
)
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.shared.exceptions.checkpoint_exceptions import (
    CheckpointNotFoundError,
)


class TestCheckpointIntegration:
    """Checkpoint 集成测试类."""

    @pytest.fixture
    def checkpoint_agent(self):
        """创建 CheckpointResumptionAgent 实例."""
        return CheckpointResumptionAgent()

    @pytest.fixture
    def generator_agent(self, checkpoint_agent):
        """创建带 checkpoint_agent 的 DecisionChainGeneratorAgent 实例."""
        return DecisionChainGeneratorAgent(checkpoint_agent=checkpoint_agent)

    def test_generator_has_checkpoint_agent(self, generator_agent):
        """测试 DecisionChainGeneratorAgent 有 checkpoint_agent 属性."""
        assert hasattr(generator_agent, "checkpoint_agent")
        assert isinstance(generator_agent.checkpoint_agent, CheckpointResumptionAgent)

    def test_generator_has_resume_session_method(self, generator_agent):
        """测试 DecisionChainGeneratorAgent 有 resume_session 方法."""
        assert hasattr(generator_agent, "resume_session")
        assert callable(generator_agent.resume_session)

    def test_classify_network_exception(self, generator_agent):
        """测试网络异常分类."""
        # 模拟网络异常
        network_errors = [
            Exception("Connection timeout"),
            Exception("Network unreachable"),
            Exception("Connection refused"),
            Exception("Disconnect from server"),
        ]

        for error in network_errors:
            result = generator_agent._classify_exception(error)
            assert result == InterruptionReason.NETWORK_DISCONNECT, f"Failed for: {error}"

    def test_classify_token_exception(self, generator_agent):
        """测试 Token 超限异常分类."""
        token_errors = [
            Exception("Token limit exceeded"),
            Exception("Rate limit reached"),
            Exception("Quota exceeded"),
            Exception("Context length too long"),
        ]

        for error in token_errors:
            result = generator_agent._classify_exception(error)
            assert result == InterruptionReason.TOKEN_LIMIT_EXCEEDED, f"Failed for: {error}"

    def test_classify_cancel_exception(self, generator_agent):
        """测试手动取消异常分类."""
        cancel_errors = [
            Exception("Operation cancelled"),
            Exception("User aborted"),
            KeyboardInterrupt("Interrupted"),
        ]

        for error in cancel_errors:
            result = generator_agent._classify_exception(error)
            assert result == InterruptionReason.MANUAL_CANCEL, f"Failed for: {error}"

    def test_classify_system_error(self, generator_agent):
        """测试系统错误分类."""
        system_errors = [
            Exception("Unknown error"),
            ValueError("Invalid value"),
            RuntimeError("Runtime failed"),
        ]

        for error in system_errors:
            result = generator_agent._classify_exception(error)
            assert result == InterruptionReason.SYSTEM_ERROR, f"Failed for: {error}"

    def test_save_checkpoint_on_exception(self, generator_agent, checkpoint_agent):
        """测试异常时自动保存断点."""
        session_id = str(uuid.uuid4())
        user_input = "测试洪水分析任务"

        # 模拟 generate_chain 抛出网络异常
        with patch.object(
            generator_agent,
            "generate_chain",
            side_effect=Exception("Connection timeout"),
        ):
            with pytest.raises(Exception):
                generator_agent._generate_chain_with_checkpoint(
                    user_input, "natural_language", session_id
                )

        # 验证断点已保存
        checkpoint = checkpoint_agent.storage.load(session_id)
        assert checkpoint is not None
        assert checkpoint.state["user_input"] == user_input
        assert checkpoint.interruption_reason == InterruptionReason.NETWORK_DISCONNECT

    def test_save_checkpoint_on_token_limit(self, generator_agent, checkpoint_agent):
        """测试 Token 超限时自动保存断点."""
        session_id = str(uuid.uuid4())
        user_input = "测试任务"

        # 模拟 Token 超限异常
        with patch.object(
            generator_agent,
            "generate_chain",
            side_effect=Exception("Token limit exceeded"),
        ):
            with pytest.raises(Exception):
                generator_agent._generate_chain_with_checkpoint(
                    user_input, "natural_language", session_id
                )

        # 验证断点已保存且原因正确
        checkpoint = checkpoint_agent.storage.load(session_id)
        assert checkpoint is not None
        assert checkpoint.interruption_reason == InterruptionReason.TOKEN_LIMIT_EXCEEDED

    def test_save_checkpoint_on_manual_cancel(self, generator_agent, checkpoint_agent):
        """测试手动取消时自动保存断点."""
        session_id = str(uuid.uuid4())
        user_input = "测试任务"

        # 模拟手动取消异常
        with patch.object(
            generator_agent,
            "generate_chain",
            side_effect=KeyboardInterrupt("User cancelled"),
        ):
            with pytest.raises(KeyboardInterrupt):
                generator_agent._generate_chain_with_checkpoint(
                    user_input, "natural_language", session_id
                )

        # 验证断点已保存且原因正确
        checkpoint = checkpoint_agent.storage.load(session_id)
        assert checkpoint is not None
        assert checkpoint.interruption_reason == InterruptionReason.MANUAL_CANCEL

    def test_resume_session_success(self, generator_agent, checkpoint_agent):
        """测试成功恢复会话."""
        session_id = str(uuid.uuid4())
        user_input = "分析洪水风险"

        # 先保存一个断点
        checkpoint_agent.save_checkpoint(
            session_id=session_id,
            state={
                "user_input": user_input,
                "input_type": "natural_language",
                "current_phase": "intent_parsing",
            },
            interruption_reason=InterruptionReason.NETWORK_DISCONNECT.value,
        )

        # 模拟正常生成
        with patch.object(
            generator_agent,
            "generate_chain",
            return_value=(Mock(), {"test": "metadata"}),
        ):
            task_graph, metadata = generator_agent.resume_session(session_id)

        # 验证恢复结果
        assert metadata["resumed_from_checkpoint"] is True
        assert metadata["session_id"] == session_id
        assert metadata["original_interruption_reason"] == "network_disconnect"

    def test_resume_session_not_found(self, generator_agent):
        """测试恢复不存在的会话."""
        with pytest.raises(CheckpointNotFoundError):
            generator_agent.resume_session("non-existent-session-id")

    def test_process_message_with_session_id(self, generator_agent):
        """测试处理带 session_id 的消息."""
        session_id = str(uuid.uuid4())
        message = BaseMessage(
            type=MessageType.TASK_REQUEST,
            sender="user",
            receiver="DecisionChainGenerator",
            payload={
                "input": "测试输入",
                "input_type": "natural_language",
                "session_id": session_id,
            },
        )

        # 模拟正常生成
        with patch.object(
            generator_agent,
            "generate_chain",
            return_value=(Mock(), {"test": "metadata"}),
        ):
            response = generator_agent.execute(message)

        # 验证响应
        assert response.type == MessageType.TASK_RESPONSE
        assert response.receiver == "NodeSchedulerAgent"

    def test_checkpoint_metadata_saved(self, generator_agent, checkpoint_agent):
        """测试断点元数据正确保存."""
        session_id = str(uuid.uuid4())

        with patch.object(
            generator_agent,
            "generate_chain",
            side_effect=Exception("Connection timeout"),
        ):
            with pytest.raises(Exception):
                generator_agent._generate_chain_with_checkpoint(
                    "测试输入", "natural_language", session_id
                )

        checkpoint = checkpoint_agent.storage.load(session_id)
        assert checkpoint.metadata["error_type"] == "Exception"
        assert "error_message" in checkpoint.metadata
        assert checkpoint.metadata["agent_id"] == generator_agent.agent_id


class TestCheckpointResumptionAgentExport:
    """测试 CheckpointResumptionAgent 导出."""

    def test_export_from_decision_chain_module(self):
        """测试从 decision_chain 模块导出."""
        from flood_decision_agent.agents.decision_chain import (
            CheckpointResumptionAgent,
            Checkpoint,
            CheckpointStatus,
            CheckpointStorage,
            MemoryCheckpointStorage,
            InterruptionReason,
        )

        # 验证所有类都可访问
        assert CheckpointResumptionAgent is not None
        assert Checkpoint is not None
        assert CheckpointStatus is not None
        assert CheckpointStorage is not None
        assert MemoryCheckpointStorage is not None
        assert InterruptionReason is not None

    def test_all_list_includes_checkpoint(self):
        """测试 __all__ 列表包含 Checkpoint 相关导出."""
        from flood_decision_agent.agents.decision_chain import __all__

        assert "CheckpointResumptionAgent" in __all__
        assert "Checkpoint" in __all__
        assert "CheckpointStatus" in __all__
        assert "CheckpointStorage" in __all__
        assert "MemoryCheckpointStorage" in __all__
        assert "InterruptionReason" in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
