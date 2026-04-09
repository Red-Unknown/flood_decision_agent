"""HeuristicOptimizer 使用示例.

演示如何使用贪心 + 启发式链路优化器进行任务链优化。
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flood_decision_agent.agents.decision_chain import HeuristicOptimizer
from flood_decision_agent.agents.decision_chain.task_decomposer import TaskNodeInfo, TaskType


def create_sample_task_chain():
    """创建示例任务链（洪水预警系统）."""
    return [
        TaskNodeInfo(
            task_id="collect_radar",
            task_type=TaskType.DATA_COLLECTION,
            description="采集雷达数据",
            inputs=[],
            outputs=["radar_data"],
            dependencies=[],
        ),
        TaskNodeInfo(
            task_id="collect_satellite",
            task_type=TaskType.DATA_COLLECTION,
            description="采集卫星数据",
            inputs=[],
            outputs=["satellite_data"],
            dependencies=[],
        ),
        TaskNodeInfo(
            task_id="collect_station",
            task_type=TaskType.DATA_COLLECTION,
            description="采集站点数据",
            inputs=[],
            outputs=["station_data"],
            dependencies=[],
        ),
        TaskNodeInfo(
            task_id="fuse_data",
            task_type=TaskType.CALCULATION,
            description="融合多源数据",
            inputs=["radar_data", "satellite_data", "station_data"],
            outputs=["fused_data"],
            dependencies=["collect_radar", "collect_satellite", "collect_station"],
        ),
        TaskNodeInfo(
            task_id="analyze_risk",
            task_type=TaskType.CALCULATION,
            description="风险评估计算",
            inputs=["fused_data"],
            outputs=["risk_level", "risk_areas"],
            dependencies=["fuse_data"],
        ),
        TaskNodeInfo(
            task_id="generate_warning",
            task_type=TaskType.DECISION,
            description="生成预警决策",
            inputs=["risk_level", "risk_areas"],
            outputs=["warning_level", "warning_message"],
            dependencies=["analyze_risk"],
        ),
        TaskNodeInfo(
            task_id="send_notification",
            task_type=TaskType.EXECUTION,
            description="发送预警通知",
            inputs=["warning_level", "warning_message"],
            outputs=["notification_status"],
            dependencies=["generate_warning"],
        ),
    ]


def demo_basic_optimization():
    """演示基本优化功能."""
    print("=" * 60)
    print("示例 1: 基本优化")
    print("=" * 60)

    # 创建优化器
    optimizer = HeuristicOptimizer(
        max_iterations=3,
        reliability_threshold=0.7,
    )

    # 创建任务链
    nodes = create_sample_task_chain()
    print(f"\n初始任务链: {len(nodes)} 个任务")
    for node in nodes:
        print(f"  - {node.task_id}: {node.description}")

    # 执行优化
    print("\n开始优化...")
    result_nodes, reliability, log = optimizer.optimize_iteratively(nodes)

    print(f"\n优化完成!")
    print(f"  - 最终可靠性: {reliability:.2f}")
    print(f"  - 优化日志:")
    for entry in log:
        print(f"    {entry}")


def demo_parallelization():
    """演示并行化优化."""
    print("\n" + "=" * 60)
    print("示例 2: 并行化优化")
    print("=" * 60)

    optimizer = HeuristicOptimizer()

    # 寻找并行化机会
    nodes = create_sample_task_chain()
    opportunities = optimizer._find_parallelization_opportunities(nodes)

    print(f"\n发现 {len(opportunities)} 个并行化机会:")
    for opp in opportunities:
        print(f"  - {opp['node_id']}: 策略={opp['strategy']}, 收益={opp['benefit']:.2f}")


def demo_split_optimization():
    """演示任务拆分优化."""
    print("\n" + "=" * 60)
    print("示例 3: 任务拆分优化")
    print("=" * 60)

    optimizer = HeuristicOptimizer()

    # 创建一个复杂任务
    complex_node = TaskNodeInfo(
        task_id="complex_analysis",
        task_type=TaskType.CALCULATION,
        description="复杂数据分析",
        inputs=["data1", "data2", "data3"],
        outputs=["result1", "result2", "result3", "result4", "result5"],
        dependencies=[],
    )

    nodes = [complex_node]

    # 寻找拆分机会
    opportunities = optimizer._find_split_opportunities(nodes)

    print(f"\n发现 {len(opportunities)} 个拆分机会:")
    for opp in opportunities:
        print(f"  - {opp['node_id']}: 原因={opp['reason']}, 建议拆分为={opp['suggested_splits']} 个")

    # 应用拆分
    if opportunities:
        result = optimizer._apply_split_optimization(nodes, opportunities[0])
        print(f"\n拆分后: {len(result)} 个任务")
        for node in result:
            print(f"  - {node.task_id}: {node.description}")


def demo_critical_path():
    """演示关键路径优化."""
    print("\n" + "=" * 60)
    print("示例 4: 关键路径识别与优化")
    print("=" * 60)

    optimizer = HeuristicOptimizer()

    nodes = create_sample_task_chain()

    # 识别关键路径
    critical_path = optimizer._identify_critical_path(nodes)

    print(f"\n关键路径 ({len(critical_path)} 个任务):")
    for task_id in critical_path:
        node = next(n for n in nodes if n.task_id == task_id)
        print(f"  - {task_id}: {node.description}")

    # 应用关键路径优化
    optimized = optimizer._apply_critical_path_optimization(nodes, critical_path)

    print("\n关键路径任务已标记:")
    for node in optimized:
        if node.metadata.get("critical_path"):
            print(f"  - {node.task_id}: 优先级={node.metadata.get('priority')}, 重试={node.metadata.get('retry_enabled')}")


def demo_alternatives():
    """演示备选链生成."""
    print("\n" + "=" * 60)
    print("示例 5: 生成备选链")
    print("=" * 60)

    optimizer = HeuristicOptimizer()

    nodes = create_sample_task_chain()

    # 生成备选链
    alternatives = optimizer.generate_heuristic_alternatives(nodes)

    print(f"\n生成 {len(alternatives)} 个备选链:")
    for i, alt in enumerate(alternatives, 1):
        print(f"\n备选链 {i}:")
        print(f"  - ID: {alt.chain_id}")
        print(f"  - 策略: {alt.strategy}")
        print(f"  - 可靠性: {alt.reliability_score:.2f}")
        print(f"  - 描述: {alt.metadata.get('description', '')}")


def demo_optimization_report():
    """演示优化报告生成."""
    print("\n" + "=" * 60)
    print("示例 6: 优化报告")
    print("=" * 60)

    optimizer = HeuristicOptimizer()

    # 原始任务链
    original_nodes = create_sample_task_chain()

    # 优化后的任务链（模拟）
    optimized_nodes = optimizer._apply_parallel_strategy(original_nodes)

    # 生成报告
    report = optimizer.get_optimization_report(original_nodes, optimized_nodes)

    print("\n优化报告:")
    print(f"  原始状态:")
    print(f"    - 任务数: {report['original']['node_count']}")
    print(f"    - 可靠性: {report['original']['reliability']:.2f}")
    print(f"    - 问题数: {report['original']['issues']}")

    print(f"\n  优化后:")
    print(f"    - 任务数: {report['optimized']['node_count']}")
    print(f"    - 可靠性: {report['optimized']['reliability']:.2f}")
    print(f"    - 问题数: {report['optimized']['issues']}")

    print(f"\n  改进:")
    print(f"    - 可靠性提升: {report['improvement']['reliability_gain']:.2f}")
    print(f"    - 问题减少: {report['improvement']['issue_reduction']}")
    print(f"    - 任务变化: {report['improvement']['node_change']}")

    print(f"\n  应用的策略:")
    for strategy in report['strategies_applied']:
        print(f"    - {strategy}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HeuristicOptimizer 使用示例")
    print("贪心 + 启发式链路优化器")
    print("=" * 60)

    # 运行所有示例
    demo_basic_optimization()
    demo_parallelization()
    demo_split_optimization()
    demo_critical_path()
    demo_alternatives()
    demo_optimization_report()

    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)
