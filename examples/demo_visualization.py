"""可视化功能演示脚本.

展示 Agent 调用链、任务执行状态和数据流的可视化效果。
"""

from __future__ import annotations

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))

from flood_decision_agent.app.visualized_pipeline import run_visualized_pipeline
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key
from flood_decision_agent.visualization.terminal import TerminalVisualizer


def demo_basic_visualization():
    """基础可视化演示.

    展示标准的任务列表和执行状态打勾效果。
    """
    print("\n" + "=" * 70)
    print("演示 1: 基础可视化 - 洪水预警任务")
    print("=" * 70)

    result = run_visualized_pipeline(
        task_request={
            "type": "flood_warning",
            "params": {
                "station": "demo_station",
                "date": "2024-01-01",
            },
        },
        seed=42,
        enable_visualization=True,
    )

    print(f"\n最终执行结果: {'✓ 成功' if result.success else '✗ 失败'}")
    print(f"执行汇总: {result.execution_summary}")


def demo_custom_visualizer():
    """自定义可视化器演示.

    展示如何配置可视化器的各种选项。
    """
    print("\n" + "=" * 70)
    print("演示 2: 自定义可视化器配置")
    print("=" * 70)

    # 创建自定义配置的可视化器
    visualizer = TerminalVisualizer(
        enabled=True,
        use_colors=True,
        use_unicode=True,
        indent_size=4,  # 更大的缩进
    )

    result = run_visualized_pipeline(
        task_request={
            "type": "reservoir_dispatch",
            "params": {
                "reservoir": "demo_reservoir",
                "target_date": "2024-01-01",
            },
        },
        seed=123,
        visualizer=visualizer,
    )

    print(f"\n最终执行结果: {'✓ 成功' if result.success else '✗ 失败'}")


def demo_disabled_visualization():
    """禁用可视化演示.

    展示关闭可视化时的效果（仅显示日志）。
    """
    print("\n" + "=" * 70)
    print("演示 3: 禁用可视化")
    print("=" * 70)
    print("(此演示关闭可视化，仅显示标准日志输出)")

    result = run_visualized_pipeline(
        task_request={
            "type": "data_query",
            "params": {"query": "water_level"},
        },
        seed=456,
        enable_visualization=False,  # 关闭可视化
    )

    print(f"\n最终执行结果: {'✓ 成功' if result.success else '✗ 失败'}")
    print(f"执行汇总: {result.execution_summary}")


def demo_event_handlers():
    """事件处理器演示.

    展示如何注册自定义事件处理器。
    """
    print("\n" + "=" * 70)
    print("演示 4: 自定义事件处理器")
    print("=" * 70)

    visualizer = TerminalVisualizer(enabled=True)

    # 注册自定义事件处理器
    def on_node_completed_handler(event):
        if event.task_info:
            print(
                f"[自定义处理器] 任务完成: {event.task_info.task_name}"
            )

    def on_agent_called_handler(event):
        if event.agent_call:
            print(
                f"[自定义处理器] Agent 调用: {event.agent_call.caller_agent} -> {event.agent_call.callee_agent}"
            )

    from flood_decision_agent.visualization.models import EventType

    visualizer.register_event_handler(EventType.NODE_COMPLETED, on_node_completed_handler)
    visualizer.register_event_handler(EventType.AGENT_CALLED, on_agent_called_handler)

    result = run_visualized_pipeline(
        task_request={
            "type": "risk_assessment",
            "params": {"area": "demo_area"},
        },
        seed=789,
        visualizer=visualizer,
    )

    print(f"\n最终执行结果: {'✓ 成功' if result.success else '✗ 失败'}")


def demo_ascii_mode():
    """ASCII 模式演示.

    展示在不支持 Unicode 的环境下的显示效果。
    """
    print("\n" + "=" * 70)
    print("演示 5: ASCII 模式（无 Unicode）")
    print("=" * 70)

    visualizer = TerminalVisualizer(
        enabled=True,
        use_unicode=False,  # 禁用 Unicode，使用 ASCII
        use_colors=True,
    )

    result = run_visualized_pipeline(
        task_request={
            "type": "weather_forecast",
            "params": {"location": "demo_city"},
        },
        seed=321,
        visualizer=visualizer,
    )

    print(f"\n最终执行结果: {'[x] 成功' if result.success else '[!] 失败'}")


def print_usage():
    """打印使用说明."""
    print("""
可视化演示脚本使用说明:

运行方式:
    python examples/demo_visualization.py [demo_name]

可选演示:
    basic       - 基础可视化演示（默认）
    custom      - 自定义可视化器配置
    disabled    - 禁用可视化
    events      - 自定义事件处理器
    ascii       - ASCII 模式
    all         - 运行所有演示

示例:
    python examples/demo_visualization.py
    python examples/demo_visualization.py basic
    python examples/demo_visualization.py all
""")


def main():
    """主函数."""
    # 检查 API Key
    try:
        require_kimi_api_key()
    except SystemExit as e:
        print("需要kimi_api_key")
        sys.exit(1)

    # 获取命令行参数
    demo_name = sys.argv[1] if len(sys.argv) > 1 else "basic"

    demos = {
        "basic": demo_basic_visualization,
        "custom": demo_custom_visualizer,
        "disabled": demo_disabled_visualization,
        "events": demo_event_handlers,
        "ascii": demo_ascii_mode,
    }

    if demo_name == "all":
        # 运行所有演示
        for name, demo_func in demos.items():
            try:
                demo_func()
            except Exception as e:
                print(f"\n演示 '{name}' 出错: {e}")
    elif demo_name in demos:
        # 运行指定演示
        try:
            demos[demo_name]()
        except Exception as e:
            print(f"\n演示出错: {e}")
            import traceback

            traceback.print_exc()
    elif demo_name in ("-h", "--help", "help"):
        print_usage()
    else:
        print(f"未知演示: {demo_name}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
