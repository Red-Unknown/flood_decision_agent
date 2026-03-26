"""评估指标模块测试."""

from __future__ import annotations

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from flood_decision_agent.evaluation.metrics import (
    AutonomyMetrics,
    EffectivenessMetrics,
    EfficiencyMetrics,
    ExplainabilityMetrics,
    RobustnessMetrics,
    SafetyMetrics,
)


class TestEffectivenessMetrics:
    """测试有效性指标."""

    def test_task_success_rate(self):
        """测试任务成功率计算."""
        metrics = EffectivenessMetrics()

        # 记录一些任务结果
        metrics.record_task_result("task1", success=True)
        metrics.record_task_result("task2", success=True)
        metrics.record_task_result("task3", success=False)

        result = metrics.task_success_rate
        assert result.value == 2 / 3
        assert result.name == "task_success_rate"

    def test_intent_accuracy(self):
        """测试意图识别准确率."""
        metrics = EffectivenessMetrics()

        metrics.record_intent_result("input1", "flood_dispatch", "flood_dispatch")
        metrics.record_intent_result("input2", "flood_dispatch", "drought_dispatch")
        metrics.record_intent_result("input3", "drought_dispatch", "drought_dispatch")

        result = metrics.intent_accuracy
        assert result.value == 2 / 3

    def test_chain_completeness(self):
        """测试决策链完整性."""
        metrics = EffectivenessMetrics()

        metrics.record_chain_result("chain1", is_complete=True, node_count=5, reliability_score=0.8)
        metrics.record_chain_result("chain2", is_complete=False, node_count=0, reliability_score=0.0)
        metrics.record_chain_result("chain3", is_complete=True, node_count=3, reliability_score=0.7)

        result = metrics.chain_completeness
        assert result.value == 2 / 3

    def test_avg_reliability_score(self):
        """测试平均可靠性评分."""
        metrics = EffectivenessMetrics()

        metrics.record_chain_result("chain1", is_complete=True, node_count=5, reliability_score=0.8)
        metrics.record_chain_result("chain2", is_complete=True, node_count=3, reliability_score=0.6)

        result = metrics.avg_reliability_score
        assert result.value == 0.7

    def test_empty_metrics(self):
        """测试空指标情况."""
        metrics = EffectivenessMetrics()

        assert metrics.task_success_rate.value == 0.0
        assert metrics.intent_accuracy.value == 0.0
        assert metrics.chain_completeness.value == 0.0


class TestEfficiencyMetrics:
    """测试效率指标."""

    def test_avg_response_time(self):
        """测试平均响应时间."""
        metrics = EfficiencyMetrics()

        metrics.record_execution(elapsed_time_ms=1000)
        metrics.record_execution(elapsed_time_ms=2000)
        metrics.record_execution(elapsed_time_ms=3000)

        result = metrics.avg_response_time
        assert result.value == 2000.0
        assert result.unit == "ms"

    def test_p95_response_time(self):
        """测试P95响应时间."""
        metrics = EfficiencyMetrics()

        for i in range(100):
            metrics.record_execution(elapsed_time_ms=float(i * 100))

        result = metrics.p95_response_time
        assert result.value == 9500.0  # 95th percentile of 0-9900

    def test_avg_token_count(self):
        """测试平均Token消耗."""
        metrics = EfficiencyMetrics()

        metrics.record_execution(elapsed_time_ms=1000, token_count=100)
        metrics.record_execution(elapsed_time_ms=1000, token_count=200)
        metrics.record_execution(elapsed_time_ms=1000, token_count=300)

        result = metrics.avg_token_count
        assert result.value == 200.0
        assert result.unit == "tokens"

    def test_avg_node_count(self):
        """测试平均任务图节点数."""
        metrics = EfficiencyMetrics()

        metrics.record_execution(elapsed_time_ms=1000, node_count=3)
        metrics.record_execution(elapsed_time_ms=1000, node_count=5)
        metrics.record_execution(elapsed_time_ms=1000, node_count=7)

        result = metrics.avg_node_count
        assert result.value == 5.0


class TestRobustnessMetrics:
    """测试鲁棒性指标."""

    def test_exception_rate(self):
        """测试异常率."""
        metrics = RobustnessMetrics()

        metrics.record_error("task1", "Timeout", is_recoverable=True, recovered=True)
        metrics.record_error("task2", "ValueError", is_recoverable=False, recovered=False)

        # 异常率计算基于错误记录数
        result = metrics.exception_rate
        assert result.value == 1.0  # 有错误记录

    def test_tool_failure_rate(self):
        """测试工具调用失败率."""
        metrics = RobustnessMetrics()

        metrics.record_tool_call("tool1", success=True)
        metrics.record_tool_call("tool2", success=False)
        metrics.record_tool_call("tool3", success=True)

        result = metrics.tool_failure_rate
        assert result.value == 1 / 3

    def test_recovery_rate(self):
        """测试恢复成功率."""
        metrics = RobustnessMetrics()

        metrics.record_error("task1", "Timeout", is_recoverable=True, recovered=True)
        metrics.record_error("task2", "NetworkError", is_recoverable=True, recovered=False)
        metrics.record_error("task3", "ValueError", is_recoverable=False, recovered=False)

        result = metrics.recovery_rate
        assert result.value == 0.5  # 1/2 recoverable errors recovered

    def test_pass_at_k(self):
        """测试pass@k指标."""
        metrics = RobustnessMetrics()

        metrics.record_retry("task1", retry_count=1, final_success=True)
        metrics.record_retry("task2", retry_count=2, final_success=False)
        metrics.record_retry("task3", retry_count=0, final_success=True)

        result = metrics.pass_at_k(3)
        assert result.value == 2 / 3


class TestSafetyMetrics:
    """测试安全性指标."""

    def test_rule_compliance_rate(self):
        """测试规则遵循率."""
        metrics = SafetyMetrics()

        metrics.record_rule_check("task1", "rule1", complied=True)
        metrics.record_rule_check("task1", "rule2", complied=True)
        metrics.record_rule_check("task2", "rule1", complied=False)

        result = metrics.rule_compliance_rate
        assert result.value == 2 / 3

    def test_unauthorized_operation_rate(self):
        """测试未授权操作率."""
        metrics = SafetyMetrics()

        metrics.record_risk_operation("task1", "high_flow", "high", authorized=True)
        metrics.record_risk_operation("task2", "emergency", "critical", authorized=False)

        result = metrics.unauthorized_operation_rate
        assert result.value == 0.5

    def test_hallucination_rate(self):
        """测试幻觉率."""
        metrics = SafetyMetrics()

        metrics.record_hallucination_check("task1", has_hallucination=False, confidence=0.9)
        metrics.record_hallucination_check("task2", has_hallucination=True, confidence=0.8)
        metrics.record_hallucination_check("task3", has_hallucination=False, confidence=0.95)

        result = metrics.hallucination_rate
        assert result.value == 1 / 3


class TestAutonomyMetrics:
    """测试自主性指标."""

    def test_auto_tool_selection_rate(self):
        """测试工具自主选用率."""
        metrics = AutonomyMetrics()

        metrics.record_tool_selection("task1", auto_selected=True, selected_tools=["tool1"], task_type="compute")
        metrics.record_tool_selection("task2", auto_selected=False, selected_tools=["tool2"], task_type="query")
        metrics.record_tool_selection("task3", auto_selected=True, selected_tools=["tool3"], task_type="compute")

        result = metrics.auto_tool_selection_rate
        assert result.value == 2 / 3

    def test_dynamic_adjustment_rate(self):
        """测试动态调整率."""
        metrics = AutonomyMetrics()

        # 先记录工具选择
        metrics.record_tool_selection("task1", auto_selected=True, selected_tools=["tool1"], task_type="compute")
        metrics.record_tool_selection("task2", auto_selected=True, selected_tools=["tool2"], task_type="query")

        # 再记录调整
        metrics.record_adjustment("task1", "strategy_change", "performance")

        result = metrics.dynamic_adjustment_rate
        assert result.value == 0.5  # 1/2 tasks adjusted

    def test_unknown_scenario_handling_rate(self):
        """测试未知场景适配率."""
        metrics = AutonomyMetrics()

        metrics.record_unknown_scenario("task1", "new_format", handled=True)
        metrics.record_unknown_scenario("task2", "unexpected_input", handled=False)

        result = metrics.unknown_scenario_handling_rate
        assert result.value == 0.5


class TestExplainabilityMetrics:
    """测试可解释性指标."""

    def test_reasoning_transparency_rate(self):
        """测试推理透明度."""
        metrics = ExplainabilityMetrics()

        metrics.record_reasoning("task1", has_reasoning_chain=True, reasoning_quality_score=0.8)
        metrics.record_reasoning("task2", has_reasoning_chain=False, reasoning_quality_score=0.0)
        metrics.record_reasoning("task3", has_reasoning_chain=True, reasoning_quality_score=0.9)

        result = metrics.reasoning_transparency_rate
        assert result.value == 2 / 3

    def test_avg_reasoning_quality(self):
        """测试平均推理质量."""
        metrics = ExplainabilityMetrics()

        metrics.record_reasoning("task1", has_reasoning_chain=True, reasoning_quality_score=0.8)
        metrics.record_reasoning("task2", has_reasoning_chain=True, reasoning_quality_score=0.6)
        metrics.record_reasoning("task3", has_reasoning_chain=True, reasoning_quality_score=1.0)

        result = metrics.avg_reasoning_quality
        assert result.value == 0.8

    def test_avg_intent_clarity(self):
        """测试平均意图清晰度."""
        metrics = ExplainabilityMetrics()

        metrics.record_interaction("task1", turn_count=2, intent_clarity_score=0.9)
        metrics.record_interaction("task2", turn_count=3, intent_clarity_score=0.7)
        metrics.record_interaction("task3", turn_count=1, intent_clarity_score=1.0)

        result = metrics.avg_intent_clarity
        assert result.value == 0.8


class TestAllMetrics:
    """测试所有指标整合."""

    def test_get_all_metrics(self):
        """测试获取所有指标."""
        effectiveness = EffectivenessMetrics()
        effectiveness.record_task_result("task1", success=True)

        all_metrics = effectiveness.get_all_metrics()
        assert "task_success_rate" in all_metrics
        assert "intent_accuracy" in all_metrics
        assert "chain_completeness" in all_metrics
        assert "avg_reliability_score" in all_metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
