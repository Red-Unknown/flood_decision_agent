"""CSV格式报告格式化器."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

from flood_decision_agent.evaluation.reports.base import EvaluationReport


class CSVFormatter:
    """CSV格式报告格式化器."""

    def format_summary(self, report: EvaluationReport) -> str:
        """格式化报告汇总为CSV.

        Args:
            report: 评估报告

        Returns:
            CSV字符串
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(["指标", "值"])

        # 写入基本数据
        writer.writerow(["报告ID", report.report_id])
        writer.writerow(["生成时间", report.created_at])
        writer.writerow(["Agent版本", report.agent_version])
        writer.writerow(["综合评分", f"{report.overall_score:.4f}"])
        writer.writerow(["总测试数", report.summary.get("total", 0)])
        writer.writerow(["通过数", report.summary.get("passed", 0)])
        writer.writerow(["失败数", report.summary.get("failed", 0)])
        writer.writerow(["通过率", f"{report.summary.get('pass_rate', 0):.4f}"])

        return output.getvalue()

    def format_metrics(self, report: EvaluationReport) -> str:
        """格式化指标为CSV.

        Args:
            report: 评估报告

        Returns:
            CSV字符串
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(["类别", "指标", "值", "单位", "说明"])

        # 写入指标数据
        for category, metrics in report.metrics.items():
            for name, metric in metrics.items():
                writer.writerow([
                    category,
                    name,
                    metric.value,
                    metric.unit,
                    metric.description,
                ])

        return output.getvalue()

    def format_test_results(self, report: EvaluationReport) -> str:
        """格式化测试结果详情为CSV.

        Args:
            report: 评估报告

        Returns:
            CSV字符串
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(["测试ID", "名称", "状态", "耗时(ms)", "错误信息"])

        # 写入测试数据
        for result in report.test_results:
            writer.writerow([
                result.get("test_case_id", ""),
                result.get("test_case_name", ""),
                "通过" if result.get("success") else "失败",
                result.get("execution_time_ms", 0),
                result.get("error_message", ""),
            ])

        return output.getvalue()

    def format_to_file(self, report: EvaluationReport, filepath: str, data_type: str = "summary") -> None:
        """格式化并保存到文件.

        Args:
            report: 评估报告
            filepath: 输出文件路径
            data_type: 数据类型 (summary, metrics, test_results)
        """
        if data_type == "summary":
            content = self.format_summary(report)
        elif data_type == "metrics":
            content = self.format_metrics(report)
        elif data_type == "test_results":
            content = self.format_test_results(report)
        else:
            raise ValueError(f"未知的数据类型: {data_type}")

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            f.write(content)
