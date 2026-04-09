"""Kimi LLM 客户端"""
import os
from typing import Any, Dict, List, Optional

from src.flood_decision_agent.shared.utils.timeout_utils import (
    with_timeout,
    TimeoutManager,
    RetryWithTimeout,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .client import LLMClient
from ..config_loader import get_api_key

# 创建LLM专用的超时管理器
llm_timeout_manager = TimeoutManager({
    "llm_chat": 60.0,
    "llm_stream": 120.0,
    "llm_complete": 60.0,
})


class KimiClient(LLMClient):
    """Kimi LLM 客户端实现
    
    使用 Moonshot AI API 进行对话生成。
    支持同步和异步调用。
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "moonshot-v1-128k",
        temperature: float = 0.7,
        max_tokens: int = 8192
    ):
        super().__init__(model, temperature, max_tokens)
        self.api_key = api_key or get_api_key("KIMI_API_KEY")
        
        if not self.api_key:
            raise ValueError("需要提供 API Key 或设置 KIMI_API_KEY 环境变量")
        
        # 初始化 OpenAI 客户端（Kimi API 兼容 OpenAI 格式）
        if OpenAI:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.moonshot.cn/v1"
            )
        else:
            self._client = None
    
    def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """同步完成接口
        
        Args:
            prompt: 用户提示词
            system_message: 系统消息（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）
            
        Returns:
            LLM生成的文本
        """
        if not self._client:
            raise RuntimeError("OpenAI 客户端未初始化，请安装 openai 包")
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Kimi API 调用失败: {e}")
    
    @llm_timeout_manager.decorator_for("llm_chat")
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天接口（带60秒超时）"""
        if not self._client:
            raise RuntimeError("OpenAI 客户端未初始化")

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Kimi API 调用失败: {e}")
    
    @llm_timeout_manager.decorator_for("llm_stream")
    async def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """流式聊天接口（带120秒超时）"""
        if not self._client:
            raise RuntimeError("OpenAI 客户端未初始化")

        try:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"Kimi API 流式调用失败: {e}")


# 全局客户端实例
_kimi_client: Optional[KimiClient] = None


def get_kimi_client() -> KimiClient:
    """获取全局 Kimi 客户端实例
    
    Returns:
        KimiClient 实例
    """
    global _kimi_client
    if _kimi_client is None:
        _kimi_client = KimiClient()
    return _kimi_client
