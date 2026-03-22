"""UnitTaskExecutionAgent 单元测试"""

import pytest
from unittest.mock import Mock, patch

from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.tools.registry import ToolMetadata, get_tool_registry


@pytest.fixture
def agent():
    """创建测试用的Agent实例"""
    return UnitTaskExecutionAgent(
        agent_id="TestExecutor",
        enable_common_tools=True,
    )


@pytest.fixture
def data_pool():
    """创建测试用的数据池"""
    pool = SharedDataPool()
    pool.set("test_key", "test_value")
    return pool


class TestToolSelection:
    """测试工具选择逻辑"""

    def test_upstream_specified_tools(self, agent, data_pool):
        """测试上游指定工具"""
        upstream_tools = [
            {"tool_name": "get_current_time", "tool_config": {}, "priority": 1}
        ]
        
        result = agent.execute_task(
            node_id="N1",
            task_type="time",
            data_pool=data_pool,
            tools=upstream_tools,
            execution_strategy="single",
        )
        
        assert result["status"] == "success"
        assert "get_current_time" in result["metrics"]["tools_used"]
        # 输出包装在 data 字段中
        assert "data" in result["output"]
        assert "current_time" in result["output"]["data"]

    def test_auto_select_tools(self, agent, data_pool):
        """测试自主选用工具"""
        result = agent.execute_task(
            node_id="N2",
            task_type="data_query",
            data_pool=data_pool,
            tools=[],  # 空列表，触发自主选用
            execution_strategy="auto",
        )
        
        assert result["status"] == "success"
        # 应该选用了 data_query 类型的工具
        assert len(result["metrics"]["tools_used"]) > 0

    def test_upstream_tool_not_available_fallback_to_auto(self, agent, data_pool):
        """测试上游指定工具不可用时回退到自主选用"""
        upstream_tools = [
            {"tool_name": "non_existent_tool", "tool_config": {}, "priority": 1}
        ]
        
        result = agent.execute_task(
            node_id="N3",
            task_type="data_query",
            data_pool=data_pool,
            tools=upstream_tools,
            execution_strategy="single",
        )
        
        assert result["status"] == "success"
        # 应该自主选用了其他工具
        assert len(result["metrics"]["tools_used"]) > 0

    def test_disable_auto_select_raises_error(self, agent, data_pool):
        """测试禁用自主选用时抛出错误"""
        upstream_tools = [
            {"tool_name": "non_existent_tool", "tool_config": {}, "priority": 1}
        ]
        
        with pytest.raises(ValueError, match="未找到适合任务类型"):
            agent.execute_task(
                node_id="N4",
                task_type="unknown_type",
                data_pool=data_pool,
                tools=upstream_tools,
                execution_strategy="single",
                context={"allow_auto_select": False},
            )


class TestExecutionStrategies:
    """测试执行策略"""

    def test_single_strategy(self, agent, data_pool):
        """测试单工具策略"""
        upstream_tools = [
            {"tool_name": "get_current_time", "tool_config": {}, "priority": 1}
        ]
        
        result = agent.execute_task(
            node_id="N1",
            task_type="time",
            data_pool=data_pool,
            tools=upstream_tools,
            execution_strategy="single",
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["execution_strategy"] == "single"
        assert result["metrics"]["tool_count"] == 1

    def test_parallel_strategy(self, agent, data_pool):
        """测试并行策略"""
        upstream_tools = [
            {"tool_name": "get_current_time", "tool_config": {}, "priority": 1},
            {"tool_name": "list_data_pool_keys", "tool_config": {}, "priority": 2},
        ]
        
        result = agent.execute_task(
            node_id="N1",
            task_type="data_query",
            data_pool=data_pool,
            tools=upstream_tools,
            execution_strategy="parallel",
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["execution_strategy"] == "parallel"
        assert result["metrics"]["tool_count"] == 2

    def test_fallback_strategy(self, agent, data_pool):
        """测试降级策略"""
        upstream_tools = [
            {"tool_name": "non_existent_tool", "tool_config": {}, "priority": 1},
            {"tool_name": "get_current_time", "tool_config": {}, "priority": 2},
        ]
        
        result = agent.execute_task(
            node_id="N1",
            task_type="time",
            data_pool=data_pool,
            tools=upstream_tools,
            execution_strategy="fallback",
        )
        
        assert result["status"] == "success"
        assert result["metrics"]["execution_strategy"] == "fallback"
        # 应该只使用了第二个工具（第一个失败了）
        assert "get_current_time" in result["metrics"]["tools_used"]

    def test_auto_strategy_single_tool(self, agent, data_pool):
        """测试auto策略（单工具情况）"""
        upstream_tools = [
            {"tool_name": "get_current_time", "tool_config": {}, "priority": 1}
        ]
        
        result = agent.execute_task(
            node_id="N1",
            task_type="time",
            data_pool=data_pool,
            tools=upstream_tools,
            execution_strategy="auto",
        )
        
        assert result["status"] == "success"
        # 只有一个工具时应该使用single策略
        assert result["metrics"]["execution_strategy"] == "single"

    def test_auto_strategy_parallel_friendly(self, agent, data_pool):
        """测试auto策略（适合并行的任务类型）"""
        upstream_tools = [
            {"tool_name": "simple_calculator", "tool_config": {"operation": "add", "a": 1, "b": 2}, "priority": 1},
            {"tool_name": "get_current_time", "tool_config": {}, "priority": 2},
        ]
        
        result = agent.execute_task(
            node_id="N1",
            task_type="compute",  # compute类型适合并行
            data_pool=data_pool,
            tools=upstream_tools,
            execution_strategy="auto",
        )
        
        assert result["status"] == "success"
        # compute类型应该使用parallel策略
        assert result["metrics"]["execution_strategy"] == "parallel"


class TestToolRegistry:
    """测试工具注册中心"""

    def test_list_available_tools(self, agent):
        """测试列出可用工具"""
        tools = agent.list_available_tools()
        assert len(tools) > 0
        # 应该包含常用工具
        assert "get_current_time" in tools
        assert "query_data_pool" in tools

    def test_get_tool_info(self, agent):
        """测试获取工具信息"""
        info = agent.get_tool_info("get_current_time")
        assert info is not None
        assert info["name"] == "get_current_time"
        assert "time" in info["task_types"]
        assert "description" in info

    def test_get_nonexistent_tool_info(self, agent):
        """测试获取不存在的工具信息"""
        info = agent.get_tool_info("non_existent_tool")
        assert info is None


class TestMessageProcessing:
    """测试消息处理"""

    def test_process_message(self, agent, data_pool):
        """测试处理消息"""
        message = BaseMessage(
            type=MessageType.NODE_EXECUTE,
            payload={
                "node_id": "N1",
                "task_type": "time",
                "tools": [{"tool_name": "get_current_time", "tool_config": {}}],
                "execution_strategy": "single",
                "data_pool": data_pool,
                "context": {},
            },
            sender="test",
        )
        
        result = agent.execute(message)
        
        assert result["status"] == "success"
        assert result["node_id"] == "N1"
        assert "metrics" in result

    def test_missing_data_pool_raises_error(self, agent):
        """测试缺少data_pool时抛出错误"""
        message = BaseMessage(
            type=MessageType.NODE_EXECUTE,
            payload={
                "node_id": "N1",
                "task_type": "time",
                "tools": [],
            },
            sender="test",
        )
        
        with pytest.raises(ValueError, match="data_pool"):
            agent.execute(message)


class TestMetrics:
    """测试性能指标"""

    def test_execution_metrics(self, agent, data_pool):
        """测试执行指标"""
        result = agent.execute_task(
            node_id="N1",
            task_type="time",
            data_pool=data_pool,
            tools=[{"tool_name": "get_current_time", "tool_config": {}}],
            execution_strategy="single",
        )
        
        metrics = result["metrics"]
        assert "elapsed_time_ms" in metrics
        assert "tools_used" in metrics
        assert "execution_strategy" in metrics
        assert "tool_count" in metrics
        
        # 验证耗时是合理的数值
        assert metrics["elapsed_time_ms"] >= 0
        assert metrics["tool_count"] == len(metrics["tools_used"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
