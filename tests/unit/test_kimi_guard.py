import os

import pytest


def test_get_api_key_returns_value() -> None:
    os.environ["KIMI_API_KEY"] = "test_key_123"
    from flood_decision_agent.infrastructure.config_loader import get_api_key
    result = get_api_key("KIMI_API_KEY")
    assert result == "test_key_123"


def test_get_api_key_optional_returns_none_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NONEXISTENT_API_KEY", raising=False)
    from flood_decision_agent.infrastructure.config_loader import get_api_key
    result = get_api_key("NONEXISTENT_API_KEY", required=False)
    assert result is None
