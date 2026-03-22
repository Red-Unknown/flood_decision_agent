"""决策链生成 Agent 单元测试.

测试 DecisionChainGeneratorAgent 的各个模块和完整流程.
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

from flood_decision_agent.agents.decision_chain_generator import (
    DecisionChainGeneratorAgent,
    DecisionPipeline,
)
from flood_decision_agent.core.chain_optimizer import (
    BottleneckInfo,
    ChainAlternative,
    ChainOptimizer,
)
from flood_decision_agent.core.intent_parser import IntentParser, TaskIntent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.task_decomposer import (
    TaskDecomposer,
    TaskNodeInfo,
    TaskType,
)
from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.core.task_graph_builder import TaskChainItem, TaskGraphBuilder


class TestIntentParser:
    """测试意图解析器."""

    def test_parse_natural_language_flood_dispatch(self):
        """测试自然语言解析 - 洪水调度."""
        parser = IntentParser()
        text = "三峡大坝需要将出库流量调整到19000立方米每秒"
        intent = parser.parse_natural_language(text)

        assert intent.task_type is not None
        assert intent.raw_input == text
        assert "outflow" in intent.goal or any(
            "出库" in str(v) for v in intent.goal.values()
        )

    def test_parse_natural_language_drought_dispatch(self):
        """测试自然语言解析 - 干旱调度."""
        parser = IntentParser()
        text = "当前是干旱期，需要增加水库蓄水量到175米"
        intent = parser.parse_natural_language(text)

        assert intent.task_type is not None
        assert intent.raw_input == text

    def test_parse_structured(self):
        """测试结构化输入解析."""
        parser = IntentParser()
        data = {
            "task_type": "flood_dispatch",
            "target": {"outflow": 19000},
            "constraints": {"max_rate": 500},
        }
        intent = parser.parse_structured(data)

        assert intent.task_type.value == "flood_dispatch"
        assert intent.goal.get("outflow") == 19000
        assert intent.constraints.get("max_rate") == 500

    def test_extract_numerical_values(self):
        """测试数值提取."""
        parser = IntentParser()
        text = "流量调整到19000立方米每秒，速率不超过500"
        intent = parser.parse_natural_language(text)

        # 验证数值被正确提取
        goal_values = [v for v in intent.goal.values() if isinstance(v, (int, float))]
        assert len(goal_values) > 0 or len(intent.goal) > 0


class TestTaskDecomposer:
    """测试任务分解器."""

    def test_decompose_backward_flood_dispatch(self):
        """测试逆向分解 - 洪水调度."""
        decomposer = TaskDecomposer()
        nodes = decomposer.decompose_backward(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
        )

        assert len(nodes) > 0
        # 验证节点类型分布
        task_types = [n.task_type for n in nodes]
        assert TaskType.DATA_COLLECTION in task_types
        assert TaskType.EXECUTION in task_types

    def test_verify_forward(self):
        """测试正向验证."""
        decomposer = TaskDecomposer()
        nodes = decomposer.decompose_backward(
            goal="测试目标",
            task_type=TaskType.EXECUTION,
            required_outputs=["result"],
        )

        is_valid, errors = decomposer.verify_forward(nodes)
        # 验证应该通过（基本结构正确）
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_structure_nodes(self):
        """测试节点结构化."""
        decomposer = TaskDecomposer()
        nodes = decomposer.decompose_backward(
            goal="调整出库流量",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow"],
        )

        structured = decomposer.structure_nodes(nodes)
        assert len(structured) == len(nodes)

        # 验证每个节点都有必要的属性
        for node in structured:
            assert node.node_id
            assert node.task_type

    def test_decompose_and_structure(self):
        """测试一站式分解和结构化."""
        decomposer = TaskDecomposer()
        task_nodes, structured_nodes, errors = decomposer.decompose_and_structure(
            goal="调整出库流量到19000m³/s",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow_rate"],
        )

        assert len(task_nodes) > 0
        assert len(structured_nodes) > 0
        assert len(task_nodes) == len(structured_nodes)


class TestChainOptimizer:
    """测试链路优化器."""

    def test_generate_alternatives(self):
        """测试生成备选链."""
        optimizer = ChainOptimizer()
        decomposer = TaskDecomposer()

        nodes = decomposer.decompose_backward(
            goal="调整出库流量",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow"],
        )

        alternatives = optimizer.generate_alternatives(nodes)
        assert len(alternatives) > 0
        assert all(isinstance(alt, ChainAlternative) for alt in alternatives)

    def test_evaluate_reliability(self):
        """测试可靠性评估."""
        optimizer = ChainOptimizer()
        decomposer = TaskDecomposer()

        nodes = decomposer.decompose_backward(
            goal="调整出库流量",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow"],
        )

        reliability, issues, details = optimizer.evaluate_reliability(nodes)
        assert 0.0 <= reliability <= 1.0
        assert isinstance(issues, list)
        assert isinstance(details, dict)

    def test_identify_bottlenecks(self):
        """测试瓶颈识别."""
        optimizer = ChainOptimizer()
        decomposer = TaskDecomposer()

        nodes = decomposer.decompose_backward(
            goal="调整出库流量",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow"],
        )

        bottlenecks = optimizer.identify_bottlenecks(nodes)
        assert isinstance(bottlenecks, list)
        # 所有瓶颈都应该是BottleneckInfo类型
        assert all(isinstance(b, BottleneckInfo) for b in bottlenecks)

    def test_optimize_iteratively(self):
        """测试迭代优化."""
        optimizer = ChainOptimizer()
        decomposer = TaskDecomposer()

        nodes = decomposer.decompose_backward(
            goal="调整出库流量",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow"],
        )

        optimized_nodes, reliability, log = optimizer.optimize_iteratively(
            nodes, max_iterations=2
        )
        assert len(optimized_nodes) > 0
        assert 0.0 <= reliability <= 1.0
        assert isinstance(log, list)

    def test_select_best_chain(self):
        """测试选择最优链."""
        optimizer = ChainOptimizer()
        decomposer = TaskDecomposer()

        nodes = decomposer.decompose_backward(
            goal="调整出库流量",
            task_type=TaskType.EXECUTION,
            required_outputs=["outflow"],
        )

        alternatives = optimizer.generate_alternatives(nodes)
        # 设置不同的可靠性评分
        for i, alt in enumerate(alternatives):
            alt.reliability_score = 0.5 + i * 0.1

        best = optimizer.select_best_chain(alternatives)
        assert best is not None
        assert best.reliability_score == max(alt.reliability_score for alt in alternatives)


class TestTaskGraphBuilder:
    """测试任务图构建器."""

    def test_build_from_chain(self):
        """测试从任务链构建图."""
        builder = TaskGraphBuilder()
        chain = [
            TaskChainItem(
                task_id="task1",
                task_type="data_collection",
                description="采集数据",
                inputs=[],
                outputs=["data"],
                dependencies=[],
            ),
            TaskChainItem(
                task_id="task2",
                task_type="calculation",
                description="计算",
                inputs=["data"],
                outputs=["result"],
                dependencies=["task1"],
            ),
        ]

        graph = builder.build_from_chain(chain)
        assert isinstance(graph, TaskGraph)
        assert len(graph.get_all_nodes()) == 2

    def test_validate_graph(self):
        """测试图验证."""
        builder = TaskGraphBuilder()
        chain = [
            TaskChainItem(
                task_id="task1",
                task_type="data_collection",
                inputs=[],
                outputs=["data"],
                dependencies=[],
            ),
            TaskChainItem(
                task_id="task2",
                task_type="calculation",
                inputs=["data"],
                outputs=["result"],
                dependencies=["task1"],
            ),
        ]

        graph = builder.build_from_chain(chain)
        is_valid, error = builder.validate_graph(graph)
        assert is_valid is True


class TestDecisionChainGeneratorAgent:
    """测试决策链生成 Agent."""

    def test_init(self):
        """测试初始化."""
        agent = DecisionChainGeneratorAgent()
        assert agent.agent_id == "DecisionChainGenerator"
        assert agent.intent_parser is not None
        assert agent.task_decomposer is not None
        assert agent.chain_optimizer is not None
        assert agent.task_graph_builder is not None

    def test_generate_chain_natural_language(self):
        """测试生成链 - 自然语言输入."""
        agent = DecisionChainGeneratorAgent()
        task_graph, metadata = agent.generate_chain(
            user_input="三峡大坝需要将出库流量调整到19000立方米每秒",
            input_type="natural_language",
        )

        assert isinstance(task_graph, TaskGraph)
        assert isinstance(metadata, dict)
        assert "intent" in metadata
        assert "decomposition" in metadata
        assert "optimization" in metadata
        assert "task_graph" in metadata

    def test_generate_chain_structured(self):
        """测试生成链 - 结构化输入."""
        agent = DecisionChainGeneratorAgent()
        structured_input = json.dumps(
            {
                "task_type": "flood_dispatch",
                "target": {"outflow": 19000},
            }
        )
        task_graph, metadata = agent.generate_chain(
            user_input=structured_input,
            input_type="structured",
        )

        assert isinstance(task_graph, TaskGraph)
        assert isinstance(metadata, dict)

    def test_execute(self):
        """测试 execute 方法."""
        agent = DecisionChainGeneratorAgent()
        message = BaseMessage(
            message_type=MessageType.USER_REQUEST,
            sender="User",
            receiver="DecisionChainGenerator",
            content={
                "input": "三峡大坝需要将出库流量调整到19000立方米每秒",
                "input_type": "natural_language",
            },
        )

        response = agent.execute(message)
        assert response.message_type == MessageType.TASK_ASSIGN
        assert response.receiver == "NodeSchedulerAgent"
        assert "task_graph" in response.content
        assert "metadata" in response.content

    def test_generate_chain_with_alternatives(self):
        """测试生成链并返回备选方案."""
        agent = DecisionChainGeneratorAgent()
        task_graph, alternatives, metadata = agent.generate_chain_with_alternatives(
            user_input="三峡大坝需要将出库流量调整到19000立方米每秒",
            input_type="natural_language",
            num_alternatives=3,
        )

        assert isinstance(task_graph, TaskGraph)
        assert isinstance(alternatives, list)
        assert len(alternatives) <= 3
        assert isinstance(metadata, dict)


class TestDecisionPipeline:
    """测试决策流程管道."""

    def test_init(self):
        """测试初始化."""
        pipeline = DecisionPipeline()
        assert pipeline.chain_generator is not None
        assert pipeline.node_scheduler is None

    def test_execute_without_scheduler(self):
        """测试执行（无调度器）."""
        pipeline = DecisionPipeline()
        result = pipeline.execute(
            user_input="三峡大坝需要将出库流量调整到19000立方米每秒",
            input_type="natural_language",
        )

        assert "task_graph" in result
        assert "generation_metadata" in result
        assert "execution_result" in result
        assert result["execution_result"] is None


class TestIntegration:
    """集成测试."""

    def test_full_flow_flood_dispatch(self):
        """测试完整流程 - 洪水调度."""
        agent = DecisionChainGeneratorAgent()

        # 自然语言输入
        task_graph, metadata = agent.generate_chain(
            user_input="三峡大坝需要将出库流量调整到19000立方米每秒，速率不超过500",
            input_type="natural_language",
        )

        # 验证生成的图
        nodes = task_graph.get_all_nodes()
        assert len(nodes) > 0

        # 验证元数据
        assert metadata["intent"]["task_type"] is not None
        assert metadata["decomposition"]["node_count"] > 0
        assert 0.0 <= metadata["optimization"]["reliability_score"] <= 1.0

        # 验证图可以拓扑排序
        sorted_ids = task_graph.topological_sort()
        assert len(sorted_ids) == len(nodes)

    def test_full_flow_drought_dispatch(self):
        """测试完整流程 - 干旱调度."""
        agent = DecisionChainGeneratorAgent()

        task_graph, metadata = agent.generate_chain(
            user_input="干旱期需要增加蓄水量到175米",
            input_type="natural_language",
        )

        nodes = task_graph.get_all_nodes()
        assert len(nodes) > 0

    def test_chain_reliability_threshold(self):
        """测试链可靠性阈值."""
        agent = DecisionChainGeneratorAgent()

        task_graph, metadata = agent.generate_chain(
            user_input="调整出库流量到19000立方米每秒",
            input_type="natural_language",
        )

        reliability = metadata["optimization"]["reliability_score"]
        # 可靠性应该在合理范围内
        assert 0.0 <= reliability <= 1.0
        # 对于有效的调度任务，可靠性应该不太低
        assert reliability >= 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
