"""极简报告模板."""

from __future__ import annotations

from typing import Any, Dict


class MinimalTemplate:
    """极简HTML报告模板."""

    @staticmethod
    def render(data: Dict[str, Any]) -> str:
        """渲染极简报告.

        Args:
            data: 报告数据

        Returns:
            HTML字符串
        """
        score = data.get("overall_score", 0)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>评估报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
        }}
        .summary {{
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background: #f5f5f5;
        }}
    </style>
</head>
<body>
    <h1>Agent评估报告</h1>
    <div class="score">{score:.1%}</div>
    <div class="summary">
        <table>
            <tr><th>指标</th><th>值</th></tr>
            <tr><td>总测试数</td><td>{data.get('summary', {{}}).get('total', 0)}</td></tr>
            <tr><td>通过</td><td>{data.get('summary', {{}}).get('passed', 0)}</td></tr>
            <tr><td>失败</td><td>{data.get('summary', {{}}).get('failed', 0)}</td></tr>
            <tr><td>通过率</td><td>{data.get('summary', {{}}).get('pass_rate', 0):.1%}</td></tr>
        </table>
    </div>
</body>
</html>"""
        return html
