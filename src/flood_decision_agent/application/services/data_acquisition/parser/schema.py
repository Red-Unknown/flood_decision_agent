"""
水利数据Schema定义模块

定义各类水利数据的结构、类型和约束规则
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from enum import Enum


class DataType(Enum):
    """数据类型枚举"""
    FLOAT = "float"
    INTEGER = "integer"
    STRING = "string"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


@dataclass
class FieldDefinition:
    """字段定义"""
    name: str
    data_type: DataType
    description: str
    required: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Any = None
    unit: Optional[str] = None
    examples: List[Any] = field(default_factory=list)


@dataclass
class SchemaMetadata:
    """Schema元数据"""
    name: str
    description: str
    version: str = "1.0"
    category: str = "hydraulic"


class HydraulicDataSchema(ABC):
    """
    水利数据Schema基类
    
    所有水利数据Schema的抽象基类，定义通用接口
    """
    
    def __init__(self):
        self._metadata: SchemaMetadata = self._define_metadata()
        self._fields: List[FieldDefinition] = self._define_fields()
    
    @property
    def metadata(self) -> SchemaMetadata:
        """获取Schema元数据"""
        return self._metadata
    
    @property
    def fields(self) -> List[FieldDefinition]:
        """获取字段定义列表"""
        return self._fields
    
    @property
    def schema_name(self) -> str:
        """获取Schema名称"""
        return self._metadata.name
    
    @abstractmethod
    def _define_metadata(self) -> SchemaMetadata:
        """定义Schema元数据，子类必须实现"""
        pass
    
    @abstractmethod
    def _define_fields(self) -> List[FieldDefinition]:
        """定义字段列表，子类必须实现"""
        pass
    
    def get_field(self, name: str) -> Optional[FieldDefinition]:
        """根据名称获取字段定义"""
        for field in self._fields:
            if field.name == name:
                return field
        return None
    
    def get_required_fields(self) -> List[FieldDefinition]:
        """获取所有必填字段"""
        return [f for f in self._fields if f.required]
    
    def to_dict(self) -> Dict[str, Any]:
        """将Schema转换为字典表示"""
        return {
            "metadata": {
                "name": self._metadata.name,
                "description": self._metadata.description,
                "version": self._metadata.version,
                "category": self._metadata.category
            },
            "fields": [
                {
                    "name": f.name,
                    "type": f.data_type.value,
                    "description": f.description,
                    "required": f.required,
                    "min_value": f.min_value,
                    "max_value": f.max_value,
                    "default": f.default,
                    "unit": f.unit,
                    "examples": f.examples
                }
                for f in self._fields
            ]
        }


class RiverCrossSectionSchema(HydraulicDataSchema):
    """
    河道断面数据Schema
    
    描述河道断面的几何特征，包括高程、宽度、边坡等参数
    """
    
    def _define_metadata(self) -> SchemaMetadata:
        return SchemaMetadata(
            name="river_cross_section",
            description="河道断面几何数据，用于描述河流横断面的形状和尺寸",
            version="1.0",
            category="hydraulic"
        )
    
    def _define_fields(self) -> List[FieldDefinition]:
        return [
            FieldDefinition(
                name="section_name",
                data_type=DataType.STRING,
                description="断面名称或编号",
                required=True,
                examples=["CS-001", "断面A", "K12+500"]
            ),
            FieldDefinition(
                name="elevation",
                data_type=DataType.FLOAT,
                description="河底高程（米）",
                required=True,
                min_value=0.0,
                max_value=10000.0,
                unit="m",
                examples=[45.5, 120.8, 8.2]
            ),
            FieldDefinition(
                name="width",
                data_type=DataType.FLOAT,
                description="河底宽度（米）",
                required=True,
                min_value=0.1,
                max_value=5000.0,
                unit="m",
                examples=[15.0, 80.5, 200.0]
            ),
            FieldDefinition(
                name="left_slope",
                data_type=DataType.FLOAT,
                description="左岸边坡系数（水平:垂直）",
                required=True,
                min_value=0.0,
                max_value=10.0,
                unit="ratio",
                examples=[1.5, 2.0, 3.0]
            ),
            FieldDefinition(
                name="right_slope",
                data_type=DataType.FLOAT,
                description="右岸边坡系数（水平:垂直）",
                required=True,
                min_value=0.0,
                max_value=10.0,
                unit="ratio",
                examples=[1.5, 2.0, 3.0]
            ),
            FieldDefinition(
                name="water_level",
                data_type=DataType.FLOAT,
                description="水位高程（米）",
                required=False,
                min_value=0.0,
                max_value=10000.0,
                unit="m",
                examples=[48.2, 125.0, 12.5]
            ),
            FieldDefinition(
                name="roughness",
                data_type=DataType.FLOAT,
                description="河床糙率系数",
                required=False,
                min_value=0.01,
                max_value=0.1,
                examples=[0.025, 0.035, 0.045]
            ),
            FieldDefinition(
                name="coordinates",
                data_type=DataType.LIST,
                description="断面坐标点列表 [(x1, y1), (x2, y2), ...]",
                required=False,
                examples=[[(0, 50), (10, 45), (30, 45), (40, 50)]]
            ),
            FieldDefinition(
                name="location",
                data_type=DataType.STRING,
                description="断面位置描述",
                required=False,
                examples=["大桥上游500米", "县城段", "支流汇合口"]
            )
        ]


class RoughnessCoefficientSchema(HydraulicDataSchema):
    """
    糙率系数数据Schema
    
    描述河道、堤岸等不同部位的糙率系数
    """
    
    def _define_metadata(self) -> SchemaMetadata:
        return SchemaMetadata(
            name="roughness_coefficient",
            description="糙率系数数据，用于描述水流阻力特性",
            version="1.0",
            category="hydraulic"
        )
    
    def _define_fields(self) -> List[FieldDefinition]:
        return [
            FieldDefinition(
                name="section_id",
                data_type=DataType.STRING,
                description="所属断面编号",
                required=True,
                examples=["CS-001", "断面A"]
            ),
            FieldDefinition(
                name="main_channel_n",
                data_type=DataType.FLOAT,
                description="主槽糙率系数",
                required=True,
                min_value=0.01,
                max_value=0.1,
                examples=[0.025, 0.030, 0.040]
            ),
            FieldDefinition(
                name="left_bank_n",
                data_type=DataType.FLOAT,
                description="左岸滩地糙率系数",
                required=False,
                min_value=0.01,
                max_value=0.15,
                examples=[0.050, 0.060, 0.080]
            ),
            FieldDefinition(
                name="right_bank_n",
                data_type=DataType.FLOAT,
                description="右岸滩地糙率系数",
                required=False,
                min_value=0.01,
                max_value=0.15,
                examples=[0.050, 0.060, 0.080]
            ),
            FieldDefinition(
                name="vegetation_type",
                data_type=DataType.STRING,
                description="植被类型",
                required=False,
                examples=["无植被", "稀疏草地", "灌木丛", "茂密树林"]
            ),
            FieldDefinition(
                name="bed_material",
                data_type=DataType.STRING,
                description="河床质类型",
                required=False,
                examples=["淤泥", "细砂", "粗砂", "砾石", "卵石", "岩石"]
            ),
            FieldDefinition(
                name="channel_condition",
                data_type=DataType.STRING,
                description="河道状况",
                required=False,
                examples=["顺直", "弯曲", "分叉", "有障碍物"]
            ),
            FieldDefinition(
                name="reference_source",
                data_type=DataType.STRING,
                description="糙率参考来源",
                required=False,
                examples=["实测", "经验取值", "曼宁公式反算"]
            )
        ]


class RainfallRunoffSchema(HydraulicDataSchema):
    """
    降雨径流数据Schema
    
    描述降雨事件和径流过程的相关参数
    """
    
    def _define_metadata(self) -> SchemaMetadata:
        return SchemaMetadata(
            name="rainfall_runoff",
            description="降雨径流数据，用于洪水计算和水文分析",
            version="1.0",
            category="hydrological"
        )
    
    def _define_fields(self) -> List[FieldDefinition]:
        return [
            FieldDefinition(
                name="event_id",
                data_type=DataType.STRING,
                description="降雨事件编号",
                required=True,
                examples=["RF20240615", "EVENT-001"]
            ),
            FieldDefinition(
                name="rainfall_duration",
                data_type=DataType.FLOAT,
                description="降雨历时（小时）",
                required=True,
                min_value=0.0,
                max_value=720.0,
                unit="h",
                examples=[3.0, 6.0, 24.0]
            ),
            FieldDefinition(
                name="total_rainfall",
                data_type=DataType.FLOAT,
                description="降雨总量（毫米）",
                required=True,
                min_value=0.0,
                max_value=2000.0,
                unit="mm",
                examples=[50.0, 150.0, 300.0]
            ),
            FieldDefinition(
                name="peak_intensity",
                data_type=DataType.FLOAT,
                description="峰值雨强（毫米/小时）",
                required=False,
                min_value=0.0,
                max_value=500.0,
                unit="mm/h",
                examples=[25.0, 50.0, 100.0]
            ),
            FieldDefinition(
                name="catchment_area",
                data_type=DataType.FLOAT,
                description="流域面积（平方公里）",
                required=True,
                min_value=0.01,
                max_value=1000000.0,
                unit="km²",
                examples=[10.5, 150.0, 5000.0]
            ),
            FieldDefinition(
                name="runoff_coefficient",
                data_type=DataType.FLOAT,
                description="径流系数",
                required=False,
                min_value=0.0,
                max_value=1.0,
                examples=[0.3, 0.5, 0.8]
            ),
            FieldDefinition(
                name="concentration_time",
                data_type=DataType.FLOAT,
                description="汇流时间（小时）",
                required=False,
                min_value=0.0,
                max_value=72.0,
                unit="h",
                examples=[1.5, 3.0, 8.0]
            ),
            FieldDefinition(
                name="peak_flow",
                data_type=DataType.FLOAT,
                description="洪峰流量（立方米/秒）",
                required=False,
                min_value=0.0,
                max_value=100000.0,
                unit="m³/s",
                examples=[50.0, 500.0, 5000.0]
            ),
            FieldDefinition(
                name="return_period",
                data_type=DataType.INTEGER,
                description="重现期（年）",
                required=False,
                min_value=1,
                max_value=10000,
                unit="year",
                examples=[5, 10, 20, 50, 100]
            ),
            FieldDefinition(
                name="rainfall_pattern",
                data_type=DataType.STRING,
                description="降雨时程分配类型",
                required=False,
                examples=["均匀型", "递增型", "递减型", "单峰型", "双峰型"]
            ),
            FieldDefinition(
                name="start_time",
                data_type=DataType.STRING,
                description="降雨开始时间",
                required=False,
                examples=["2024-06-15 08:00:00"]
            ),
            FieldDefinition(
                name="rainfall_series",
                data_type=DataType.LIST,
                description="降雨过程序列 [(time, rainfall), ...]",
                required=False,
                examples=[[(0, 0), (1, 10), (2, 25), (3, 15), (4, 0)]]
            )
        ]


# Schema注册表
SCHEMA_REGISTRY: Dict[str, Type[HydraulicDataSchema]] = {
    "river_cross_section": RiverCrossSectionSchema,
    "roughness_coefficient": RoughnessCoefficientSchema,
    "rainfall_runoff": RainfallRunoffSchema,
}


def get_schema(schema_type: str) -> Optional[HydraulicDataSchema]:
    """
    根据类型名称获取Schema实例
    
    Args:
        schema_type: Schema类型名称
        
    Returns:
        Schema实例，如果不存在则返回None
    """
    schema_class = SCHEMA_REGISTRY.get(schema_type)
    if schema_class:
        return schema_class()
    return None


def list_available_schemas() -> List[str]:
    """
    获取所有可用的Schema类型列表
    
    Returns:
        Schema类型名称列表
    """
    return list(SCHEMA_REGISTRY.keys())


def register_schema(name: str, schema_class: Type[HydraulicDataSchema]) -> None:
    """
    注册新的Schema类型
    
    Args:
        name: Schema类型名称
        schema_class: Schema类
    """
    SCHEMA_REGISTRY[name] = schema_class
