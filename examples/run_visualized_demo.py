"""可视化演示运行脚本 - 使用真实 API.

使用方法:
    1. 确保已设置环境变量 KIMI_API_KEY
    2. 运行: python examples/run_visualized_demo.py <编号>
"""

from __future__ import annotations

import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))

# 禁用 loguru 日志输出
from loguru import logger

logger.remove()  # 移除所有处理器

from flood_decision_agent.app.visualized_pipeline import run_visualized_pipeline
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key


def check_api_key():
    """检查 API Key 是否已设置."""
    try:
        require_kimi_api_key()
        print("✓ API Key 已设置")
        return True
    except SystemExit:
        print("✗ 需要设置 KIMI_API_KEY 环境变量")
        print("\n设置方法:")
        print("  PowerShell: $env:KIMI_API_KEY='your_api_key'")
        print("  CMD:        set KIMI_API_KEY=your_api_key")
        return False


def run_example(name: str, user_input: str):
    """运行单个示例.

    Args:
        name: 示例名称
        user_input: 用户输入文本
    """
    print("\n" + "=" * 70)
    print(f"问题: {name}")
    print("=" * 70)
    print(f"输入: {user_input}")
    print()

    try:
        # 使用自然语言输入
        result = run_visualized_pipeline(
            task_request={
                "type": "natural_language",
                "input": user_input,
            },
            seed=42,
            enable_visualization=True,
        )

        print(f"\n执行结果: {'✓ 成功' if result.success else '✗ 失败'}")
        print(f"执行汇总: {result.execution_summary}")

        # 展示数据池中的输出
        if result.data_pool_snapshot:
            print("\n任务输出:")
            for key, value in result.data_pool_snapshot.items():
                if isinstance(value, dict):
                    print(f"  • {key}: {list(value.keys())}")
                else:
                    print(f"  • {key}: {str(value)[:100]}...")

    except Exception as e:
        print(f"\n✗ 执行出错: {e}")
        import traceback
        traceback.print_exc()


def example_1():
    """示例 1: 洪水预警."""
    run_example(
        name="洪水预警分析",
        user_input="查询宜昌站、枝城站、沙市站的实时水情，结合未来72小时降雨预报，分析洪水演进趋势，生成预警方案",
    )


def example_2():
    """示例 2: 水库调度."""
    run_example(
        name="水库联合调度",
        user_input="基于三峡、葛洲坝、丹江口三库当前水位和入库流量预报，优化三库联合调度方案，平衡防洪与发电效益",
    )


def example_3():
    """示例 3: 数据查询."""
    run_example(
        name="数据查询",
        user_input="查询长江流域最近24小时的降雨分布情况",
    )


def example_4():
    """示例 4: 风险评估."""
    run_example(
        name="洪水风险评估",
        user_input="评估武汉市在暴雨情景下的洪水风险等级",
    )


def example_5():
    """示例 5: 应急响应."""
    run_example(
        name="应急响应决策",
        user_input="武汉关水位超警戒且持续上涨，制定应急响应方案",
    )


def example_custom():
    """自定义问题."""
    print("\n" + "=" * 70)
    print("自定义问题")
    print("=" * 70)

    if len(sys.argv) > 2:
        question = " ".join(sys.argv[2:])
    else:
        question = input("\n请输入您的问题: ").strip()

    if not question:
        print("问题不能为空")
        return

    run_example(
        name="自定义问题",
        user_input=question,
    )


def print_menu():
    """打印菜单."""
    print("\n" + "=" * 70)
    print("可视化演示 - 使用真实 LLM API")
    print("=" * 70)
    print("\n可用示例:")
    print("  1. 洪水预警分析")
    print("  2. 水库联合调度")
    print("  3. 数据查询")
    print("  4. 洪水风险评估")
    print("  5. 应急响应决策")
    print("  6. 自定义问题")
    print("\n  all - 运行所有预设示例")
    print("\n使用方法:")
    print("  python examples/run_visualized_demo.py <编号>")
    print("  python examples/run_visualized_demo.py 6 '你的问题'")


def main():
    """主函数."""
    print("\n" + "=" * 70)
    print("可视化演示脚本")
    print("=" * 70)

    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    # 获取命令行参数
    if len(sys.argv) < 2:
        print_menu()
        sys.exit(0)

    choice = sys.argv[1].lower()

    examples = {
        "1": example_1,
        "2": example_2,
        "3": example_3,
        "4": example_4,
        "5": example_5,
        "6": example_custom,
    }

    if choice == "all":
        # 运行所有预设示例
        for key in ["1", "2", "3", "4", "5"]:
            examples[key]()
    elif choice in examples:
        examples[choice]()
    else:
        print(f"未知选项: {choice}")
        print_menu()
        sys.exit(1)


if __name__ == "__main__":
    main()
