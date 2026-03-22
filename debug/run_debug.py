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

    config_path = Path("debug") / "scenarios" / "bei_jiang" / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    result = run_minimal_pipeline(
        task_request=config["task_request"],
        seed=int(config.get("seed", 42)),
    )

    out_dir = Path("outputs") / "debug" / "bei_jiang"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "data_pool_snapshot.json").write_text(
        json.dumps(
            result.data_pool_snapshot, ensure_ascii=False, default=str, indent=2
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
