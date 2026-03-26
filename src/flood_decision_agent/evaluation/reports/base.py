"""评估报告模块 - 生成综合评估报告.

支持多种格式的报告输出，包括：
- Markdown格式（便于阅读）
- JSON格式（便于程序处理）
- HTML格式（可视化展示）
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flood_decision_agent.evaluation.metrics.base import MetricValue


@dataclass
class EvaluationReport:
    """评估报告数据类."""

    # 基本信息
    report_id: str
    created_at: str
    agent_version: str = ""
    description: str = ""

    # 汇总统计
    summary: Dict[str, Any] = field(default_factory=dict)

    # 详细指标
    metrics: Dict[str, Dict[str, MetricValue]] = field(default_factory=dict)

    # 测试结果
    test_results: List[Dict[str, Any]] = field(default_factory=list)

    # 维度评分
    dimension_scores: Dict[str, float] = field(default_factory=dict)

    # 综合评分
    overall_score: float = 0.0

    # 改进建议
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典."""
        return {
            "report_id": self.report_id,
            "created_at": self.created_at,
            "agent_version": self.agent_version,
            "description": self.description,
            "summary": self.summary,
            "metrics": {
                category: {
                    name: {
                        "value": metric.value,
                        "unit": metric.unit,
                        "description": metric.description,
                    }
                    for name, metric in metrics.items()
                }
                for category, metrics in self.metrics.items()
            },
            "test_results": self.test_results,
            "dimension_scores": self.dimension_scores,
            "overall_score": self.overall_score,
            "recommendations": self.recommendations,
        }

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_markdown(self) -> str:
        """转换为Markdown格式报告."""
        lines = []

        # 标题
        lines.append("# Agent量化评估报告")
        lines.append("")
        lines.append(f"**报告ID**: {self.report_id}")
        lines.append(f"**生成时间**: {self.created_at}")
        lines.append(f"**Agent版本**: {self.agent_version}")
        if self.description:
            lines.append(f"**描述**: {self.description}")
        lines.append("")

        # 综合评分
        lines.append("## 综合评分")
        lines.append("")
        score_emoji = "🟢" if self.overall_score >= 0.8 else "🟡" if self.overall_score >= 0.6 else "🔴"
        lines.append(f"{score_emoji} **{self.overall_score:.2%}**")
        lines.append("")

        # 汇总统计
        lines.append("## 汇总统计")
        lines.append("")
        summary = self.summary
        lines.append(f"- **总测试数**: {summary.get('total', 0)}")
        lines.append(f"- **通过数**: {summary.get('passed', 0)} ✅")
        lines.append(f"- **失败数**: {summary.get('failed', 0)} ❌")
        lines.append(f"- **通过率**: {summary.get('pass_rate', 0):.2%}")
        lines.append("")

        # 按类型统计
        if "type_stats" in summary:
            lines.append("### 按类型统计")
            lines.append("")
            lines.append("| 类型 | 总数 | 通过 | 通过率 |")
            lines.append("|------|------|------|--------|")
            for type_name, stats in summary["type_stats"].items():
                total = stats.get("total", 0)
                passed = stats.get("passed", 0)
                rate = passed / total if total > 0 else 0.0
                lines.append(f"| {type_name} | {total} | {passed} | {rate:.2%} |")
            lines.append("")

        # 维度评分
        lines.append("## 六大维度评分")
        lines.append("")
        lines.append("| 维度 | 评分 | 状态 |")
        lines.append("|------|------|------|")
        for dimension, score in self.dimension_scores.items():
            status = "🟢 优秀" if score >= 0.8 else "🟡 良好" if score >= 0.6 else "🔴 需改进"
            lines.append(f"| {dimension} | {score:.2%} | {status} |")
        lines.append("")

        # 详细指标
        lines.append("## 详细指标")
        lines.append("")

        for category, metrics in self.metrics.items():
            lines.append(f"### {self._translate_category(category)}")
            lines.append("")
            lines.append("| 指标 | 值 | 单位 | 说明 |")
            lines.append("|------|-----|------|------|")
            for name, metric in metrics.items():
                value_str = f"{metric.value:.4f}" if isinstance(metric.value, float) else str(metric.value)
                lines.append(f"| {name} | {value_str} | {metric.unit} | {metric.description} |")
            lines.append("")

        # 测试结果详情
        if self.test_results:
            lines.append("## 测试结果详情")
            lines.append("")
            lines.append("| 测试ID | 名称 | 状态 | 耗时(ms) |")
            lines.append("|--------|------|------|----------|")
            for result in self.test_results[:20]:  # 只显示前20个
                status = "✅ 通过" if result.get("success") else "❌ 失败"
                lines.append(
                    f"| {result.get('test_case_id', '-')} | "
                    f"{result.get('test_case_name', '-')} | "
                    f"{status} | "
                    f"{result.get('execution_time_ms', 0):.0f} |"
                )
            if len(self.test_results) > 20:
                lines.append(f"| ... | 还有 {len(self.test_results) - 20} 个测试 | | |")
            lines.append("")

        # 改进建议
        if self.recommendations:
            lines.append("## 改进建议")
            lines.append("")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        return "\n".join(lines)

    def _translate_category(self, category: str) -> str:
        """翻译指标类别."""
        translations = {
            "effectiveness": "有效性",
            "efficiency": "效率",
            "robustness": "鲁棒性",
            "safety": "安全性",
            "autonomy": "自主性",
            "explainability": "可解释性",
        }
        return translations.get(category, category)

    def save_to_file(self, filepath: str, format: str = "markdown") -> None:
        """保存报告到文件.

        Args:
            filepath: 文件路径
            format: 格式 (markdown, json, html)
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            content = self.to_json()
        elif format == "html":
            content = self._to_html()
        else:  # markdown
            content = self.to_markdown()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def _to_html(self) -> str:
        """转换为HTML格式."""
        # 简化的HTML模板
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Agent评估报告 - {self.report_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        h3 {{ color: #666; }}
        .score {{ font-size: 48px; font-weight: bold; text-align: center; padding: 20px; border-radius: 8px; }}
        .score-good {{ background: #4CAF50; color: white; }}
        .score-medium {{ background: #FFC107; color: black; }}
        .score-bad {{ background: #f44336; color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .metric-card {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #4CAF50; }}
        .recommendation {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 4px; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Agent量化评估报告</h1>
        <p><strong>报告ID:</strong> {self.report_id}</p>
        <p><strong>生成时间:</strong> {self.created_at}</p>
        <p><strong>Agent版本:</strong> {self.agent_version}</p>

        <h2>综合评分</h2>
        <div class="score {'score-good' if self.overall_score >= 0.8 else 'score-medium' if self.overall_score >= 0.6 else 'score-bad'}">
            {self.overall_score:.2%}
        </div>

        <h2>汇总统计</h2>
        <table>
            <tr><th>指标</th><th>值</th></tr>
            <tr><td>总测试数</td><td>{self.summary.get('total', 0)}</td></tr>
            <tr><td>通过数</td><td>{self.summary.get('passed', 0)}</td></tr>
            <tr><td>失败数</td><td>{self.summary.get('failed', 0)}</td></tr>
            <tr><td>通过率</td><td>{self.summary.get('pass_rate', 0):.2%}</td></tr>
        </table>

        <h2>六大维度评分</h2>
        <table>
            <tr><th>维度</th><th>评分</th><th>状态</th></tr>
"""
        for dimension, score in self.dimension_scores.items():
            status = "优秀" if score >= 0.8 else "良好" if score >= 0.6 else "需改进"
            html += f"            <tr><td>{self._translate_category(dimension)}</td><td>{score:.2%}</td><td>{status}</td></tr>\n"

        html += """        </table>
    </div>
</body>
</html>"""
        return html

    @classmethod
    def from_evaluation_result(
        cls,
        result: Dict[str, Any],
        metrics: Dict[str, Dict[str, MetricValue]],
        agent_version: str = "",
        description: str = "",
    ) -> "EvaluationReport":
        """从评估结果创建报告.

        Args:
            result: 评估结果汇总
            metrics: 指标数据
            agent_version: Agent版本
            description: 报告描述

        Returns:
            评估报告
        """
        import uuid

        # 计算各维度评分
        dimension_scores = {}
        for category, category_metrics in metrics.items():
            if category_metrics:
                # 取该维度所有指标的平均值
                values = [m.value for m in category_metrics.values()]
                dimension_scores[category] = sum(values) / len(values) if values else 0.0

        # 计算综合评分（加权平均）
        weights = {
            "effectiveness": 0.25,
            "efficiency": 0.15,
            "robustness": 0.20,
            "safety": 0.20,
            "autonomy": 0.10,
            "explainability": 0.10,
        }
        overall_score = sum(
            dimension_scores.get(dim, 0.0) * weight
            for dim, weight in weights.items()
        )

        # 生成改进建议
        recommendations = cls._generate_recommendations(metrics, dimension_scores)

        return cls(
            report_id=str(uuid.uuid4())[:8],
            created_at=datetime.now().isoformat(),
            agent_version=agent_version,
            description=description,
            summary=result,
            metrics=metrics,
            test_results=result.get("test_results", []),
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            recommendations=recommendations,
        )

    @staticmethod
    def _generate_recommendations(
        metrics: Dict[str, Dict[str, MetricValue]],
        dimension_scores: Dict[str, float],
    ) -> List[str]:
        """生成改进建议."""
        recommendations = []

        # 基于各维度评分生成建议
        if dimension_scores.get("effectiveness", 1.0) < 0.7:
            recommendations.append("有效性指标偏低，建议优化意图识别准确率和任务完成率")

        if dimension_scores.get("efficiency", 1.0) < 0.7:
            recommendations.append("效率指标偏低，建议优化响应时间和资源消耗")

        if dimension_scores.get("robustness", 1.0) < 0.7:
            recommendations.append("鲁棒性指标偏低，建议加强错误处理和容错机制")

        if dimension_scores.get("safety", 1.0) < 0.7:
            recommendations.append("安全性指标偏低，建议加强规则验证和越权检测")

        if dimension_scores.get("autonomy", 1.0) < 0.7:
            recommendations.append("自主性指标偏低，建议提升工具自主选用和动态调整能力")

        if dimension_scores.get("explainability", 1.0) < 0.7:
            recommendations.append("可解释性指标偏低，建议增强推理过程的透明度")

        # 基于具体指标生成建议
        effectiveness = metrics.get("effectiveness", {})
        if effectiveness.get("task_success_rate", MetricValue("", 1.0)).value < 0.8:
            recommendations.append("任务成功率低于80%，建议检查核心逻辑和边界条件处理")

        efficiency = metrics.get("efficiency", {})
        if efficiency.get("avg_response_time", MetricValue("", 0.0)).value > 5000:
            recommendations.append("平均响应时间超过5秒，建议优化性能瓶颈")

        robustness = metrics.get("robustness", {})
        if robustness.get("tool_failure_rate", MetricValue("", 0.0)).value > 0.1:
            recommendations.append("工具调用失败率超过10%，建议增强工具容错和降级策略")

        if not recommendations:
            recommendations.append("各项指标表现良好，继续保持！")

        return recommendations
