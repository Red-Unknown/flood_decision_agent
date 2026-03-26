"""MCP Core Session - MCP 会话管理

提供 MCP 会话的生命周期管理和状态跟踪。
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Callable
import uuid

from flood_decision_agent.mcp.protocol.types import (
    MCPMessage,
    MCPRequest,
    MCPResponse,
    MessageType,
)
from flood_decision_agent.mcp.protocol.constants import (
    DEFAULT_TIMEOUT,
    HEARTBEAT_INTERVAL,
)
from flood_decision_agent.infra.logging import get_logger


class SessionState(Enum):
    """会话状态"""
    CREATED = auto()      # 已创建
    CONNECTING = auto()   # 连接中
    CONNECTED = auto()    # 已连接
    READY = auto()        # 就绪（已初始化）
    CLOSING = auto()      # 关闭中
    CLOSED = auto()       # 已关闭
    ERROR = auto()        # 错误状态


@dataclass
class SessionStats:
    """会话统计信息
    
    Attributes:
        messages_sent: 发送消息数
        messages_received: 接收消息数
        requests_pending: 待处理请求数
        errors_count: 错误计数
        connected_at: 连接时间
        last_activity: 最后活动时间
    """
    messages_sent: int = 0
    messages_received: int = 0
    requests_pending: int = 0
    errors_count: int = 0
    connected_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    def record_sent(self) -> None:
        """记录发送"""
        self.messages_sent += 1
        self.last_activity = datetime.now()
    
    def record_received(self) -> None:
        """记录接收"""
        self.messages_received += 1
        self.last_activity = datetime.now()
    
    def record_error(self) -> None:
        """记录错误"""
        self.errors_count += 1


@dataclass
class PendingRequest:
    """待处理请求
    
    Attributes:
        request_id: 请求 ID
        future: 异步 Future
        timeout: 超时时间
        created_at: 创建时间
    """
    request_id: str
    future: asyncio.Future
    timeout: float
    created_at: datetime
    
    def is_expired(self) -> bool:
        """检查是否已超时"""
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.timeout


class MCPSession:
    """MCP 会话
    
    管理 MCP 连接会话的生命周期，处理消息收发和状态跟踪。
    
    Example:
        ```python
        session = MCPSession(session_id="sess-001")
        await session.initialize()
        
        # 发送请求
        response = await session.send_request(request)
        
        await session.close()
        ```
    """
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        heartbeat_interval: float = HEARTBEAT_INTERVAL,
    ):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.timeout = timeout
        self.heartbeat_interval = heartbeat_interval
        
        self._state = SessionState.CREATED
        self._stats = SessionStats()
        self._pending_requests: Dict[str, PendingRequest] = {}
        self._handlers: Dict[str, List[Callable]] = {}
        self._logger = get_logger().bind(name=f"MCPSession-{self.session_id}")
        
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> SessionState:
        """当前状态"""
        return self._state
    
    @property
    def is_active(self) -> bool:
        """会话是否活跃"""
        return self._state in (SessionState.CONNECTED, SessionState.READY)
    
    @property
    def is_ready(self) -> bool:
        """会话是否就绪"""
        return self._state == SessionState.READY
    
    @property
    def stats(self) -> SessionStats:
        """会话统计"""
        return self._stats
    
    async def initialize(self) -> bool:
        """初始化会话
        
        Returns:
            初始化是否成功
        """
        async with self._lock:
            if self._state != SessionState.CREATED:
                return False
            
            self._state = SessionState.CONNECTING
            
            try:
                # 启动后台任务
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                
                self._state = SessionState.READY
                self._stats.connected_at = datetime.now()
                self._logger.info("会话已初始化")
                return True
                
            except Exception as e:
                self._state = SessionState.ERROR
                self._logger.error(f"会话初始化失败: {e}")
                return False
    
    async def close(self) -> None:
        """关闭会话"""
        async with self._lock:
            if self._state in (SessionState.CLOSED, SessionState.CLOSING):
                return
            
            self._state = SessionState.CLOSING
            
            # 取消所有待处理请求
            for pending in self._pending_requests.values():
                if not pending.future.done():
                    pending.future.set_exception(asyncio.CancelledError("会话关闭"))
            self._pending_requests.clear()
            
            # 取消后台任务
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            self._state = SessionState.CLOSED
            self._logger.info("会话已关闭")
    
    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """发送请求并等待响应
        
        Args:
            request: MCP 请求
            
        Returns:
            MCP 响应
            
        Raises:
            RuntimeError: 会话未就绪
            asyncio.TimeoutError: 请求超时
        """
        if not self.is_active:
            raise RuntimeError("会话未就绪")
        
        request_id = request.request_id or str(uuid.uuid4())[:8]
        
        # 创建 Future
        future = asyncio.get_event_loop().create_future()
        
        pending = PendingRequest(
            request_id=request_id,
            future=future,
            timeout=request.timeout or self.timeout,
            created_at=datetime.now(),
        )
        
        self._pending_requests[request_id] = pending
        self._stats.requests_pending = len(self._pending_requests)
        
        try:
            # 实际发送由子类或传输层实现
            await self._do_send_request(request, request_id)
            
            # 等待响应
            response = await asyncio.wait_for(
                future,
                timeout=pending.timeout,
            )
            
            self._stats.record_sent()
            return response
            
        except asyncio.TimeoutError:
            self._stats.record_error()
            raise
        finally:
            self._pending_requests.pop(request_id, None)
            self._stats.requests_pending = len(self._pending_requests)
    
    async def handle_response(self, response: MCPResponse) -> None:
        """处理收到的响应
        
        Args:
            response: MCP 响应
        """
        request_id = response.request_id
        if not request_id:
            self._logger.warning("收到无 request_id 的响应")
            return
        
        pending = self._pending_requests.get(request_id)
        if pending and not pending.future.done():
            pending.future.set_result(response)
            self._stats.record_received()
        else:
            self._logger.warning(f"收到未知或已处理的响应: {request_id}")
    
    def on_event(self, event: str, handler: Callable) -> None:
        """注册事件处理器
        
        Args:
            event: 事件名称
            handler: 处理函数
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
    
    def off_event(self, event: str, handler: Optional[Callable] = None) -> None:
        """注销事件处理器
        
        Args:
            event: 事件名称
            handler: 处理函数，None 则移除所有
        """
        if event in self._handlers:
            if handler is None:
                self._handlers[event] = []
            else:
                self._handlers[event] = [h for h in self._handlers[event] if h != handler]
    
    async def _emit(self, event: str, *args, **kwargs) -> None:
        """触发事件"""
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                self._logger.error(f"事件处理器出错: {e}")
    
    async def _do_send_request(self, request: MCPRequest, request_id: str) -> None:
        """实际发送请求（子类实现）"""
        # 由具体实现覆盖
        pass
    
    async def _heartbeat_loop(self) -> None:
        """心跳循环"""
        try:
            while self.is_active:
                await asyncio.sleep(self.heartbeat_interval)
                if self.is_active:
                    await self._send_heartbeat()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._logger.error(f"心跳循环出错: {e}")
    
    async def _send_heartbeat(self) -> None:
        """发送心跳（子类实现）"""
        # 由具体实现覆盖
        pass
    
    async def _cleanup_loop(self) -> None:
        """清理循环"""
        try:
            while self.is_active:
                await asyncio.sleep(5.0)
                await self._cleanup_expired_requests()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._logger.error(f"清理循环出错: {e}")
    
    async def _cleanup_expired_requests(self) -> None:
        """清理过期请求"""
        expired = [
            req_id for req_id, pending in self._pending_requests.items()
            if pending.is_expired()
        ]
        
        for req_id in expired:
            pending = self._pending_requests.pop(req_id, None)
            if pending and not pending.future.done():
                pending.future.set_exception(asyncio.TimeoutError("请求超时"))
                self._stats.record_error()
        
        self._stats.requests_pending = len(self._pending_requests)
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
