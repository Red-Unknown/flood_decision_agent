"""对话状态管理 - 定义对话状态和生命周期."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ConversationStatus(Enum):
    """对话状态枚举."""
    
    INIT = "init"  # 初始化
    ACTIVE = "active"  # 进行中
    WAITING_USER_INPUT = "waiting_user_input"  # 等待用户输入
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 出错
    TIMEOUT = "timeout"  # 超时


@dataclass
class ConversationTurn:
    """对话轮次记录."""
    
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    user_input: str = ""
    agent_response: str = ""
    intent: Dict[str, Any] = field(default_factory=dict)
    task_graph: Optional[Any] = None
    execution_result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    """对话状态类.
    
    管理单个对话的完整生命周期和状态信息。
    """
    
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    status: ConversationStatus = ConversationStatus.INIT
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    # 对话历史
    turns: List[ConversationTurn] = field(default_factory=list)
    max_turns: int = 20  # 最大轮数
    
    # 上下文信息
    context: Dict[str, Any] = field(default_factory=dict)
    
    # 当前任务信息
    current_task_type: Optional[str] = None
    current_task_graph: Optional[Any] = None
    accumulated_data: Dict[str, Any] = field(default_factory=dict)
    
    # 统计信息
    total_tokens: int = 0
    error_count: int = 0
    
    def add_turn(self, user_input: str, agent_response: str = "", 
                 intent: Optional[Dict[str, Any]] = None,
                 execution_result: Optional[Dict[str, Any]] = None) -> ConversationTurn:
        """添加对话轮次.
        
        Args:
            user_input: 用户输入
            agent_response: Agent响应
            intent: 意图解析结果
            execution_result: 执行结果
            
        Returns:
            创建的对话轮次
        """
        turn = ConversationTurn(
            user_input=user_input,
            agent_response=agent_response,
            intent=intent or {},
            execution_result=execution_result
        )
        self.turns.append(turn)
        
        # 限制历史长度
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
        
        self.updated_at = time.time()
        return turn
    
    def update_status(self, status: ConversationStatus) -> None:
        """更新对话状态.
        
        Args:
            status: 新状态
        """
        self.status = status
        self.updated_at = time.time()
    
    def get_recent_turns(self, n: int = 3) -> List[ConversationTurn]:
        """获取最近n轮对话.
        
        Args:
            n: 轮数
            
        Returns:
            最近n轮对话列表
        """
        return self.turns[-n:] if self.turns else []
    
    def get_full_context(self) -> str:
        """获取完整对话上下文文本.
        
        Returns:
            格式化的对话历史
        """
        context_lines = []
        for i, turn in enumerate(self.turns, 1):
            context_lines.append(f"轮次 {i}:")
            context_lines.append(f"用户: {turn.user_input}")
            if turn.agent_response:
                context_lines.append(f"助手: {turn.agent_response}")
            context_lines.append("")
        return "\n".join(context_lines)
    
    def accumulate_data(self, key: str, value: Any) -> None:
        """累积数据到对话上下文.
        
        Args:
            key: 数据键
            value: 数据值
        """
        if key not in self.accumulated_data:
            self.accumulated_data[key] = []
        if isinstance(self.accumulated_data[key], list):
            self.accumulated_data[key].append(value)
        else:
            self.accumulated_data[key] = value
        self.updated_at = time.time()
    
    def is_expired(self, timeout_seconds: float = 3600) -> bool:
        """检查对话是否过期.
        
        Args:
            timeout_seconds: 超时时间（秒）
            
        Returns:
            是否过期
        """
        return time.time() - self.updated_at > timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典.
        
        Returns:
            状态字典
        """
        return {
            "conversation_id": self.conversation_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "turn_count": len(self.turns),
            "current_task_type": self.current_task_type,
            "context": self.context,
            "accumulated_data": self.accumulated_data,
        }
