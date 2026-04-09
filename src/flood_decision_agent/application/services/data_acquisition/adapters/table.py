import csv
import io
from typing import Any, Dict, List, Optional

from src.flood_decision_agent.application.services.data_acquisition.adapters.base import (
    BaseInputAdapter,
)


class TableInputAdapter(BaseInputAdapter):
    """表格输入适配器 - 处理CSV/TSV格式的表格粘贴"""

    def __init__(self):
        super().__init__()
        self._supported_formats = ["csv", "tsv", "table"]

    def parse(self, input_data: Any, delimiter: Optional[str] = None) -> Dict[str, Any]:
        """
        解析CSV/TSV格式的表格数据

        Args:
            input_data: 表格文本数据（字符串）
            delimiter: 分隔符，如果为None则自动检测

        Returns:
            Dict[str, Any]: 解析后的结构化数据

        Raises:
            ValueError: 当输入数据格式不正确时
        """
        if not self.validate(input_data):
            raise ValueError("输入数据不能为空")

        if not isinstance(input_data, str):
            raise ValueError(f"期望字符串类型输入，但收到 {type(input_data).__name__}")

        text_content = input_data.strip()

        if not text_content:
            raise ValueError("输入数据为空字符串")

        # 自动检测分隔符
        detected_delimiter = delimiter or self._detect_delimiter(text_content)

        try:
            # 使用StringIO将文本转换为文件对象
            csv_file = io.StringIO(text_content)

            # 读取CSV数据
            reader = csv.reader(csv_file, delimiter=detected_delimiter)
            rows = list(reader)

            if not rows:
                raise ValueError("未能解析出任何数据行")

            # 提取表头（第一行）和数据行
            headers = rows[0] if rows else []
            data_rows = rows[1:] if len(rows) > 1 else []

            # 转换为字典列表
            records = []
            for row in data_rows:
                record = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        record[header] = row[i]
                    else:
                        record[header] = ""
                records.append(record)

            return {
                "type": "table",
                "content": {
                    "headers": headers,
                    "rows": data_rows,
                    "records": records,
                },
                "metadata": {
                    **self.get_metadata(input_data),
                    "row_count": len(data_rows),
                    "column_count": len(headers),
                    "delimiter": detected_delimiter,
                    "detected_format": "tsv" if detected_delimiter == "\t" else "csv",
                },
                "format": "tsv" if detected_delimiter == "\t" else "csv",
            }

        except csv.Error as e:
            raise ValueError(f"CSV解析错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"解析表格数据时发生错误: {str(e)}")

    def validate(self, input_data: Any) -> bool:
        """
        验证表格输入数据是否有效

        Args:
            input_data: 待验证的输入数据

        Returns:
            bool: 数据是否为有效的表格格式
        """
        if input_data is None or not isinstance(input_data, str):
            return False

        text_content = input_data.strip()
        if not text_content:
            return False

        # 检查是否包含常见的分隔符
        lines = text_content.split("\n")
        if not lines:
            return False

        first_line = lines[0]
        return "," in first_line or "\t" in first_line or ";" in first_line

    def _detect_delimiter(self, text: str) -> str:
        """
        自动检测分隔符

        Args:
            text: 待检测的文本

        Returns:
            str: 检测到的分隔符
        """
        # 获取第一行进行分隔符检测
        first_line = text.split("\n")[0] if text else ""

        if not first_line:
            return ","

        # 统计各种分隔符的出现次数
        delimiters = {
            "\t": first_line.count("\t"),
            ",": first_line.count(","),
            ";": first_line.count(";"),
            "|": first_line.count("|"),
        }

        # 选择出现次数最多的分隔符
        max_delimiter = max(delimiters, key=delimiters.get)

        # 如果没有找到分隔符，默认使用逗号
        return max_delimiter if delimiters[max_delimiter] > 0 else ","

    def to_dict_list(self, input_data: str, delimiter: Optional[str] = None) -> List[Dict[str, str]]:
        """
        将表格数据转换为字典列表

        Args:
            input_data: 表格文本数据
            delimiter: 分隔符

        Returns:
            List[Dict[str, str]]: 字典列表
        """
        result = self.parse(input_data, delimiter)
        return result.get("content", {}).get("records", [])

    def get_column_names(self, input_data: str, delimiter: Optional[str] = None) -> List[str]:
        """
        获取表格的列名

        Args:
            input_data: 表格文本数据
            delimiter: 分隔符

        Returns:
            List[str]: 列名列表
        """
        result = self.parse(input_data, delimiter)
        return result.get("content", {}).get("headers", [])
