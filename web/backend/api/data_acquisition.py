"""数据获取服务API接口。

提供数据解析、确认、请求等功能的RESTful API。
"""

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field

from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps, fast_json_loads
from flood_decision_agent.application.services.data_acquisition.service import DataAcquisitionService
from flood_decision_agent.application.services.data_acquisition.models import (
    DataRequest,
    DataResponse,
    DataSource,
)
from flood_decision_agent.application.services.data_acquisition.adapters.detector import InputFormatDetector
from flood_decision_agent.application.services.data_acquisition.parser.engine import IntelligentParserEngine
from flood_decision_agent.application.services.data_acquisition.parser.schema import (
    RiverCrossSectionSchema,
    RoughnessCoefficientSchema,
)
from flood_decision_agent.application.services.data_acquisition.confirmation.manager import ConfirmationManager
from flood_decision_agent.application.services.data_acquisition.clarification.manager import ClarificationManager
from flood_decision_agent.application.services.data_acquisition.defaults.provider import DefaultValueProvider


router = APIRouter(prefix="/data", tags=["data_acquisition"])

# 全局服务实例（实际应用中应使用依赖注入）
_data_service: Optional[DataAcquisitionService] = None
_confirmation_manager: Optional[ConfirmationManager] = None
_clarification_manager: Optional[ClarificationManager] = None
_default_provider: Optional[DefaultValueProvider] = None


def get_data_service() -> DataAcquisitionService:
    """获取数据获取服务实例。"""
    global _data_service
    if _data_service is None:
        _data_service = DataAcquisitionService()
    return _data_service


def get_confirmation_manager() -> ConfirmationManager:
    """获取确认管理器实例。"""
    global _confirmation_manager
    if _confirmation_manager is None:
        _confirmation_manager = ConfirmationManager()
    return _confirmation_manager


def get_clarification_manager() -> ClarificationManager:
    """获取澄清管理器实例。"""
    global _clarification_manager
    if _clarification_manager is None:
        default_provider = get_default_provider()
        data_service = get_data_service()
        _clarification_manager = ClarificationManager(data_service, default_provider)
    return _clarification_manager


def get_default_provider() -> DefaultValueProvider:
    """获取默认值提供者实例。"""
    global _default_provider
    if _default_provider is None:
        _default_provider = DefaultValueProvider()
    return _default_provider


# ========== 请求/响应模型 ==========

class ParseInputRequest(BaseModel):
    """解析输入请求。"""
    input_data: str = Field(..., description="输入数据")
    input_type: Optional[str] = Field(default=None, description="输入类型(text/csv/tsv/excel)")
    schema_type: str = Field(default="river_cross_section", description="Schema类型")


class ParseInputResponse(BaseModel):
    """解析输入响应。"""
    success: bool
    parsed_data: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0)
    missing_fields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source: str = Field(default="")


class ConfirmDataRequest(BaseModel):
    """确认数据请求。"""
    confirmation_id: str = Field(..., description="确认ID")
    status: str = Field(..., description="确认状态(confirmed/rejected/modified)")
    modified_data: Optional[Dict[str, Any]] = Field(default=None, description="修改后的数据")
    user_notes: Optional[str] = Field(default=None, description="用户备注")


class ConfirmDataResponse(BaseModel):
    """确认数据响应。"""
    success: bool
    data_key: str = Field(default="")
    stored_value: Any = Field(default=None)
    message: str = Field(default="")


class DataRequestRequest(BaseModel):
    """数据请求。"""
    data_key: str = Field(..., description="数据键名")
    description: str = Field(default="", description="数据描述")
    required: bool = Field(default=True, description="是否必需")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class DataRequestResponse(BaseModel):
    """数据请求响应。"""
    value: Any = Field(default=None)
    source: str = Field(default="")
    confidence: float = Field(default=0.0)
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)


class DefaultValuesResponse(BaseModel):
    """默认值响应。"""
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)


class LineageResponse(BaseModel):
    """数据血缘响应。"""
    data_key: str
    acquisition_path: List[Dict[str, Any]] = Field(default_factory=list)
    history: List[Dict[str, Any]] = Field(default_factory=list)


class ClarificationSessionRequest(BaseModel):
    """创建澄清会话请求。"""
    task_id: str = Field(..., description="任务ID")
    data_dependencies: List[Dict[str, Any]] = Field(default_factory=list, description="数据依赖列表")


class ClarificationSessionResponse(BaseModel):
    """创建澄清会话响应。"""
    session_id: str
    pending_requests: List[Dict[str, Any]] = Field(default_factory=list)


class ClarificationResolveRequest(BaseModel):
    """解决数据请求请求。"""
    session_id: str = Field(..., description="会话ID")
    request_id: str = Field(..., description="请求ID")
    resolution_type: str = Field(..., description="解决类型(default/user_input/skip)")
    value: Optional[Any] = Field(default=None, description="用户提供的值")


class ClarificationResolveResponse(BaseModel):
    """解决数据请求响应。"""
    success: bool
    can_resume: bool = Field(default=False)
    message: str = Field(default="")


# ========== API端点 ==========

@router.post("/parse", response_model=ParseInputResponse)
async def parse_input(
    request: ParseInputRequest,
    parser: IntelligentParserEngine = Depends(lambda: IntelligentParserEngine()),
):
    """解析多模态输入。
    
    支持自然语言、表格粘贴、文件上传等多种输入格式。
    """
    try:
        # 检测输入格式
        detector = InputFormatDetector()
        detected_type = request.input_type or detector.detect_format(request.input_data)
        
        # 根据schema类型选择对应的schema
        schema_map = {
            "river_cross_section": RiverCrossSectionSchema(),
            "roughness_coefficient": RoughnessCoefficientSchema(),
        }
        schema = schema_map.get(request.schema_type)
        
        if not schema:
            raise HTTPException(status_code=400, detail=f"未知的schema类型: {request.schema_type}")
        
        # 解析输入
        result = parser.parse(request.input_data, request.schema_type)
        
        return ParseInputResponse(
            success=result.success,
            parsed_data=result.data if result.data else {},
            confidence=result.confidence,
            missing_fields=result.errors if result.errors else [],
            warnings=result.warnings if result.warnings else [],
            source=detected_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.post("/confirm", response_model=ConfirmDataResponse)
async def confirm_data(
    request: ConfirmDataRequest,
    confirmation_manager: ConfirmationManager = Depends(get_confirmation_manager),
):
    """提交数据确认结果。
    
    用户确认、修改或拒绝解析后的数据。
    """
    try:
        result = confirmation_manager.process_confirmation(
            confirmation_id=request.confirmation_id,
            user_response={
                "status": request.status,
                "modified_data": request.modified_data,
                "user_notes": request.user_notes,
            }
        )
        
        return ConfirmDataResponse(
            success=result.status in ("confirmed", "modified"),
            data_key=result.data_key if hasattr(result, 'data_key') else "",
            stored_value=result.modified_data if hasattr(result, 'modified_data') else None,
            message="数据已确认" if result.status == "confirmed" else "数据已更新",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"确认失败: {str(e)}")


@router.post("/request", response_model=DataRequestResponse)
async def request_data(
    request: DataRequestRequest,
    data_service: DataAcquisitionService = Depends(get_data_service),
    default_provider: DefaultValueProvider = Depends(get_default_provider),
):
    """请求特定数据。
    
    系统返回数据值及默认值建议。
    """
    try:
        # 构建数据请求
        data_request = DataRequest(
            data_key=request.data_key,
            description=request.description,
            required=request.required,
        )
        
        # 请求数据
        response = data_service.request_data(data_request)
        
        # 获取默认值建议
        suggestions = default_provider.get_all_suggestions(
            request.data_key, request.context
        )
        
        return DataRequestResponse(
            value=response.value,
            source=response.source.value if response.source else "",
            confidence=response.confidence.value if response.confidence else 0.0,
            suggestions=[
                {
                    "value": s.value,
                    "source_type": s.source_type.value,
                    "description": s.description,
                    "confidence": s.confidence,
                }
                for s in suggestions
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"请求数据失败: {str(e)}")


@router.get("/defaults", response_model=DefaultValuesResponse)
async def get_default_values(
    data_key: str,
    conditions: Optional[str] = None,
    default_provider: DefaultValueProvider = Depends(get_default_provider),
):
    """获取默认值选项。
    
    根据数据键名和条件返回默认值建议列表。
    """
    try:
        context = fast_json_loads(conditions) if conditions else {}
        
        suggestions = default_provider.get_all_suggestions(data_key, context)
        
        return DefaultValuesResponse(
            suggestions=[
                {
                    "value": s.value,
                    "source_type": s.source_type.value,
                    "description": s.description,
                    "confidence": s.confidence,
                    "source_reference": s.source_reference,
                }
                for s in suggestions
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取默认值失败: {str(e)}")


@router.get("/lineage/{data_key}", response_model=LineageResponse)
async def get_data_lineage(
    data_key: str,
    data_service: DataAcquisitionService = Depends(get_data_service),
):
    """获取数据血缘/溯源。
    
    返回数据的完整获取路径和历史记录。
    """
    try:
        lineage = data_service.get_data_lineage(data_key)
        history = data_service.get_data_history(data_key)
        
        return LineageResponse(
            data_key=data_key,
            acquisition_path=lineage.get("path", []),
            history=[
                {
                    "record_id": h.record_id,
                    "timestamp": h.created_at,
                    "source": h.response.source.value if h.response else "",
                }
                for h in history
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据血缘失败: {str(e)}")


@router.post("/clarification/session", response_model=ClarificationSessionResponse)
async def create_clarification_session(
    request: ClarificationSessionRequest,
    clarification_manager: ClarificationManager = Depends(get_clarification_manager),
):
    """创建澄清会话。
    
    用于执行中数据请求的会话管理。
    """
    try:
        session = clarification_manager.create_session(
            task_id=request.task_id,
            data_dependencies=request.data_dependencies,
        )
        
        return ClarificationSessionResponse(
            session_id=session.session_id,
            pending_requests=[
                {
                    "request_id": r.request_id,
                    "data_key": r.data_key,
                    "description": r.description,
                    "request_type": r.request_type.value,
                }
                for r in session.pending_requests
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.post("/clarification/resolve", response_model=ClarificationResolveResponse)
async def resolve_clarification(
    request: ClarificationResolveRequest,
    clarification_manager: ClarificationManager = Depends(get_clarification_manager),
):
    """解决数据请求。
    
    用户使用默认值、提供自定义值或跳过请求。
    """
    try:
        if request.resolution_type == "default":
            # 使用默认值
            success = clarification_manager.resolve_with_default(
                session_id=request.session_id,
                request_id=request.request_id,
                default_value=None,  # 使用系统推荐的最佳值
            )
        elif request.resolution_type == "user_input":
            # 使用用户输入
            success = clarification_manager.resolve_with_user_input(
                session_id=request.session_id,
                request_id=request.request_id,
                user_value=request.value,
            )
        elif request.resolution_type == "skip":
            # 跳过请求
            success = clarification_manager.skip_request(
                session_id=request.session_id,
                request_id=request.request_id,
            )
        else:
            raise HTTPException(status_code=400, detail=f"未知的解决类型: {request.resolution_type}")
        
        # 检查是否可以恢复执行
        can_resume = clarification_manager.can_resume(request.session_id)
        
        return ClarificationResolveResponse(
            success=success,
            can_resume=can_resume,
            message="数据请求已解决，可以继续执行" if can_resume else "还有其他待处理的数据请求",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解决请求失败: {str(e)}")


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    schema_type: str = "river_cross_section",
    parser: IntelligentParserEngine = Depends(lambda: IntelligentParserEngine()),
):
    """上传文件并解析。
    
    支持CSV和Excel文件。
    """
    try:
        content = await file.read()
        
        # 根据文件扩展名处理
        if file.filename.endswith('.csv'):
            import pandas as pd
            import io
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            input_data = df.to_json(orient='records', force_ascii=False)
        elif file.filename.endswith(('.xlsx', '.xls')):
            import pandas as pd
            import io
            df = pd.read_excel(io.BytesIO(content))
            input_data = df.to_json(orient='records', force_ascii=False)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式，请上传CSV或Excel文件")
        
        # 解析数据
        result = parser.parse(input_data, schema_type)
        
        return {
            "success": result.success,
            "parsed_data": result.data if result.data else {},
            "filename": file.filename,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")
