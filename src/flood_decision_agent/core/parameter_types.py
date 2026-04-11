from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from flood_decision_agent.application.services.data_acquisition.models import (
    DataConfidenceLevel,
    DataSource,
    DataRequest,
)


class ParameterSource(str, Enum):
    """参数来源枚举
    
    表示参数的获取来源，按优先级排序：
    - USER_INPUT: 用户直接输入
    - USER_PROVIDED: 用户澄清时提供
    - DATA_POOL: 前置任务输出的数据
    - EXPERIENCE: 水利领域经验参数
    """

    USER_INPUT = "user_input"
    USER_PROVIDED = "user_provided"
    DATA_POOL = "data_pool"
    EXPERIENCE = "experience"


@dataclass
class ParameterRequirement:
    """参数需求定义
    
    基于 DataRequest 扩展，用于 ParameterPlanner 场景。
    定义执行某个工具所需的参数规范。
    
    Attributes:
        param_name: 参数名称
        param_type: 参数类型 (string/number/boolean/list/dict)
        required: 是否必需
        default_value: 默认值
        description: 参数描述
        validation_rules: 验证规则列表
        source_hint: 数据来源提示
        domain_key: 对应 water_domain_prompts 中的 key
        value_schema: 数据格式约束
    """

    param_name: str
    param_type: str
    required: bool = True
    default_value: Any = None
    description: str = ""
    validation_rules: List[str] = field(default_factory=list)
    source_hint: DataSource = DataSource.USER_INPUT
    domain_key: Optional[str] = None
    value_schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "param_name": self.param_name,
            "param_type": self.param_type,
            "required": self.required,
            "default_value": self.default_value,
            "description": self.description,
            "validation_rules": self.validation_rules,
            "source_hint": self.source_hint.value if self.source_hint else None,
            "domain_key": self.domain_key,
            "value_schema": self.value_schema,
        }

    def to_data_request(self) -> DataRequest:
        """转换为 DataRequest 用于数据获取服务"""
        return DataRequest(
            data_key=self.param_name,
            description=self.description,
            required=self.required,
            default_value=self.default_value,
            value_schema=self.value_schema,
        )


@dataclass
class ParameterValue:
    """单个参数值
    
    基于 DataResponse 扩展，用于 ParameterPlanner 场景。
    表示一个已获取的参数值及其元数据。
    
    Attributes:
        param_name: 参数名称
        value: 参数值
        source: 数据来源
        confidence: 数据置信度
        timestamp: 获取时间戳
        acquisition_path: 获取路径描述
    """

    param_name: str
    value: Any
    source: ParameterSource
    confidence: DataConfidenceLevel = DataConfidenceLevel.REFERENCE
    timestamp: datetime = field(default_factory=datetime.now)
    acquisition_path: str = ""

    @classmethod
    def from_data_response(
        cls,
        param_name: str,
        response: Any,
    ) -> "ParameterValue":
        """从 DataResponse 创建（兼容旧接口）"""
        if hasattr(response, "value"):
            return cls(
                param_name=param_name,
                value=response.value,
                source=ParameterSource.DATA_POOL,
                confidence=response.confidence or DataConfidenceLevel.REFERENCE,
                timestamp=response.timestamp if hasattr(response, "timestamp") else datetime.now(),
                acquisition_path=response.acquisition_path or "" if hasattr(response, "acquisition_path") else "",
            )
        return cls(
            param_name=param_name,
            value=response,
            source=ParameterSource.DATA_POOL,
            confidence=DataConfidenceLevel.REFERENCE,
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "param_name": self.param_name,
            "value": self.value,
            "source": self.source.value,
            "confidence": self.confidence.value if self.confidence else None,
            "timestamp": self.timestamp.isoformat(),
            "acquisition_path": self.acquisition_path,
        }


@dataclass
class ParameterPlan:
    """完整参数计划
    
    ParameterPlanner 的输出，包含单个任务节点的完整参数信息。
    
    Attributes:
        node_id: 节点ID
        task_type: 任务类型
        selected_tool: 最终选择的工具名称
        parameters: 参数值列表
        missing_params: 仍缺失的参数列表
        clarification_history: 用户澄清历史
    """

    node_id: str
    task_type: str
    selected_tool: str
    parameters: List[ParameterValue] = field(default_factory=list)
    missing_params: List[str] = field(default_factory=list)
    clarification_history: List[Dict[str, Any]] = field(default_factory=list)

    def get_param_dict(self) -> Dict[str, Any]:
        """获取参数字典（仅值）"""
        return {p.param_name: p.value for p in self.parameters}

    def get_param(self, param_name: str, default: Any = None) -> Any:
        """获取单个参数值"""
        for p in self.parameters:
            if p.param_name == param_name:
                return p.value
        return default

    def has_param(self, param_name: str) -> bool:
        """检查参数是否存在"""
        return any(p.param_name == param_name for p in self.parameters)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "node_id": self.node_id,
            "task_type": self.task_type,
            "selected_tool": self.selected_tool,
            "parameters": [p.to_dict() for p in self.parameters],
            "missing_params": self.missing_params,
            "clarification_history": self.clarification_history,
        }
