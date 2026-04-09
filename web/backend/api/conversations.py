"""对话管理API.

提供对话的创建、查询、删除等管理功能。
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.flood_decision_agent.infrastructure.persistence.file_storage import get_file_storage

router = APIRouter()


class Conversation(BaseModel):
    """对话模型."""

    id: str = Field(..., description="对话ID")
    title: str = Field(..., description="对话标题")
    created_at: float = Field(..., description="创建时间戳")
    updated_at: float = Field(..., description="更新时间戳")
    message_count: int = Field(default=0, description="消息数量")


class ConversationCreate(BaseModel):
    """创建对话请求."""

    title: Optional[str] = Field(default=None, description="对话标题")


class ConversationResponse(BaseModel):
    """对话响应."""

    id: str
    title: str
    created_at: float
    updated_at: float
    message_count: int


# 内存存储（生产环境应使用数据库）
_conversations: Dict[str, Conversation] = {}


def generate_title() -> str:
    """生成默认对话标题."""
    return f"新对话 {len(_conversations) + 1}"


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations() -> List[ConversationResponse]:
    """获取对话列表.

    Returns:
        对话列表，按更新时间倒序排列
    """
    sorted_conversations = sorted(
        _conversations.values(),
        key=lambda x: x.updated_at,
        reverse=True,
    )
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=c.message_count,
        )
        for c in sorted_conversations
    ]


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(data: ConversationCreate) -> ConversationResponse:
    """创建新对话.

    Args:
        data: 创建对话请求数据

    Returns:
        新创建的对话信息
    """
    conversation_id = str(uuid.uuid4())
    now = time.time()

    conversation = Conversation(
        id=conversation_id,
        title=data.title or generate_title(),
        created_at=now,
        updated_at=now,
        message_count=0,
    )

    _conversations[conversation_id] = conversation

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=conversation.message_count,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str) -> ConversationResponse:
    """获取对话详情.

    Args:
        conversation_id: 对话ID

    Returns:
        对话详情

    Raises:
        HTTPException: 对话不存在时返回404
    """
    conversation = _conversations.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=conversation.message_count,
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict:
    """删除对话.

    Args:
        conversation_id: 对话ID

    Returns:
        删除结果

    Raises:
        HTTPException: 对话不存在时返回404
    """
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="对话不存在")

    del _conversations[conversation_id]

    return {"success": True, "message": "对话已删除"}


def update_conversation_message_count(conversation_id: str, count: int) -> None:
    """更新对话消息数量.

    Args:
        conversation_id: 对话ID
        count: 消息数量
    """
    if conversation_id in _conversations:
        _conversations[conversation_id].message_count = count
        _conversations[conversation_id].updated_at = time.time()


def update_conversation_title(conversation_id: str, title: str) -> None:
    """更新对话标题.

    Args:
        conversation_id: 对话ID
        title: 新标题
    """
    if conversation_id in _conversations:
        _conversations[conversation_id].title = title
        _conversations[conversation_id].updated_at = time.time()


# ==================== Plan/Spec 列表 API ====================

class PlanListItem(BaseModel):
    """规划列表项"""
    plan_id: str = Field(..., description="规划ID")
    title: str = Field(default="", description="规划标题")
    status: str = Field(default="draft", description="规划状态")
    version: int = Field(default=1, description="版本号")
    created_at: Optional[float] = Field(default=None, description="创建时间")
    updated_at: Optional[float] = Field(default=None, description="更新时间")


class SpecListItem(BaseModel):
    """规格列表项"""
    spec_id: str = Field(..., description="规格ID")
    feature_name: str = Field(..., description="功能名称")
    display_name: str = Field(default="", description="显示名称")
    status: str = Field(default="draft", description="规格状态")
    version: int = Field(default=1, description="版本号")
    created_at: Optional[float] = Field(default=None, description="创建时间")
    updated_at: Optional[float] = Field(default=None, description="更新时间")


class PaginationInfo(BaseModel):
    """分页信息"""
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页数量")
    total: int = Field(default=0, description="总数量")
    total_pages: int = Field(default=0, description="总页数")


class PlanListResponse(BaseModel):
    """规划列表响应"""
    success: bool = Field(default=True, description="是否成功")
    data: List[PlanListItem] = Field(default_factory=list, description="规划列表")
    pagination: PaginationInfo = Field(default_factory=PaginationInfo, description="分页信息")


class SpecListResponse(BaseModel):
    """规格列表响应"""
    success: bool = Field(default=True, description="是否成功")
    data: List[SpecListItem] = Field(default_factory=list, description="规格列表")
    pagination: PaginationInfo = Field(default_factory=PaginationInfo, description="分页信息")


@router.get("/conversations/{conversation_id}/plans", response_model=PlanListResponse)
async def get_conversation_plans(
    conversation_id: str,
    status: Optional[str] = Query(None, description="状态过滤（draft/confirmed/executing/completed/cancelled）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
) -> PlanListResponse:
    """获取指定对话的规划列表.

    Args:
        conversation_id: 对话ID
        status: 状态过滤
        page: 页码
        page_size: 每页数量

    Returns:
        规划列表

    Raises:
        HTTPException: 对话不存在时返回404
    """
    # 检查对话是否存在
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="对话不存在")

    try:
        storage = get_file_storage()
        
        # 获取所有规划文档
        all_plans = storage.list_documents(document_type="plan", status=status)
        
        # 转换为响应格式
        plan_items = []
        for plan in all_plans:
            metadata = plan.get("metadata", {})
            plan_items.append(PlanListItem(
                plan_id=plan["document_id"],
                title=metadata.get("title", "未命名规划"),
                status=metadata.get("status", "draft"),
                version=metadata.get("version", 1),
                created_at=_iso_to_timestamp(metadata.get("created_at")),
                updated_at=_iso_to_timestamp(metadata.get("updated_at")),
            ))
        
        # 分页
        total = len(plan_items)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_plans = plan_items[start_idx:end_idx]
        
        return PlanListResponse(
            success=True,
            data=paginated_plans,
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规划列表失败: {str(e)}")


@router.get("/conversations/{conversation_id}/specs", response_model=SpecListResponse)
async def get_conversation_specs(
    conversation_id: str,
    status: Optional[str] = Query(None, description="状态过滤（draft/confirmed/executing/completed/cancelled）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
) -> SpecListResponse:
    """获取指定对话的规格列表.

    Args:
        conversation_id: 对话ID
        status: 状态过滤
        page: 页码
        page_size: 每页数量

    Returns:
        规格列表

    Raises:
        HTTPException: 对话不存在时返回404
    """
    # 检查对话是否存在
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="对话不存在")

    try:
        storage = get_file_storage()
        
        # 获取所有规格文档
        all_specs = storage.list_documents(document_type="spec", status=status)
        
        # 转换为响应格式
        spec_items = []
        for spec in all_specs:
            metadata = spec.get("metadata", {})
            spec_items.append(SpecListItem(
                spec_id=spec["document_id"],
                feature_name=metadata.get("feature_name", spec["document_id"]),
                display_name=metadata.get("display_name", "未命名规格"),
                status=metadata.get("status", "draft"),
                version=metadata.get("version", 1),
                created_at=_iso_to_timestamp(metadata.get("created_at")),
                updated_at=_iso_to_timestamp(metadata.get("updated_at")),
            ))
        
        # 分页
        total = len(spec_items)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_specs = spec_items[start_idx:end_idx]
        
        return SpecListResponse(
            success=True,
            data=paginated_specs,
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规格列表失败: {str(e)}")


def _iso_to_timestamp(iso_str: Optional[str]) -> Optional[float]:
    """将ISO格式时间字符串转换为时间戳.

    Args:
        iso_str: ISO格式时间字符串

    Returns:
        时间戳（秒）
    """
    if not iso_str:
        return None
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso_str)
        return dt.timestamp()
    except Exception:
        return None
