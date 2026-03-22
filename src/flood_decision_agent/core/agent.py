from __future__ import annotations

import abc
import enum
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Protocol, Union

from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.infra.logging import get_logger


class AgentStatus(enum.Enum):
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    STOPPED = "stopped"
    ERROR = "error"


class ExecutionStrategy(Protocol):
    """策略模式接口：定义 Agent 处理消息的具体逻辑"""

    def process(self, agent: "BaseAgent", message: BaseMessage) -> Any:
        ...


class DefaultExecutionStrategy(ExecutionStrategy):
    """默认策略：直接调用 Agent 的 _process 方法"""

    def process(self, agent: "BaseAgent", message: BaseMessage) -> Any:
        return agent._process(message)


class BaseAgent(ABC):
    """Agent 基类，提供完整的生命周期管理与标准化的消息处理机制"""

    def __init__(
        self,
        agent_id: str,
        strategy: Optional[ExecutionStrategy] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.agent_id = agent_id
        self.logger = get_logger()
        self.status = AgentStatus.INITIALIZING
        self.strategy = strategy or DefaultExecutionStrategy()
        self.metadata = metadata or {}
        self.processed_messages: Dict[str, Any] = {}  # 用于简单幂等性检查

        self.logger.info(f"[Agent {self.agent_id}] 初始化完成")
        self.on_start()
        self.status = AgentStatus.IDLE

    # --- 生命周期钩子 (Lifecycle Hooks) ---

    def on_start(self) -> None:
        """Agent 启动时的回调"""
        pass

    def on_stop(self) -> None:
        """Agent 停止时的回调"""
        self.status = AgentStatus.STOPPED

    def before_execute(self, message: BaseMessage) -> None:
        """消息处理前的回调"""
        self.status = AgentStatus.BUSY
        self.logger.debug(f"[Agent {self.agent_id}] 开始处理消息: {message.id}")

    def after_execute(self, message: BaseMessage, result: Any) -> None:
        """消息处理后的回调"""
        self.status = AgentStatus.IDLE
        self.logger.debug(f"[Agent {self.agent_id}] 消息处理成功: {message.id}")

    def on_error(self, message: BaseMessage, error: Exception) -> None:
        """消息处理发生错误时的回调"""
        self.status = AgentStatus.ERROR
        error_msg = f"[Agent {self.agent_id}] 处理消息 {message.id} 失败: {str(error)}\n{traceback.format_exc()}"
        self.logger.error(error_msg)

    # --- 消息处理机制 ---

    def execute(self, message: BaseMessage) -> Any:
        """
        统一的消息执行入口，包含：
        1. 幂等性检查
        2. 生命周期管理
        3. 异常处理
        4. 策略模式调用
        """
        # 幂等性检查 (基于 idempotency_key)
        ikey = message.get_idempotency_key()
        if ikey in self.processed_messages:
            self.logger.warning(f"[Agent {self.agent_id}] 收到重复消息: {ikey}，跳过执行")
            return self.processed_messages[ikey]

        try:
            self.before_execute(message)

            # 调用策略执行核心逻辑
            result = self.strategy.process(self, message)

            # 记录结果（用于幂等性）
            self.processed_messages[ikey] = result

            self.after_execute(message, result)
            return result

        except Exception as e:
            self.on_error(message, e)
            raise e  # 向上抛出异常，或根据需求在此处封装统一错误消息

    @abstractmethod
    def _process(self, message: BaseMessage) -> Any:
        """
        具体的业务逻辑处理，由子类实现。
        如果使用默认策略，该方法将被调用。
        """
        pass

    def set_strategy(self, strategy: ExecutionStrategy) -> None:
        """动态更换执行策略"""
        self.strategy = strategy
        self.logger.info(f"[Agent {self.agent_id}] 执行策略已更新")

    def stop(self) -> None:
        """停止 Agent"""
        self.on_stop()
        self.logger.info(f"[Agent {self.agent_id}] 已停止")
