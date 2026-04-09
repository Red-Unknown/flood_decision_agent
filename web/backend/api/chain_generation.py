"""
决策链生成 API 路由

提供决策链生成功能，支持三种模式：
- 普通模式：用户输入直接生成决策链
- Plan模式：基于已确认的Plan文档生成决策链
- Spec模式：基于已确认的Spec文档生成决策链

所有生成操作通过 WebSocket 流式返回结果
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from src.flood_decision_agent.infrastructure.persistence.file_storage import get_file_storage

router = APIRouter(prefix="/chain-generation", tags=["决策链生成"])


# ==================== Pydantic 模型 ====================

class ChainGenerateRequest(BaseModel):
    """决策链生成请求（普通模式）"""
    user_input: str = Field(..., description="用户输入")
    conversation_id: Optional[str] = Field(None, description="对话ID")


class ChainGenerateFromPlanRequest(BaseModel):
    """从Plan文档生成决策链请求"""
    plan_id: str = Field(..., description="规划文档ID")
    conversation_id: Optional[str] = Field(None, description="对话ID")


class ChainGenerateFromSpecRequest(BaseModel):
    """从Spec文档生成决策链请求"""
    feature_name: str = Field(..., description="规格功能名称")
    conversation_id: Optional[str] = Field(None, description="对话ID")


class ChainGenerationResponse(BaseModel):
    """决策链生成响应"""
    success: bool = Field(..., description="是否成功")
    generation_id: str = Field(..., description="生成任务ID")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


class ChainExecutionRequest(BaseModel):
    """决策链执行请求"""
    generation_id: str = Field(..., description="生成任务ID")
    mode: str = Field(default="normal", description="执行模式：normal/plan/spec")
    auto_execute: bool = Field(default=True, description="是否自动执行")


class ChainExecutionResponse(BaseModel):
    """决策链执行响应"""
    success: bool = Field(..., description="是否成功")
    execution_id: str = Field(..., description="执行任务ID")
    status: str = Field(..., description="执行状态")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


class ChainStatusResponse(BaseModel):
    """决策链状态响应"""
    success: bool = Field(default=True, description="是否成功")
    generation_id: str = Field(..., description="生成任务ID")
    status: str = Field(..., description="当前状态")
    progress: float = Field(default=0.0, description="进度 0-1")
    tasks: Optional[List[Dict[str, Any]]] = Field(None, description="任务列表")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")


# ==================== 辅助函数 ====================

def generate_generation_id() -> str:
    """生成决策链生成任务ID"""
    return f"chain_gen_{uuid.uuid4().hex[:12]}"


def generate_execution_id() -> str:
    """生成执行任务ID"""
    return f"chain_exec_{uuid.uuid4().hex[:12]}"


# 内存存储（后续可迁移到Redis）
_chain_generations: Dict[str, Dict[str, Any]] = {}
_chain_executions: Dict[str, Dict[str, Any]] = {}


# ==================== API 端点 ====================

@router.post("/generate", response_model=ChainGenerationResponse)
async def generate_chain(request: ChainGenerateRequest):
    """
    普通模式：从用户输入生成决策链
    
    - 解析用户意图
    - 分解任务
    - 生成决策链
    - 通过 WebSocket 流式返回结果
    """
    try:
        if not request.user_input.strip():
            raise HTTPException(status_code=400, detail="用户输入不能为空")
        
        generation_id = generate_generation_id()
        
        # 保存生成任务信息
        _chain_generations[generation_id] = {
            "generation_id": generation_id,
            "mode": "normal",
            "user_input": request.user_input,
            "conversation_id": request.conversation_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "tasks": [],
            "result": None,
        }
        
        return ChainGenerationResponse(
            success=True,
            generation_id=generation_id,
            message="决策链生成任务已创建",
            data={
                "mode": "normal",
                "status": "pending",
                "websocket_message_type": "generate_chain_normal",
                "note": "请通过 WebSocket 发送 generate_chain_normal 消息开始生成",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建生成任务失败: {str(e)}")


@router.post("/generate-from-plan", response_model=ChainGenerationResponse)
async def generate_chain_from_plan(request: ChainGenerateFromPlanRequest):
    """
    Plan模式：从已确认的Plan文档生成决策链
    
    - 加载Plan文档
    - 解析实施步骤
    - 转换为任务节点
    - 生成决策链
    - 通过 WebSocket 流式返回结果
    """
    try:
        storage = get_file_storage()
        
        # 检查Plan文档是否存在
        doc = storage.load_document(request.plan_id)
        if not doc:
            raise HTTPException(status_code=404, detail="规划文档不存在")
        
        # 检查文档状态
        metadata = doc.get("metadata", {})
        if metadata.get("status") != "confirmed":
            raise HTTPException(status_code=400, detail="规划文档未确认，请先确认规划")
        
        generation_id = generate_generation_id()
        
        # 保存生成任务信息
        _chain_generations[generation_id] = {
            "generation_id": generation_id,
            "mode": "plan",
            "plan_id": request.plan_id,
            "document_content": doc.get("content", ""),
            "conversation_id": request.conversation_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "tasks": [],
            "result": None,
        }
        
        return ChainGenerationResponse(
            success=True,
            generation_id=generation_id,
            message="决策链生成任务已创建（Plan模式）",
            data={
                "mode": "plan",
                "plan_id": request.plan_id,
                "status": "pending",
                "websocket_message_type": "generate_chain",
                "note": "请通过 WebSocket 发送 generate_chain 消息开始生成",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建生成任务失败: {str(e)}")


@router.post("/generate-from-spec", response_model=ChainGenerationResponse)
async def generate_chain_from_spec(request: ChainGenerateFromSpecRequest):
    """
    Spec模式：从已确认的Spec文档生成决策链
    
    - 加载Spec文档
    - 解析任务分解部分
    - 转换为任务节点
    - 生成决策链
    - 通过 WebSocket 流式返回结果
    """
    try:
        storage = get_file_storage()
        
        # 检查Spec文档是否存在
        doc = storage.load_document(request.feature_name)
        if not doc:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        # 检查文档状态
        metadata = doc.get("metadata", {})
        if metadata.get("status") != "confirmed":
            raise HTTPException(status_code=400, detail="规格文档未确认，请先确认规格")
        
        generation_id = generate_generation_id()
        
        # 保存生成任务信息
        _chain_generations[generation_id] = {
            "generation_id": generation_id,
            "mode": "spec",
            "feature_name": request.feature_name,
            "document_content": doc.get("content", ""),
            "conversation_id": request.conversation_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "tasks": [],
            "result": None,
        }
        
        return ChainGenerationResponse(
            success=True,
            generation_id=generation_id,
            message="决策链生成任务已创建（Spec模式）",
            data={
                "mode": "spec",
                "feature_name": request.feature_name,
                "status": "pending",
                "websocket_message_type": "generate_chain",
                "note": "请通过 WebSocket 发送 generate_chain 消息开始生成",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建生成任务失败: {str(e)}")


@router.get("/{generation_id}/status", response_model=ChainStatusResponse)
async def get_chain_generation_status(generation_id: str):
    """
    获取决策链生成状态
    
    查询生成任务的当前状态和进度
    """
    try:
        if generation_id not in _chain_generations:
            raise HTTPException(status_code=404, detail="生成任务不存在")
        
        gen_info = _chain_generations[generation_id]
        
        return ChainStatusResponse(
            success=True,
            generation_id=generation_id,
            status=gen_info.get("status", "unknown"),
            progress=gen_info.get("progress", 0.0),
            tasks=gen_info.get("tasks"),
            result=gen_info.get("result"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询状态失败: {str(e)}")


@router.post("/{generation_id}/execute", response_model=ChainExecutionResponse)
async def execute_chain(generation_id: str, request: ChainExecutionRequest):
    """
    执行已生成的决策链
    
    - 验证决策链已生成
    - 启动执行流程
    - 通过 WebSocket 流式返回执行进度
    """
    try:
        if generation_id not in _chain_generations:
            raise HTTPException(status_code=404, detail="生成任务不存在")
        
        gen_info = _chain_generations[generation_id]
        
        if gen_info.get("status") != "completed":
            raise HTTPException(status_code=400, detail="决策链尚未生成完成")
        
        execution_id = generate_execution_id()
        
        # 保存执行任务信息
        _chain_executions[execution_id] = {
            "execution_id": execution_id,
            "generation_id": generation_id,
            "mode": request.mode,
            "status": "pending" if request.auto_execute else "ready",
            "created_at": datetime.now().isoformat(),
            "result": None,
        }
        
        return ChainExecutionResponse(
            success=True,
            execution_id=execution_id,
            status="pending" if request.auto_execute else "ready",
            message="决策链执行任务已创建",
            data={
                "mode": request.mode,
                "auto_execute": request.auto_execute,
                "websocket_message_type": "execute_chain",
                "note": "请通过 WebSocket 发送 execute_chain 消息开始执行",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建执行任务失败: {str(e)}")


@router.get("/executions/{execution_id}/status", response_model=ChainStatusResponse)
async def get_chain_execution_status(execution_id: str):
    """
    获取决策链执行状态
    
    查询执行任务的当前状态和进度
    """
    try:
        if execution_id not in _chain_executions:
            raise HTTPException(status_code=404, detail="执行任务不存在")
        
        exec_info = _chain_executions[execution_id]
        
        return ChainStatusResponse(
            success=True,
            generation_id=exec_info.get("generation_id", ""),
            status=exec_info.get("status", "unknown"),
            progress=exec_info.get("progress", 0.0),
            tasks=exec_info.get("tasks"),
            result=exec_info.get("result"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询状态失败: {str(e)}")


@router.post("/executions/{execution_id}/cancel")
async def cancel_chain_execution(execution_id: str):
    """
    取消决策链执行
    
    停止正在执行的决策链任务
    """
    try:
        if execution_id not in _chain_executions:
            raise HTTPException(status_code=404, detail="执行任务不存在")
        
        exec_info = _chain_executions[execution_id]
        
        if exec_info.get("status") in ["completed", "failed", "cancelled"]:
            raise HTTPException(status_code=400, detail="任务已结束，无法取消")
        
        exec_info["status"] = "cancelled"
        exec_info["cancelled_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "execution_id": execution_id,
            "status": "cancelled",
            "message": "执行任务已取消",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


# ==================== WebSocket 消息类型扩展 ====================

class ChainGenerationWebSocketMessage:
    """决策链生成相关的 WebSocket 消息类型"""
    
    # 普通模式生成
    GENERATE_CHAIN_NORMAL = "generate_chain_normal"
    
    # Plan/Spec 模式生成
    GENERATE_CHAIN = "generate_chain"
    
    # 执行决策链
    EXECUTE_CHAIN = "execute_chain"
    
    # 生成阶段通知
    GENERATION_STAGE = "generation_stage"
    
    # 任务图生成完成
    TASK_GRAPH_GENERATED = "task_graph_generated"
    
    # 决策链生成完成
    CHAIN_GENERATION_COMPLETE = "chain_generation_complete"
    
    # 执行开始
    EXECUTION_STARTED = "execution_started"
    
    # 任务状态更新
    TASK_UPDATE = "task_update"
    
    # 执行进度
    EXECUTION_PROGRESS = "execution_progress"
    
    # 执行完成
    EXECUTION_COMPLETE = "execution_complete"
    
    # 执行错误
    EXECUTION_ERROR = "execution_error"
