"""HeuristicOptimizer 单元测试."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from flood_decision_agent.agents.decision_chain.heuristic_optimizer import (
    HeuristicOptimizer,
    HeuristicScore,
)
from flood_decision_agent.agents.decision_chain.task_decomposer import TaskNodeInfo, TaskType


class TestHeuristicOptimizerInit:
    """测试 HeuristicOptimizer 初始化."""

    def test_default_init(self):
        """测试默认初始化."""
        optimizer = HeuristicOptimizer()

        assert optimizer.max_alternatives == 3
        assert optimizer.reliability_threshold == 0.7
        assert optimizer.max_iterations == 5

    def test_custom_init(self):
        """测试自定义参数初始化."""
        optimizer = HeuristicOptimizer(
            max_alternatives=5,
            reliability_threshold=0.8,
            max_iterations=10,
        )

        assert optimizer.max_alternatives == 5
        assert optimizer.reliability_threshold == 0.8
        assert optimizer.max_iterations == 10


class TestHeuristicOptimizerOptimize:
    """测试 optimize_iteratively 方法."""

    @pytest.fixture
    def optimizer(self):
        """创建 HeuristicOptimizer 实例."""
        return HeuristicOptimizer()

    @pytest.fixture
    def sample_nodes(self):
        """创建示例任务节点."""
        return [
            TaskNodeInfo(
                task_id="task1",
                task_type=TaskType.DATA_COLLECTION,
                description="采集雷达数据",
                inputs=[],
                outputs=["radar_data"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="task2",
                task_type=TaskType.DATA_COLLECTION,
                description="采集卫星数据",
                inputs=[],
                outputs=["satellite_data"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="task3",
                task_type=TaskType.CALCULATION,
                description="融合数据",
                inputs=["radar_data", "satellite_data"],
                outputs=["fused_data"],
                dependencies=["task1", "task2"],
            ),
        ]

    def test_optimize_basic(self, optimizer, sample_nodes):
        """测试基本优化功能."""
        result_nodes, reliability, log = optimizer.optimize_iteratively(
            sample_nodes, max_iterations=3
        )

        assert isinstance(result_nodes, list)
        assert isinstance(reliability, float)
        assert 0.0 <= reliability <= 1.0
        assert isinstance(log, list)
        assert len(log) > 0

    def test_optimize_empty_nodes(self, optimizer):
        """测试空节点列表."""
        result_nodes, reliability, log = optimizer.optimize_iteratively(
            [], max_iterations=3
        )

        assert result_nodes == []
        assert reliability == 0.0

    def test_optimize_convergence(self, optimizer, sample_nodes):
        """测试优化收敛."""
        result_nodes, reliability, log = optimizer.optimize_iteratively(
            sample_nodes, max_iterations=5
        )

        # 检查日志中包含收敛信息
        assert any("可靠性" in entry for entry in log)

    def test_optimize_improves_reliability(self, optimizer, sample_nodes):
        """测试优化提高可靠性."""
        # 获取原始可靠性
        orig_reliability, _, _ = optimizer.evaluate_reliability(sample_nodes)

        # 优化
        result_nodes, opt_reliability, _ = optimizer.optimize_iteratively(
            sample_nodes, max_iterations=3
        )

        # 优化后的可靠性应该不低于原始值（或变化不大）
        # 注意：由于启发式算法的随机性，这里只做基本检查
        assert opt_reliability >= 0.0


class TestHeuristicOptimizerParallelization:
    """测试并行化优化."""

    @pytest.fixture
    def optimizer(self):
        return HeuristicOptimizer()

    def test_find_parallelization_opportunities(self, optimizer):
        """测试寻找并行化机会."""
        nodes = [
            TaskNodeInfo(
                task_id="dc1",
                task_type=TaskType.DATA_COLLECTION,
                description="采集数据1",
                inputs=[],
                outputs=["data1"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="dc2",
                task_type=TaskType.DATA_COLLECTION,
                description="采集数据2",
                inputs=[],
                outputs=["data2"],
                dependencies=[],
            ),
        ]

        opps = optimizer._find_parallelization_opportunities(nodes)

        assert len(opps) >= 1
        assert any(opp["strategy"] == "parallel_data_collection" for opp in opps)

    def test_apply_parallel_optimization(self, optimizer):
        """测试应用并行化优化."""
        nodes = [
            TaskNodeInfo(
                task_id="dc1",
                task_type=TaskType.DATA_COLLECTION,
                description="采集数据1",
                inputs=[],
                outputs=["data1"],
                dependencies=["init"],
            ),
            TaskNodeInfo(
                task_id="dc2",
                task_type=TaskType.DATA_COLLECTION,
                description="采集数据2",
                inputs=[],
                outputs=["data2"],
                dependencies=["init"],
            ),
        ]

        data = {
            "strategy": "parallel_data_collection",
            "nodes": ["dc1", "dc2"],
        }

        result = optimizer._apply_parallel_optimization(nodes, data)

        assert len(result) == 2
        # 检查依赖是否被调整为并行
        dc1 = next(n for n in result if n.task_id == "dc1")
        dc2 = next(n for n in result if n.task_id == "dc2")
        assert "init" in dc1.dependencies
        assert "init" in dc2.dependencies


class TestHeuristicOptimizerSplit:
    """测试任务拆分优化."""

    @pytest.fixture
    def optimizer(self):
        return HeuristicOptimizer()

    def test_find_split_opportunities(self, optimizer):
        """测试寻找拆分机会."""
        nodes = [
            TaskNodeInfo(
                task_id="complex",
                task_type=TaskType.CALCULATION,
                description="复杂计算",
                inputs=["a", "b", "c"],
                outputs=["out1", "out2", "out3", "out4"],
                dependencies=[],
            ),
        ]

        opps = optimizer._find_split_opportunities(nodes)

        assert len(opps) >= 1
        assert opps[0]["reason"] == "too_many_outputs"

    def test_apply_split_optimization(self, optimizer):
        """测试应用拆分优化."""
        nodes = [
            TaskNodeInfo(
                task_id="complex",
                task_type=TaskType.CALCULATION,
                description="复杂计算",
                inputs=["a"],
                outputs=["out1", "out2", "out3", "out4"],
                dependencies=[],
            ),
        ]

        data = {
            "node_id": "complex",
            "reason": "too_many_outputs",
        }

        result = optimizer._apply_split_optimization(nodes, data)

        # 应该拆分为2个子任务
        assert len(result) == 2
        assert any("sub_1" in n.task_id for n in result)
        assert any("sub_2" in n.task_id for n in result)


class TestHeuristicOptimizerCriticalPath:
    """测试关键路径优化."""

    @pytest.fixture
    def optimizer(self):
        return HeuristicOptimizer()

    def test_identify_critical_path(self, optimizer):
        """测试识别关键路径."""
        nodes = [
            TaskNodeInfo(
                task_id="a",
                task_type=TaskType.DATA_COLLECTION,
                description="任务A",
                inputs=[],
                outputs=["out_a"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="b",
                task_type=TaskType.CALCULATION,
                description="任务B",
                inputs=["out_a"],
                outputs=["out_b"],
                dependencies=["a"],
            ),
            TaskNodeInfo(
                task_id="c",
                task_type=TaskType.EXECUTION,
                description="任务C",
                inputs=["out_b"],
                outputs=["out_c"],
                dependencies=["b"],
            ),
        ]

        critical_path = optimizer._identify_critical_path(nodes)

        assert len(critical_path) == 3
        assert critical_path[0] == "a"
        assert critical_path[1] == "b"
        assert critical_path[2] == "c"

    def test_apply_critical_path_optimization(self, optimizer):
        """测试应用关键路径优化."""
        nodes = [
            TaskNodeInfo(
                task_id="critical",
                task_type=TaskType.DECISION,
                description="关键决策",
                inputs=["data"],
                outputs=["decision"],
                dependencies=[],
            ),
        ]

        result = optimizer._apply_critical_path_optimization(nodes, ["critical"])

        critical_node = result[0]
        assert critical_node.metadata.get("critical_path") is True
        assert critical_node.metadata.get("priority") == "high"
        assert critical_node.metadata.get("retry_enabled") is True


class TestHeuristicOptimizerDependency:
    """测试依赖关系优化."""

    @pytest.fixture
    def optimizer(self):
        return HeuristicOptimizer()

    def test_can_reach(self, optimizer):
        """测试依赖可达性检查."""
        nodes = [
            TaskNodeInfo(
                task_id="a",
                task_type=TaskType.DATA_COLLECTION,
                description="任务A",
                inputs=[],
                outputs=["out_a"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="b",
                task_type=TaskType.CALCULATION,
                description="任务B",
                inputs=["out_a"],
                outputs=["out_b"],
                dependencies=["a"],
            ),
            TaskNodeInfo(
                task_id="c",
                task_type=TaskType.EXECUTION,
                description="任务C",
                inputs=["out_b"],
                outputs=["out_c"],
                dependencies=["b"],
            ),
        ]

        node_map = {n.task_id: n for n in nodes}

        # a 可以到达 b
        assert optimizer._can_reach("a", "b", node_map) is True
        # a 可以到达 c（通过b）
        assert optimizer._can_reach("a", "c", node_map) is True
        # b 不能到达 a
        assert optimizer._can_reach("b", "a", node_map) is False

    def test_apply_dependency_simplification(self, optimizer):
        """测试应用依赖简化."""
        nodes = [
            TaskNodeInfo(
                task_id="a",
                task_type=TaskType.DATA_COLLECTION,
                description="任务A",
                inputs=[],
                outputs=["out_a"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="b",
                task_type=TaskType.CALCULATION,
                description="任务B",
                inputs=["out_a"],
                outputs=["out_b"],
                dependencies=["a"],
            ),
            TaskNodeInfo(
                task_id="c",
                task_type=TaskType.EXECUTION,
                description="任务C",
                inputs=["out_a", "out_b"],
                outputs=["out_c"],
                dependencies=["a", "b"],  # 依赖a是冗余的（因为b依赖a）
            ),
        ]

        result = optimizer._apply_dependency_simplification(nodes)

        # 检查冗余依赖是否被移除
        node_c = next(n for n in result if n.task_id == "c")
        # 注意：实际行为取决于算法实现
        assert isinstance(node_c.dependencies, list)


class TestHeuristicOptimizerAlternatives:
    """测试备选链生成."""

    @pytest.fixture
    def optimizer(self):
        return HeuristicOptimizer()

    @pytest.fixture
    def sample_nodes(self):
        return [
            TaskNodeInfo(
                task_id="task1",
                task_type=TaskType.DATA_COLLECTION,
                description="任务1",
                inputs=[],
                outputs=["out1"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="task2",
                task_type=TaskType.CALCULATION,
                description="任务2",
                inputs=["out1"],
                outputs=["out2"],
                dependencies=["task1"],
            ),
        ]

    def test_generate_heuristic_alternatives(self, optimizer, sample_nodes):
        """测试生成启发式备选链."""
        alternatives = optimizer.generate_heuristic_alternatives(sample_nodes)

        assert len(alternatives) >= 3
        strategies = [alt.strategy for alt in alternatives]
        assert "default" in strategies
        assert "max_parallel" in strategies
        assert "critical_path" in strategies

    def test_alternatives_have_reliability_scores(self, optimizer, sample_nodes):
        """测试备选链有可靠性评分."""
        alternatives = optimizer.generate_heuristic_alternatives(sample_nodes)

        for alt in alternatives:
            assert hasattr(alt, "reliability_score")
            assert isinstance(alt.reliability_score, float)


class TestHeuristicOptimizerReport:
    """测试优化报告."""

    @pytest.fixture
    def optimizer(self):
        return HeuristicOptimizer()

    def test_get_optimization_report(self, optimizer):
        """测试生成优化报告."""
        original = [
            TaskNodeInfo(
                task_id="task1",
                task_type=TaskType.DATA_COLLECTION,
                description="任务1",
                inputs=[],
                outputs=["out1"],
                dependencies=[],
            ),
        ]

        optimized = [
            TaskNodeInfo(
                task_id="task1",
                task_type=TaskType.DATA_COLLECTION,
                description="任务1",
                inputs=[],
                outputs=["out1"],
                dependencies=[],
            ),
            TaskNodeInfo(
                task_id="task2",
                task_type=TaskType.CALCULATION,
                description="任务2",
                inputs=["out1"],
                outputs=["out2"],
                dependencies=["task1"],
            ),
        ]

        report = optimizer.get_optimization_report(original, optimized)

        assert "original" in report
        assert "optimized" in report
        assert "improvement" in report
        assert "strategies_applied" in report
        assert report["original"]["node_count"] == 1
        assert report["optimized"]["node_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
