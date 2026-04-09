"""TaskDecomposer 模块测试."""

import pytest

from flood_decision_agent.core.task_decomposer import (
    DecompositionRule,
    DecompositionRuleLibrary,
    TaskDecomposer,
    TaskNodeInfo,
    TaskType,
)
from flood_decision_agent.core.task_graph import Node


class TestTaskType:
    """任务类型枚举测试."""

    def test_task_type_values(self):
        """测试任务类型枚举值."""
        assert TaskType.DATA_COLLECTION.value == "data_collection"
        assert TaskType.PREDICTION.value == "prediction"
        assert TaskType.CALCULATION.value == "calculation"
        assert TaskType.DECISION.value == "decision"
        assert TaskType.EXECUTION.value == "execution"
        assert TaskType.VERIFICATION.value == "verification"


class TestTaskNodeInfo:
    """任务节点信息测试."""

    def test_task_node_info_creation(self):
        """测试任务节点信息创建."""
        node = TaskNodeInfo(
            task_id="test_001",
            task_type=TaskType.EXECUTION,
            description="测试任务",
            inputs=["input1", "input2"],
            outputs=["output1"],
            dependencies=["dep_001"],
            metadata={"key": "value"},
        )

        assert node.task_id == "test_001"
        assert node.task_type == TaskType.EXECUTION
        assert node.description == "测试任务"
        assert node.inputs == ["input1", "input2"]
        assert node.outputs == ["output1"]
        assert node.dependencies == ["dep_001"]
        assert node.metadata == {"key": "value"}

    def test_task_node_info_defaults(self):
        """测试任务节点信息默认值."""
        node = TaskNodeInfo(
            task_id="test_001",
            task_type=TaskType.DATA_COLLECTION,
            description="测试任务",
        )

        assert node.inputs == []
        assert node.outputs == []
        assert node.dependencies == []
        assert node.metadata == {}

    def test_to_dict(self):
        """测试转换为字典."""
        node = TaskNodeInfo(
            task_id="test_001",
            task_type=TaskType.EXECUTION,
            description="测试任务",
            inputs=["input1"],
            outputs=["output1"],
        )

        result = node.to_dict()

        assert result["task_id"] == "test_001"
        assert result["task_type"] == "execution"
        assert result["description"] == "测试任务"
        assert result["inputs"] == ["input1"]
        assert result["outputs"] == ["output1"]


class TestDecompositionRuleLibrary:
    """分解规则库测试."""

    def test_initialization(self):
        """测试规则库初始化."""
        library = DecompositionRuleLibrary()

        # 检查预定义规则是否存在
        assert library.get_rule(TaskType.EXECUTION) is not None
        assert library.get_rule(TaskType.DECISION) is not None
        assert library.get_rule(TaskType.PREDICTION) is not None

    def test_get_rule_nonexistent(self):
        """测试获取不存在的规则."""
        library = DecompositionRuleLibrary()

        # 验证任务类型没有预定义规则
        assert library.get_rule(TaskType.VERIFICATION) is None

    def test_add_rule(self):
        """测试添加自定义规则."""
        library = DecompositionRuleLibrary()

        new_rule = DecompositionRule(
            task_type=TaskType.VERIFICATION,
            sub_tasks=[
                {
                    "task_type": TaskType.VERIFICATION,
                    "description": "验证结果",
                    "inputs": ["result"],
                    "outputs": ["verification_result"],
                }
            ],
        )

        library.add_rule(new_rule)

        retrieved = library.get_rule(TaskType.VERIFICATION)
        assert retrieved is not None
        assert retrieved.task_type == TaskType.VERIFICATION

    def test_get_all_rules(self):
        """测试获取所有规则."""
        library = DecompositionRuleLibrary()

        rules = library.get_all_rules()

        assert TaskType.EXECUTION in rules
        assert TaskType.DECISION in rules
        assert TaskType.PREDICTION in rules


class TestTaskDecomposer:
    """任务分解器测试."""

    @pytest.fixture
    def decomposer(self):
        """创建任务分解器实例."""
        return TaskDecomposer()

    def test_initialization(self, decomposer):
        """测试分解器初始化."""
        assert decomposer.rule_library is not None
        assert decomposer.get_cache_stats()["cache_size"] == 0

    def test_decompose_backward_execution(self, decomposer):
        """测试逆向分解执行任务类型."""
        nodes = decomposer.decompose_backward(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
        )

        # 验证节点数量（应该有6个子任务）
        assert len(nodes) == 6

        # 验证第一个节点是数据采集（执行顺序的第一个）
        assert nodes[0].task_type == TaskType.DATA_COLLECTION
        assert "降雨数据" in nodes[0].description or "上游流量" in nodes[0].description

        # 验证最后一个节点是执行
        assert nodes[-1].task_type == TaskType.EXECUTION
        assert "执行调度" in nodes[-1].description

    def test_decompose_backward_caching(self, decomposer):
        """测试分解结果缓存."""
        # 第一次分解
        nodes1 = decomposer.decompose_backward(
            goal="测试目标",
            task_type=TaskType.PREDICTION,
            required_outputs=["prediction_result"],
        )

        # 第二次分解相同目标（应该命中缓存）
        nodes2 = decomposer.decompose_backward(
            goal="测试目标",
            task_type=TaskType.PREDICTION,
            required_outputs=["prediction_result"],
        )

        assert decomposer.get_cache_stats()["cache_size"] == 1
        assert nodes1 == nodes2

    def test_decompose_backward_no_rule(self, decomposer):
        """测试无规则时的分解."""
        # 创建一个没有规则的类型（使用VERIFICATION，默认无规则）
        library = DecompositionRuleLibrary()
        decomposer_no_rule = TaskDecomposer(library)

        nodes = decomposer_no_rule.decompose_backward(
            goal="验证某事",
            task_type=TaskType.VERIFICATION,
            required_outputs=["result"],
        )

        # 应该创建单节点任务
        assert len(nodes) == 1
        assert nodes[0].task_type == TaskType.VERIFICATION
        assert nodes[0].description == "验证某事"

    def test_verify_forward_success(self, decomposer):
        """测试正向验证成功."""
        nodes = decomposer.decompose_backward(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
        )

        is_valid, errors = decomposer.verify_forward(nodes)

        assert is_valid is True
        assert len(errors) == 0

    def test_verify_forward_empty_list(self, decomposer):
        """测试验证空列表."""
        is_valid, errors = decomposer.verify_forward([])

        assert is_valid is False
        assert "任务节点列表为空" in errors

    def test_verify_forward_duplicate_ids(self, decomposer):
        """测试验证重复ID."""
        nodes = [
            TaskNodeInfo(
                task_id="same_id",
                task_type=TaskType.DATA_COLLECTION,
                description="任务1",
            ),
            TaskNodeInfo(
                task_id="same_id",
                task_type=TaskType.EXECUTION,
                description="任务2",
            ),
        ]

        is_valid, errors = decomposer.verify_forward(nodes)

        assert is_valid is False
        assert any("重复" in error for error in errors)

    def test_verify_forward_missing_dependency(self, decomposer):
        """测试验证缺失依赖."""
        nodes = [
            TaskNodeInfo(
                task_id="task_001",
                task_type=TaskType.EXECUTION,
                description="执行任务",
                dependencies=["nonexistent_task"],
            ),
        ]

        is_valid, errors = decomposer.verify_forward(nodes)

        assert is_valid is False
        assert any("不存在" in error for error in errors)

    def test_verify_forward_missing_input(self, decomposer):
        """测试验证缺失输入."""
        nodes = [
            TaskNodeInfo(
                task_id="task_001",
                task_type=TaskType.EXECUTION,
                description="执行任务",
                inputs=["missing_input"],
                outputs=["output1"],
            ),
        ]

        is_valid, errors = decomposer.verify_forward(nodes)

        assert is_valid is False
        assert any("missing_input" in error for error in errors)

    def test_structure_nodes(self, decomposer):
        """测试节点结构化."""
        task_nodes = decomposer.decompose_backward(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
        )

        structured = decomposer.structure_nodes(task_nodes)

        assert len(structured) == len(task_nodes)

        # 验证Node对象属性
        for idx, node in enumerate(structured):
            assert isinstance(node, Node)
            assert node.node_id == f"N{idx + 1}"
            assert node.task_type == task_nodes[idx].task_type.value
            assert node.output_keys == task_nodes[idx].outputs

    def test_structure_nodes_with_start_id(self, decomposer):
        """测试节点结构化指定起始ID."""
        task_nodes = [
            TaskNodeInfo(
                task_id="test_001",
                task_type=TaskType.DATA_COLLECTION,
                description="测试任务",
                outputs=["output1"],
            ),
        ]

        structured = decomposer.structure_nodes(task_nodes, start_id=10)

        assert structured[0].node_id == "N10"

    def test_decompose_and_structure(self, decomposer):
        """测试一站式分解和结构化."""
        task_nodes, structured_nodes, errors = decomposer.decompose_and_structure(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
            context={"priority": "high"},
        )

        assert len(task_nodes) == 6
        assert len(structured_nodes) == 6
        assert len(errors) == 0

        # 验证上下文传递
        assert task_nodes[0].metadata.get("priority") == "high"

    def test_clear_cache(self, decomposer):
        """测试清除缓存."""
        # 先进行一次分解
        decomposer.decompose_backward(
            goal="测试目标",
            task_type=TaskType.PREDICTION,
            required_outputs=["prediction_result"],
        )

        assert decomposer.get_cache_stats()["cache_size"] == 1

        decomposer.clear_cache()

        assert decomposer.get_cache_stats()["cache_size"] == 0


class TestFloodDispatchExample:
    """洪水调度示例测试."""

    def test_flood_dispatch_decomposition(self):
        """测试洪水调度任务分解示例."""
        decomposer = TaskDecomposer()

        nodes = decomposer.decompose_backward(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
        )

        # 验证分解结果符合预期
        assert len(nodes) == 6

        # 验证执行顺序（从数据采集到执行）
        expected_order = [
            TaskType.DATA_COLLECTION,  # 采集降雨数据
            TaskType.DATA_COLLECTION,  # 采集上游流量
            TaskType.PREDICTION,       # 预测未来来水
            TaskType.DATA_COLLECTION,  # 获取当前水库状态
            TaskType.CALCULATION,      # 计算调度方案
            TaskType.EXECUTION,        # 执行调度操作
        ]

        actual_order = [node.task_type for node in nodes]
        assert actual_order == expected_order

        # 验证输入输出依赖关系
        # 执行调度操作依赖计算调度方案
        execution_node = nodes[-1]
        assert "dispatch_plan" in execution_node.inputs

        # 计算调度方案依赖来水预测
        calculation_node = nodes[-2]
        assert "inflow_forecast" in calculation_node.inputs

        # 验证正向验证通过
        is_valid, errors = decomposer.verify_forward(nodes)
        assert is_valid is True
        assert len(errors) == 0

    def test_flood_dispatch_structure(self):
        """测试洪水调度节点结构化."""
        decomposer = TaskDecomposer()

        _, structured_nodes, errors = decomposer.decompose_and_structure(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
        )

        assert len(errors) == 0
        assert len(structured_nodes) == 6

        # 验证节点ID格式
        for idx, node in enumerate(structured_nodes):
            assert node.node_id == f"N{idx + 1}"

        # 验证最后一个节点是执行节点
        last_node = structured_nodes[-1]
        assert last_node.task_type == "execution"
        assert "outflow_rate" in last_node.output_keys
