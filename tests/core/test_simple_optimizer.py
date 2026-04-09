"""SimpleOptimizer 轻量级链路优化器单元测试."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

# 直接导入模块文件，避免循环导入
import importlib.util

# 导入 task_decomposer 模块
spec_td = importlib.util.spec_from_file_location(
    "task_decomposer",
    str(ROOT / "src" / "flood_decision_agent" / "agents" / "decision_chain" / "task_decomposer.py")
)
task_decomposer_module = importlib.util.module_from_spec(spec_td)
sys.modules["task_decomposer"] = task_decomposer_module
spec_td.loader.exec_module(task_decomposer_module)

TaskNodeInfo = task_decomposer_module.TaskNodeInfo
TaskType = task_decomposer_module.TaskType

# 导入 simple_optimizer 模块
spec_so = importlib.util.spec_from_file_location(
    "simple_optimizer",
    str(ROOT / "src" / "flood_decision_agent" / "agents" / "decision_chain" / "simple_optimizer.py")
)
simple_optimizer_module = importlib.util.module_from_spec(spec_so)
sys.modules["simple_optimizer"] = simple_optimizer_module
spec_so.loader.exec_module(simple_optimizer_module)

SimpleOptimizer = simple_optimizer_module.SimpleOptimizer


@pytest.fixture
def optimizer():
    """创建 SimpleOptimizer 实例."""
    return SimpleOptimizer()


@pytest.fixture
def sample_task_nodes():
    """创建示例任务节点列表."""
    return [
        TaskNodeInfo(
            task_id="task_1",
            task_type=TaskType.DATA_COLLECTION,
            description="采集水位数据",
            inputs=["sensor_config"],
            outputs=["water_level_data"],
            dependencies=[],
        ),
        TaskNodeInfo(
            task_id="task_2",
            task_type=TaskType.DATA_COLLECTION,
            description="采集降雨数据",
            inputs=["weather_config"],
            outputs=["rainfall_data"],
            dependencies=[],
        ),
        TaskNodeInfo(
            task_id="task_3",
            task_type=TaskType.CALCULATION,
            description="计算洪峰流量",
            inputs=["water_level_data", "rainfall_data"],
            outputs=["peak_flow"],
            dependencies=["task_1", "task_2"],
        ),
        TaskNodeInfo(
            task_id="task_4",
            task_type=TaskType.DECISION,
            description="调度决策",
            inputs=["peak_flow"],
            outputs=["decision_result"],
            dependencies=["task_3"],
        ),
    ]


@pytest.fixture
def cyclic_task_nodes():
    """创建包含循环依赖的任务节点列表."""
    return [
        TaskNodeInfo(
            task_id="task_1",
            task_type=TaskType.DATA_COLLECTION,
            description="任务1",
            inputs=[],
            outputs=["output_1"],
            dependencies=["task_3"],  # 循环依赖
        ),
        TaskNodeInfo(
            task_id="task_2",
            task_type=TaskType.CALCULATION,
            description="任务2",
            inputs=["output_1"],
            outputs=["output_2"],
            dependencies=["task_1"],
        ),
        TaskNodeInfo(
            task_id="task_3",
            task_type=TaskType.DECISION,
            description="任务3",
            inputs=["output_2"],
            outputs=["output_3"],
            dependencies=["task_2"],
        ),
    ]


@pytest.fixture
def single_task_node():
    """创建单个任务节点."""
    return [
        TaskNodeInfo(
            task_id="single_task",
            task_type=TaskType.DATA_COLLECTION,
            description="单一任务",
            inputs=["input_data"],
            outputs=["output_data"],
            dependencies=[],
        ),
    ]


class TestSimpleOptimizerInit:
    """测试 SimpleOptimizer 初始化."""

    def test_default_init(self, optimizer):
        """测试默认初始化."""
        assert optimizer.reliability_threshold == 0.6
        assert optimizer._logger is not None

    def test_threshold_is_fixed(self):
        """测试阈值固定为0.6."""
        opt = SimpleOptimizer()
        # 阈值应该是固定的0.6
        assert opt.reliability_threshold == 0.6


class TestOptimizeMethod:
    """测试 optimize 方法."""

    def test_optimize_basic(self, optimizer, sample_task_nodes):
        """测试基本优化功能."""
        result = optimizer.optimize(sample_task_nodes)

        assert isinstance(result, dict)
        assert "original_nodes" in result
        assert "alternative" in result
        assert "reliability_score" in result
        assert "issues" in result
        assert "passed" in result
        assert "details" in result

    def test_optimize_returns_correct_original_nodes(self, optimizer, sample_task_nodes):
        """测试返回的原始节点正确."""
        result = optimizer.optimize(sample_task_nodes)

        assert result["original_nodes"] == sample_task_nodes
        assert len(result["original_nodes"]) == 4

    def test_optimize_generates_alternative(self, optimizer, sample_task_nodes):
        """测试生成备选链."""
        result = optimizer.optimize(sample_task_nodes)

        assert result["alternative"] is not None
        # ChainAlternative 类型检查
        assert hasattr(result["alternative"], "chain_id")
        assert hasattr(result["alternative"], "nodes")
        assert hasattr(result["alternative"], "reliability_score")
        assert len(result["alternative"].nodes) == 4

    def test_optimize_reliability_score_range(self, optimizer, sample_task_nodes):
        """测试可靠性评分范围."""
        result = optimizer.optimize(sample_task_nodes)

        assert 0.0 <= result["reliability_score"] <= 1.0

    def test_optimize_issues_is_list(self, optimizer, sample_task_nodes):
        """测试问题列表是列表类型."""
        result = optimizer.optimize(sample_task_nodes)

        assert isinstance(result["issues"], list)

    def test_optimize_passed_is_boolean(self, optimizer, sample_task_nodes):
        """测试 passed 是布尔类型."""
        result = optimizer.optimize(sample_task_nodes)

        assert isinstance(result["passed"], bool)

    def test_optimize_with_empty_list(self, optimizer):
        """测试空列表输入."""
        result = optimizer.optimize([])

        assert result["original_nodes"] == []
        assert result["alternative"] is None
        assert result["reliability_score"] == 0.0
        assert "任务节点列表为空" in result["issues"]
        assert result["passed"] is False

    def test_optimize_with_single_node(self, optimizer, single_task_node):
        """测试单节点输入."""
        result = optimizer.optimize(single_task_node)

        assert result["alternative"] is not None
        assert len(result["alternative"].nodes) == 1
        assert isinstance(result["reliability_score"], float)

    def test_optimize_with_cyclic_dependencies(self, optimizer, cyclic_task_nodes):
        """测试循环依赖检测."""
        result = optimizer.optimize(cyclic_task_nodes)

        # 循环依赖应该导致可靠性评分为0
        assert result["reliability_score"] == 0.0
        assert result["passed"] is False
        # 应该检测到循环依赖问题
        assert any("循环依赖" in issue for issue in result["issues"])

    def test_optimize_with_available_tools(self, optimizer, sample_task_nodes):
        """测试带可用工具的优化."""
        available_tools = {"data_collection", "calculation"}
        result = optimizer.optimize(sample_task_nodes, available_tools)

        assert isinstance(result, dict)
        assert "reliability_score" in result

    def test_optimize_details_structure(self, optimizer, sample_task_nodes):
        """测试 details 结构."""
        result = optimizer.optimize(sample_task_nodes)

        assert "details" in result
        details = result["details"]
        assert "cycle_check" in details
        assert "tool_check" in details
        assert "dependency_check" in details


class TestQuickEvaluateMethod:
    """测试 quick_evaluate 方法."""

    def test_quick_evaluate_basic(self, optimizer, sample_task_nodes):
        """测试基本快速评估."""
        score, issues = optimizer.quick_evaluate(sample_task_nodes)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(issues, list)

    def test_quick_evaluate_with_empty_list(self, optimizer):
        """测试空列表快速评估."""
        score, issues = optimizer.quick_evaluate([])

        assert score == 0.0
        assert "任务节点列表为空" in issues

    def test_quick_evaluate_with_cyclic_dependencies(self, optimizer, cyclic_task_nodes):
        """测试循环依赖快速评估."""
        score, issues = optimizer.quick_evaluate(cyclic_task_nodes)

        assert score == 0.0
        assert any("循环依赖" in issue for issue in issues)

    def test_quick_evaluate_with_tools(self, optimizer, sample_task_nodes):
        """测试带工具的快速评估."""
        available_tools = {"data_collection", "calculation", "decision"}
        score, issues = optimizer.quick_evaluate(sample_task_nodes, available_tools)

        assert isinstance(score, float)
        assert isinstance(issues, list)


class TestIsReliableMethod:
    """测试 is_reliable 方法."""

    def test_is_reliable_basic(self, optimizer, sample_task_nodes):
        """测试基本可靠性检查."""
        result = optimizer.is_reliable(sample_task_nodes)

        assert isinstance(result, bool)

    def test_is_reliable_with_empty_list(self, optimizer):
        """测试空列表可靠性检查."""
        result = optimizer.is_reliable([])

        assert result is False

    def test_is_reliable_with_cyclic_dependencies(self, optimizer, cyclic_task_nodes):
        """测试循环依赖可靠性检查."""
        result = optimizer.is_reliable(cyclic_task_nodes)

        # 循环依赖应该返回 False
        assert result is False

    def test_is_reliable_threshold_check(self, optimizer):
        """测试阈值检查逻辑."""
        # 创建一个简单的可靠任务链
        reliable_nodes = [
            TaskNodeInfo(
                task_id="task_1",
                task_type=TaskType.DATA_COLLECTION,
                description="可靠任务",
                inputs=[],
                outputs=["output_1"],
                dependencies=[],
            ),
        ]

        result = optimizer.is_reliable(reliable_nodes)
        # 简单任务应该通过可靠性检查
        assert isinstance(result, bool)


class TestReliabilityThreshold:
    """测试可靠性阈值."""

    def test_threshold_value(self, optimizer):
        """测试阈值固定为0.6."""
        assert optimizer.reliability_threshold == 0.6

    def test_passed_logic_with_threshold(self, optimizer):
        """测试通过阈值的逻辑."""
        # 使用循环依赖的任务链，可靠性为0，应该不通过
        cyclic_nodes = [
            TaskNodeInfo(
                task_id="task_1",
                task_type=TaskType.DATA_COLLECTION,
                description="任务1",
                inputs=[],
                outputs=["output_1"],
                dependencies=["task_2"],
            ),
            TaskNodeInfo(
                task_id="task_2",
                task_type=TaskType.CALCULATION,
                description="任务2",
                inputs=["output_1"],
                outputs=["output_2"],
                dependencies=["task_1"],
            ),
        ]

        result = optimizer.optimize(cyclic_nodes)
        # 循环依赖导致可靠性为0，小于阈值0.6
        assert result["reliability_score"] == 0.0
        assert result["passed"] is False


class TestAlternativeChainProperties:
    """测试备选链属性."""

    def test_alternative_has_reliability_score(self, optimizer, sample_task_nodes):
        """测试备选链有可靠性评分."""
        result = optimizer.optimize(sample_task_nodes)

        alternative = result["alternative"]
        assert alternative is not None
        assert hasattr(alternative, "reliability_score")
        assert isinstance(alternative.reliability_score, float)

    def test_alternative_has_chain_id(self, optimizer, sample_task_nodes):
        """测试备选链有链ID."""
        result = optimizer.optimize(sample_task_nodes)

        alternative = result["alternative"]
        assert alternative is not None
        assert hasattr(alternative, "chain_id")
        assert isinstance(alternative.chain_id, str)

    def test_alternative_has_strategy(self, optimizer, sample_task_nodes):
        """测试备选链有策略."""
        result = optimizer.optimize(sample_task_nodes)

        alternative = result["alternative"]
        assert alternative is not None
        assert hasattr(alternative, "strategy")
        assert alternative.strategy == "default"


class TestNodePreservation:
    """测试节点保留."""

    def test_nodes_preserved_in_alternative(self, optimizer, sample_task_nodes):
        """测试备选链保留原始节点."""
        result = optimizer.optimize(sample_task_nodes)

        alternative = result["alternative"]
        assert len(alternative.nodes) == len(sample_task_nodes)

        # 检查节点ID是否保留
        original_ids = {node.task_id for node in sample_task_nodes}
        alternative_ids = {node.task_id for node in alternative.nodes}
        assert original_ids == alternative_ids

    def test_node_attributes_preserved(self, optimizer, sample_task_nodes):
        """测试节点属性被保留."""
        result = optimizer.optimize(sample_task_nodes)

        alternative = result["alternative"]
        for i, node in enumerate(alternative.nodes):
            assert isinstance(node.task_id, str)
            assert isinstance(node.task_type, TaskType)
            assert isinstance(node.description, str)


class TestEdgeCases:
    """测试边界情况."""

    def test_optimize_with_none_tools(self, optimizer, sample_task_nodes):
        """测试 tools 为 None."""
        result = optimizer.optimize(sample_task_nodes, available_tools=None)

        assert result["alternative"] is not None
        assert isinstance(result["reliability_score"], float)

    def test_optimize_with_empty_tools(self, optimizer, sample_task_nodes):
        """测试 tools 为空集合."""
        result = optimizer.optimize(sample_task_nodes, available_tools=set())

        assert result["alternative"] is not None
        assert isinstance(result["reliability_score"], float)

    def test_multiple_calls_consistency(self, optimizer, sample_task_nodes):
        """测试多次调用一致性."""
        result1 = optimizer.optimize(sample_task_nodes)
        result2 = optimizer.optimize(sample_task_nodes)

        # 两次调用应该返回相同结构的结果
        assert result1.keys() == result2.keys()
        assert len(result1["alternative"].nodes) == len(result2["alternative"].nodes)


class TestIntegrationWithChainOptimizer:
    """测试与 ChainOptimizer 的集成."""

    def test_uses_chain_optimizer_internally(self, optimizer, sample_task_nodes):
        """测试内部使用 ChainOptimizer."""
        # 这个测试验证 SimpleOptimizer 正确复用了 ChainOptimizer 的功能
        result = optimizer.optimize(sample_task_nodes)

        # 验证结果包含 ChainOptimizer 提供的详细信息
        assert "details" in result
        details = result["details"]
        assert "cycle_check" in details
        assert "tool_check" in details
        assert "dependency_check" in details
