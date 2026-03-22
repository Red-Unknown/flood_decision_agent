"""NodeSchedulerAgent 演示脚本

演示场景：
1. 场景1: 线性依赖执行 (N1→N2→N3)
2. 场景2: 并行节点执行 (N1→N2,N3)
3. 场景3: 复杂依赖图 (北江洪水调度简化版)
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 检查 KIMI_API_KEY
if not os.environ.get("KIMI_API_KEY"):
    print("需要kimi_api_key")
    sys.exit(1)

# 添加src到路径
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent
from flood_decision_agent.agents.unit_task_executor import UnitTaskExecutionAgent
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import Node, TaskGraph
from flood_decision_agent.tools.registry import ToolMetadata, register_tool


# ============================================================================
# 注册演示用的业务工具
# ============================================================================

@register_tool(ToolMetadata(
    name="get_rainfall_data",
    description="获取降雨数据",
    task_types={"data_query"},
    priority=10,
    output_keys={"rainfall_data"}
))
def get_rainfall_data(data_pool, config):
    """获取降雨数据"""
    location = config.get("location", "北江流域")
    return {
        "rainfall_data": {
            "location": location,
            "24h_rainfall": 85.5,
            "unit": "mm",
            "timestamp": datetime.now().isoformat()
        }
    }


@register_tool(ToolMetadata(
    name="calculate_inflow",
    description="计算入库流量",
    task_types={"hydrological_model"},
    priority=10,
    required_keys={"rainfall_data"},
    output_keys={"inflow_forecast"}
))
def calculate_inflow(data_pool, config):
    """根据降雨计算入库流量"""
    rainfall = data_pool.get("rainfall_data", {})
    rainfall_mm = rainfall.get("24h_rainfall", 0)

    # 简化模型：降雨转流量
    catchment_area = config.get("catchment_area", 5000)  # km²
    runoff_coefficient = 0.7
    inflow = rainfall_mm * catchment_area * runoff_coefficient / 86.4  # m³/s

    return {
        "inflow_forecast": {
            "peak_flow": round(inflow, 2),
            "unit": "m³/s",
            "catchment_area": catchment_area,
            "calculation_time": datetime.now().isoformat()
        }
    }


@register_tool(ToolMetadata(
    name="generate_dispatch_plan",
    description="生成水库调度方案",
    task_types={"reservoir_dispatch"},
    priority=10,
    required_keys={"inflow_forecast"},
    output_keys={"dispatch_plan"}
))
def generate_dispatch_plan(data_pool, config):
    """生成调度方案"""
    inflow = data_pool.get("inflow_forecast", {})
    peak_flow = inflow.get("peak_flow", 0)

    reservoir = config.get("reservoir", "飞来峡")
    limit_flow = config.get("limit_flow", 19000)

    if peak_flow > limit_flow:
        plan = {
            "action": "预泄",
            "reason": f"预报入库流量{peak_flow} m³/s超过限制{limit_flow} m³/s",
            "target_outflow": limit_flow,
            "start_time": "立即执行"
        }
    else:
        plan = {
            "action": "维持",
            "reason": f"预报入库流量{peak_flow} m³/s在安全范围内",
            "target_outflow": "按正常调度",
            "start_time": "无需调整"
        }

    return {
        "dispatch_plan": {
            "reservoir": reservoir,
            "plan": plan,
            "generated_at": datetime.now().isoformat()
        }
    }


@register_tool(ToolMetadata(
    name="validate_data",
    description="数据验证工具",
    task_types={"validation"},
    priority=10,
    output_keys={"validation_result"}
))
def validate_data(data_pool, config):
    """验证数据完整性"""
    return {
        "validation_result": {
            "status": "passed",
            "checked_at": datetime.now().isoformat()
        }
    }


@register_tool(ToolMetadata(
    name="log_execution",
    description="执行日志记录",
    task_types={"logging"},
    priority=10,
    output_keys={"log_entry"}
))
def log_execution(data_pool, config):
    """记录执行日志"""
    return {
        "log_entry": {
            "level": "INFO",
            "message": config.get("message", "执行完成"),
            "timestamp": datetime.now().isoformat()
        }
    }


# ============================================================================
# 演示场景
# ============================================================================

def demo_linear_dependency():
    """场景1: 线性依赖执行 (N1→N2→N3)

    展示顺序执行流程：
    - N1: 获取降雨数据
    - N2: 计算入库流量 (依赖N1)
    - N3: 生成调度方案 (依赖N2)
    """
    print("\n" + "=" * 70)
    print("场景1: 线性依赖执行 (N1→N2→N3)")
    print("=" * 70)
    print("执行流程: 获取降雨数据 → 计算入库流量 → 生成调度方案")
    print("-" * 70)

    start_time = time.time()

    # 创建任务图
    graph = TaskGraph()

    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=[],
        output_keys=["rainfall_data"],
        tool_candidates=[{"name": "get_rainfall_data", "priority": 10}],
    )
    node2 = Node(
        node_id="N2",
        task_type="hydrological_model",
        dependencies=["N1"],
        output_keys=["inflow_forecast"],
        tool_candidates=[{"name": "calculate_inflow", "priority": 10}],
    )
    node3 = Node(
        node_id="N3",
        task_type="reservoir_dispatch",
        dependencies=["N2"],
        output_keys=["dispatch_plan"],
        tool_candidates=[{"name": "generate_dispatch_plan", "priority": 10}],
    )

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    # 创建数据池和调度器
    data_pool = SharedDataPool()
    scheduler = NodeSchedulerAgent(agent_id="LinearScheduler")

    # 执行任务图
    result = scheduler.execute_task_graph(graph, data_pool)

    elapsed_time = time.time() - start_time

    # 输出结果
    print(f"\n执行结果:")
    print(f"  状态: {result['status']}")
    print(f"  成功节点: {result['completed_count']}个")
    print(f"  失败节点: {result['failed_count']}个")
    print(f"  执行顺序: {' → '.join(result['completed_nodes'])}")
    print(f"  总耗时: {elapsed_time:.2f}秒")

    # 输出数据池内容
    print(f"\n数据池内容:")
    for key in data_pool.keys():
        value = data_pool.get(key)
        print(f"  {key}: {value}")

    return result


def demo_parallel_execution():
    """场景2: 并行节点执行 (N1→N2,N3)

    展示N2和N3在N1完成后并行执行：
    - N1: 获取降雨数据
    - N2: 数据验证 (依赖N1)
    - N3: 日志记录 (依赖N1)
    """
    print("\n" + "=" * 70)
    print("场景2: 并行节点执行 (N1→N2,N3)")
    print("=" * 70)
    print("执行流程: 获取降雨数据 → [数据验证 || 日志记录] (并行)")
    print("-" * 70)

    start_time = time.time()

    # 创建任务图
    graph = TaskGraph()

    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=[],
        output_keys=["rainfall_data"],
        tool_candidates=[{"name": "get_rainfall_data", "priority": 10}],
    )
    node2 = Node(
        node_id="N2",
        task_type="validation",
        dependencies=["N1"],
        output_keys=["validation_result"],
        tool_candidates=[{"name": "validate_data", "priority": 10}],
    )
    node3 = Node(
        node_id="N3",
        task_type="logging",
        dependencies=["N1"],
        output_keys=["log_entry"],
        tool_candidates=[{"name": "log_execution", "priority": 10}],
    )

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    # 创建数据池和调度器
    data_pool = SharedDataPool()
    scheduler = NodeSchedulerAgent(agent_id="ParallelScheduler")

    # 执行任务图
    result = scheduler.execute_task_graph(graph, data_pool)

    elapsed_time = time.time() - start_time

    # 输出结果
    print(f"\n执行结果:")
    print(f"  状态: {result['status']}")
    print(f"  成功节点: {result['completed_count']}个")
    print(f"  失败节点: {result['failed_count']}个")
    print(f"  执行顺序: {' → '.join(result['completed_nodes'])}")
    print(f"  总耗时: {elapsed_time:.2f}秒")

    # 输出数据池内容
    print(f"\n数据池内容:")
    for key in data_pool.keys():
        value = data_pool.get(key)
        print(f"  {key}: {value}")

    return result


def demo_complex_flood_dispatch():
    """场景3: 复杂依赖图 (北江洪水调度简化版)

    展示完整调度流程：
    - N1: 获取降雨数据
    - N2: 计算入库流量 (依赖N1)
    - N3: 生成调度方案 (依赖N2)
    - N4: 数据验证 (依赖N1)
    - N5: 日志记录 (依赖N3, N4)

    依赖关系:
        N1 → N2 → N3 → N5
         ↓         ↑
        N4 ────────┘
    """
    print("\n" + "=" * 70)
    print("场景3: 复杂依赖图 (北江洪水调度简化版)")
    print("=" * 70)
    print("执行流程:")
    print("  N1(获取降雨) → N2(计算流量) → N3(生成方案) → N5(日志)")
    print("       ↓                        ↑")
    print("      N4(验证) ─────────────────┘")
    print("-" * 70)

    start_time = time.time()

    # 创建任务图
    graph = TaskGraph()

    node1 = Node(
        node_id="N1",
        task_type="data_query",
        dependencies=[],
        output_keys=["rainfall_data"],
        tool_candidates=[{"name": "get_rainfall_data", "priority": 10}],
    )
    node2 = Node(
        node_id="N2",
        task_type="hydrological_model",
        dependencies=["N1"],
        output_keys=["inflow_forecast"],
        tool_candidates=[{"name": "calculate_inflow", "priority": 10}],
    )
    node3 = Node(
        node_id="N3",
        task_type="reservoir_dispatch",
        dependencies=["N2"],
        output_keys=["dispatch_plan"],
        tool_candidates=[{"name": "generate_dispatch_plan", "priority": 10}],
    )
    node4 = Node(
        node_id="N4",
        task_type="validation",
        dependencies=["N1"],
        output_keys=["validation_result"],
        tool_candidates=[{"name": "validate_data", "priority": 10}],
    )
    node5 = Node(
        node_id="N5",
        task_type="logging",
        dependencies=["N3", "N4"],
        output_keys=["log_entry"],
        tool_candidates=[{"name": "log_execution", "priority": 10}],
    )

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_node(node5)

    # 创建数据池和调度器
    data_pool = SharedDataPool()
    scheduler = NodeSchedulerAgent(agent_id="FloodDispatchScheduler")

    # 执行任务图
    result = scheduler.execute_task_graph(graph, data_pool)

    elapsed_time = time.time() - start_time

    # 输出结果
    print(f"\n执行结果:")
    print(f"  状态: {result['status']}")
    print(f"  成功节点: {result['completed_count']}个")
    print(f"  失败节点: {result['failed_count']}个")
    print(f"  执行顺序: {' → '.join(result['completed_nodes'])}")
    print(f"  总迭代次数: {result['metrics']['iteration_count']}")
    print(f"  总耗时: {elapsed_time:.2f}秒")

    # 输出各节点执行详情
    print(f"\n各节点执行详情:")
    for node_id, node_result in result['results'].items():
        status = node_result.get('status', 'unknown')
        status_icon = "✓" if status == "success" else "✗"
        print(f"  {status_icon} {node_id}: {status}")
        if 'metrics' in node_result:
            retry_count = node_result['metrics'].get('retry_count', 0)
            if retry_count > 0:
                print(f"      重试次数: {retry_count}")

    # 输出数据池内容
    print(f"\n数据池内容:")
    for key in sorted(data_pool.keys()):
        value = data_pool.get(key)
        print(f"  {key}:")
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"    {value}")

    return result


def demo_execution_strategy():
    """场景4: 执行策略演示

    展示不同任务类型对应的执行策略：
    - compute类型: parallel策略
    - reservoir_dispatch类型: fallback策略
    - data_query类型: single策略
    """
    print("\n" + "=" * 70)
    print("场景4: 执行策略演示")
    print("=" * 70)
    print("展示不同任务类型对应的执行策略")
    print("-" * 70)

    scheduler = NodeSchedulerAgent(agent_id="StrategyDemo")

    # 测试不同任务类型的策略生成
    test_cases = [
        ("compute", 3, "parallel"),
        ("reservoir_dispatch", 3, "fallback"),
        ("data_query", 1, "single"),
        ("flood_warning", 2, "fallback"),
        ("statistics", 2, "parallel"),
        ("unknown_type", 2, "parallel"),  # 默认策略
    ]

    print("\n策略生成测试:")
    for task_type, tool_count, expected in test_cases:
        node = Node(node_id="test", task_type=task_type)
        strategy = scheduler.generate_execution_strategy(node, tool_count)
        match = "✓" if strategy == expected else "✗"
        print(f"  {match} {task_type} (工具数={tool_count}): {strategy} (期望: {expected})")


def main():
    """主函数"""
    print("=" * 70)
    print("NodeSchedulerAgent 演示脚本")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 运行所有演示场景
        demo_linear_dependency()
        demo_parallel_execution()
        demo_complex_flood_dispatch()
        demo_execution_strategy()

        print("\n" + "=" * 70)
        print("所有演示完成!")
        print("=" * 70)
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"\n演示出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
