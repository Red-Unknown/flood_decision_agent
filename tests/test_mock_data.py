import pandas as pd

from flood_decision_agent.data.mock_data import MockDataGenerator


def test_generate_all_and_validate_all_ok() -> None:
    gen = MockDataGenerator(seed=123)
    datasets = gen.generate_all()
    report = gen.validate_all(datasets)
    assert report.ok is True
    assert "rainfall_forecast" in datasets
    assert "inflow_forecast" in datasets


def test_validate_time_index_detects_non_monotonic() -> None:
    gen = MockDataGenerator(seed=1)
    df = pd.DataFrame(
        {
            "timestamp": ["2025-01-02T00:00:00Z", "2025-01-01T00:00:00Z"],
            "rainfall_mm": [1.0, 2.0],
        }
    )
    report = gen.validate_rainfall_forecast(df)
    assert report.ok is False
    assert any("不是单调递增" in e for e in report.errors)
