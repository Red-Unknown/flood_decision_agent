"""默认值提供者模块。

提供从多种来源获取默认值的功能。
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class DefaultValueSourceType(str, Enum):
    """默认值来源类型。"""

    STANDARD = "standard"  # 规范查表
    FORMULA = "formula"  # 公式计算
    SIMILAR_PROJECT = "similar_project"  # 类似工程
    DATABASE = "database"  # 数据库
    EXPERT = "expert"  # 专家经验


class DefaultValue(BaseModel):
    """默认值模型。"""

    value: Any = Field(..., description="默认值")
    source_type: DefaultValueSourceType = Field(..., description="来源类型")
    description: str = Field(default="", description="值描述")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="可信度(0-1)")
    source_reference: str = Field(default="", description="来源引用")
    applicable_conditions: Dict[str, Any] = Field(
        default_factory=dict, description="适用条件"
    )


class DefaultValueProvider:
    """默认值提供者。

    从多种来源提供默认值建议。
    """

    def __init__(self, case_library: List[Dict] = None):
        """初始化默认值提供者。

        Args:
            case_library: 案例库，用于类似工程匹配
        """
        self.case_library = case_library or []
        self._init_config()

    def _init_config(self):
        """初始化配置引用。"""
        from .config import DefaultValueConfig

        self.config = DefaultValueConfig

    def lookup_from_standard(
        self, data_key: str, conditions: Dict[str, Any]
    ) -> Optional[DefaultValue]:
        """从规范查表获取默认值。

        Args:
            data_key: 数据键名
            conditions: 查询条件

        Returns:
            默认值对象，未找到返回 None
        """
        value = None
        description = ""

        # 糙率系数查询
        if data_key == "roughness" or data_key == "糙率系数":
            soil_type = conditions.get("soil_type") or conditions.get("土壤类型")
            vegetation = conditions.get("vegetation") or conditions.get("植被覆盖")
            condition = conditions.get("condition") or conditions.get("河道状况")
            channel_type = conditions.get("channel_type") or conditions.get("渠道类型")

            value = self.config.get_roughness(soil_type, vegetation, condition, channel_type)

            if value:
                description = f"基于{soil_type or condition or channel_type}的糙率系数"

        # 径流系数查询
        elif data_key == "runoff_coefficient" or data_key == "径流系数":
            land_use = conditions.get("land_use") or conditions.get("土地利用")
            sub_type = conditions.get("sub_type") or conditions.get("子类型")

            value = self.config.get_runoff_coefficient(land_use, sub_type)

            if value:
                description = f"基于{land_use}的径流系数"

        # 河道参数查询
        elif data_key.startswith("channel_") or data_key.startswith("河道"):
            param_name = conditions.get("param_name") or conditions.get("参数名")
            channel_size = conditions.get("channel_size") or conditions.get("河道规模")

            value = self.config.get_channel_parameter(param_name, channel_size)

        if value is not None:
            return DefaultValue(
                value=value,
                source_type=DefaultValueSourceType.STANDARD,
                description=description,
                confidence=0.7,
                source_reference="《水文手册》及相关规范",
                applicable_conditions=conditions,
            )

        return None

    def calculate_from_formula(
        self, data_key: str, params: Dict[str, Any]
    ) -> Optional[DefaultValue]:
        """使用经验公式计算默认值。

        Args:
            data_key: 数据键名
            params: 计算参数

        Returns:
            默认值对象，计算失败返回 None
        """
        from .formulas import EmpiricalFormulaCalculator

        calculator = EmpiricalFormulaCalculator()
        value = None
        description = ""

        # 糙率系数计算
        if data_key == "roughness" or data_key == "糙率系数":
            soil_type = params.get("soil_type") or params.get("土壤类型")
            vegetation = params.get("vegetation") or params.get("植被覆盖")
            condition = params.get("condition") or params.get("河道状况")

            value = calculator.calculate_roughness(soil_type, vegetation, condition)
            description = f"基于{soil_type}和{vegetation}的经验公式计算"

        # 洪峰流量计算
        elif data_key == "flood_peak" or data_key == "洪峰流量":
            rainfall_duration = params.get("rainfall_duration") or params.get("降雨历时")
            total_rainfall = params.get("total_rainfall") or params.get("降雨总量")
            basin_area = params.get("basin_area") or params.get("流域面积")
            runoff_coefficient = params.get("runoff_coefficient") or params.get("径流系数")

            if all([rainfall_duration, total_rainfall, basin_area]):
                value = calculator.calculate_flood_peak(
                    rainfall_duration=rainfall_duration,
                    total_rainfall=total_rainfall,
                    basin_area=basin_area,
                    runoff_coefficient=runoff_coefficient or 0.7,
                )
                description = "基于推理公式的洪峰流量计算"

        # 径流系数计算
        elif data_key == "runoff_coefficient" or data_key == "径流系数":
            land_use = params.get("land_use") or params.get("土地利用")
            soil_type = params.get("soil_type") or params.get("土壤类型")
            slope = params.get("slope") or params.get("坡度")

            value = calculator.calculate_runoff_coefficient(land_use, soil_type, slope)
            description = f"基于{land_use}和{soil_type}的综合计算"

        # 汇流时间计算
        elif data_key == "concentration_time" or data_key == "汇流时间":
            basin_length = params.get("basin_length") or params.get("流域长度")
            slope = params.get("slope") or params.get("坡度")

            if basin_length and slope:
                value = calculator.calculate_concentration_time(basin_length, slope)
                description = "基于Kirpich公式的汇流时间计算"

        if value is not None:
            return DefaultValue(
                value=value,
                source_type=DefaultValueSourceType.FORMULA,
                description=description,
                confidence=0.6,
                source_reference="经验公式计算",
                applicable_conditions=params,
            )

        return None

    def match_similar_project(
        self,
        data_key: str,
        project_conditions: Dict[str, Any],
        case_library: List[Dict] = None,
    ) -> Optional[DefaultValue]:
        """从案例库匹配类似工程。

        Args:
            data_key: 数据键名
            project_conditions: 当前工程条件
            case_library: 案例库，默认使用初始化时的案例库

        Returns:
            默认值对象，未找到返回 None
        """
        library = case_library or self.case_library

        if not library:
            return None

        # 简单的相似度匹配
        best_match = None
        best_score = 0.0

        for case in library:
            score = self._calculate_similarity(project_conditions, case)
            if score > best_score and score > 0.5:  # 相似度阈值
                best_score = score
                best_match = case

        if best_match and data_key in best_match:
            return DefaultValue(
                value=best_match[data_key],
                source_type=DefaultValueSourceType.SIMILAR_PROJECT,
                description=f"类似工程参考: {best_match.get('name', '未知工程')}",
                confidence=0.5 * best_score,
                source_reference=f"案例库: {best_match.get('id', 'N/A')}",
                applicable_conditions=project_conditions,
            )

        return None

    def _calculate_similarity(
        self, conditions1: Dict[str, Any], conditions2: Dict[str, Any]
    ) -> float:
        """计算两个条件的相似度。

        Args:
            conditions1: 条件1
            conditions2: 条件2

        Returns:
            相似度分数 (0-1)
        """
        common_keys = set(conditions1.keys()) & set(conditions2.keys())

        if not common_keys:
            return 0.0

        matches = 0
        for key in common_keys:
            if conditions1[key] == conditions2[key]:
                matches += 1

        return matches / len(common_keys)

    def get_all_suggestions(
        self, data_key: str, context: Dict[str, Any]
    ) -> List[DefaultValue]:
        """获取所有可用的默认值建议。

        Args:
            data_key: 数据键名
            context: 上下文信息

        Returns:
            默认值建议列表，按可信度排序
        """
        suggestions = []

        # 1. 规范查表
        standard_value = self.lookup_from_standard(data_key, context)
        if standard_value:
            suggestions.append(standard_value)

        # 2. 公式计算
        formula_value = self.calculate_from_formula(data_key, context)
        if formula_value:
            suggestions.append(formula_value)

        # 3. 类似工程
        similar_value = self.match_similar_project(data_key, context)
        if similar_value:
            suggestions.append(similar_value)

        # 按可信度排序
        suggestions.sort(key=lambda x: x.confidence, reverse=True)

        return suggestions

    def get_best_suggestion(
        self, data_key: str, context: Dict[str, Any]
    ) -> Optional[DefaultValue]:
        """获取最佳默认值建议。

        Args:
            data_key: 数据键名
            context: 上下文信息

        Returns:
            最佳默认值对象，未找到返回 None
        """
        suggestions = self.get_all_suggestions(data_key, context)
        return suggestions[0] if suggestions else None

    def add_case_to_library(self, case: Dict[str, Any]) -> bool:
        """添加案例到案例库。

        Args:
            case: 案例数据

        Returns:
            是否添加成功
        """
        if "id" not in case:
            return False

        # 检查是否已存在
        existing = [c for c in self.case_library if c.get("id") == case["id"]]
        if existing:
            # 更新现有案例
            idx = self.case_library.index(existing[0])
            self.case_library[idx] = case
        else:
            # 添加新案例
            self.case_library.append(case)

        return True

    def get_parameter_options(self, data_key: str) -> Dict[str, List[str]]:
        """获取参数的可选值列表。

        Args:
            data_key: 数据键名

        Returns:
            可选值字典
        """
        if data_key in ["roughness", "糙率系数"]:
            return self.config.get_all_roughness_options()

        return {}
