"""LLM 客户端基类"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMClient(ABC):
    """LLM 客户端抽象基类"""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 8192):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天接口"""
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """流式聊天接口"""
        pass
