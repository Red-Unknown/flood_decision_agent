import json
from datetime import datetime
import pytest
from flood_decision_agent.core.message import BaseMessage, MessageType

def test_message_initialization():
    payload = {"key": "value"}
    msg = BaseMessage(
        type=MessageType.TASK_REQUEST,
        payload=payload,
        sender="AgentA"
    )
    assert msg.type == MessageType.TASK_REQUEST
    assert msg.payload == payload
    assert msg.sender == "AgentA"
    assert msg.id is not None
    assert isinstance(msg.timestamp, datetime)

def test_message_serialization():
    payload = {"data": [1, 2, 3]}
    msg = BaseMessage(
        type=MessageType.EVENT,
        payload=payload,
        sender="SenderX",
        receiver="ReceiverY",
        idempotency_key="key123"
    )
    
    serialized = msg.serialize()
    deserialized = BaseMessage.deserialize(serialized)
    
    assert deserialized.type == msg.type
    assert deserialized.payload == msg.payload
    assert deserialized.sender == msg.sender
    assert deserialized.receiver == msg.receiver
    assert deserialized.id == msg.id
    assert deserialized.idempotency_key == msg.idempotency_key
    assert deserialized.timestamp == msg.timestamp

def test_idempotency_key():
    msg = BaseMessage(
        type=MessageType.NODE_EXECUTE,
        payload={},
        sender="AgentB"
    )
    # Default key
    expected_default = f"{msg.sender}:{msg.type.value}:{msg.id}"
    assert msg.get_idempotency_key() == expected_default
    
    # Custom key
    msg2 = BaseMessage(
        type=MessageType.NODE_EXECUTE,
        payload={},
        sender="AgentB",
        idempotency_key="custom_key"
    )
    assert msg2.get_idempotency_key() == "custom_key"

def test_message_frozen():
    msg = BaseMessage(type=MessageType.EVENT, payload={}, sender="A")
    with pytest.raises(Exception):
        msg.sender = "B"
