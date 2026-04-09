from typing import Any, Dict, Set, Union
import unittest.mock as mock
import pytest
from flood_decision_agent.core.agent import BaseAgent, AgentStatus, ExecutionStrategy
from flood_decision_agent.core.message import BaseMessage, MessageType

class ConcreteAgent(BaseAgent):
    def _process(self, message: BaseMessage) -> str:
        if "error" in message.payload:
            raise ValueError("Intentional error")
        return f"Processed: {message.payload.get('data')}"

@pytest.fixture
def agent():
    return ConcreteAgent(agent_id="TestAgent")

def test_agent_initialization(agent):
    assert agent.agent_id == "TestAgent"
    assert agent.status == AgentStatus.IDLE
    assert agent.logger is not None

def test_agent_lifecycle_hooks(agent):
    # Use mocks to track hook calls, but preserve original behavior where needed
    with mock.patch.object(ConcreteAgent, 'before_execute', wraps=agent.before_execute) as m_before:
        with mock.patch.object(ConcreteAgent, 'after_execute', wraps=agent.after_execute) as m_after:
            msg = BaseMessage(type=MessageType.EVENT, payload={"data": "test"}, sender="User")
            result = agent.execute(msg)
            
            assert result == "Processed: test"
            m_before.assert_called_once_with(msg)
            m_after.assert_called_once()

def test_agent_error_handling(agent):
    msg = BaseMessage(type=MessageType.EVENT, payload={"error": True}, sender="User")
    
    with pytest.raises(ValueError, match="Intentional error"):
        agent.execute(msg)
    
    assert agent.status == AgentStatus.ERROR

def test_agent_idempotency(agent):
    msg = BaseMessage(
        type=MessageType.EVENT, 
        payload={"data": "once"}, 
        sender="User",
        id="unique_msg_id"
    )
    
    # First execution
    res1 = agent.execute(msg)
    assert res1 == "Processed: once"
    
    # Second execution (same message)
    # Use a flag to check if _process is called
    with mock.patch.object(ConcreteAgent, '_process', side_effect=agent._process) as m_process:
        res2 = agent.execute(msg)
        assert res2 == "Processed: once"
        m_process.assert_not_called()

def test_strategy_pattern(agent):
    class CustomStrategy(ExecutionStrategy):
        def process(self, agent: "BaseAgent", message: BaseMessage) -> Any:
            return "Custom result"
    
    agent.set_strategy(CustomStrategy())
    msg = BaseMessage(type=MessageType.EVENT, payload={}, sender="User")
    result = agent.execute(msg)
    
    assert result == "Custom result"

def test_agent_stop(agent):
    agent.stop()
    assert agent.status == AgentStatus.STOPPED
