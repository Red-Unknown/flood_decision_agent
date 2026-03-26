"""Kimi Guard - 安全守卫"""
from typing import Any, Dict, List


class KimiGuard:
    """Kimi 安全守卫"""
    
    def __init__(self):
        self.sensitive_keywords = []
    
    def check_input(self, content: str) -> Dict[str, Any]:
        """检查输入内容"""
        return {"safe": True, "reason": None}
    
    def check_output(self, content: str) -> Dict[str, Any]:
        """检查输出内容"""
        return {"safe": True, "reason": None}
