from __future__ import annotations

import json
import os
import sys
from pathlib import Path

if not os.getenv("KIMI_API_KEY", "").strip():
    print("需要kimi_api_key")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flood_decision_agent.app.pipeline import run_minimal_pipeline  # noqa: E402
from flood_decision_agent.infra.logging import setup_logging  # noqa: E402


def main() -> None:
    setup_logging()

    task_request = {
        "name": "北江超标准洪水调度",
        "goal_peak_limit_m3s": 19000,
        "constraints": ["遵守工程运行规则", "启用蓄洪区需满足规则条件"],
    }
    result = run_minimal_pipeline(task_request=task_request, seed=42)

    out_dir = Path("outputs") / "quick_start"
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshot = result.data_pool_snapshot
    rainfall = snapshot.get("rainfall_forecast")
    inflow = snapshot.get("inflow_forecast")
    plan = snapshot.get("dispatch_plan")
    order_text = snapshot.get("dispatch_order_text")

    if rainfall is not None:
        rainfall.to_csv(out_dir / "rainfall_forecast.csv", index=False)
    if inflow is not None:
        inflow.to_csv(out_dir / "inflow_forecast.csv", index=False)
    if plan is not None:
        (out_dir / "dispatch_plan.json").write_text(
            json.dumps(plan, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if order_text is not None:
        (out_dir / "dispatch_order.txt").write_text(str(order_text), encoding="utf-8")

    (out_dir / "data_pool_keys.json").write_text(
        json.dumps(sorted(snapshot.keys()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
