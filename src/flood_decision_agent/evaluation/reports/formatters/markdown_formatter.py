"""Markdown格式报告格式化器."""

from __future__ import annotations

from typing import Any, Dict, List

from flood_decision_agent.evaluation.reports.base import EvaluationReport


class MarkdownFormatter:
    """Markdown格式报告格式化器."""

    def format(self, report: EvaluationReport) -> str:
        """格式化报告为Markdown字符串.

        Args:
            report: 评估报告

        Returns:
            Markdown字符串
        """
        return report.to_markdown()

    def format_to_file(self, report: EvaluationReport, filepath: str) -> None:
        """格式化并保存到文件.

        Args:
            report: 评估报告
            filepath: 输出文件路径
        """
        content = self.format(report)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def format_comparison(self, reports: List[EvaluationReport]) -> str:
        """格式化多个报告的对比.

        Args:
            reports: 报告列表

        Returns:
            Markdown字符串
        """
        lines = []
        lines.append("# 评估报告对比")
        lines.append("")
        lines.append("| 报告ID | 时间 | 综合评分 | 通过率 |")
        lines.append("|--------|------|----------|--------|")

        for report in reports:
            lines.append(
                f"| {report.report_id} | "
                f"{report.created_at[:19]} | "
                f"{report.overall_score:.2%} | "
                f"{report.summary.get('pass_rate', 0):.2%} |"
            )

        lines.append("")
        lines.append("## 维度评分对比")
        lines.append("")
        lines.append("| 维度 | " + " | ".join(r.report_id for r in reports) + " |")
        lines.append("|------|" + "|".join("------" for _ in reports) + "|")

        # 获取所有维度
        all_dimensions = set()
        for report in reports:
            all_dimensions.update(report.dimension_scores.keys())

        for dimension in sorted(all_dimensions):
            scores = [f"{r.dimension_scores.get(dimension, 0):.2%}" for r in reports]
            lines.append(f"| {dimension} | " + " | ".join(scores) + " |")

        return "\n".join(lines)
