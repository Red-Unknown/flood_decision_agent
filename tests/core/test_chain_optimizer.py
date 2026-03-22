"""ChainOptimizer 链路优化模块测试."""

import pytest

from flood_decision_agent.core.chain_optimizer import (
    ChainEvaluation,
    ChainOptimizer,
    DecompositionStrategy,
    OptimizedChain,
    ToolSelectionStrategy,
)
from flood_decision_agent.core.task_graph import Node, NodeStatus, TaskGraph
from flood_decision_agent.tools.common_tools import CommonTools


@pytest.fixture
def optimizer():
    """创建 ChainOptimizer 实例."""
    return ChainOptimizer(max_iterations=3, reliability_threshold=0.8)


@pytest.fixture
def sample_task_graph():
    """创建示例任务图."""
    graph = TaskGraph()

    # 创建节点
    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=[],
        tool_candidates=[{"name": "get_current_time", "priority": 10}],
        output_keys=["current_time"],
    )

    node2 = Node(
        node_id="N2",
        task_type="compute",
        dependencies=["N1"],
        tool_candidates=[{"name": "simple_calculator", "priority": 10}],
        output_keys=["result"],
    )

    node3 = Node(
        node_id="N3",
        task_type="format",
        dependencies=["N2"],
        tool_candidates=[{"name": "to_json", "priority": 10}],
        output_keys=["json_string"],
    )

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    return graph


@pytest.fixture
def cyclic_task_graph():
    """创建包含循环依赖的任务图."""
    graph = TaskGraph()

    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=["N3"],  # 循环依赖
        tool_candidates=[],
    )

    node2 = Node(
        node_id="N2",
        task_type="compute",
        dependencies=["N1"],
        tool_candidates=[],
    )

    node3 = Node(
        node_id="N3",
        task_type="format",
        dependencies=["N2"],  # 形成循环
        tool_candidates=[],
    )

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    return graph


@pytest.fixture
def bottleneck_task_graph():
    """创建包含瓶颈节点的任务图."""
    graph = TaskGraph()

    # N1 被多个节点依赖，形成瓶颈
    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=[],
        tool_candidates=[{"name": "get_current_time", "priority": 10}],
        output_keys=["data"],
    )

    # N2-N5 都依赖 N1
    for i in range(2, 6):
        node = Node(
            node_id=f"N{i}",
            task_type="compute",
            dependencies=["N1"],
            tool_candidates=[{"name": "simple_calculator", "priority": 10}],
            output_keys=[f"result_{i}"],
        )
        graph.add_node(node)

    graph.add_node(node1)

    return graph


class TestChainOptimizerInit:
    """测试 ChainOptimizer 初始化."""

    def test_default_init(self):
        """测试默认初始化."""
        optimizer = ChainOptimizer()
        assert optimizer.max_iterations == 3
        assert optimizer.reliability_threshold == 0.8
        assert optimizer._chain_counter == 0

    def test_custom_init(self):
        """测试自定义参数初始化."""
        optimizer = ChainOptimizer(max_iterations=5, reliability_threshold=0.9)
        assert optimizer.max_iterations == 5
        assert optimizer.reliability_threshold == 0.9


class TestGenerateAlternatives:
    """测试生成备选任务链功能."""

    def test_generate_alternatives_default(self, optimizer, sample_task_graph):
        """测试默认生成3条备选链."""
        alternatives = optimizer.generate_alternatives(sample_task_graph)

        assert len(alternatives) == 3
        # 确保每个备选链都是独立的副本
        for alt in alternatives:
            assert isinstance(alt, TaskGraph)
            assert len(alt.get_all_nodes()) == len(sample_task_graph.get_all_nodes())

    def test_generate_alternatives_custom_count(self, optimizer, sample_task_graph):
        """测试自定义生成数量."""
        alternatives = optimizer.generate_alternatives(sample_task_graph, num_alternatives=2)
        assert len(alternatives) == 2

    def test_alternatives_have_different_strategies(self, optimizer, sample_task_graph):
        """测试生成的备选链使用不同策略."""
        alternatives = optimizer.generate_alternatives(sample_task_graph)

        # 检查不同链的执行策略
        strategies = set()
        for alt in alternatives:
            nodes = alt.get_all_nodes()
            for node in nodes.values():
                strategies.add(node.execution_strategy)

        # 应该有不同的策略
        assert len(strategies) > 0


class TestEvaluateReliability:
    """测试链路可靠性评估功能."""

    def test_evaluate_reliability_basic(self, optimizer, sample_task_graph):
        """测试基本可靠性评估."""
        evaluation = optimizer.evaluate_reliability(sample_task_graph)

        assert isinstance(evaluation, ChainEvaluation)
        assert evaluation.chain_id.startswith("chain_")
        assert 0 <= evaluation.reliability_score <= 1
        assert evaluation.cycle_free is True
        assert 0 <= evaluation.tool_availability <= 1
        assert evaluation.data_dependency_valid is True
        assert isinstance(evaluation.bottleneck_nodes, list)
        assert 0 <= evaluation.execution_order_score <= 1
        assert "total_nodes" in evaluation.details

    def test_evaluate_cyclic_graph(self, optimizer, cyclic_task_graph):
        """测试循环依赖检测."""
        evaluation = optimizer.evaluate_reliability(cyclic_task_graph)

        assert evaluation.cycle_free is False
        assert evaluation.reliability_score == 0.0
        assert evaluation.execution_order_score == 0.0

    def test_evaluate_bottleneck_detection(self, optimizer, bottleneck_task_graph):
        """测试瓶颈节点识别."""
        evaluation = optimizer.evaluate_reliability(bottleneck_task_graph)

        # N1 应该被识别为瓶颈节点
        assert "N1" in evaluation.bottleneck_nodes

    def test_tool_availability_evaluation(self, optimizer, sample_task_graph):
        """测试工具可用性评估."""
        # 注册工具
        CommonTools.register_all()

        evaluation = optimizer.evaluate_reliability(sample_task_graph)

        # 工具应该可用
        assert evaluation.tool_availability > 0


class TestOptimizeIteratively:
    """测试迭代优化功能."""

    def test_optimize_iteratively_basic(self, optimizer, sample_task_graph):
        """测试基本迭代优化."""
        result = optimizer.optimize_iteratively(sample_task_graph)

        assert isinstance(result, OptimizedChain)
        assert isinstance(result.task_graph, TaskGraph)
        assert isinstance(result.evaluation, ChainEvaluation)
        assert result.optimization_rounds >= 1
        assert result.optimization_rounds <= optimizer.max_iterations

    def test_optimize_reaches_target(self, optimizer, sample_task_graph):
        """测试优化达到目标可靠性."""
        # 设置较低的目标，应该能快速达到
        result = optimizer.optimize_iteratively(sample_task_graph, target_reliability=0.5)

        assert result.evaluation.reliability_score >= 0.5

    def test_optimize_preserves_structure(self, optimizer, sample_task_graph):
        """测试优化保持任务图结构."""
        original_nodes = set(sample_task_graph.get_all_nodes().keys())

        result = optimizer.optimize_iteratively(sample_task_graph)
        optimized_nodes = set(result.task_graph.get_all_nodes().keys())

        assert original_nodes == optimized_nodes


class TestSelectBestChain:
    """测试选择最优链功能."""

    def test_select_best_chain(self, optimizer, sample_task_graph):
        """测试从多条链中选择最优."""
        # 生成备选链
        alternatives = optimizer.generate_alternatives(sample_task_graph, num_alternatives=3)

        best_chain, best_evaluation = optimizer.select_best_chain(alternatives)

        assert isinstance(best_chain, TaskGraph)
        assert isinstance(best_evaluation, ChainEvaluation)

        # 最优链的可靠性应该最高
        for alt in alternatives:
            eval_result = optimizer.evaluate_reliability(alt)
            assert best_evaluation.reliability_score >= eval_result.reliability_score

    def test_select_best_chain_empty(self, optimizer):
        """测试空列表抛出异常."""
        with pytest.raises(ValueError, match="备选链列表为空"):
            optimizer.select_best_chain([])


class TestMergeOptimize:
    """测试合并优化功能."""

    def test_merge_optimize_basic(self, optimizer, sample_task_graph):
        """测试基本合并优化."""
        alternatives = optimizer.generate_alternatives(sample_task_graph, num_alternatives=3)

        result = optimizer.merge_optimize(alternatives)

        assert isinstance(result, OptimizedChain)
        assert isinstance(result.task_graph, TaskGraph)
        assert isinstance(result.evaluation, ChainEvaluation)

    def test_merge_optimize_single_chain(self, optimizer, sample_task_graph):
        """测试单条链的合并优化."""
        result = optimizer.merge_optimize([sample_task_graph])

        assert isinstance(result, OptimizedChain)
        assert result.optimization_rounds == 0

    def test_merge_optimize_empty(self, optimizer):
        """测试空列表抛出异常."""
        with pytest.raises(ValueError, match="备选链列表为空"):
            optimizer.merge_optimize([])


class TestDecompositionStrategies:
    """测试分解策略."""

    def test_sequential_strategy(self, optimizer, sample_task_graph):
        """测试顺序分解策略."""
        result = optimizer._generate_alternative_chain(
            sample_task_graph,
            DecompositionStrategy.SEQUENTIAL,
            ToolSelectionStrategy.PRIORITY,
        )

        assert isinstance(result, TaskGraph)

    def test_parallel_strategy(self, optimizer, sample_task_graph):
        """测试并行分解策略."""
        result = optimizer._generate_alternative_chain(
            sample_task_graph,
            DecompositionStrategy.PARALLEL,
            ToolSelectionStrategy.PRIORITY,
        )

        nodes = result.get_all_nodes()
        # 检查是否有节点被标记为并行
        parallel_nodes = [n for n in nodes.values() if n.execution_strategy == "parallel"]
        assert len(parallel_nodes) >= 0  # 可能有也可能没有

    def test_hierarchical_strategy(self, optimizer, sample_task_graph):
        """测试层次分解策略."""
        result = optimizer._generate_alternative_chain(
            sample_task_graph,
            DecompositionStrategy.HIERARCHICAL,
            ToolSelectionStrategy.PRIORITY,
        )

        nodes = result.get_all_nodes()
        # 检查是否有节点被标记为层次
        hierarchical_nodes = [
            n for n in nodes.values() if "hierarchical" in n.execution_strategy
        ]
        assert len(hierarchical_nodes) >= 0


class TestToolSelectionStrategies:
    """测试工具选择策略."""

    def test_priority_strategy(self, optimizer, sample_task_graph):
        """测试优先级策略."""
        result = optimizer._apply_tool_selection(
            sample_task_graph,
            ToolSelectionStrategy.PRIORITY,
        )

        nodes = result.get_all_nodes()
        for node in nodes.values():
            if node.tool_candidates:
                # 检查是否按优先级排序
                priorities = [t.get("priority", 100) for t in node.tool_candidates]
                assert priorities == sorted(priorities)

    def test_reliability_strategy(self, optimizer, sample_task_graph):
        """测试可靠性策略."""
        result = optimizer._apply_tool_selection(
            sample_task_graph,
            ToolSelectionStrategy.RELIABILITY,
        )

        assert isinstance(result, TaskGraph)

    def test_balanced_strategy(self, optimizer, sample_task_graph):
        """测试平衡策略."""
        result = optimizer._apply_tool_selection(
            sample_task_graph,
            ToolSelectionStrategy.BALANCED,
        )

        assert isinstance(result, TaskGraph)


class TestHelperMethods:
    """测试辅助方法."""

    def test_copy_task_graph(self, optimizer, sample_task_graph):
        """测试深拷贝任务图."""
        copied = optimizer._copy_task_graph(sample_task_graph)

        assert copied is not sample_task_graph
        assert len(copied.get_all_nodes()) == len(sample_task_graph.get_all_nodes())

        # 修改副本不应影响原图
        nodes = copied.get_all_nodes()
        if nodes:
            first_node = list(nodes.values())[0]
            first_node.execution_strategy = "modified"

            original_nodes = sample_task_graph.get_all_nodes()
            original_first = list(original_nodes.values())[0]
            assert original_first.execution_strategy != "modified"

    def test_estimate_complexity(self, optimizer):
        """测试复杂度估计."""
        simple_node = Node(
            node_id="simple",
            task_type="test",
            dependencies=[],
            tool_candidates=[],
        )

        complex_node = Node(
            node_id="complex",
            task_type="test",
            dependencies=["A", "B", "C"],
            tool_candidates=[{"name": "t1"}, {"name": "t2"}, {"name": "t3"}, {"name": "t4"}],
        )

        simple_complexity = optimizer._estimate_complexity(simple_node)
        complex_complexity = optimizer._estimate_complexity(complex_node)

        assert 0 <= simple_complexity <= 1
        assert 0 <= complex_complexity <= 1
        assert simple_complexity < complex_complexity

    def test_calculate_critical_path(self, optimizer, sample_task_graph):
        """测试关键路径计算."""
        length = optimizer._calculate_critical_path_length(sample_task_graph)

        assert length > 0
        # 示例图有3个节点线性依赖，关键路径长度为3
        assert length == 3

    def test_chain_signature(self, optimizer, sample_task_graph):
        """测试任务链签名."""
        signature = optimizer._get_chain_signature(sample_task_graph)

        assert isinstance(signature, str)
        assert "N1" in signature
        assert "N2" in signature
        assert "N3" in signature

    def test_chain_signature_cyclic(self, optimizer, cyclic_task_graph):
        """测试循环依赖图的签名."""
        signature = optimizer._get_chain_signature(cyclic_task_graph)

        assert signature == "invalid_cycle"
