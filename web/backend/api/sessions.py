"""
会话管理API

提供会话状态管理和断点续传功能
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/sessions", tags=["会话管理"])


# ==================== 数据模型 ====================

class SessionStatus(str, Enum):
    """会话状态枚举"""
    IDLE = "idle"                    # 空闲
    PROCESSING = "processing"        # 处理中
    AWAITING_CONFIRMATION = "awaiting_confirmation"  # 等待确认
    COMPLETED = "completed"          # 已完成
    CANCELLED = "cancelled"          # 已取消
    ERROR = "error"                  # 错误


class SessionMode(str, Enum):
    """会话模式枚举"""
    SIMPLE = "simple"    # 简单问答
    PLAN = "plan"        # 规划模式
    SPEC = "spec"        # 规格模式


class SessionStage(str, Enum):
    """会话阶段枚举"""
    SIMPLE_ANSWER = "simple_answer"      # 简单回答
    PLANNING = "planning"                # 规划中
    SPEC_DESIGN = "spec_design"          # 规格设计中
    EXECUTING = "executing"              # 执行中
    AWAITING_CONFIRMATION = "awaiting_confirmation"  # 等待确认


class DocumentInfo(BaseModel):
    """文档信息"""
    type: str = Field(..., description="文档类型: plan/spec")
    id: str = Field(..., description="文档ID")
    title: str = Field(default="", description="文档标题")
    status: str = Field(default="draft", description="文档状态")
    content_preview: str = Field(default="", description="内容预览")


class SessionState(BaseModel):
    """会话状态"""
    session_id: str = Field(..., description="会话ID")
    mode: Optional[SessionMode] = Field(default=None, description="当前模式")
    stage: Optional[SessionStage] = Field(default=None, description="当前阶段")
    status: SessionStatus = Field(default=SessionStatus.IDLE, description="会话状态")
    current_document: Optional[DocumentInfo] = Field(default=None, description="当前文档")
    can_resume: bool = Field(default=False, description="是否可恢复")
    created_at: float = Field(default_factory=time.time, description="创建时间")
    updated_at: float = Field(default_factory=time.time, description="更新时间")
    conversation_id: Optional[str] = Field(default=None, description="关联的对话ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class SessionStatusResponse(BaseModel):
    """会话状态响应"""
    success: bool = Field(default=True, description="是否成功")
    session_id: str = Field(..., description="会话ID")
    mode: Optional[str] = Field(default=None, description="当前模式")
    stage: Optional[str] = Field(default=None, description="当前阶段")
    status: str = Field(..., description="会话状态")
    current_document: Optional[DocumentInfo] = Field(default=None, description="当前文档")
    can_resume: bool = Field(default=False, description="是否可恢复")
    created_at: float = Field(..., description="创建时间")
    updated_at: float = Field(..., description="更新时间")
    conversation_id: Optional[str] = Field(default=None, description="关联的对话ID")


class ResumeSessionRequest(BaseModel):
    """恢复会话请求"""
    session_id: str = Field(..., description="会话ID")


class ResumeSessionResponse(BaseModel):
    """恢复会话响应"""
    success: bool = Field(default=True, description="是否成功")
    session_id: str = Field(..., description="会话ID")
    resumed_from: Dict[str, Any] = Field(..., description="恢复前的状态")
    current_data: Optional[DocumentInfo] = Field(default=None, description="当前文档数据")
    message: str = Field(default="会话已恢复", description="响应消息")


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    conversation_id: Optional[str] = Field(default=None, description="关联的对话ID")
    mode: Optional[SessionMode] = Field(default=None, description="初始模式")


class CreateSessionResponse(BaseModel):
    """创建会话响应"""
    success: bool = Field(default=True, description="是否成功")
    session_id: str = Field(..., description="会话ID")
    message: str = Field(default="会话已创建", description="响应消息")


# ==================== 内存存储（生产环境应使用Redis）====================

# 会话存储: {session_id: SessionState}
_sessions: Dict[str, SessionState] = {}


# ==================== 辅助函数 ====================

def generate_session_id() -> str:
    """生成会话ID"""
    return f"sess_{uuid.uuid4().hex[:16]}"


def get_or_create_session(session_id: Optional[str] = None) -> SessionState:
    """获取或创建会话"""
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    
    # 创建新会话
    new_session = SessionState(
        session_id=session_id or generate_session_id(),
        status=SessionStatus.IDLE,
    )
    _sessions[new_session.session_id] = new_session
    return new_session


def update_session(session_id: str, updates: Dict[str, Any]) -> Optional[SessionState]:
    """更新会话状态"""
    if session_id not in _sessions:
        return None
    
    session = _sessions[session_id]
    for key, value in updates.items():
        if hasattr(session, key):
            setattr(session, key, value)
    
    session.updated_at = time.time()
    return session


# ==================== API端点 ====================

@router.post("", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """创建新会话
    
    创建一个新的会话，用于跟踪用户操作流程
    """
    session_id = generate_session_id()
    
    session = SessionState(
        session_id=session_id,
        mode=request.mode,
        status=SessionStatus.IDLE,
        conversation_id=request.conversation_id,
    )
    
    _sessions[session_id] = session
    
    return CreateSessionResponse(
        success=True,
        session_id=session_id,
        message="会话已创建",
    )


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """获取会话状态
    
    查询指定会话的当前状态，用于断点续传
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = _sessions[session_id]
    
    return SessionStatusResponse(
        success=True,
        session_id=session.session_id,
        mode=session.mode.value if session.mode else None,
        stage=session.stage.value if session.stage else None,
        status=session.status.value,
        current_document=session.current_document,
        can_resume=session.can_resume,
        created_at=session.created_at,
        updated_at=session.updated_at,
        conversation_id=session.conversation_id,
    )


@router.post("/{session_id}/resume", response_model=ResumeSessionResponse)
async def resume_session(session_id: str):
    """恢复会话
    
    恢复之前中断的会话，返回当前状态和数据
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = _sessions[session_id]
    
    # 检查是否可以恢复
    if not session.can_resume:
        raise HTTPException(status_code=400, detail="该会话不可恢复")
    
    # 更新状态为等待确认
    session.status = SessionStatus.AWAITING_CONFIRMATION
    session.updated_at = time.time()
    
    return ResumeSessionResponse(
        success=True,
        session_id=session_id,
        resumed_from={
            "mode": session.mode.value if session.mode else None,
            "stage": session.stage.value if session.stage else None,
            "status": session.status.value,
        },
        current_data=session.current_document,
        message="会话已恢复",
    )


@router.post("/{session_id}/update", response_model=SessionStatusResponse)
async def update_session_state(session_id: str, updates: Dict[str, Any]):
    """更新会话状态（内部使用）
    
    更新会话的各种状态字段
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = _sessions[session_id]
    
    # 更新允许的字段
    allowed_fields = ["mode", "stage", "status", "current_document", "can_resume", "conversation_id"]
    for field in allowed_fields:
        if field in updates:
            if field == "mode":
                session.mode = SessionMode(updates[field]) if updates[field] else None
            elif field == "stage":
                session.stage = SessionStage(updates[field]) if updates[field] else None
            elif field == "status":
                session.status = SessionStatus(updates[field])
            else:
                setattr(session, field, updates[field])
    
    session.updated_at = time.time()
    
    return SessionStatusResponse(
        success=True,
        session_id=session.session_id,
        mode=session.mode.value if session.mode else None,
        stage=session.stage.value if session.stage else None,
        status=session.status.value,
        current_document=session.current_document,
        can_resume=session.can_resume,
        created_at=session.created_at,
        updated_at=session.updated_at,
        conversation_id=session.conversation_id,
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话
    
    清理会话数据
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    del _sessions[session_id]
    
    return {"success": True, "message": "会话已删除"}


@router.get("", response_model=List[SessionStatusResponse])
async def list_sessions(
    status: Optional[str] = None,
    mode: Optional[str] = None,
):
    """列出所有会话（管理用途）
    
    可选按状态和模式过滤
    """
    sessions = list(_sessions.values())
    
    # 过滤
    if status:
        sessions = [s for s in sessions if s.status.value == status]
    if mode:
        sessions = [s for s in sessions if s.mode and s.mode.value == mode]
    
    return [
        SessionStatusResponse(
            success=True,
            session_id=s.session_id,
            mode=s.mode.value if s.mode else None,
            stage=s.stage.value if s.stage else None,
            status=s.status.value,
            current_document=s.current_document,
            can_resume=s.can_resume,
            created_at=s.created_at,
            updated_at=s.updated_at,
            conversation_id=s.conversation_id,
        )
        for s in sessions
    ]


# ==================== 兼容前端旧接口 ====================

@router.post("/resume", response_model=ResumeSessionResponse)
async def resume_session_legacy(request: ResumeSessionRequest):
    """恢复会话（兼容旧接口）
    
    POST /api/resume 的兼容实现
    """
    return await resume_session(request.session_id)
