"""NodeSchedulerAgent 单元测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent
from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import Node, NodeStatus, TaskGraph
from flood_decision_agent.tools.registry import ToolMetadata, get_tool_registry


@pytest.fixture
def scheduler_agent():
    """创建测试用的NodeSchedulerAgent实例"""
    return NodeSchedulerAgent(
        agent_id="TestScheduler",
        max_retries=2,
        base_retry_delay=0.1,
    )


@pytest.fixture
def mock_executor():
    """创建Mock的UnitTaskExecutionAgent"""
    executor = Mock(spec=UnitTaskExecutionAgent)
    executor.execute_task.return_value = {
        "status": "success",
        "output": {"test_result": "success"},
        "metrics": {"elapsed_time_ms": 100},
    }
    return executor


@pytest.fixture
def data_pool():
    """创建测试用的数据池"""
    pool = SharedDataPool()
    pool.set("test_key", "test_value")
    return pool


@pytest.fixture
def sample_task_graph():
    """创建示例任务图"""
    graph = TaskGraph()

    # 创建节点
    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=[],
        output_keys=["data1"],
    )
    node2 = Node(
        node_id="N2",
        task_type="compute",
        dependencies=["N1"],
        output_keys=["data2"],
    )
    node3 = Node(
        node_id="N3",
        task_type="analysis",
        dependencies=["N2"],
        output_keys=["data3"],
    )

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    return graph


@pytest.fixture
def parallel_task_graph():
    """创建并行任务图 (N1 -> N2, N3)"""
    graph = TaskGraph()

    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=[],
        output_keys=["data1"],
    )
    node2 = Node(
        node_id="N2",
        task_type="compute",
        dependencies=["N1"],
        output_keys=["data2"],
    )
    node3 = Node(
        node_id="N3",
        task_type="compute",
        dependencies=["N1"],
        output_keys=["data3"],
    )

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    return graph


class TestTaskGraph:
    """TaskGraph功能测试"""

    def test_topological_sort(self, sample_task_graph):
        """测试拓扑排序"""
        sorted_nodes = sample_task_graph.topological_sort()

        # 验证排序结果
        assert len(sorted_nodes) == 3
        assert sorted_nodes[0] == "N1"  # N1没有依赖，应该排在最前面
        assert sorted_nodes[1] == "N2"  # N2依赖N1
        assert sorted_nodes[2] == "N3"  # N3依赖N2

    def test_topological_sort_circular_dependency(self):
        """测试循环依赖检测"""
        graph = TaskGraph()

        node1 = Node(node_id="N1", task_type="test", dependencies=["N3"])
        node2 = Node(node_id="N2", task_type="test", dependencies=["N1"])
        node3 = Node(node_id="N3", task_type="test", dependencies=["N2"])

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)

        with pytest.raises(ValueError, match="循环依赖"):
            graph.topological_sort()

    def test_get_ready_nodes(self, sample_task_graph):
        """测试获取可执行节点"""
        # 初始状态，只有N1没有依赖
        ready_nodes = sample_task_graph.get_ready_nodes()
        assert "N1" in ready_nodes
        assert "N2" not in ready_nodes
        assert "N3" not in ready_nodes

        # 将N1标记为完成
        sample_task_graph.update_node_status("N1", NodeStatus.COMPLETED)

        # 现在N2应该可以执行
        ready_nodes = sample_task_graph.get_ready_nodes()
        assert "N2" in ready_nodes
        assert "N3" not in ready_nodes

        # 将N2标记为完成
        sample_task_graph.update_node_status("N2", NodeStatus.COMPLETED)

        # 现在N3应该可以执行
        ready_nodes = sample_task_graph.get_ready_nodes()
        assert "N3" in ready_nodes

    def test_add_node_and_edge(self):
        """测试添加节点和边"""
        graph = TaskGraph()

        node1 = Node(node_id="N1", task_type="test", dependencies=[])
        node2 = Node(node_id="N2", task_type="test", dependencies=["N1"])

        graph.add_node(node1)
        graph.add_node(node2)

        assert graph.get_node("N1") is not None
        assert graph.get_node("N2") is not None
        assert graph.get_dependencies("N2") == ["N1"]

    def test_add_duplicate_node_raises_error(self):
        """测试添加重复节点时抛出错误"""
        graph = TaskGraph()
        node1 = Node(node_id="N1", task_type="test")
        node1_dup = Node(node_id="N1", task_type="test2")

        graph.add_node(node1)

        with pytest.raises(ValueError, match="节点ID已存在"):
            graph.add_node(node1_dup)


class TestNodeSchedulerAgent:
    """NodeSchedulerAgent功能测试"""

    def test_check_dependencies_satisfied(self, scheduler_agent, sample_task_graph):
        """测试依赖检查 - 依赖已满足"""
        # 将N1标记为完成
        sample_task_graph.update_node_status("N1", NodeStatus.COMPLETED)

        is_satisfied, missing_deps = scheduler_agent.check_dependencies("N2", sample_task_graph)

        assert is_satisfied is True
        assert len(missing_deps) == 0

    def test_check_dependencies_not_satisfied(self, scheduler_agent, sample_task_graph):
        """测试依赖检查 - 依赖未满足"""
        is_satisfied, missing_deps = scheduler_agent.check_dependencies("N2", sample_task_graph)

        assert is_satisfied is False
        assert "N1" in missing_deps

    def test_check_dependencies_nonexistent_node(self, scheduler_agent, sample_task_graph):
        """测试依赖检查 - 节点不存在"""
        with pytest.raises(ValueError, match="节点不存在"):
            scheduler_agent.check_dependencies("NONEXISTENT", sample_task_graph)

    def test_fetch_predecessor_results(self, scheduler_agent, sample_task_graph, data_pool):
        """测试结果获取"""
        # 设置前置节点的输出数据
        data_pool.set("data1", {"value": 100})
        sample_task_graph.update_node_status("N1", NodeStatus.COMPLETED)

        results = scheduler_agent.fetch_predecessor_results("N2", data_pool, sample_task_graph)

        assert "data1" in results
        assert results["data1"]["value"] == 100

    def test_fetch_predecessor_results_no_dependencies(self, scheduler_agent, sample_task_graph, data_pool):
        """测试结果获取 - 无依赖节点"""
        results = scheduler_agent.fetch_predecessor_results("N1", data_pool, sample_task_graph)

        assert len(results) == 0

    def test_build_tool_candidates(self, scheduler_agent):
        """测试工具候选集构建"""
        # 注册测试工具
        registry = get_tool_registry()

        @registry.register(
            ToolMetadata(
                name="test_tool_1",
                description="测试工具1",
                task_types={"test_type"},
                priority=10,
                required_keys={"input1"},
                output_keys={"output1"},
            )
        )
        def test_tool_1(data_pool, config):
            return {"output1": "result"}

        candidates = scheduler_agent.build_tool_candidates("test_type")

        # 验证候选列表包含测试工具
        tool_names = [c["name"] for c in candidates]
        assert "test_tool_1" in tool_names

        # 验证工具信息完整
        test_tool = next(c for c in candidates if c["name"] == "test_tool_1")
        assert test_tool["priority"] == 10
        assert "input1" in test_tool["required_keys"]
        assert "output1" in test_tool["output_keys"]

    def test_generate_execution_strategy_single(self, scheduler_agent):
        """测试策略生成 - 单工具"""
        node = Node(node_id="N1", task_type="compute")

        strategy = scheduler_agent.generate_execution_strategy(node, 1)

        assert strategy == "single"

    def test_generate_execution_strategy_parallel(self, scheduler_agent):
        """测试策略生成 - 并行策略"""
        node = Node(node_id="N1", task_type="compute")

        strategy = scheduler_agent.generate_execution_strategy(node, 3)

        assert strategy == "parallel"

    def test_generate_execution_strategy_fallback(self, scheduler_agent):
        """测试策略生成 - 降级策略"""
        node = Node(node_id="N1", task_type="reservoir_dispatch")

        strategy = scheduler_agent.generate_execution_strategy(node, 3)

        assert strategy == "fallback"

    def test_generate_execution_strategy_auto(self, scheduler_agent):
        """测试策略生成 - 无工具时返回auto"""
        node = Node(node_id="N1", task_type="compute")

        strategy = scheduler_agent.generate_execution_strategy(node, 0)

        assert strategy == "auto"

    @patch.object(NodeSchedulerAgent, "_is_retryable_error")
    def test_execute_node_success(self, mock_is_retryable, scheduler_agent, data_pool):
        """测试单节点执行 - 成功"""
        mock_is_retryable.return_value = True

        # 使用mock executor
        mock_exec = Mock(spec=UnitTaskExecutionAgent)
        mock_exec.execute_task.return_value = {
            "status": "success",
            "output": {"result": "success"},
            "metrics": {"elapsed_time_ms": 100},
        }
        scheduler_agent.executor = mock_exec

        node = Node(
            node_id="N1",
            task_type="data_query",
            tool_candidates=[{"name": "test_tool", "priority": 1}],
        )

        result = scheduler_agent.execute_node(node, data_pool)

        assert result["status"] == "success"
        assert result["node_id"] == "N1"
        assert node.status == NodeStatus.COMPLETED
        mock_exec.execute_task.assert_called_once()

    @patch.object(NodeSchedulerAgent, "_is_retryable_error")
    def test_execute_node_failure(self, mock_is_retryable, scheduler_agent, data_pool):
        """测试单节点执行 - 失败"""
        mock_is_retryable.return_value = False  # 不可重试

        # 使用mock executor，抛出异常
        mock_exec = Mock(spec=UnitTaskExecutionAgent)
        mock_exec.execute_task.side_effect = Exception("执行失败")
        scheduler_agent.executor = mock_exec

        node = Node(
            node_id="N1",
            task_type="data_query",
            tool_candidates=[{"name": "test_tool", "priority": 1}],
        )

        result = scheduler_agent.execute_node(node, data_pool)

        assert result["status"] == "failed"
        assert result["node_id"] == "N1"
        assert "执行失败" in result["error"]
        assert node.status == NodeStatus.FAILED

    def test_is_retryable_error(self, scheduler_agent):
        """测试可重试错误判断"""
        # 可重试错误
        assert scheduler_agent._is_retryable_error(Exception("Connection timeout")) is True
        assert scheduler_agent._is_retryable_error(Exception("Network error")) is True
        assert scheduler_agent._is_retryable_error(Exception("Service unavailable")) is True

        # 不可重试错误
        assert scheduler_agent._is_retryable_error(ValueError("Invalid input")) is False
        assert scheduler_agent._is_retryable_error(KeyError("key not found")) is False
        assert scheduler_agent._is_retryable_error(Exception("Unauthorized")) is False

    def test_calculate_retry_delay(self, scheduler_agent):
        """测试重试延迟计算"""
        delay1 = scheduler_agent._calculate_retry_delay(1)
        delay2 = scheduler_agent._calculate_retry_delay(2)
        delay3 = scheduler_agent._calculate_retry_delay(3)

        # 验证指数退避
        assert delay1 >= 0.1
        assert delay2 > delay1
        assert delay3 > delay2

        # 验证有随机抖动
        delays = [scheduler_agent._calculate_retry_delay(1) for _ in range(10)]
        assert len(set(delays)) > 1  # 应该有变化


class TestIntegration:
    """集成测试"""

    @patch.object(NodeSchedulerAgent, "execute_node")
    def test_execute_task_graph_linear(self, mock_execute_node, scheduler_agent, sample_task_graph, data_pool):
        """测试线性依赖图执行 (N1->N2->N3)"""
        # Mock execute_node返回成功
        mock_execute_node.return_value = {
            "status": "success",
            "output": {"data": "test"},
            "metrics": {"elapsed_time_ms": 100},
        }

        result = scheduler_agent.execute_task_graph(sample_task_graph, data_pool)

        assert result["status"] == "success"
        assert len(result["completed_nodes"]) == 3
        assert "N1" in result["completed_nodes"]
        assert "N2" in result["completed_nodes"]
        assert "N3" in result["completed_nodes"]
        assert result["failed_count"] == 0

        # 验证execute_node被调用了3次
        assert mock_execute_node.call_count == 3

    @patch.object(NodeSchedulerAgent, "execute_node")
    def test_execute_task_graph_parallel(self, mock_execute_node, scheduler_agent, parallel_task_graph, data_pool):
        """测试并行节点执行 (N1->N2,N3)"""
        # Mock execute_node返回成功
        mock_execute_node.return_value = {
            "status": "success",
            "output": {"data": "test"},
            "metrics": {"elapsed_time_ms": 100},
        }

        result = scheduler_agent.execute_task_graph(parallel_task_graph, data_pool)

        assert result["status"] == "success"
        assert len(result["completed_nodes"]) == 3
        assert "N2" in result["completed_nodes"]
        assert "N3" in result["completed_nodes"]

        # 验证execute_node被调用了3次
        assert mock_execute_node.call_count == 3

    @patch.object(NodeSchedulerAgent, "execute_node")
    def test_execute_task_graph_complex(self, mock_execute_node, scheduler_agent, data_pool):
        """测试复杂依赖图执行"""
        # 创建复杂依赖图
        # N1 -> N2 -> N4
        # N1 -> N3 -> N4
        graph = TaskGraph()

        node1 = Node(node_id="N1", task_type="data_query", dependencies=[], output_keys=["data1"])
        node2 = Node(node_id="N2", task_type="compute", dependencies=["N1"], output_keys=["data2"])
        node3 = Node(node_id="N3", task_type="compute", dependencies=["N1"], output_keys=["data3"])
        node4 = Node(node_id="N4", task_type="analysis", dependencies=["N2", "N3"], output_keys=["data4"])

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        graph.add_node(node4)

        # Mock execute_node返回成功
        mock_execute_node.return_value = {
            "status": "success",
            "output": {"data": "test"},
            "metrics": {"elapsed_time_ms": 100},
        }

        result = scheduler_agent.execute_task_graph(graph, data_pool)

        assert result["status"] == "success"
        assert len(result["completed_nodes"]) == 4
        assert "N4" in result["completed_nodes"]

    @patch.object(NodeSchedulerAgent, "execute_node")
    def test_execute_task_graph_partial_failure(self, mock_execute_node, scheduler_agent, sample_task_graph, data_pool):
        """测试部分节点失败的场景"""
        # 第一次调用成功，第二次失败，第三次成功
        mock_execute_node.side_effect = [
            {"status": "success", "output": {}, "metrics": {}},
            {"status": "failed", "output": {}, "error": "执行失败", "metrics": {}},
            {"status": "success", "output": {}, "metrics": {}},
        ]

        result = scheduler_agent.execute_task_graph(sample_task_graph, data_pool)

        assert result["status"] == "partial_failed"
        assert len(result["completed_nodes"]) == 2  # N1和N3成功
        assert len(result["failed_nodes"]) == 1  # N2失败
        assert "N2" in result["failed_nodes"]

    @patch.object(NodeSchedulerAgent, "execute_node")
    def test_execute_task_graph_all_failure(self, mock_execute_node, scheduler_agent, sample_task_graph, data_pool):
        """测试全部节点失败的场景"""
        mock_execute_node.return_value = {
            "status": "failed",
            "output": {},
            "error": "执行失败",
            "metrics": {},
        }

        result = scheduler_agent.execute_task_graph(sample_task_graph, data_pool)

        # N1失败后，N2和N3无法执行（依赖不满足）
        assert result["status"] in ["failed", "partial_failed"]


class TestMessageProcessing:
    """测试消息处理"""

    @patch.object(NodeSchedulerAgent, "execute_task_graph")
    def test_process_graph_message(self, mock_execute_graph, scheduler_agent, sample_task_graph, data_pool):
        """测试处理任务图执行消息"""
        mock_execute_graph.return_value = {"status": "success"}

        message = BaseMessage(
            type=MessageType.NODE_RESULT,
            payload={"graph": sample_task_graph, "data_pool": data_pool},
            sender="test",
        )

        result = scheduler_agent.execute(message)

        assert result["status"] == "success"
        mock_execute_graph.assert_called_once_with(sample_task_graph, data_pool)

    @patch.object(NodeSchedulerAgent, "execute_node")
    def test_process_node_message(self, mock_execute_node, scheduler_agent, data_pool):
        """测试处理单节点执行消息"""
        mock_execute_node.return_value = {"status": "success"}

        node = Node(node_id="N1", task_type="test")

        message = BaseMessage(
            type=MessageType.NODE_RESULT,
            payload={"node": node, "data_pool": data_pool},
            sender="test",
        )

        result = scheduler_agent.execute(message)

        assert result["status"] == "success"
        mock_execute_node.assert_called_once_with(node, data_pool)

    def test_process_invalid_message(self, scheduler_agent):
        """测试处理无效消息"""
        message = BaseMessage(
            type=MessageType.NODE_RESULT,
            payload={"invalid": "payload"},
            sender="test",
        )

        with pytest.raises(ValueError, match="payload"):
            scheduler_agent.execute(message)


class TestRunMethod:
    """测试run方法"""

    @patch.object(NodeSchedulerAgent, "execute_task_graph")
    def test_run_method(self, mock_execute_graph, scheduler_agent, sample_task_graph, data_pool):
        """测试run兼容性方法"""
        mock_execute_graph.return_value = {"status": "success"}

        result = scheduler_agent.run(sample_task_graph, data_pool)

        assert result["status"] == "success"
        mock_execute_graph.assert_called_once_with(sample_task_graph, data_pool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
