"""统一的任务类型定义.

提供业务领域类型和通用执行类型的统一枚举，解决 IntentParser 和 TaskDecomposer 之间的类型不匹配问题。
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Set


class BusinessTaskType(Enum):
    """业务领域任务类型.

    对应具体的业务场景，用于意图识别阶段。
    """

    # 洪水相关
    FLOOD_WARNING = "flood_warning"  # 洪水预警
    FLOOD_DISPATCH = "flood_dispatch"  # 洪水调度
    FLOOD_EMERGENCY = "flood_emergency"  # 洪水应急响应

    # 干旱相关
    DROUGHT_DISPATCH = "drought_dispatch"  # 干旱调度
    DROUGHT_MONITORING = "drought_monitoring"  # 干旱监测

    # 水库相关
    RESERVOIR_DISPATCH = "reservoir_dispatch"  # 水库调度
    RESERVOIR_OPTIMIZATION = "reservoir_optimization"  # 水库优化

    # 数据相关
    DATA_QUERY = "data_query"  # 数据查询
    DATA_ANALYSIS = "data_analysis"  # 数据分析
    WEATHER_FORECAST = "weather_forecast"  # 天气预报
    RAINFALL_FORECAST = "rainfall_forecast"  # 降雨预报

    # 分析评估
    RISK_ASSESSMENT = "risk_assessment"  # 风险评估
    WATERSHED_ANALYSIS = "watershed_analysis"  # 流域分析
    IMPACT_EVALUATION = "impact_evaluation"  # 影响评估

    # 规划决策
    STRATEGIC_PLANNING = "strategic_planning"  # 战略规划
    EMERGENCY_RESPONSE = "emergency_response"  # 应急响应
    DECISION_SUPPORT = "decision_support"  # 决策支持

    # 通用
    GENERAL_QUERY = "general_query"  # 通用查询
    UNKNOWN = "unknown"  # 未知类型


class ExecutionTaskType(Enum):
    """执行层任务类型.

    对应具体的执行动作，用于任务分解阶段。
    """

    DATA_COLLECTION = "data_collection"  # 数据采集
    DATA_PROCESSING = "data_processing"  # 数据处理
    PREDICTION = "prediction"  # 预测预报
    CALCULATION = "calculation"  # 计算分析
    SIMULATION = "simulation"  # 模拟仿真
    OPTIMIZATION = "optimization"  # 优化计算
    DECISION = "decision"  # 决策生成
    EXECUTION = "execution"  # 执行操作
    VERIFICATION = "verification"  # 验证检查
    REPORTING = "reporting"  # 报告生成
    UNIVERSAL_QUERY = "universal_query"  # 通用查询（使用LLM直接回答）


# 业务类型到执行类型的映射
# 定义每种业务类型需要哪些执行步骤
BUSINESS_TO_EXECUTION_MAP: Dict[BusinessTaskType, List[ExecutionTaskType]] = {
    BusinessTaskType.FLOOD_WARNING: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.PREDICTION,
        ExecutionTaskType.CALCULATION,
        ExecutionTaskType.DECISION,
        ExecutionTaskType.REPORTING,
    ],
    BusinessTaskType.FLOOD_DISPATCH: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.SIMULATION,
        ExecutionTaskType.CALCULATION,
        ExecutionTaskType.DECISION,
        ExecutionTaskType.EXECUTION,
        ExecutionTaskType.VERIFICATION,
    ],
    BusinessTaskType.RESERVOIR_DISPATCH: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.PREDICTION,
        ExecutionTaskType.SIMULATION,
        ExecutionTaskType.OPTIMIZATION,
        ExecutionTaskType.DECISION,
        ExecutionTaskType.EXECUTION,
    ],
    BusinessTaskType.DATA_QUERY: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.DATA_PROCESSING,
        ExecutionTaskType.REPORTING,
    ],
    BusinessTaskType.RISK_ASSESSMENT: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.CALCULATION,
        ExecutionTaskType.SIMULATION,
        ExecutionTaskType.DECISION,
        ExecutionTaskType.REPORTING,
    ],
    BusinessTaskType.WATERSHED_ANALYSIS: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.DATA_PROCESSING,
        ExecutionTaskType.CALCULATION,
        ExecutionTaskType.SIMULATION,
        ExecutionTaskType.REPORTING,
    ],
    BusinessTaskType.EMERGENCY_RESPONSE: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.CALCULATION,
        ExecutionTaskType.DECISION,
        ExecutionTaskType.EXECUTION,
        ExecutionTaskType.VERIFICATION,
        ExecutionTaskType.REPORTING,
    ],
    BusinessTaskType.STRATEGIC_PLANNING: [
        ExecutionTaskType.DATA_COLLECTION,
        ExecutionTaskType.DATA_PROCESSING,
        ExecutionTaskType.CALCULATION,
        ExecutionTaskType.SIMULATION,
        ExecutionTaskType.DECISION,
        ExecutionTaskType.REPORTING,
    ],
    BusinessTaskType.GENERAL_QUERY: [
        ExecutionTaskType.UNIVERSAL_QUERY,
    ],
}


# 执行类型到自然语言描述的映射
EXECUTION_TYPE_DESCRIPTIONS: Dict[ExecutionTaskType, str] = {
    ExecutionTaskType.DATA_COLLECTION: "数据采集",
    ExecutionTaskType.DATA_PROCESSING: "数据处理",
    ExecutionTaskType.PREDICTION: "预测预报",
    ExecutionTaskType.CALCULATION: "计算分析",
    ExecutionTaskType.SIMULATION: "模拟仿真",
    ExecutionTaskType.OPTIMIZATION: "优化计算",
    ExecutionTaskType.DECISION: "决策生成",
    ExecutionTaskType.EXECUTION: "执行操作",
    ExecutionTaskType.VERIFICATION: "验证检查",
    ExecutionTaskType.REPORTING: "报告生成",
    ExecutionTaskType.UNIVERSAL_QUERY: "智能问答",
}


# 业务类型到自然语言描述的映射
BUSINESS_TYPE_DESCRIPTIONS: Dict[BusinessTaskType, str] = {
    BusinessTaskType.FLOOD_WARNING: "洪水预警",
    BusinessTaskType.FLOOD_DISPATCH: "洪水调度",
    BusinessTaskType.FLOOD_EMERGENCY: "洪水应急",
    BusinessTaskType.DROUGHT_DISPATCH: "干旱调度",
    BusinessTaskType.DROUGHT_MONITORING: "干旱监测",
    BusinessTaskType.RESERVOIR_DISPATCH: "水库调度",
    BusinessTaskType.RESERVOIR_OPTIMIZATION: "水库优化",
    BusinessTaskType.DATA_QUERY: "数据查询",
    BusinessTaskType.DATA_ANALYSIS: "数据分析",
    BusinessTaskType.WEATHER_FORECAST: "天气预报",
    BusinessTaskType.RAINFALL_FORECAST: "降雨预报",
    BusinessTaskType.RISK_ASSESSMENT: "风险评估",
    BusinessTaskType.WATERSHED_ANALYSIS: "流域分析",
    BusinessTaskType.IMPACT_EVALUATION: "影响评估",
    BusinessTaskType.STRATEGIC_PLANNING: "战略规划",
    BusinessTaskType.EMERGENCY_RESPONSE: "应急响应",
    BusinessTaskType.DECISION_SUPPORT: "决策支持",
    BusinessTaskType.GENERAL_QUERY: "通用查询",
    BusinessTaskType.UNKNOWN: "未知任务",
}


def get_execution_types_for_business(
    business_type: BusinessTaskType,
) -> List[ExecutionTaskType]:
    """获取业务类型对应的执行类型列表.

    Args:
        business_type: 业务类型

    Returns:
        执行类型列表
    """
    return BUSINESS_TO_EXECUTION_MAP.get(business_type, [ExecutionTaskType.DATA_COLLECTION])


def get_business_type_description(business_type: BusinessTaskType) -> str:
    """获取业务类型的中文描述.

    Args:
        business_type: 业务类型

    Returns:
        中文描述
    """
    return BUSINESS_TYPE_DESCRIPTIONS.get(business_type, business_type.value)


def get_execution_type_description(execution_type: ExecutionTaskType) -> str:
    """获取执行类型的中文描述.

    Args:
        execution_type: 执行类型

    Returns:
        中文描述
    """
    return EXECUTION_TYPE_DESCRIPTIONS.get(execution_type, execution_type.value)


# 为了保持向后兼容，提供别名
TaskType = BusinessTaskType
