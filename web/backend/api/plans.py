"""
Plan 模式 API 路由

提供规划文档的管理功能：
- 更新规划文档（用户直接编辑）
- 生成规划内容（AI生成，WebSocket流式返回）
- 自然语言修改规划（全量重新生成）
- 确认规划文档（进入执行阶段）
- 取消规划任务

注意：创建和获取通过 WebSocket 处理，不单独提供 REST 接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from src.flood_decision_agent.infrastructure.persistence.file_storage import get_file_storage

router = APIRouter(prefix="/plans", tags=["Plan模式"])


# ==================== Pydantic 模型 ====================

class PlanUpdateRequest(BaseModel):
    """更新规划请求"""
    content: str = Field(..., description="规划文档内容（Markdown格式）")


class PlanGenerateRequest(BaseModel):
    """生成规划请求"""
    user_input: str = Field(..., description="用户原始输入")


class PlanModifyRequest(BaseModel):
    """修改规划请求"""
    instruction: str = Field(..., description="自然语言修改指令")


class PlanConfirmRequest(BaseModel):
    """确认规划请求"""
    action: str = Field(default="proceed", description="确认动作：proceed/upgrade_to_spec")


class PlanCancelRequest(BaseModel):
    """取消规划请求"""
    reason: Optional[str] = Field(None, description="取消原因")


class PlanResponse(BaseModel):
    """规划响应"""
    success: bool = Field(..., description="是否成功")
    plan_id: str = Field(..., description="规划ID")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


# ==================== 辅助函数 ====================

def generate_plan_id() -> str:
    """生成规划ID"""
    return f"plan_{uuid.uuid4().hex[:12]}"


def get_plan_storage_path(plan_id: str) -> str:
    """获取规划存储路径"""
    return f"documents/{plan_id}"


# ==================== API 端点 ====================

@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(plan_id: str, request: PlanUpdateRequest):
    """
    更新规划文档（用户直接编辑）
    
    - 保存用户编辑的规划内容
    - 更新元数据
    """
    try:
        storage = get_file_storage()
        
        # 检查规划是否存在
        existing = storage.load_document(plan_id)
        if not existing:
            raise HTTPException(status_code=404, detail="规划文档不存在")
        
        # 保存更新后的内容
        metadata = existing.get("metadata", {})
        metadata.update({
            "updated_at": datetime.now().isoformat(),
            "updated_by": "user",
        })
        
        success = storage.save_document(plan_id, request.content, metadata)
        
        if not success:
            raise HTTPException(status_code=500, detail="保存规划文档失败")
        
        return PlanResponse(
            success=True,
            plan_id=plan_id,
            message="规划文档已更新",
            data={"updated_at": metadata["updated_at"]}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新规划失败: {str(e)}")


@router.post("/{plan_id}/generate", response_model=PlanResponse)
async def generate_plan(plan_id: str, request: PlanGenerateRequest, background_tasks: BackgroundTasks):
    """
    生成规划内容
    
    - 调用 LLM 生成规划文档
    - 返回生成任务ID
    - 实际生成通过 WebSocket 流式返回
    """
    try:
        storage = get_file_storage()
        
        # 创建生成任务
        generation_id = f"gen_{uuid.uuid4().hex[:8]}"
        
        # 初始化规划文档（如果还不存在）
        existing = storage.load_document(plan_id)
        if not existing:
            # 创建新的规划文档
            metadata = {
                "plan_id": plan_id,
                "created_at": datetime.now().isoformat(),
                "status": "generating",
                "generation_id": generation_id,
            }
            storage.save_document(plan_id, "# 规划生成中...", metadata)
        else:
            # 更新状态为生成中
            metadata = existing.get("metadata", {})
            metadata.update({
                "status": "generating",
                "generation_id": generation_id,
            })
            storage.save_document(plan_id, existing.get("content", ""), metadata)
        
        # 注意：实际的 LLM 生成在 WebSocket 中处理
        # 这里只返回任务ID，前端通过 WebSocket 接收流式内容
        
        return PlanResponse(
            success=True,
            plan_id=plan_id,
            message="规划生成任务已创建",
            data={
                "generation_id": generation_id,
                "status": "generating",
                "note": "请通过 WebSocket 接收流式生成内容"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建生成任务失败: {str(e)}")


@router.post("/{plan_id}/modify", response_model=PlanResponse)
async def modify_plan(plan_id: str, request: PlanModifyRequest):
    """
    自然语言修改规划（全量重新生成）
    
    - 根据用户指令重新生成规划
    - 全量替换原有内容
    - 通过 WebSocket 流式返回
    """
    try:
        storage = get_file_storage()
        
        # 检查规划是否存在
        existing = storage.load_document(plan_id)
        if not existing:
            raise HTTPException(status_code=404, detail="规划文档不存在")
        
        # 创建修改任务
        modification_id = f"mod_{uuid.uuid4().hex[:8]}"
        
        # 更新元数据
        metadata = existing.get("metadata", {})
        metadata.update({
            "status": "modifying",
            "modification_id": modification_id,
            "modify_instruction": request.instruction,
            "modified_at": datetime.now().isoformat(),
        })
        storage.save_document(plan_id, existing.get("content", ""), metadata)
        
        # 注意：实际的修改生成在 WebSocket 中处理
        
        return PlanResponse(
            success=True,
            plan_id=plan_id,
            message="规划修改任务已创建",
            data={
                "modification_id": modification_id,
                "instruction": request.instruction,
                "note": "请通过 WebSocket 接收流式修改内容"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建修改任务失败: {str(e)}")


@router.post("/{plan_id}/confirm", response_model=PlanResponse)
async def confirm_plan(plan_id: str, request: PlanConfirmRequest):
    """
    确认规划文档，进入执行阶段
    
    - 保存确认状态
    - 生成决策链
    - 开始执行任务
    """
    try:
        storage = get_file_storage()
        
        # 检查规划是否存在
        existing = storage.load_document(plan_id)
        if not existing:
            raise HTTPException(status_code=404, detail="规划文档不存在")
        
        # 更新状态为已确认
        metadata = existing.get("metadata", {})
        metadata.update({
            "status": "confirmed",
            "confirmed_at": datetime.now().isoformat(),
            "action": request.action,
        })
        storage.save_document(plan_id, existing.get("content", ""), metadata)
        
        # TODO: 生成决策链并开始执行
        # 这里应该调用决策链生成器和任务执行器
        
        return PlanResponse(
            success=True,
            plan_id=plan_id,
            message="规划已确认，进入执行阶段",
            data={
                "status": "confirmed",
                "action": request.action,
                "next_stage": "executing",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"确认规划失败: {str(e)}")


@router.post("/{plan_id}/cancel", response_model=PlanResponse)
async def cancel_plan(plan_id: str, request: PlanCancelRequest):
    """
    取消规划任务
    
    - 保存当前状态
    - 清理执行资源
    """
    try:
        storage = get_file_storage()
        
        # 检查规划是否存在
        existing = storage.load_document(plan_id)
        if not existing:
            raise HTTPException(status_code=404, detail="规划文档不存在")
        
        # 更新状态为已取消
        metadata = existing.get("metadata", {})
        metadata.update({
            "status": "cancelled",
            "cancelled_at": datetime.now().isoformat(),
            "cancel_reason": request.reason or "用户取消",
        })
        storage.save_document(plan_id, existing.get("content", ""), metadata)
        
        return PlanResponse(
            success=True,
            plan_id=plan_id,
            message="规划任务已取消",
            data={
                "status": "cancelled",
                "cancelled_at": metadata["cancelled_at"],
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消规划失败: {str(e)}")
