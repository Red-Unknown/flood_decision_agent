"""评估模块入口.

提供完整的Agent量化评估功能，包括：
- 六大维度指标计算
- 测试用例管理
- 评估执行
- 报告生成
- 测试场景
"""

# 基础模块（不依赖其他模块）
from flood_decision_agent.evaluation.metrics.base import (
    AutonomyMetrics,
    BaseMetrics,
    EffectivenessMetrics,
    EfficiencyMetrics,
    ExplainabilityMetrics,
    MetricValue,
    RobustnessMetrics,
    SafetyMetrics,
)
from flood_decision_agent.evaluation.reports.base import EvaluationReport
from flood_decision_agent.evaluation.test_cases.base import (
    ExpectedResult,
    TestCase,
    TestCaseType,
    TestPriority,
    TestSuite,
)
from flood_decision_agent.evaluation.test_cases.builder import (
    TestCaseBuilder,
    TestSuiteBuilder,
    TestTemplates,
)

# 以下模块延迟导入以避免循环依赖
# - core 模块（evaluator, runner, registry）
# - scenarios 模块
# - reports.formatters 模块

__all__ = [
    # Metrics
    "MetricValue",
    "BaseMetrics",
    "EffectivenessMetrics",
    "EfficiencyMetrics",
    "RobustnessMetrics",
    "SafetyMetrics",
    "AutonomyMetrics",
    "ExplainabilityMetrics",
    # Reports
    "EvaluationReport",
    # Test Cases
    "TestCase",
    "TestCaseType",
    "TestPriority",
    "ExpectedResult",
    "TestSuite",
    "TestCaseBuilder",
    "TestSuiteBuilder",
    "TestTemplates",
]


def __getattr__(name):
    """延迟导入核心模块."""
    if name in ("AgentEvaluator", "TestResult", "ComponentRegistry",
                "get_registry", "reset_registry", "EvaluationRunner",
                "RunConfig", "RunResult"):
        from flood_decision_agent.evaluation.core import (
            AgentEvaluator,
            ComponentRegistry,
            EvaluationRunner,
            RunConfig,
            RunResult,
            TestResult,
            get_registry,
            reset_registry,
        )
        return locals()[name]

    if name in ("BaseScenario", "ScenarioContext", "ScenarioRegistry",
                "FloodDispatchScenario", "EmergencyResponseScenario"):
        from flood_decision_agent.evaluation.scenarios import (
            BaseScenario,
            EmergencyResponseScenario,
            FloodDispatchScenario,
            ScenarioContext,
            ScenarioRegistry,
        )
        return locals()[name]

    if name in ("JSONFormatter", "MarkdownFormatter", "CSVFormatter"):
        from flood_decision_agent.evaluation.reports import (
            CSVFormatter,
            JSONFormatter,
            MarkdownFormatter,
        )
        return locals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
