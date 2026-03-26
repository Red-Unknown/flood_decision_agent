"""MCP Core Transport - MCP 传输层

提供 MCP 协议的传输层实现，支持多种传输方式。
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple, Union

from flood_decision_agent.mcp.protocol.types import MCPMessage
from flood_decision_agent.mcp.protocol.constants import (
    DEFAULT_BUFFER_SIZE,
    STDIO_ENCODING,
    MAX_MESSAGE_SIZE,
)
from flood_decision_agent.infra.logging import get_logger


class TransportType(Enum):
    """传输类型"""
    STDIO = auto()      # 标准输入输出
    SOCKET = auto()     # TCP Socket
    WEBSOCKET = auto()  # WebSocket
    HTTP = auto()       # HTTP
    MEMORY = auto()     # 内存（测试用）


@dataclass
class TransportConfig:
    """传输配置
    
    Attributes:
        transport_type: 传输类型
        buffer_size: 缓冲区大小
        encoding: 编码
        max_message_size: 最大消息大小
    """
    transport_type: TransportType = TransportType.STDIO
    buffer_size: int = DEFAULT_BUFFER_SIZE
    encoding: str = STDIO_ENCODING
    max_message_size: int = MAX_MESSAGE_SIZE


class MCPTransport(ABC):
    """MCP 传输基类
    
    提供 MCP 协议传输层的基础接口。
    
    Example:
        ```python
        transport = StdioTransport()
        await transport.connect()
        
        async for message in transport.receive_messages():
            # 处理消息
            pass
        
        await transport.send(message)
        await transport.close()
        ```
    """
    
    def __init__(self, config: Optional[TransportConfig] = None):
        self.config = config or TransportConfig()
        self._connected = False
        self._logger = get_logger().bind(name=f"MCPTransport-{self.config.transport_type.name}")
        self._lock = asyncio.Lock()
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    @property
    def transport_type(self) -> TransportType:
        """传输类型"""
        return self.config.transport_type
    
    async def connect(self) -> bool:
        """建立连接
        
        Returns:
            连接是否成功
        """
        async with self._lock:
            if self._connected:
                return True
            
            try:
                success = await self._do_connect()
                self._connected = success
                if success:
                    self._logger.info(f"传输层已连接: {self.transport_type.name}")
                return success
            except Exception as e:
                self._logger.error(f"连接失败: {e}")
                return False
    
    async def close(self) -> None:
        """关闭连接"""
        async with self._lock:
            if not self._connected:
                return
            
            try:
                await self._do_close()
                self._connected = False
                self._logger.info("传输层已关闭")
            except Exception as e:
                self._logger.error(f"关闭连接时出错: {e}")
    
    async def send(self, message: Union[str, bytes, MCPMessage]) -> bool:
        """发送消息
        
        Args:
            message: 要发送的消息
            
        Returns:
            发送是否成功
        """
        if not self._connected:
            self._logger.error("发送失败：未连接")
            return False
        
        try:
            # 序列化消息
            if isinstance(message, MCPMessage):
                data = message.to_dict()
                import json
                message = json.dumps(data, ensure_ascii=False)
            
            if isinstance(message, str):
                message = message.encode(self.config.encoding)
            
            # 检查消息大小
            if len(message) > self.config.max_message_size:
                self._logger.error(f"消息过大: {len(message)} bytes")
                return False
            
            await self._do_send(message)
            return True
            
        except Exception as e:
            self._logger.error(f"发送失败: {e}")
            return False
    
    async def receive(self) -> Optional[bytes]:
        """接收消息
        
        Returns:
            接收到的消息，失败返回 None
        """
        if not self._connected:
            return None
        
        try:
            return await self._do_receive()
        except Exception as e:
            self._logger.error(f"接收失败: {e}")
            return None
    
    async def receive_messages(self) -> AsyncIterator[MCPMessage]:
        """接收消息迭代器
        
        Yields:
            MCPMessage 实例
        """
        while self._connected:
            try:
                data = await self.receive()
                if data is None:
                    break
                
                # 解析消息
                import json
                message_dict = json.loads(data.decode(self.config.encoding))
                message = MCPMessage(
                    message_type=message_dict.get("message_type"),
                    payload=message_dict.get("payload", {}),
                    metadata=message_dict.get("metadata", {}),
                )
                yield message
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"消息解析失败: {e}")
                continue
    
    @abstractmethod
    async def _do_connect(self) -> bool:
        """执行连接（子类实现）"""
        pass
    
    @abstractmethod
    async def _do_close(self) -> None:
        """执行关闭（子类实现）"""
        pass
    
    @abstractmethod
    async def _do_send(self, data: bytes) -> None:
        """执行发送（子类实现）"""
        pass
    
    @abstractmethod
    async def _do_receive(self) -> Optional[bytes]:
        """执行接收（子类实现）"""
        pass
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


class StdioTransport(MCPTransport):
    """标准输入输出传输
    
    通过标准输入输出进行 MCP 通信。
    """
    
    def __init__(self, config: Optional[TransportConfig] = None):
        if config is None:
            config = TransportConfig(transport_type=TransportType.STDIO)
        super().__init__(config)
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
    
    async def _do_connect(self) -> bool:
        """连接到标准输入输出"""
        try:
            # 获取标准输入输出
            self._reader = asyncio.StreamReader()
            self._writer = None  # 标准输出通过 print 或 sys.stdout
            
            # 在 Windows 上需要特殊处理
            import sys
            if sys.platform == "win32":
                # Windows 需要设置二进制模式
                import msvcrt
                msvcrt.setmode(sys.stdin.fileno(), 0x8000)  # O_BINARY
                msvcrt.setmode(sys.stdout.fileno(), 0x8000)
            
            return True
        except Exception as e:
            self._logger.error(f"STDIO 连接失败: {e}")
            return False
    
    async def _do_close(self) -> None:
        """关闭 STDIO 连接"""
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except:
                pass
    
    async def _do_send(self, data: bytes) -> None:
        """通过标准输出发送"""
        import sys
        # 使用长度前缀协议
        length = len(data)
        header = f"Content-Length: {length}\r\n\r\n".encode(self.config.encoding)
        
        sys.stdout.buffer.write(header)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    
    async def _do_receive(self) -> Optional[bytes]:
        """从标准输入接收"""
        import sys
        
        try:
            # 读取头部
            header_lines = []
            while True:
                line = await self._reader.readline()
                if not line:
                    return None
                line = line.decode(self.config.encoding).strip()
                if not line:
                    break
                header_lines.append(line)
            
            # 解析 Content-Length
            content_length = 0
            for line in header_lines:
                if line.startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())
                    break
            
            if content_length == 0:
                return None
            
            # 读取内容
            data = await self._reader.readexactly(content_length)
            return data
            
        except asyncio.IncompleteReadError:
            return None
        except Exception as e:
            self._logger.error(f"接收失败: {e}")
            return None


class MemoryTransport(MCPTransport):
    """内存传输（用于测试）
    
    通过内存队列进行 MCP 通信，主要用于单元测试。
    """
    
    def __init__(
        self,
        send_queue: asyncio.Queue,
        receive_queue: asyncio.Queue,
        config: Optional[TransportConfig] = None,
    ):
        if config is None:
            config = TransportConfig(transport_type=TransportType.MEMORY)
        super().__init__(config)
        self._send_queue = send_queue
        self._receive_queue = receive_queue
    
    async def _do_connect(self) -> bool:
        """连接（内存传输总是成功）"""
        return True
    
    async def _do_close(self) -> None:
        """关闭（无需操作）"""
        pass
    
    async def _do_send(self, data: bytes) -> None:
        """发送到队列"""
        await self._send_queue.put(data)
    
    async def _do_receive(self) -> Optional[bytes]:
        """从队列接收"""
        try:
            # 设置超时，避免永久阻塞
            return await asyncio.wait_for(
                self._receive_queue.get(),
                timeout=1.0,
            )
        except asyncio.TimeoutError:
            return None


class TransportFactory:
    """传输工厂
    
    用于创建不同类型的传输实例。
    """
    
    @staticmethod
    def create_stdio_transport() -> StdioTransport:
        """创建 STDIO 传输"""
        config = TransportConfig(transport_type=TransportType.STDIO)
        return StdioTransport(config)
    
    @staticmethod
    def create_memory_transport(
        send_queue: asyncio.Queue,
        receive_queue: asyncio.Queue,
    ) -> MemoryTransport:
        """创建内存传输"""
        config = TransportConfig(transport_type=TransportType.MEMORY)
        return MemoryTransport(send_queue, receive_queue, config)
