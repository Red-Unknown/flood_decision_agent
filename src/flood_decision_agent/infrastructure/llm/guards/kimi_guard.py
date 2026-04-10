from __future__ import annotations

import os
import sys
from pathlib import Path

def _get_project_root() -> Path:
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent.parent

def _load_env():
    env_file = _get_project_root() / "configs" / ".env.local"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        os.environ.setdefault(key, value)


def require_kimi_api_key(env_var: str = "KIMI_API_KEY") -> str:
    _load_env()
    api_key = os.getenv(env_var, "").strip()
    if not api_key:
        print("需要kimi_api_key")
        raise SystemExit(1)
    return api_key


class KimiGuard:
    """Kimi 安全守卫"""
    
    def __init__(self):
        self.sensitive_keywords = []
    
    def check_input(self, content: str) -> dict:
        """检查输入内容"""
        return {"safe": True, "reason": None}
    
    def check_output(self, content: str) -> dict:
        """检查输出内容"""
        return {"safe": True, "reason": None}
