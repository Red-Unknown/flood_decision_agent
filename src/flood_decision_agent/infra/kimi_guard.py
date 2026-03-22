from __future__ import annotations

import os


def require_kimi_api_key(env_var: str = "KIMI_API_KEY") -> str:
    api_key = os.getenv(env_var, "").strip()
    if not api_key:
        print("需要kimi_api_key")
        raise SystemExit(1)
    return api_key
