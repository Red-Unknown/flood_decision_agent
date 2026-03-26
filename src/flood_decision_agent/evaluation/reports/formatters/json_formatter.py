"""JSON格式报告格式化器."""

from __future__ import annotations

import json
from typing import Any, Dict

from flood_decision_agent.evaluation.reports.base import EvaluationReport


class JSONFormatter:
    """JSON格式报告格式化器."""

    def format(self, report: EvaluationReport, indent: int = 2) -> str:
        """格式化报告为JSON字符串.

        Args:
            report: 评估报告
            indent: 缩进空格数

        Returns:
            JSON字符串
        """
        return report.to_json(indent=indent)

    def format_to_file(self, report: EvaluationReport, filepath: str, indent: int = 2) -> None:
        """格式化并保存到文件.

        Args:
            report: 评估报告
            filepath: 输出文件路径
            indent: 缩进空格数
        """
        content = self.format(report, indent)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def format_batch(self, reports: list[EvaluationReport]) -> str:
        """批量格式化多个报告.

        Args:
            reports: 报告列表

        Returns:
            JSON字符串
        """
        data = [r.to_dict() for r in reports]
        return json.dumps(data, ensure_ascii=False, indent=2)
