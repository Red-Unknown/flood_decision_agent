"""PlanOptimizer 单元测试."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from flood_decision_agent.agents.decision_chain.plan_optimizer import PlanOptimizer


class TestPlanOptimizerInit:
    """测试 PlanOptimizer 初始化."""

    def test_default_init(self):
        """测试默认初始化."""
        optimizer = PlanOptimizer()

        assert optimizer.max_iterations == 2
        assert optimizer.reliability_threshold == 0.75
        assert optimizer.max_alternatives == 3

    def test_custom_init(self):
        """测试自定义参数初始化."""
        optimizer = PlanOptimizer(
            max_iterations=3,
            reliability_threshold=0.8,
            max_alternatives=2,
        )

        assert optimizer.max_iterations == 3
        assert optimizer.reliability_threshold == 0.8
        assert optimizer.max_alternatives == 2


class TestPlanOptimizerOptimize:
    """测试 optimize 方法."""

    @pytest.fixture
    def optimizer(self):
        """创建 PlanOptimizer 实例."""
        return PlanOptimizer()

    @pytest.fixture
    def sample_nodes(self):
        """创建示例任务节点."""
        return [
            {"id": "task1", "name": "任务1", "tool": "tool_a"},
            {"id": "task2", "name": "任务2", "tool": "tool_b"},
            {"id": "task3", "name": "任务3", "tool": "tool_c"},
        ]

    def test_optimize_basic(self, optimizer, sample_nodes):
        """测试基本优化功能."""
        result = optimizer.optimize(sample_nodes)

        assert "original_nodes" in result
        assert "alternatives" in result
        assert "reliability_score" in result
        assert "issues" in result
        assert "passed" in result
        assert "iterations" in result

        assert len(result["original_nodes"]) == 3
        assert result["iterations"] == 2  # 默认迭代次数

    def test_optimize_empty_nodes(self, optimizer):
        """测试空节点列表."""
        result = optimizer.optimize([])

        assert result["original_nodes"] == []
        assert result["alternatives"] == []
        assert result["reliability_score"] == 0.0
        assert result["passed"] is False
        assert result["iterations"] == 0
        assert "任务节点为空" in result["issues"]

    def test_optimize_iterations(self, optimizer, sample_nodes):
        """测试迭代次数."""
        result = optimizer.optimize(sample_nodes)

        # 验证迭代次数在合理范围内
        assert 1 <= result["iterations"] <= optimizer.max_iterations

    def test_optimize_reliability_threshold(self, optimizer, sample_nodes):
        """测试可靠性阈值."""
        result = optimizer.optimize(sample_nodes)

        # 检查 passed 字段是否正确计算
        if result["reliability_score"] >= optimizer.reliability_threshold:
            assert result["passed"] is True

    def test_optimize_alternatives_count(self, optimizer, sample_nodes):
        """测试备选链数量."""
        result = optimizer.optimize(sample_nodes)

        # 备选链数量不应超过最大值
        assert len(result["alternatives"]) <= optimizer.max_alternatives

    def test_optimize_with_tools(self, optimizer, sample_nodes):
        """测试带工具列表的优化."""
        tools = ["tool_a", "tool_b", "tool_c"]
        result = optimizer.optimize(sample_nodes, tools)

        assert "original_nodes" in result
        assert "alternatives" in result


class TestPlanOptimizerEvaluate:
    """测试评估方法."""

    @pytest.fixture
    def optimizer(self):
        """创建 PlanOptimizer 实例."""
        return PlanOptimizer()

    @pytest.fixture
    def sample_nodes(self):
        """创建示例任务节点."""
        return [
            {"id": "task1", "name": "任务1"},
            {"id": "task2", "name": "任务2"},
        ]

    def test_quick_evaluate(self, optimizer, sample_nodes):
        """测试快速评估."""
        score, issues = optimizer.quick_evaluate(sample_nodes)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(issues, list)

    def test_quick_evaluate_empty(self, optimizer):
        """测试空节点评估."""
        score, issues = optimizer.quick_evaluate([])

        assert score == 0.0
        assert "任务节点为空" in issues

    def test_is_reliable(self, optimizer, sample_nodes):
        """测试可靠性检查."""
        result = optimizer.is_reliable(sample_nodes)

        assert isinstance(result, bool)

    def test_is_reliable_threshold(self, optimizer):
        """测试阈值判断."""
        # 空节点应该返回 False
        assert optimizer.is_reliable([]) is False


class TestPlanOptimizerDetails:
    """测试优化器详情."""

    def test_get_optimization_details(self):
        """测试获取优化器详情."""
        optimizer = PlanOptimizer(
            max_iterations=3,
            reliability_threshold=0.8,
            max_alternatives=2,
        )

        details = optimizer.get_optimization_details()

        assert details["type"] == "PlanOptimizer"
        assert details["max_iterations"] == 3
        assert details["reliability_threshold"] == 0.8
        assert details["max_alternatives"] == 2
        assert details["status"] == "placeholder_implementation"


class TestPlanOptimizerComparison:
    """测试与其他优化器的对比."""

    def test_threshold_comparison(self):
        """测试阈值对比."""
        from flood_decision_agent.agents.decision_chain.simple_optimizer import (
            SimpleOptimizer,
        )

        plan_opt = PlanOptimizer()
        simple_opt = SimpleOptimizer()

        # Plan 优化器的阈值应该高于 Simple 优化器
        assert plan_opt.reliability_threshold > simple_opt.reliability_threshold

    def test_iterations_comparison(self):
        """测试迭代次数对比."""
        plan_opt = PlanOptimizer(max_iterations=2)

        # Plan 优化器应该支持多迭代
        assert plan_opt.max_iterations >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
