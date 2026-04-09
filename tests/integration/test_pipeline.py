from flood_decision_agent.app.pipeline import run_minimal_pipeline


def test_run_minimal_pipeline_produces_expected_keys() -> None:
    result = run_minimal_pipeline(task_request={"name": "test"}, seed=7)
    snapshot = result.data_pool_snapshot
    assert "rainfall_forecast" in snapshot
    assert "inflow_forecast" in snapshot
    assert "dispatch_plan" in snapshot
    assert "dispatch_order_text" in snapshot
