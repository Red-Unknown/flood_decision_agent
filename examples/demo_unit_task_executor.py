"""UnitTaskExecutionAgent 演示示例"""

import os
import sys

# 检查 KIMI_API_KEY
if not os.environ.get("KIMI_API_KEY"):
    print("需要kimi_api_key")
    sys.exit(1)

from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.tools.registry import ToolMetadata, register_tool


# 注册一些业务特定的工具
@register_tool(ToolMetadata(
    name="rainfall_predictor",
    description="降雨预测模型",
    task_types={"hydrological_model"},
    priority=10,
    output_keys={"rainfall_forecast"}
))
def rainfall_predictor(data_pool, config):
    """模拟降雨预测"""
    return {
        "rainfall_forecast": {
            "location": config.get("location", "北江流域"),
            "next_24h": 50.5,
            "unit": "mm"
        }
    }


@register_tool(ToolMetadata(
    name="inflow_calculator",
    description="入库流量计算",
    task_types={"hydrological_model"},
    priority=20,
    output_keys={"inflow_forecast"}
))
def inflow_calculator(data_pool, config):
    """模拟入库流量计算"""
    rainfall = data_pool.get("rainfall_forecast", {})
    rainfall_mm = rainfall.get("next_24h", 0)
    
    # 简单计算：降雨转流量
    inflow = rainfall_mm * 10  # 简化模型
    
    return {
        "inflow_forecast": {
            "peak_flow": inflow,
            "unit": "m3/s"
        }
    }


def demo_upstream_specified_tools():
    """演示：上游指定工具"""
    print("\n" + "="*60)
    print("演示1: 上游指定工具")
    print("="*60)
    
    agent = UnitTaskExecutionAgent(agent_id="DemoExecutor1")
    data_pool = SharedDataPool()
    
    # 上游指定工具
    upstream_tools = [
        {"tool_name": "rainfall_predictor", "tool_config": {"location": "飞来峡"}, "priority": 1}
    ]
    
    result = agent.execute_task(
        node_id="N1",
        task_type="hydrological_model",
        data_pool=data_pool,
        tools=upstream_tools,
        execution_strategy="single",
    )
    
    print(f"执行结果: {result}")


def demo_auto_select_tools():
    """演示：自主选用工具"""
    print("\n" + "="*60)
    print("演示2: 自主选用工具（上游未指定）")
    print("="*60)
    
    agent = UnitTaskExecutionAgent(agent_id="DemoExecutor2")
    data_pool = SharedDataPool()
    
    # 上游未指定工具，Agent自主选用
    result = agent.execute_task(
        node_id="N2",
        task_type="data_query",  # 会匹配到常用工具库中的工具
        data_pool=data_pool,
        tools=[],  # 空列表
        execution_strategy="auto",
    )
    
    print(f"执行结果: {result}")


def demo_parallel_execution():
    """演示：并行执行多个工具"""
    print("\n" + "="*60)
    print("演示3: 并行执行多个工具")
    print("="*60)
    
    agent = UnitTaskExecutionAgent(agent_id="DemoExecutor3")
    data_pool = SharedDataPool()
    
    # 先放入一些数据
    data_pool.set("test_data", {"value": 100, "name": "测试数据"})
    
    # 指定多个工具并行执行
    upstream_tools = [
        {"tool_name": "query_data_pool", "tool_config": {"key": "test_data"}, "priority": 1},
        {"tool_name": "get_current_time", "tool_config": {}, "priority": 2},
    ]
    
    result = agent.execute_task(
        node_id="N3",
        task_type="data_query",
        data_pool=data_pool,
        tools=upstream_tools,
        execution_strategy="parallel",
    )
    
    print(f"执行结果: {result}")


def demo_fallback_strategy():
    """演示：降级策略"""
    print("\n" + "="*60)
    print("演示4: 降级策略（fallback）")
    print("="*60)
    
    agent = UnitTaskExecutionAgent(agent_id="DemoExecutor4")
    data_pool = SharedDataPool()
    
    # 指定多个工具，按优先级尝试
    upstream_tools = [
        {"tool_name": "non_existent_tool", "tool_config": {}, "priority": 1},  # 不存在，会失败
        {"tool_name": "get_current_time", "tool_config": {}, "priority": 2},  # 会成功
    ]
    
    result = agent.execute_task(
        node_id="N4",
        task_type="time",
        data_pool=data_pool,
        tools=upstream_tools,
        execution_strategy="fallback",
    )
    
    print(f"执行结果: {result}")


def demo_list_tools():
    """演示：列出可用工具"""
    print("\n" + "="*60)
    print("演示5: 列出所有可用工具")
    print("="*60)
    
    agent = UnitTaskExecutionAgent(agent_id="DemoExecutor5")
    
    tools = agent.list_available_tools()
    print(f"可用工具总数: {len(tools)}")
    print("\n工具列表:")
    for tool_name in tools:
        info = agent.get_tool_info(tool_name)
        if info:
            print(f"  - {tool_name}: {info['description']}")
            print(f"    支持任务类型: {info['task_types']}")


def main():
    """主函数"""
    print("UnitTaskExecutionAgent 演示")
    print("="*60)
    
    try:
        demo_upstream_specified_tools()
        demo_auto_select_tools()
        demo_parallel_execution()
        demo_fallback_strategy()
        demo_list_tools()
        
        print("\n" + "="*60)
        print("所有演示完成!")
        print("="*60)
        
    except Exception as e:
        print(f"演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
