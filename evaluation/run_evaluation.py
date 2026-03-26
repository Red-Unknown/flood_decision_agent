"""评估运行入口 - 基于Anthropic第五步：迭代优化评估.

将评估本身视为产品，持续修复评分bug、消除任务歧义，
不断提升信噪比与置信度。

使用方法:
    python evaluation/run_evaluation.py [--suite SUITE] [--output OUTPUT]

示例:
    python evaluation/run_evaluation.py
    python evaluation/run_evaluation.py --suite custom_suite.json
    python evaluation/run_evaluation.py --output reports/eval_2024.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# 检查环境变量
if not os.getenv("KIMI_API_KEY", "").strip():
    print("需要kimi_api_key")
    raise SystemExit(1)

# 添加项目根目录到路径
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flood_decision_agent.evaluation import (
    AgentEvaluator,
    EvaluationReport,
    TestSuite,
)
from flood_decision_agent.evaluation.test_case import (
    create_default_flood_dispatch_test_suite,
)
from flood_decision_agent.infra.logging import setup_logging


def run_evaluation(
    test_suite_path: Optional[str] = None,
    output_dir: str = "evaluation/reports",
    agent_version: str = "1.0.0",
    use_balanced: bool = True,
) -> Dict[str, Any]:
    """运行完整评估流程.

    Args:
        test_suite_path: 测试集文件路径，None则使用默认测试集
        output_dir: 报告输出目录
        agent_version: Agent版本号
        use_balanced: 是否使用平衡的测试集

    Returns:
        评估结果
    """
    print("=" * 60)
    print("Agent量化评估系统")
    print("=" * 60)

    # 1. 加载测试集
    if test_suite_path and Path(test_suite_path).exists():
        print(f"\n📂 加载测试集: {test_suite_path}")
        test_suite = TestSuite.load_from_file(test_suite_path)
    else:
        print("\n📂 使用默认洪水调度测试集")
        test_suite = create_default_flood_dispatch_test_suite()
        # 保存默认测试集供参考
        default_path = Path(output_dir).parent / "test_suites" / "default_suite.json"
        default_path.parent.mkdir(parents=True, exist_ok=True)
        test_suite.save_to_file(str(default_path))
        print(f"   默认测试集已保存到: {default_path}")

    print(f"   测试用例总数: {len(test_suite)}")
    print(f"   正向测试: {len(test_suite.get_by_type(TestCaseType.POSITIVE))}")
    print(f"   反向测试: {len(test_suite.get_by_type(TestCaseType.NEGATIVE))}")
    print(f"   边界测试: {len(test_suite.get_by_type(TestCaseType.BOUNDARY))}")
    print(f"   安全测试: {len(test_suite.get_by_type(TestCaseType.SAFETY))}")
    print(f"   鲁棒性测试: {len(test_suite.get_by_type(TestCaseType.ROBUSTNESS))}")

    # 2. 创建评估器
    print("\n🔧 初始化评估器...")
    evaluator = AgentEvaluator()

    # 3. 执行评估
    print("\n🚀 开始执行评估...")
    print("-" * 60)

    result = evaluator.evaluate_test_suite(test_suite, use_balanced=use_balanced)

    print("-" * 60)
    print("✅ 评估执行完成")

    # 4. 生成报告
    print("\n📊 生成评估报告...")

    metrics = evaluator.get_all_metrics()
    report = EvaluationReport.from_evaluation_result(
        result=result,
        metrics=metrics,
        agent_version=agent_version,
        description=f"洪水调度决策Agent评估 - {test_suite.name}",
    )

    # 5. 保存报告
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = report.created_at.replace(":", "-").replace("T", "_")

    # Markdown报告
    md_path = output_path / f"evaluation_report_{timestamp}.md"
    report.save_to_file(str(md_path), format="markdown")
    print(f"   Markdown报告: {md_path}")

    # JSON报告
    json_path = output_path / f"evaluation_report_{timestamp}.json"
    report.save_to_file(str(json_path), format="json")
    print(f"   JSON报告: {json_path}")

    # HTML报告
    html_path = output_path / f"evaluation_report_{timestamp}.html"
    report.save_to_file(str(html_path), format="html")
    print(f"   HTML报告: {html_path}")

    # 6. 打印汇总
    print("\n" + "=" * 60)
    print("评估结果汇总")
    print("=" * 60)
    print(f"\n🎯 综合评分: {report.overall_score:.2%}")
    print(f"\n📈 测试统计:")
    print(f"   总测试数: {result['total']}")
    print(f"   通过数: {result['passed']} ✅")
    print(f"   失败数: {result['failed']} ❌")
    print(f"   通过率: {result['pass_rate']:.2%}")

    print(f"\n📊 六大维度评分:")
    for dimension, score in report.dimension_scores.items():
        status = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
        print(f"   {status} {dimension:20s}: {score:.2%}")

    if report.recommendations:
        print(f"\n💡 改进建议:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"   {i}. {rec}")

    print("\n" + "=" * 60)
    print(f"评估完成！报告已保存到: {output_dir}")
    print("=" * 60)

    return {
        "report": report.to_dict(),
        "output_files": {
            "markdown": str(md_path),
            "json": str(json_path),
            "html": str(html_path),
        },
    }


def compare_evaluations(
    report_paths: List[str],
    output_path: str = "evaluation/reports/comparison.md",
) -> None:
    """对比多次评估结果.

    Args:
        report_paths: 评估报告JSON文件路径列表
        output_path: 对比报告输出路径
    """
    print("\n📊 生成评估对比报告...")

    reports = []
    for path in report_paths:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            reports.append(data)

    # 生成对比报告
    lines = []
    lines.append("# Agent评估对比报告")
    lines.append("")
    lines.append("| 评估时间 | 综合评分 | 通过率 | 有效性 | 效率 | 鲁棒性 | 安全性 | 自主性 | 可解释性 |")
    lines.append("|----------|----------|--------|--------|------|--------|--------|--------|----------|")

    for report in reports:
        created_at = report.get("created_at", "-")[:19]
        overall = report.get("overall_score", 0)
        pass_rate = report.get("summary", {}).get("pass_rate", 0)
        dimensions = report.get("dimension_scores", {})

        lines.append(
            f"| {created_at} | {overall:.2%} | {pass_rate:.2%} | "
            f"{dimensions.get('effectiveness', 0):.2%} | "
            f"{dimensions.get('efficiency', 0):.2%} | "
            f"{dimensions.get('robustness', 0):.2%} | "
            f"{dimensions.get('safety', 0):.2%} | "
            f"{dimensions.get('autonomy', 0):.2%} | "
            f"{dimensions.get('explainability', 0):.2%} |"
        )

    lines.append("")

    # 保存对比报告
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"对比报告已保存: {output_path}")


def main():
    """主入口."""
    parser = argparse.ArgumentParser(
        description="Agent量化评估系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行默认评估
  python evaluation/run_evaluation.py

  # 使用自定义测试集
  python evaluation/run_evaluation.py --suite my_suite.json

  # 指定输出目录
  python evaluation/run_evaluation.py --output reports/

  # 对比多次评估结果
  python evaluation/run_evaluation.py --compare report1.json report2.json
        """,
    )

    parser.add_argument(
        "--suite",
        type=str,
        default=None,
        help="测试集文件路径（JSON格式）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation/reports",
        help="报告输出目录",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="1.0.0",
        help="Agent版本号",
    )
    parser.add_argument(
        "--no-balanced",
        action="store_true",
        help="不使用平衡的测试集",
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        metavar="REPORT",
        help="对比多个评估报告",
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging()

    if args.compare:
        # 对比模式
        compare_evaluations(args.compare, f"{args.output}/comparison.md")
    else:
        # 评估模式
        from flood_decision_agent.evaluation.test_case import TestCaseType

        run_evaluation(
            test_suite_path=args.suite,
            output_dir=args.output,
            agent_version=args.version,
            use_balanced=not args.no_balanced,
        )


if __name__ == "__main__":
    main()
