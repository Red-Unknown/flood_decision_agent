"""
Spec 模式 API 路由

提供规格文档的管理功能：
- 更新规格文档（用户直接编辑）
- 生成规格内容（AI生成，WebSocket流式返回）
- 自然语言修改规格（全量重新生成）
- 确认规格文档（进入执行阶段）
- 取消规格任务

注意：创建和获取通过 WebSocket 处理，不单独提供 REST 接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from src.flood_decision_agent.infrastructure.persistence.file_storage import get_file_storage

router = APIRouter(prefix="/specs", tags=["Spec模式"])


# ==================== Pydantic 模型 ====================

class SpecUpdateRequest(BaseModel):
    """更新规格请求"""
    content: str = Field(..., description="规格文档内容（Markdown格式）")


class SpecGenerateRequest(BaseModel):
    """生成规格请求"""
    user_input: str = Field(..., description="用户原始输入")


class SpecModifyRequest(BaseModel):
    """修改规格请求"""
    instruction: str = Field(..., description="自然语言修改指令")


class SpecConfirmRequest(BaseModel):
    """确认规格请求"""
    action: str = Field(default="proceed", description="确认动作：proceed")


class SpecCancelRequest(BaseModel):
    """取消规格请求"""
    reason: Optional[str] = Field(None, description="取消原因")


class SpecResponse(BaseModel):
    """规格响应"""
    success: bool = Field(..., description="是否成功")
    feature_name: str = Field(..., description="功能名称")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


# ==================== 辅助函数 ====================

def generate_feature_name() -> str:
    """生成功能名称"""
    return f"feature_{uuid.uuid4().hex[:12]}"


# ==================== API 端点 ====================

@router.put("/{feature_name}", response_model=SpecResponse)
async def update_spec(feature_name: str, request: SpecUpdateRequest):
    """
    更新规格文档（用户直接编辑）
    
    - 保存用户编辑的规格内容
    - 更新元数据
    """
    try:
        storage = get_file_storage()
        
        # 检查规格是否存在
        existing = storage.load_document(feature_name)
        if not existing:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        # 保存更新后的内容
        metadata = existing.get("metadata", {})
        metadata.update({
            "updated_at": datetime.now().isoformat(),
            "updated_by": "user",
        })
        
        success = storage.save_document(feature_name, request.content, metadata)
        
        if not success:
            raise HTTPException(status_code=500, detail="保存规格文档失败")
        
        return SpecResponse(
            success=True,
            feature_name=feature_name,
            message="规格文档已更新",
            data={"updated_at": metadata["updated_at"]}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新规格失败: {str(e)}")


@router.post("/{feature_name}/generate", response_model=SpecResponse)
async def generate_spec(feature_name: str, request: SpecGenerateRequest, background_tasks: BackgroundTasks):
    """
    生成规格内容
    
    - 调用 LLM 生成规格文档
    - 返回生成任务ID
    - 实际生成通过 WebSocket 流式返回
    """
    try:
        storage = get_file_storage()
        
        # 创建生成任务
        generation_id = f"gen_{uuid.uuid4().hex[:8]}"
        
        # 初始化规格文档（如果还不存在）
        existing = storage.load_document(feature_name)
        if not existing:
            # 创建新的规格文档
            metadata = {
                "feature_name": feature_name,
                "created_at": datetime.now().isoformat(),
                "status": "generating",
                "generation_id": generation_id,
            }
            storage.save_document(feature_name, "# 规格生成中...", metadata)
        else:
            # 更新状态为生成中
            metadata = existing.get("metadata", {})
            metadata.update({
                "status": "generating",
                "generation_id": generation_id,
            })
            storage.save_document(feature_name, existing.get("content", ""), metadata)
        
        # 注意：实际的 LLM 生成在 WebSocket 中处理
        # 这里只返回任务ID，前端通过 WebSocket 接收流式内容
        
        return SpecResponse(
            success=True,
            feature_name=feature_name,
            message="规格生成任务已创建",
            data={
                "generation_id": generation_id,
                "status": "generating",
                "note": "请通过 WebSocket 接收流式生成内容"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建生成任务失败: {str(e)}")


@router.post("/{feature_name}/modify", response_model=SpecResponse)
async def modify_spec(feature_name: str, request: SpecModifyRequest):
    """
    自然语言修改规格（全量重新生成）
    
    - 根据用户指令重新生成规格
    - 全量替换原有内容
    - 通过 WebSocket 流式返回
    """
    try:
        storage = get_file_storage()
        
        # 检查规格是否存在
        existing = storage.load_document(feature_name)
        if not existing:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
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
        storage.save_document(feature_name, existing.get("content", ""), metadata)
        
        # 注意：实际的修改生成在 WebSocket 中处理
        
        return SpecResponse(
            success=True,
            feature_name=feature_name,
            message="规格修改任务已创建",
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


@router.post("/{feature_name}/confirm", response_model=SpecResponse)
async def confirm_spec(feature_name: str, request: SpecConfirmRequest):
    """
    确认规格文档，进入执行阶段
    
    - 保存确认状态
    - 生成决策链
    - 开始执行任务
    """
    try:
        storage = get_file_storage()
        
        # 检查规格是否存在
        existing = storage.load_document(feature_name)
        if not existing:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        # 更新状态为已确认
        metadata = existing.get("metadata", {})
        metadata.update({
            "status": "confirmed",
            "confirmed_at": datetime.now().isoformat(),
            "action": request.action,
        })
        storage.save_document(feature_name, existing.get("content", ""), metadata)
        
        # TODO: 生成决策链并开始执行
        # 这里应该调用决策链生成器和任务执行器
        
        return SpecResponse(
            success=True,
            feature_name=feature_name,
            message="规格已确认，进入执行阶段",
            data={
                "status": "confirmed",
                "action": request.action,
                "next_stage": "executing",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"确认规格失败: {str(e)}")


@router.post("/{feature_name}/cancel", response_model=SpecResponse)
async def cancel_spec(feature_name: str, request: SpecCancelRequest):
    """
    取消规格任务
    
    - 保存当前状态
    - 清理执行资源
    """
    try:
        storage = get_file_storage()
        
        # 检查规格是否存在
        existing = storage.load_document(feature_name)
        if not existing:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        # 更新状态为已取消
        metadata = existing.get("metadata", {})
        metadata.update({
            "status": "cancelled",
            "cancelled_at": datetime.now().isoformat(),
            "cancel_reason": request.reason or "用户取消",
        })
        storage.save_document(feature_name, existing.get("content", ""), metadata)
        
        return SpecResponse(
            success=True,
            feature_name=feature_name,
            message="规格任务已取消",
            data={
                "status": "cancelled",
                "cancelled_at": metadata["cancelled_at"],
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消规格失败: {str(e)}")


# ==================== 文件分片获取API（前端兼容）====================

class SpecFileResponse(BaseModel):
    """规格文件响应"""
    success: bool = Field(default=True, description="是否成功")
    feature_name: str = Field(..., description="功能名称")
    file_name: str = Field(..., description="文件名")
    content: str = Field(..., description="文件内容")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class SpecFilesListResponse(BaseModel):
    """规格文件列表响应"""
    success: bool = Field(default=True, description="是否成功")
    feature_name: str = Field(..., description="功能名称")
    files: list = Field(default_factory=list, description="文件列表")


@router.get("", response_model=list)
async def list_specs():
    """获取规格列表（前端兼容）
    
    返回所有规格文档的列表
    """
    try:
        storage = get_file_storage()
        all_docs = storage.list_documents(document_type="spec")
        
        specs = []
        for doc in all_docs:
            metadata = doc.get("metadata", {})
            specs.append({
                "feature_name": doc["document_id"],
                "display_name": metadata.get("display_name", doc["document_id"]),
                "status": metadata.get("status", "draft"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
            })
        
        return specs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规格列表失败: {str(e)}")


@router.get("/{feature_name}", response_model=Dict[str, Any])
async def get_spec(feature_name: str):
    """获取规格详情（完整文档）
    
    返回规格的完整信息，包括所有文件内容
    """
    try:
        storage = get_file_storage()
        doc = storage.load_document(feature_name)
        
        if not doc:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        metadata = doc.get("metadata", {})
        
        # 解析内容，尝试提取各个文件
        content = doc.get("content", "")
        files = parse_spec_content(content)
        
        return {
            "success": True,
            "feature_name": feature_name,
            "display_name": metadata.get("display_name", feature_name),
            "status": metadata.get("status", "draft"),
            "content": content,
            "files": files,
            "metadata": metadata,
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规格详情失败: {str(e)}")


@router.get("/{feature_name}/files", response_model=SpecFilesListResponse)
async def get_spec_files(feature_name: str):
    """获取规格文件列表
    
    返回规格包含的所有文件列表
    """
    try:
        storage = get_file_storage()
        doc = storage.load_document(feature_name)
        
        if not doc:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        # 解析内容获取文件列表
        content = doc.get("content", "")
        files = parse_spec_content(content)
        
        return SpecFilesListResponse(
            success=True,
            feature_name=feature_name,
            files=[
                {
                    "file_name": name,
                    "title": info.get("title", name),
                    "sections_count": len(info.get("sections", [])),
                }
                for name, info in files.items()
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.get("/{feature_name}/{file_name}", response_model=SpecFileResponse)
async def get_spec_file(feature_name: str, file_name: str):
    """获取规格单个文件内容
    
    返回规格中指定文件的内容
    支持的文件: spec, tasks, checklist
    """
    try:
        storage = get_file_storage()
        doc = storage.load_document(feature_name)
        
        if not doc:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        
        # 解析内容
        files = parse_spec_content(content)
        
        # 映射文件名
        file_mapping = {
            "spec.md": "spec",
            "tasks.md": "tasks",
            "checklist.md": "checklist",
            "spec": "spec",
            "tasks": "tasks",
            "checklist": "checklist",
        }
        
        mapped_name = file_mapping.get(file_name, file_name)
        
        if mapped_name not in files:
            raise HTTPException(status_code=404, detail=f"文件 '{file_name}' 不存在")
        
        file_info = files[mapped_name]
        
        return SpecFileResponse(
            success=True,
            feature_name=feature_name,
            file_name=file_name,
            content=file_info.get("content", ""),
            metadata={
                "title": file_info.get("title", ""),
                "sections": file_info.get("sections", []),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件内容失败: {str(e)}")


@router.post("", response_model=SpecResponse)
async def create_spec(request: SpecGenerateRequest):
    """创建规格（前端兼容）
    
    创建新的规格文档
    """
    try:
        storage = get_file_storage()
        
        # 生成 feature_name
        feature_name = generate_feature_name()
        
        # 初始化规格文档
        metadata = {
            "feature_name": feature_name,
            "created_at": datetime.now().isoformat(),
            "status": "draft",
        }
        storage.save_document(feature_name, "# 新规格文档\n\n待生成内容...", metadata)
        
        return SpecResponse(
            success=True,
            feature_name=feature_name,
            message="规格已创建",
            data={"feature_name": feature_name}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建规格失败: {str(e)}")


@router.put("/{feature_name}/{file_name}", response_model=SpecFileResponse)
async def update_spec_file(feature_name: str, file_name: str, request: SpecUpdateRequest):
    """更新规格文件（前端兼容）
    
    更新规格中指定文件的内容
    """
    try:
        storage = get_file_storage()
        
        # 检查规格是否存在
        existing = storage.load_document(feature_name)
        if not existing:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        # 更新元数据
        metadata = existing.get("metadata", {})
        metadata.update({
            "updated_at": datetime.now().isoformat(),
            "updated_by": "user",
        })
        
        # 保存更新后的内容
        storage.save_document(feature_name, request.content, metadata)
        
        return SpecFileResponse(
            success=True,
            feature_name=feature_name,
            file_name=file_name,
            content=request.content,
            metadata=metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文件失败: {str(e)}")


@router.patch("/{feature_name}/{file_name}/section")
async def update_spec_section(
    feature_name: str,
    file_name: str,
    section: str,
    content: str,
):
    """更新规格章节（前端兼容）
    
    更新规格中指定文件的某个章节
    """
    try:
        storage = get_file_storage()
        
        # 检查规格是否存在
        existing = storage.load_document(feature_name)
        if not existing:
            raise HTTPException(status_code=404, detail="规格文档不存在")
        
        # 获取当前内容
        current_content = existing.get("content", "")
        
        # TODO: 实现章节级别的更新逻辑
        # 这里简化处理，直接替换整个内容
        metadata = existing.get("metadata", {})
        metadata.update({
            "updated_at": datetime.now().isoformat(),
            "updated_by": "user",
            "modified_section": section,
        })
        storage.save_document(feature_name, content, metadata)
        
        return {
            "success": True,
            "feature_name": feature_name,
            "file_name": file_name,
            "section": section,
            "message": "章节已更新",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新章节失败: {str(e)}")


@router.post("/{feature_name}/approve", response_model=SpecResponse)
async def approve_spec(feature_name: str):
    """审批通过规格（前端兼容）
    
    将规格状态更新为已确认
    """
    return await confirm_spec(feature_name, SpecConfirmRequest(action="proceed"))


# ==================== 辅助函数 ====================

def parse_spec_content(content: str) -> Dict[str, Any]:
    """解析规格内容，提取各个文件
    
    从LLM生成的规格文档中解析出 spec.md、tasks.md、checklist.md
    
    Args:
        content: 规格文档内容
        
    Returns:
        文件字典 {file_name: {title, content, sections}}
    """
    files = {}
    
    # 尝试识别文件分隔标记
    import re
    
    # 模式1: === filename === 分隔
    pattern1 = r'===\s*(\S+)\s*==='
    # 模式2: # filename 标题
    pattern2 = r'^#\s+(\S+\.md)\s*$'
    
    # 默认将整个内容作为 spec.md
    files["spec"] = {
        "title": "规格文档",
        "content": content,
        "sections": extract_sections(content),
    }
    
    # 尝试提取 tasks 和 checklist 部分
    tasks_match = re.search(r'(?:#{1,3}\s*(?:任务|tasks|Tasks)[^#]*)(.*?)(?=\n#{1,3}\s|$)', content, re.DOTALL | re.IGNORECASE)
    if tasks_match:
        files["tasks"] = {
            "title": "任务列表",
            "content": tasks_match.group(0),
            "sections": extract_sections(tasks_match.group(0)),
        }
    
    checklist_match = re.search(r'(?:#{1,3}\s*(?:检查|checklist|Checklist)[^#]*)(.*?)(?=\n#{1,3}\s|$)', content, re.DOTALL | re.IGNORECASE)
    if checklist_match:
        files["checklist"] = {
            "title": "检查清单",
            "content": checklist_match.group(0),
            "sections": extract_sections(checklist_match.group(0)),
        }
    
    return files


def extract_sections(content: str) -> list:
    """提取文档中的章节
    
    Args:
        content: 文档内容
        
    Returns:
        章节列表
    """
    import re
    sections = []
    
    # 匹配 ## 标题
    pattern = r'^##\s+(.+)$'
    matches = re.finditer(pattern, content, re.MULTILINE)
    
    for match in matches:
        sections.append({
            "title": match.group(1).strip(),
            "level": 2,
        })
    
    return sections
