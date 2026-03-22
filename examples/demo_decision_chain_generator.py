"""决策链生成 Agent 演示脚本.

展示 DecisionChainGeneratorAgent 的完整功能，包括：
1. 意图理解
2. 任务分解
3. 链路优化
4. TaskGraph 生成
5. 与 NodeSchedulerAgent 集成执行
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.agents.decision_chain_generator import (
    DecisionChainGeneratorAgent,
    DecisionPipeline,
)
from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool


def print_section(title: str) -> None:
    """打印章节标题."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_subsection(title: str) -> None:
    """打印子章节标题."""
    print(f"\n--- {title} ---")


def demo_intent_parsing():
    """演示意图理解功能."""
    print_section("演示 1: 意图理解")

    from flood_decision_agent.core.intent_parser import IntentParser

    parser = IntentParser()

    # 示例1: 自然语言输入 - 洪水调度
    print_subsection("自然语言输入 - 洪水调度")
    text1 = "三峡大坝需要将出库流量调整到19000立方米每秒，速率不超过500"
    print(f"输入: {text1}")

    intent1 = parser.parse_natural_language(text1)
    print(f"任务类型: {intent1.task_type.value if intent1.task_type else 'unknown'}")
    print(f"目标: {intent1.goal}")
    print(f"约束: {intent1.constraints}")

    # 示例2: 自然语言输入 - 干旱调度
    print_subsection("自然语言输入 - 干旱调度")
    text2 = "当前是干旱期，需要增加水库蓄水量到175米"
    print(f"输入: {text2}")

    intent2 = parser.parse_natural_language(text2)
    print(f"任务类型: {intent2.task_type.value if intent2.task_type else 'unknown'}")
    print(f"目标: {intent2.goal}")

    # 示例3: 结构化输入
    print_subsection("结构化输入")
    structured_data = {
        "task_type": "flood_dispatch",
        "target": {"outflow": 20000, "target_level": 145.0},
        "constraints": {"max_rate": 600, "min_outflow": 10000},
        "context": {"current_level": 150.0, "current_inflow": 25000},
    }
    print(f"输入: {structured_data}")

    intent3 = parser.parse_structured(structured_data)
    print(f"任务类型: {intent3.task_type.value if intent3.task_type else 'unknown'}")
    print(f"目标: {intent3.goal}")
    print(f"约束: {intent3.constraints}")
    print(f"上下文: {intent3.context}")


def demo_task_decomposition():
    """演示任务分解功能."""
    print_section("演示 2: 任务分解")

    from flood_decision_agent.core.task_decomposer import TaskDecomposer, TaskType

    decomposer = TaskDecomposer()

    # 逆向分解
    print_subsection("逆向分解 - 洪水调度")
    goal = "调整出库流量到19000m³/s"
    print(f"最终目标: {goal}")

    nodes = decomposer.decompose_backward(
        goal=goal,
        task_type=TaskType.EXECUTION,
        required_outputs=["outflow_rate"],
    )

    print(f"\n分解为 {len(nodes)} 个任务节点:")
    print("-" * 40)
    for i, node in enumerate(nodes, 1):
        print(f"{i}. [{node.task_type.value}] {node.task_id}")
        print(f"   描述: {node.description}")
        print(f"   输入: {node.inputs}")
        print(f"   输出: {node.outputs}")
        print(f"   依赖: {node.dependencies}")
        print()

    # 正向验证
    print_subsection("正向验证")
    is_valid, errors = decomposer.verify_forward(nodes)
    print(f"验证结果: {'通过' if is_valid else '未通过'}")
    if errors:
        print(f"问题: {errors}")
    else:
        print("未发现明显问题")

    # 节点结构化
    print_subsection("节点结构化")
    structured_nodes = decomposer.structure_nodes(nodes)
    print(f"结构化节点数: {len(structured_nodes)}")
    for node in structured_nodes:
        print(f"  - {node.node_id}: {node.task_type}")


def demo_chain_optimization():
    """演示链路优化功能."""
    print_section("演示 3: 链路优化")

    from flood_decision_agent.core.chain_optimizer import ChainOptimizer
    from flood_decision_agent.core.task_decomposer import TaskDecomposer, TaskType

    decomposer = TaskDecomposer()
    optimizer = ChainOptimizer()

    # 生成基础任务链
    nodes = decomposer.decompose_backward(
        goal="调整出库流量到19000m³/s",
        task_type=TaskType.EXECUTION,
        required_outputs=["outflow_rate"],
    )

    # 生成备选链
    print_subsection("生成备选任务链")
    alternatives = optimizer.generate_alternatives(nodes)
    print(f"生成 {len(alternatives)} 条备选链:")
    for alt in alternatives:
        print(f"  - {alt.chain_id}: 策略={alt.strategy}, 节点数={len(alt.nodes)}")

    # 评估可靠性
    print_subsection("评估链路可靠性")
    for alt in alternatives:
        reliability, issues, details = optimizer.evaluate_reliability(alt.nodes)
        alt.reliability_score = reliability
        print(f"\n{alt.chain_id}:")
        print(f"  可靠性评分: {reliability:.2f}")
        print(f"  问题数: {len(issues)}")
        if issues:
            for issue in issues[:3]:  # 只显示前3个问题
                print(f"    - {issue}")

    # 识别瓶颈
    print_subsection("识别瓶颈节点")
    best_chain = max(alternatives, key=lambda x: x.reliability_score)
    bottlenecks = optimizer.identify_bottlenecks(best_chain.nodes)
    if bottlenecks:
        print(f"发现 {len(bottlenecks)} 个瓶颈:")
        for b in bottlenecks:
            print(f"  - {b.node_id}: {b.bottleneck_type} (严重程度: {b.severity:.2f})")
            for suggestion in b.suggestions:
                print(f"      建议: {suggestion}")
    else:
        print("未发现明显瓶颈")

    # 选择最优链
    print_subsection("选择最优任务链")
    selected = optimizer.select_best_chain(alternatives)
    if selected:
        print(f"选择: {selected.chain_id}")
        print(f"可靠性: {selected.reliability_score:.2f}")
        print(f"策略: {selected.strategy}")


def demo_task_graph_building():
    """演示 TaskGraph 构建功能."""
    print_section("演示 4: TaskGraph 构建")

    from flood_decision_agent.core.task_graph_builder import TaskGraphBuilder, TaskChainItem

    builder = TaskGraphBuilder()

    # 创建任务链
    print_subsection("从任务链构建 TaskGraph")
    chain = [
        TaskChainItem(
            task_id="collect_rainfall",
            task_type="data_collection",
            description="采集降雨数据",
            inputs=[],
            outputs=["rainfall_data"],
            dependencies=[],
        ),
        TaskChainItem(
            task_id="collect_upstream",
            task_type="data_collection",
            description="采集上游流量",
            inputs=[],
            outputs=["upstream_flow"],
            dependencies=[],
        ),
        TaskChainItem(
            task_id="predict_inflow",
            task_type="prediction",
            description="预测来水",
            inputs=["rainfall_data", "upstream_flow"],
            outputs=["inflow_forecast"],
            dependencies=["collect_rainfall", "collect_upstream"],
        ),
        TaskChainItem(
            task_id="calculate_plan",
            task_type="calculation",
            description="计算调度方案",
            inputs=["inflow_forecast", "current_state"],
            outputs=["dispatch_plan"],
            dependencies=["predict_inflow"],
        ),
        TaskChainItem(
            task_id="execute_dispatch",
            task_type="execution",
            description="执行调度",
            inputs=["dispatch_plan"],
            outputs=["execution_result"],
            dependencies=["calculate_plan"],
        ),
    ]

    print("任务链:")
    for item in chain:
        print(f"  - {item.task_id}: {item.description}")
        print(f"    依赖: {item.dependencies if item.dependencies else '无'}")

    # 构建图
    task_graph = builder.build_from_chain(chain)
    print(f"\nTaskGraph 构建完成:")
    print(f"  节点数: {len(task_graph.get_all_nodes())}")

    # 验证图
    is_valid, error = builder.validate_graph(task_graph)
    print(f"  验证结果: {'通过' if is_valid else '失败'}")
    if error:
        print(f"  错误: {error}")

    # 拓扑排序
    print_subsection("拓扑排序")
    sorted_ids = task_graph.topological_sort()
    print("执行顺序:")
    for i, node_id in enumerate(sorted_ids, 1):
        node = task_graph.get_node(node_id)
        print(f"  {i}. {node_id} ({node.task_type})")


def demo_full_pipeline():
    """演示完整流程."""
    print_section("演示 5: 完整决策链生成流程")

    agent = DecisionChainGeneratorAgent()

    # 自然语言输入
    print_subsection("自然语言输入")
    user_input = "三峡大坝需要将出库流量调整到19000立方米每秒，速率不超过500立方米每秒"
    print(f"用户输入: {user_input}")

    # 生成决策链
    print("\n开始生成决策链...")
    print("-" * 40)

    task_graph, metadata = agent.generate_chain(
        user_input=user_input,
        input_type="natural_language",
    )

    # 展示结果
    print_subsection("阶段 1: 意图理解结果")
    intent_meta = metadata["intent"]
    print(f"任务类型: {intent_meta['task_type']}")
    print(f"目标: {intent_meta['goal']}")
    print(f"约束: {intent_meta['constraints']}")

    print_subsection("阶段 2: 任务分解结果")
    decomp_meta = metadata["decomposition"]
    print(f"节点数: {decomp_meta['node_count']}")
    print("任务节点:")
    for node_info in decomp_meta["nodes"]:
        print(f"  - {node_info['id']}: {node_info['type']}")

    print_subsection("阶段 3: 链路优化结果")
    opt_meta = metadata["optimization"]
    print(f"可靠性评分: {opt_meta['reliability_score']:.2f}")
    print("优化日志:")
    for log_entry in opt_meta["log"]:
        print(f"  {log_entry}")

    print_subsection("阶段 4: TaskGraph 生成结果")
    graph_meta = metadata["task_graph"]
    print(f"节点数: {graph_meta['node_count']}")
    print(f"边数: {graph_meta['edge_count']}")

    # 展示拓扑排序
    print("\n执行顺序 (拓扑排序):")
    sorted_ids = task_graph.topological_sort()
    for i, node_id in enumerate(sorted_ids, 1):
        node = task_graph.get_node(node_id)
        print(f"  {i}. {node_id} ({node.task_type})")


def demo_with_node_scheduler():
    """演示与 NodeSchedulerAgent 集成."""
    print_section("演示 6: 与 NodeSchedulerAgent 集成")

    print("注意: 此演示需要配置 API Key 才能完整运行")
    print("-" * 40)

    # 创建 Pipeline
    chain_generator = DecisionChainGeneratorAgent()

    # 尝试创建 NodeSchedulerAgent（可能需要 API Key）
    try:
        node_scheduler = NodeSchedulerAgent()
        pipeline = DecisionPipeline(
            chain_generator=chain_generator,
            node_scheduler=node_scheduler,
        )
        print("✓ NodeSchedulerAgent 创建成功")
    except Exception as e:
        print(f"✗ NodeSchedulerAgent 创建失败: {e}")
        print("  将仅演示决策链生成部分")
        pipeline = DecisionPipeline(chain_generator=chain_generator)

    # 执行
    user_input = "三峡大坝需要将出库流量调整到19000立方米每秒"
    print(f"\n用户输入: {user_input}")
    print("\n执行中...")

    try:
        result = pipeline.execute(
            user_input=user_input,
            input_type="natural_language",
        )

        print_subsection("执行结果")
        print(f"任务图节点数: {len(result['task_graph'].get_all_nodes())}")
        print(f"生成元数据: {list(result['generation_metadata'].keys())}")

        if result['execution_result']:
            print(f"执行结果: {result['execution_result']}")
        else:
            print("执行结果: 未执行（无调度器）")

    except Exception as e:
        print(f"执行出错: {e}")
        import traceback
        traceback.print_exc()


def demo_alternatives():
    """演示备选链生成功能."""
    print_section("演示 7: 备选任务链生成")

    agent = DecisionChainGeneratorAgent()

    user_input = "三峡大坝需要将出库流量调整到19000立方米每秒"
    print(f"用户输入: {user_input}")

    # 生成并展示所有备选链
    task_graph, alternatives, metadata = agent.generate_chain_with_alternatives(
        user_input=user_input,
        input_type="natural_language",
        num_alternatives=3,
    )

    print_subsection("所有备选链")
    for i, alt in enumerate(alternatives, 1):
        print(f"\n备选链 {i}: {alt.chain_id}")
        print(f"  策略: {alt.strategy}")
        print(f"  可靠性评分: {alt.reliability_score:.2f}")
        print(f"  节点数: {len(alt.nodes)}")
        if alt.metadata.get("issues"):
            print(f"  问题数: {len(alt.metadata['issues'])}")

    print_subsection("最终选择")
    print(f"选择链: {metadata['selected_chain']}")
    print(f"任务图节点数: {len(task_graph.get_all_nodes())}")


def main():
    """主函数."""
    print("\n" + "=" * 60)
    print("  DecisionChainGeneratorAgent 功能演示")
    print("=" * 60)
    print("\n本演示展示决策链生成 Agent 的完整功能:")
    print("  1. 意图理解 - 解析自然语言和结构化输入")
    print("  2. 任务分解 - 逆向分解 + 正向验证")
    print("  3. 链路优化 - 生成备选链 + 可靠性评估")
    print("  4. TaskGraph 构建 - 生成可执行的任务图")
    print("  5. 完整流程 - 端到端决策链生成")
    print("  6. 集成演示 - 与 NodeSchedulerAgent 集成")
    print("  7. 备选链展示 - 查看所有备选方案")

    # 运行所有演示
    demo_intent_parsing()
    demo_task_decomposition()
    demo_chain_optimization()
    demo_task_graph_building()
    demo_full_pipeline()
    demo_with_node_scheduler()
    demo_alternatives()

    print("\n" + "=" * 60)
    print("  演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
