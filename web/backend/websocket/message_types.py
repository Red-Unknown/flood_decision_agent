"""
WebSocket 消息类型定义模块

定义所有 WebSocket 通信中使用的消息类型和数据结构
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MessageType(str, Enum):
    """WebSocket 消息类型枚举"""
    # 基础消息
    CHAT_MESSAGE = "chat_message"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    CONNECTED = "connected"
    COMPLETE = "complete"
    
    # Plan/Spec 模式消息
    START_PLAN = "start_plan"
    START_SPEC = "start_spec"
    CONFIRM_PLAN = "confirm_plan"
    CONFIRM_SPEC = "confirm_spec"
    DOCUMENT_CHUNK = "document_chunk"
    DOCUMENT_COMPLETE = "document_complete"
    PLAN_CONFIRMED = "plan_confirmed"
    SPEC_CONFIRMED = "spec_confirmed"
    
    # 决策链生成消息
    GENERATE_CHAIN_NORMAL = "generate_chain_normal"
    GENERATE_CHAIN = "generate_chain"
    CHAIN_GENERATION_STARTED = "chain_generation_started"
    GENERATION_STAGE = "generation_stage"
    CHAIN_GENERATION_STAGE = "chain_generation_stage"
    TASK_GRAPH_GENERATED = "task_graph_generated"
    CHAIN_GENERATED = "chain_generated"
    CHAIN_GENERATION_COMPLETE = "chain_generation_complete"
    
    # 决策链执行消息
    EXECUTE_CHAIN = "execute_chain"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_PROGRESS = "execution_progress"
    EXECUTION_COMPLETE = "execution_complete"
    EXECUTION_ERROR = "execution_error"
    
    # 任务执行消息
    TASK_UPDATE = "task_update"
    TASK_EXTRACTING = "task_extracting"
    PROCESS_EVENT = "process_event"
    
    # 意图解析消息
    INTENT_PARSED = "intent_parsed"
    USER_MESSAGE_CONFIRM = "user_message_confirm"
    ASSISTANT_MESSAGE = "assistant_message"
    
    # 操作控制消息
    CANCEL_OPERATION = "cancel_operation"
    OPERATION_CANCELLED = "operation_cancelled"


class WebSocketMessage(BaseModel):
    """WebSocket 消息基类"""
    type: MessageType = Field(..., description="消息类型")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="时间戳")
    
    class Config:
        use_enum_values = True


class ChatMessage(WebSocketMessage):
    """聊天消息"""
    type: MessageType = MessageType.CHAT_MESSAGE
    role: str = Field(..., description="消息角色：user/assistant")
    content: str = Field(..., description="消息内容")
    conversation_id: str = Field(..., description="对话ID")


class StartPlanMessage(WebSocketMessage):
    """启动 Plan 模式消息"""
    type: MessageType = MessageType.START_PLAN
    conversation_id: str = Field(..., description="对话ID")
    user_input: str = Field(..., description="用户输入")


class StartSpecMessage(WebSocketMessage):
    """启动 Spec 模式消息"""
    type: MessageType = MessageType.START_SPEC
    conversation_id: str = Field(..., description="对话ID")
    user_input: str = Field(..., description="用户输入")


class DocumentChunkMessage(WebSocketMessage):
    """文档生成内容块消息"""
    type: MessageType = MessageType.DOCUMENT_CHUNK
    document_id: str = Field(..., description="文档ID")
    content: str = Field(..., description="内容片段")
    accumulated: Optional[str] = Field(None, description="累计内容")


class DocumentCompleteMessage(WebSocketMessage):
    """文档生成完成消息"""
    type: MessageType = MessageType.DOCUMENT_COMPLETE
    document_id: str = Field(..., description="文档ID")
    content: str = Field(..., description="完整文档内容")
    document_type: str = Field(..., description="文档类型：plan/spec")


class TaskUpdateMessage(WebSocketMessage):
    """任务状态更新消息"""
    type: MessageType = MessageType.TASK_UPDATE
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态：pending/running/completed/failed")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")
    detail: Optional[Dict[str, Any]] = Field(None, description="任务执行详情（支持多模态）")


class TaskDetail(BaseModel):
    """任务执行详情"""
    stage: str = Field(..., description="当前阶段")
    message: str = Field(..., description="阶段描述")
    progress: float = Field(0.0, description="进度（0-1）")
    modalities: Optional[Dict[str, Any]] = Field(None, description="多模态内容预留")


class IntentParsedMessage(WebSocketMessage):
    """意图解析结果消息"""
    type: MessageType = MessageType.INTENT_PARSED
    intent: Dict[str, Any] = Field(..., description="解析后的意图")
    confidence: float = Field(0.0, description="置信度")


class ChainGenerationStageMessage(WebSocketMessage):
    """决策链生成阶段消息"""
    type: MessageType = MessageType.CHAIN_GENERATION_STAGE
    stage: str = Field(..., description="当前阶段")
    stage_name: str = Field(..., description="阶段名称（前端展示用）")
    progress: float = Field(0.0, description="进度（0-1）")
    message: str = Field(..., description="阶段描述")


class TaskGraphGeneratedMessage(WebSocketMessage):
    """任务图生成完成消息"""
    type: MessageType = MessageType.TASK_GRAPH_GENERATED
    tasks: List[Dict[str, Any]] = Field(..., description="任务列表")
    total_count: int = Field(..., description="任务总数")
    reliability_score: float = Field(0.0, description="可靠性评分")


class ChainGeneratedMessage(WebSocketMessage):
    """决策链生成完成消息"""
    type: MessageType = MessageType.CHAIN_GENERATED
    generation_id: str = Field(..., description="生成ID")
    task_graph: Dict[str, Any] = Field(..., description="任务图数据")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ExecutionStartedMessage(WebSocketMessage):
    """执行开始消息"""
    type: MessageType = MessageType.EXECUTION_STARTED
    execution_id: str = Field(..., description="执行ID")
    total_tasks: int = Field(..., description="总任务数")


class ExecutionProgressMessage(WebSocketMessage):
    """执行进度消息"""
    type: MessageType = MessageType.EXECUTION_PROGRESS
    completed_tasks: int = Field(..., description="已完成任务数")
    total_tasks: int = Field(..., description="总任务数")
    progress: float = Field(..., description="进度（0-1）")


class ExecutionCompleteMessage(WebSocketMessage):
    """执行完成消息"""
    type: MessageType = MessageType.EXECUTION_COMPLETE
    success: bool = Field(..., description="是否成功")
    summary: Dict[str, Any] = Field(default_factory=dict, description="执行汇总")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="执行结果")


class AssistantMessage(WebSocketMessage):
    """AI 回复消息"""
    type: MessageType = MessageType.ASSISTANT_MESSAGE
    content: str = Field(..., description="回复内容")


class ProcessEventMessage(WebSocketMessage):
    """过程事件消息"""
    type: MessageType = MessageType.PROCESS_EVENT
    stage: str = Field(..., description="处理阶段")
    data: Dict[str, Any] = Field(default_factory=dict, description="事件数据")


class ErrorMessage(WebSocketMessage):
    """错误消息"""
    type: MessageType = MessageType.ERROR
    code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细错误信息")


class PingMessage(WebSocketMessage):
    """心跳请求消息"""
    type: MessageType = MessageType.PING


class PongMessage(WebSocketMessage):
    """心跳响应消息"""
    type: MessageType = MessageType.PONG


class ConnectedMessage(WebSocketMessage):
    """连接成功消息"""
    type: MessageType = MessageType.CONNECTED
    conversation_id: str = Field(..., description="对话ID")
    message: str = Field(default="连接成功", description="连接消息")


class CompleteMessage(WebSocketMessage):
    """处理完成消息"""
    type: MessageType = MessageType.COMPLETE
    content: str = Field(..., description="完成内容")
    conversation_id: str = Field(..., description="对话ID")


# 消息类型映射表，用于路由
MESSAGE_TYPE_MAP = {
    MessageType.CHAT_MESSAGE: ChatMessage,
    MessageType.START_PLAN: StartPlanMessage,
    MessageType.START_SPEC: StartSpecMessage,
    MessageType.DOCUMENT_CHUNK: DocumentChunkMessage,
    MessageType.DOCUMENT_COMPLETE: DocumentCompleteMessage,
    MessageType.TASK_UPDATE: TaskUpdateMessage,
    MessageType.PROCESS_EVENT: ProcessEventMessage,
    MessageType.ERROR: ErrorMessage,
    MessageType.PING: PingMessage,
    MessageType.PONG: PongMessage,
}


def parse_message(data: dict) -> WebSocketMessage:
    """
    解析消息数据为对应的消息类型
    
    Args:
        data: 消息字典数据
        
    Returns:
        对应类型的消息对象
        
    Raises:
        ValueError: 未知的消息类型
    """
    msg_type = data.get("type")
    if not msg_type:
        raise ValueError("消息缺少 type 字段")
    
    # 查找对应的消息类
    message_class = None
    for mt, cls in MESSAGE_TYPE_MAP.items():
        if mt.value == msg_type:
            message_class = cls
            break
    
    if not message_class:
        raise ValueError(f"未知的消息类型: {msg_type}")
    
    return message_class(**data)


def create_message(msg_type: MessageType, **kwargs) -> WebSocketMessage:
    """
    创建指定类型的消息
    
    Args:
        msg_type: 消息类型
        **kwargs: 消息字段
        
    Returns:
        消息对象
    """
    message_class = MESSAGE_TYPE_MAP.get(msg_type)
    if not message_class:
        raise ValueError(f"未知的消息类型: {msg_type}")
    
    return message_class(type=msg_type, **kwargs)
