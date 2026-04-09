"""数据获取服务模型定义"""
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DataConfidenceLevel(Enum):
    """数据置信度级别

    表示数据的可靠程度，从最高到最低：
    - measured: 实测数据，最可靠
    - calculated: 计算数据，基于可靠公式
    - reference: 参考数据，来自权威来源
    - estimated: 估算数据，基于经验
    - assumed: 假设数据，可靠性最低
    """

    MEASURED = "measured"
    CALCULATED = "calculated"
    REFERENCE = "reference"
    ESTIMATED = "estimated"
    ASSUMED = "assumed"

    @property
    def priority(self) -> int:
        """获取置信度优先级，数值越高越可靠"""
        priorities = {
            DataConfidenceLevel.MEASURED: 5,
            DataConfidenceLevel.CALCULATED: 4,
            DataConfidenceLevel.REFERENCE: 3,
            DataConfidenceLevel.ESTIMATED: 2,
            DataConfidenceLevel.ASSUMED: 1,
        }
        return priorities[self]

    def is_more_reliable_than(self, other: "DataConfidenceLevel") -> bool:
        """判断当前置信度是否比另一个更可靠"""
        return self.priority > other.priority


class DataSource(Enum):
    """数据来源类型

    记录数据是如何获取的：
    - user_input: 用户直接输入
    - table_paste: 表格粘贴
    - file_upload: 文件上传
    - formula_calculation: 公式计算
    - standard_lookup: 标准规范查询
    - similar_project: 类似项目参考
    - llm_extraction: LLM提取/解析
    """

    USER_INPUT = "user_input"
    TABLE_PASTE = "table_paste"
    FILE_UPLOAD = "file_upload"
    FORMULA_CALCULATION = "formula_calculation"
    STANDARD_LOOKUP = "standard_lookup"
    SIMILAR_PROJECT = "similar_project"
    LLM_EXTRACTION = "llm_extraction"


class DataRequest(BaseModel):
    """数据请求模型

    用于向数据获取服务请求特定数据

    Attributes:
        data_key: 数据唯一标识符
        description: 数据描述说明
        required: 是否为必需数据
        value_schema: 数据格式约束（JSON Schema）
        default_value: 默认值
        validation_rules: 自定义验证规则
    """

    data_key: str = Field(..., description="数据唯一标识符")
    description: str = Field(..., description="数据描述说明")
    required: bool = Field(default=True, description="是否为必需数据")
    value_schema: Optional[Dict[str, Any]] = Field(
        default=None, description="数据格式约束（JSON Schema）"
    )
    default_value: Optional[Any] = Field(default=None, description="默认值")
    validation_rules: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="自定义验证规则"
    )

    class Config:
        frozen = True


class DataResponse(BaseModel):
    """数据响应模型

    包含获取到的数据及其元信息

    Attributes:
        value: 数据值
        source: 数据来源
        confidence: 数据置信度
        timestamp: 获取时间戳
        acquisition_path: 获取路径/方式描述
        metadata: 额外元数据
    """

    value: Any = Field(default=None, description="数据值")
    source: Optional[DataSource] = Field(default=None, description="数据来源")
    confidence: Optional[DataConfidenceLevel] = Field(default=None, description="数据置信度")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="获取时间戳"
    )
    acquisition_path: Optional[str] = Field(default=None, description="获取路径/方式描述")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="额外元数据"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class DataAcquisitionRecord(BaseModel):
    """数据获取记录

    用于数据追溯和审计

    Attributes:
        record_id: 记录唯一标识
        data_key: 数据标识符
        request: 原始请求
        response: 获取结果
        parent_records: 父记录ID列表（用于追溯依赖关系）
        created_at: 记录创建时间
        updated_at: 记录更新时间
    """

    record_id: str = Field(..., description="记录唯一标识")
    data_key: str = Field(..., description="数据标识符")
    request: DataRequest = Field(..., description="原始请求")
    response: DataResponse = Field(..., description="获取结果")
    parent_records: List[str] = Field(
        default_factory=list, description="父记录ID列表（用于追溯依赖关系）"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="记录创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="记录更新时间"
    )

    def update_timestamp(self) -> None:
        """更新记录时间戳"""
        self.updated_at = datetime.now()

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
