import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class InputFormatDetector:
    """输入格式检测器 - 自动识别输入数据的格式类型"""

    # 支持的格式类型
    SUPPORTED_FORMATS = ["text", "csv", "tsv", "excel"]

    # Excel文件魔数
    EXCEL_MAGIC = {
        "xlsx": b"PK",  # ZIP格式，用于.xlsx
        "xls": b"\xd0\xcf\x11\xe0",  # OLE格式，用于.xls
    }

    def __init__(self):
        self._confidence_threshold = 0.5

    def detect_format(self, input_data: Any) -> str:
        """
        检测输入数据的格式类型

        Args:
            input_data: 输入数据，可以是字符串、字节流或文件路径

        Returns:
            str: 识别出的格式类型 ("text", "csv", "tsv", "excel")

        Raises:
            ValueError: 当无法识别格式时
        """
        if input_data is None:
            raise ValueError("输入数据不能为空")

        # 根据输入类型进行不同的检测
        if isinstance(input_data, (str, Path)):
            # 可能是文件路径或纯文本
            path_str = str(input_data)
            if os.path.isfile(path_str):
                return self._detect_file_format(path_str)
            else:
                return self._detect_text_format(input_data)

        elif isinstance(input_data, bytes):
            return self._detect_bytes_format(input_data)

        else:
            raise ValueError(f"不支持的输入数据类型: {type(input_data).__name__}")

    def _detect_file_format(self, file_path: str) -> str:
        """
        检测文件格式

        Args:
            file_path: 文件路径

        Returns:
            str: 文件格式类型
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        # 根据扩展名判断
        if suffix in [".csv"]:
            return "csv"
        elif suffix in [".tsv"]:
            return "tsv"
        elif suffix in [".xlsx", ".xls"]:
            return "excel"
        elif suffix in [".txt", ".md", ".json", ".yaml", ".yml"]:
            return "text"

        # 如果扩展名无法识别，尝试读取内容判断
        try:
            with open(file_path, "rb") as f:
                first_bytes = f.read(1024)
                return self._detect_bytes_format(first_bytes)
        except Exception:
            return "text"

    def _detect_text_format(self, text: str) -> str:
        """
        检测文本数据的格式

        Args:
            text: 文本字符串

        Returns:
            str: 文本格式类型
        """
        if not isinstance(text, str):
            return "text"

        text = text.strip()

        if not text:
            return "text"

        lines = text.split("\n")

        if not lines:
            return "text"

        # 检查是否为表格格式
        first_line = lines[0]

        # 检测TSV（制表符分隔）
        if "\t" in first_line:
            tab_count = first_line.count("\t")
            comma_count = first_line.count(",")
            if tab_count > comma_count:
                return "tsv"

        # 检测CSV（逗号分隔）
        if "," in first_line:
            # 检查是否每行都有相似数量的逗号
            comma_counts = [line.count(",") for line in lines if line.strip()]
            if len(set(comma_counts)) <= 1 and comma_counts[0] > 0:
                return "csv"

        # 检测分号分隔（某些欧洲CSV格式）
        if ";" in first_line:
            semicolon_counts = [line.count(";") for line in lines if line.strip()]
            if len(set(semicolon_counts)) <= 1 and semicolon_counts[0] > 0:
                return "csv"

        # 默认为纯文本
        return "text"

    def _detect_bytes_format(self, data: bytes) -> str:
        """
        检测字节流的格式

        Args:
            data: 字节流数据

        Returns:
            str: 字节流格式类型
        """
        if not data:
            return "text"

        # 检查Excel魔数
        if data.startswith(self.EXCEL_MAGIC["xlsx"]):
            return "excel"
        elif data.startswith(self.EXCEL_MAGIC["xls"]):
            return "excel"

        # 尝试作为文本解码
        try:
            text = data.decode("utf-8")
            return self._detect_text_format(text)
        except UnicodeDecodeError:
            try:
                text = data.decode("gbk")
                return self._detect_text_format(text)
            except UnicodeDecodeError:
                pass

        # 无法识别时返回text
        return "text"

    def detect_with_confidence(self, input_data: Any) -> Dict[str, float]:
        """
        检测格式并返回置信度分数

        Args:
            input_data: 输入数据

        Returns:
            Dict[str, float]: 各格式的置信度分数
        """
        confidence_scores = {fmt: 0.0 for fmt in self.SUPPORTED_FORMATS}

        if input_data is None:
            return confidence_scores

        try:
            detected = self.detect_format(input_data)
            confidence_scores[detected] = 1.0
        except ValueError:
            pass

        return confidence_scores

    def get_supported_formats(self) -> List[str]:
        """
        获取支持的格式列表

        Returns:
            List[str]: 支持的格式类型列表
        """
        return self.SUPPORTED_FORMATS.copy()

    def is_format_supported(self, format_type: str) -> bool:
        """
        检查格式是否受支持

        Args:
            format_type: 格式类型

        Returns:
            bool: 是否支持该格式
        """
        return format_type in self.SUPPORTED_FORMATS
