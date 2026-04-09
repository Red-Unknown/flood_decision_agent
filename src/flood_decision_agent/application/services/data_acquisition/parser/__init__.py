"""
智能解析引擎模块

提供水利数据的智能解析、验证和处理功能
"""

from .schema import (
    # 枚举和基础类
    DataType,
    FieldDefinition,
    SchemaMetadata,
    HydraulicDataSchema,
    # Schema实现
    RiverCrossSectionSchema,
    RoughnessCoefficientSchema,
    RainfallRunoffSchema,
    # 工具函数
    get_schema,
    list_available_schemas,
    register_schema,
    SCHEMA_REGISTRY,
)

from .engine import (
    IntelligentParserEngine,
    ParsedDataResult,
)

from .validator import (
    DataValidator,
    ValidationResult,
    ValidationIssue,
    ValidationLevel,
)

__all__ = [
    # Schema相关
    "DataType",
    "FieldDefinition",
    "SchemaMetadata",
    "HydraulicDataSchema",
    "RiverCrossSectionSchema",
    "RoughnessCoefficientSchema",
    "RainfallRunoffSchema",
    "get_schema",
    "list_available_schemas",
    "register_schema",
    "SCHEMA_REGISTRY",
    # 引擎相关
    "IntelligentParserEngine",
    "ParsedDataResult",
    # 验证器相关
    "DataValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationLevel",
]

__version__ = "1.0.0"
