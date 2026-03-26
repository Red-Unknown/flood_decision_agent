"""默认报告模板."""

from __future__ import annotations

from typing import Any, Dict


class DefaultTemplate:
    """默认HTML报告模板."""

    @staticmethod
    def render(data: Dict[str, Any]) -> str:
        """渲染报告.

        Args:
            data: 报告数据

        Returns:
            HTML字符串
        """
        score = data.get("overall_score", 0)
        score_class = "good" if score >= 0.8 else "medium" if score >= 0.6 else "bad"
        score_color = "#4CAF50" if score >= 0.8 else "#FFC107" if score >= 0.6 else "#f44336"

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent评估报告 - {data.get('report_id', 'unknown')}</title>
    <style>
        :root {{
            --primary-color: #4CAF50;
            --secondary-color: #2196F3;
            --warning-color: #FFC107;
            --danger-color: #f44336;
            --bg-color: #f5f5f5;
            --card-bg: #ffffff;
            --text-color: #333333;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .meta {{
            opacity: 0.9;
            font-size: 0.95em;
        }}

        .score-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .score-display {{
            font-size: 5em;
            font-weight: bold;
            color: {score_color};
            margin: 20px 0;
        }}

        .score-label {{
            font-size: 1.2em;
            color: #666;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .card h2 {{
            font-size: 1.3em;
            margin-bottom: 16px;
            color: var(--primary-color);
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}

        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }}

        .stat-row:last-child {{
            border-bottom: none;
        }}

        .stat-label {{
            color: #666;
        }}

        .stat-value {{
            font-weight: 600;
        }}

        .dimension-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}

        .dimension-item {{
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}

        .dimension-name {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
        }}

        .dimension-score {{
            font-size: 1.8em;
            font-weight: bold;
        }}

        .recommendations {{
            background: #fff3cd;
            border-left: 4px solid var(--warning-color);
            padding: 20px;
            border-radius: 8px;
        }}

        .recommendations h3 {{
            color: #856404;
            margin-bottom: 12px;
        }}

        .recommendations ul {{
            list-style: none;
            padding-left: 0;
        }}

        .recommendations li {{
            padding: 8px 0;
            padding-left: 24px;
            position: relative;
        }}

        .recommendations li::before {{
            content: "💡";
            position: absolute;
            left: 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .status-pass {{
            color: var(--primary-color);
        }}

        .status-fail {{
            color: var(--danger-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Agent量化评估报告</h1>
            <div class="meta">
                <p>报告ID: {data.get('report_id', 'unknown')}</p>
                <p>生成时间: {data.get('created_at', 'unknown')}</p>
                <p>Agent版本: {data.get('agent_version', 'unknown')}</p>
            </div>
        </div>

        <div class="score-card">
            <div class="score-label">综合评分</div>
            <div class="score-display">{score:.1%}</div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>汇总统计</h2>
                <div class="stat-row">
                    <span class="stat-label">总测试数</span>
                    <span class="stat-value">{data.get('summary', {{}}).get('total', 0)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">通过数</span>
                    <span class="stat-value" style="color: var(--primary-color);">{data.get('summary', {{}}).get('passed', 0)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">失败数</span>
                    <span class="stat-value" style="color: var(--danger-color);">{data.get('summary', {{}}).get('failed', 0)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">通过率</span>
                    <span class="stat-value">{data.get('summary', {{}}).get('pass_rate', 0):.1%}</span>
                </div>
            </div>

            <div class="card">
                <h2>六大维度评分</h2>
                <div class="dimension-grid">
                    {DefaultTemplate._render_dimensions(data.get('dimension_scores', {{}}))}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        return html

    @staticmethod
    def _render_dimensions(dimensions: Dict[str, float]) -> str:
        """渲染维度评分."""
        translations = {
            "effectiveness": "有效性",
            "efficiency": "效率",
            "robustness": "鲁棒性",
            "safety": "安全性",
            "autonomy": "自主性",
            "explainability": "可解释性",
        }

        html = ""
        for key, score in dimensions.items():
            name = translations.get(key, key)
            color = "#4CAF50" if score >= 0.8 else "#FFC107" if score >= 0.6 else "#f44336"
            html += f"""
                    <div class="dimension-item">
                        <div class="dimension-name">{name}</div>
                        <div class="dimension-score" style="color: {color}">{score:.0%}</div>
                    </div>"""
        return html
