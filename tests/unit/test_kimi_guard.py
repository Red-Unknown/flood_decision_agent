import os

import pytest

from flood_decision_agent.infra.kimi_guard import require_kimi_api_key


def test_require_kimi_api_key_missing_exits(capsys: pytest.CaptureFixture[str]) -> None:
    os.environ.pop("KIMI_API_KEY", None)
    with pytest.raises(SystemExit) as excinfo:
        require_kimi_api_key()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "需要kimi_api_key" in captured.out


def test_require_kimi_api_key_returns_value() -> None:
    os.environ["KIMI_API_KEY"] = "test_key"
    assert require_kimi_api_key() == "test_key"
