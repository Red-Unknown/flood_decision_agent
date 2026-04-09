"""
数据验证器模块

提供水利数据的完整性校验和合理性校验功能
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set
from enum import Enum

from .schema import (
    HydraulicDataSchema,
    DataType,
    FieldDefinition,
    get_schema,
    RiverCrossSectionSchema,
    RoughnessCoefficientSchema,
    RainfallRunoffSchema
)


class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "error"       # 错误，数据不可用
    WARNING = "warning"   # 警告，数据可用但需关注
    INFO = "info"         # 信息，仅供参考


@dataclass
class ValidationIssue:
    """验证问题"""
    field: str
    message: str
    level: ValidationLevel
    code: str = ""
    suggestion: str = ""


@dataclass
class ValidationResult:
    """验证结果类"""
    is_valid: bool
    schema_type: str = ""
    completeness_score: float = 0.0
    reasonableness_score: float = 0.0
    overall_score: float = 0.0
    issues: List[ValidationIssue] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    invalid_fields: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "schema_type": self.schema_type,
            "completeness_score": self.completeness_score,
            "reasonableness_score": self.reasonableness_score,
            "overall_score": self.overall_score,
            "issues": [
                {
                    "field": i.field,
                    "message": i.message,
                    "level": i.level.value,
                    "code": i.code,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "missing_fields": self.missing_fields,
            "invalid_fields": self.invalid_fields,
            "metadata": self.metadata
        }
    
    def get_errors(self) -> List[ValidationIssue]:
        """获取所有错误级别的问题"""
        return [i for i in self.issues if i.level == ValidationLevel.ERROR]
    
    def get_warnings(self) -> List[ValidationIssue]:
        """获取所有警告级别的问题"""
        return [i for i in self.issues if i.level == ValidationLevel.WARNING]
    
    def has_critical_issues(self) -> bool:
        """检查是否存在严重问题"""
        return any(i.level == ValidationLevel.ERROR for i in self.issues)


class DataValidator:
    """
    数据验证器
    
    提供数据完整性校验和合理性校验功能
    """
    
    # 合理性规则定义
    REASONABLENESS_RULES: Dict[str, List[Dict[str, Any]]] = {
        "river_cross_section": [
            {
                "field": "elevation",
                "check": lambda v: v > 0,
                "message": "高程必须为正数",
                "code": "ELEVATION_POSITIVE"
            },
            {
                "field": "width",
                "check": lambda v: 0.1 <= v <= 5000,
                "message": "河底宽度应在0.1米到5000米之间",
                "code": "WIDTH_RANGE"
            },
            {
                "field": "left_slope",
                "check": lambda v: 0 <= v <= 10,
                "message": "左岸边坡系数应在0到10之间",
                "code": "LEFT_SLOPE_RANGE"
            },
            {
                "field": "right_slope",
                "check": lambda v: 0 <= v <= 10,
                "message": "右岸边坡系数应在0到10之间",
                "code": "RIGHT_SLOPE_RANGE"
            },
            {
                "field": "roughness",
                "check": lambda v: 0.01 <= v <= 0.1,
                "message": "糙率系数应在0.01到0.1之间",
                "code": "ROUGHNESS_RANGE"
            },
            {
                "field": "water_level",
                "check": lambda v, data: v > data.get("elevation", 0),
                "message": "水位高程应高于河底高程",
                "code": "WATER_LEVEL_ABOVE_BED",
                "depends_on": ["elevation"]
            }
        ],
        "roughness_coefficient": [
            {
                "field": "main_channel_n",
                "check": lambda v: 0.01 <= v <= 0.1,
                "message": "主槽糙率系数应在0.01到0.1之间",
                "code": "MAIN_CHANNEL_N_RANGE"
            },
            {
                "field": "left_bank_n",
                "check": lambda v: 0.01 <= v <= 0.15,
                "message": "左岸滩地糙率系数应在0.01到0.15之间",
                "code": "LEFT_BANK_N_RANGE"
            },
            {
                "field": "right_bank_n",
                "check": lambda v: 0.01 <= v <= 0.15,
                "message": "右岸滩地糙率系数应在0.01到0.15之间",
                "code": "RIGHT_BANK_N_RANGE"
            },
            {
                "field": "main_channel_n",
                "check": lambda v, data: v <= data.get("left_bank_n", 1) and v <= data.get("right_bank_n", 1),
                "message": "主槽糙率通常应小于或等于滩地糙率",
                "code": "MAIN_VS_BANK_N",
                "depends_on": ["left_bank_n", "right_bank_n"],
                "level": ValidationLevel.WARNING
            }
        ],
        "rainfall_runoff": [
            {
                "field": "rainfall_duration",
                "check": lambda v: 0 < v <= 720,
                "message": "降雨历时应在0到720小时之间",
                "code": "DURATION_RANGE"
            },
            {
                "field": "total_rainfall",
                "check": lambda v: 0 <= v <= 2000,
                "message": "降雨总量应在0到2000毫米之间",
                "code": "TOTAL_RAINFALL_RANGE"
            },
            {
                "field": "peak_intensity",
                "check": lambda v: 0 <= v <= 500,
                "message": "峰值雨强应在0到500毫米/小时之间",
                "code": "PEAK_INTENSITY_RANGE"
            },
            {
                "field": "catchment_area",
                "check": lambda v: 0.01 <= v <= 1000000,
                "message": "流域面积应在0.01到1000000平方公里之间",
                "code": "CATCHMENT_AREA_RANGE"
            },
            {
                "field": "runoff_coefficient",
                "check": lambda v: 0 <= v <= 1,
                "message": "径流系数应在0到1之间",
                "code": "RUNOFF_COEFFICIENT_RANGE"
            },
            {
                "field": "concentration_time",
                "check": lambda v: 0 <= v <= 72,
                "message": "汇流时间应在0到72小时之间",
                "code": "CONCENTRATION_TIME_RANGE"
            },
            {
                "field": "peak_flow",
                "check": lambda v: 0 <= v <= 100000,
                "message": "洪峰流量应在0到100000立方米/秒之间",
                "code": "PEAK_FLOW_RANGE"
            },
            {
                "field": "return_period",
                "check": lambda v: 1 <= v <= 10000,
                "message": "重现期应在1到10000年之间",
                "code": "RETURN_PERIOD_RANGE"
            },
            {
                "field": "total_rainfall",
                "check": lambda v, data: v <= data.get("peak_intensity", 0) * data.get("rainfall_duration", 1),
                "message": "降雨总量不应超过峰值雨强乘以降雨历时",
                "code": "RAINFALL_CONSISTENCY",
                "depends_on": ["peak_intensity", "rainfall_duration"],
                "level": ValidationLevel.WARNING
            }
        ]
    }
    
    def __init__(self):
        """初始化验证器"""
        self._custom_rules: Dict[str, List[Dict[str, Any]]] = {}
    
    def validate(
        self,
        data: Dict[str, Any],
        schema: HydraulicDataSchema,
        strict: bool = False
    ) -> ValidationResult:
        """
        验证数据
        
        Args:
            data: 待验证的数据
            schema: 数据Schema
            strict: 是否使用严格模式（任何警告都视为错误）
            
        Returns:
            ValidationResult: 验证结果
        """
        schema_type = schema.metadata.name
        issues: List[ValidationIssue] = []
        
        # 完整性校验
        completeness_issues, completeness_score = self._check_completeness(data, schema)
        issues.extend(completeness_issues)
        
        # 合理性校验
        reasonableness_issues, reasonableness_score = self._check_reasonableness(data, schema)
        issues.extend(reasonableness_issues)
        
        # 收集缺失和无效字段
        missing_fields = [i.field for i in issues if i.code.startswith("MISSING_")]
        invalid_fields = [i.field for i in issues if i.code.startswith(("RANGE_", "INVALID_"))]
        
        # 计算综合得分
        overall_score = (completeness_score * 0.5 + reasonableness_score * 0.5)
        
        # 判断是否有效
        has_errors = any(i.level == ValidationLevel.ERROR for i in issues)
        is_valid = not has_errors and completeness_score >= 0.8
        
        if strict and any(i.level == ValidationLevel.WARNING for i in issues):
            is_valid = False
        
        return ValidationResult(
            is_valid=is_valid,
            schema_type=schema_type,
            completeness_score=completeness_score,
            reasonableness_score=reasonableness_score,
            overall_score=overall_score,
            issues=issues,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
            metadata={
                "strict_mode": strict,
                "total_fields": len(schema.fields),
                "provided_fields": len(data)
            }
        )
    
    def _check_completeness(
        self,
        data: Dict[str, Any],
        schema: HydraulicDataSchema
    ) -> tuple[List[ValidationIssue], float]:
        """
        检查数据完整性
        
        Args:
            data: 待验证的数据
            schema: 数据Schema
            
        Returns:
            (问题列表, 完整性得分)
        """
        issues: List[ValidationIssue] = []
        
        required_fields = schema.get_required_fields()
        all_fields = schema.fields
        
        # 检查必填字段
        for field_def in required_fields:
            if field_def.name not in data or data[field_def.name] is None:
                issues.append(ValidationIssue(
                    field=field_def.name,
                    message=f"必填字段缺失: {field_def.description}",
                    level=ValidationLevel.ERROR,
                    code=f"MISSING_REQUIRED_{field_def.name.upper()}",
                    suggestion=f"请提供 {field_def.name} 的值"
                ))
        
        # 检查字段类型
        for field_name, value in data.items():
            field_def = schema.get_field(field_name)
            if field_def and value is not None:
                type_valid = self._validate_type(value, field_def.data_type)
                if not type_valid:
                    issues.append(ValidationIssue(
                        field=field_name,
                        message=f"字段类型错误: 期望 {field_def.data_type.value}，实际为 {type(value).__name__}",
                        level=ValidationLevel.ERROR,
                        code=f"INVALID_TYPE_{field_name.upper()}",
                        suggestion=f"请将 {field_name} 转换为 {field_def.data_type.value} 类型"
                    ))
        
        # 计算完整性得分
        filled_required = sum(
            1 for f in required_fields
            if f.name in data and data[f.name] is not None
        )
        filled_optional = sum(
            1 for f in all_fields if not f.required
            and f.name in data and data[f.name] is not None
        )
        
        required_score = filled_required / len(required_fields) if required_fields else 1.0
        optional_score = filled_optional / max(1, len(all_fields) - len(required_fields))
        
        completeness_score = required_score * 0.8 + optional_score * 0.2
        
        return issues, completeness_score
    
    def _check_reasonableness(
        self,
        data: Dict[str, Any],
        schema: HydraulicDataSchema
    ) -> tuple[List[ValidationIssue], float]:
        """
        检查数据合理性
        
        Args:
            data: 待验证的数据
            schema: 数据Schema
            
        Returns:
            (问题列表, 合理性得分)
        """
        issues: List[ValidationIssue] = []
        schema_type = schema.metadata.name
        
        # 获取规则
        rules = self.REASONABLENESS_RULES.get(schema_type, [])
        custom_rules = self._custom_rules.get(schema_type, [])
        all_rules = rules + custom_rules
        
        passed_checks = 0
        total_checks = 0
        
        for rule in all_rules:
            field_name = rule["field"]
            
            # 检查依赖字段
            depends_on = rule.get("depends_on", [])
            if depends_on and not all(d in data and data[d] is not None for d in depends_on):
                continue
            
            # 检查字段是否存在
            if field_name not in data or data[field_name] is None:
                continue
            
            total_checks += 1
            value = data[field_name]
            check_func = rule["check"]
            
            # 执行检查
            try:
                if depends_on:
                    result = check_func(value, data)
                else:
                    result = check_func(value)
                
                if not result:
                    level = rule.get("level", ValidationLevel.ERROR)
                    issues.append(ValidationIssue(
                        field=field_name,
                        message=rule["message"],
                        level=level,
                        code=rule["code"],
                        suggestion=rule.get("suggestion", "请检查数值是否合理")
                    ))
                else:
                    passed_checks += 1
            except Exception:
                # 检查函数执行失败，视为未通过
                issues.append(ValidationIssue(
                    field=field_name,
                    message=f"无法验证字段 {field_name} 的合理性",
                    level=ValidationLevel.WARNING,
                    code=f"CHECK_FAILED_{field_name.upper()}"
                ))
        
        # 计算合理性得分
        reasonableness_score = passed_checks / total_checks if total_checks > 0 else 1.0
        
        return issues, reasonableness_score
    
    def _validate_type(self, value: Any, data_type: DataType) -> bool:
        """
        验证值的数据类型
        
        Args:
            value: 待验证的值
            data_type: 期望的数据类型
            
        Returns:
            类型是否匹配
        """
        if data_type == DataType.FLOAT:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif data_type == DataType.INTEGER:
            return isinstance(value, int) and not isinstance(value, bool)
        elif data_type == DataType.STRING:
            return isinstance(value, str)
        elif data_type == DataType.BOOLEAN:
            return isinstance(value, bool)
        elif data_type == DataType.LIST:
            return isinstance(value, list)
        elif data_type == DataType.DICT:
            return isinstance(value, dict)
        return False
    
    def add_custom_rule(
        self,
        schema_type: str,
        field: str,
        check: Callable,
        message: str,
        code: str,
        level: ValidationLevel = ValidationLevel.ERROR,
        depends_on: Optional[List[str]] = None,
        suggestion: str = ""
    ) -> None:
        """
        添加自定义验证规则
        
        Args:
            schema_type: Schema类型名称
            field: 字段名
            check: 检查函数
            message: 错误消息
            code: 错误代码
            level: 验证级别
            depends_on: 依赖字段列表
            suggestion: 建议信息
        """
        if schema_type not in self._custom_rules:
            self._custom_rules[schema_type] = []
        
        self._custom_rules[schema_type].append({
            "field": field,
            "check": check,
            "message": message,
            "code": code,
            "level": level,
            "depends_on": depends_on or [],
            "suggestion": suggestion
        })
    
    def validate_batch(
        self,
        data_list: List[Dict[str, Any]],
        schema_type: str,
        strict: bool = False
    ) -> List[ValidationResult]:
        """
        批量验证数据
        
        Args:
            data_list: 数据列表
            schema_type: Schema类型名称
            strict: 是否使用严格模式
            
        Returns:
            验证结果列表
        """
        schema = get_schema(schema_type)
        if not schema:
            return [
                ValidationResult(
                    is_valid=False,
                    schema_type=schema_type,
                    issues=[ValidationIssue(
                        field="",
                        message=f"未知的Schema类型: {schema_type}",
                        level=ValidationLevel.ERROR,
                        code="UNKNOWN_SCHEMA"
                    )]
                )
            ] * len(data_list)
        
        return [self.validate(data, schema, strict) for data in data_list]
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        获取批量验证的汇总信息
        
        Args:
            results: 验证结果列表
            
        Returns:
            汇总信息字典
        """
        total = len(results)
        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = total - valid_count
        
        error_count = sum(len(r.get_errors()) for r in results)
        warning_count = sum(len(r.get_warnings()) for r in results)
        
        avg_completeness = sum(r.completeness_score for r in results) / total if total > 0 else 0
        avg_reasonableness = sum(r.reasonableness_score for r in results) / total if total > 0 else 0
        avg_overall = sum(r.overall_score for r in results) / total if total > 0 else 0
        
        # 统计最常见的错误
        error_codes: Dict[str, int] = {}
        for result in results:
            for issue in result.issues:
                if issue.level == ValidationLevel.ERROR:
                    error_codes[issue.code] = error_codes.get(issue.code, 0) + 1
        
        top_errors = sorted(error_codes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_records": total,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "valid_rate": valid_count / total if total > 0 else 0,
            "total_errors": error_count,
            "total_warnings": warning_count,
            "average_completeness_score": avg_completeness,
            "average_reasonableness_score": avg_reasonableness,
            "average_overall_score": avg_overall,
            "top_errors": [{"code": code, "count": count} for code, count in top_errors]
        }
