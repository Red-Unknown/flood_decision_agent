import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.flood_decision_agent.application.services.data_acquisition.adapters.base import (
    BaseInputAdapter,
)


class FileInputAdapter(BaseInputAdapter):
    """文件输入适配器 - 处理文件上传（CSV和Excel）"""

    def __init__(self):
        super().__init__()
        self._supported_formats = ["csv", "excel", "xlsx", "xls"]

    def parse(
        self,
        input_data: Union[str, bytes, Path],
        file_format: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        解析文件输入（CSV和Excel）

        Args:
            input_data: 文件路径（字符串或Path）或文件字节流
            file_format: 文件格式，如果为None则自动检测
            **kwargs: 传递给pandas读取函数的额外参数

        Returns:
            Dict[str, Any]: 解析后的结构化数据

        Raises:
            ValueError: 当输入数据格式不正确或文件不存在时
            ImportError: 当缺少必要的依赖时
        """
        if not self.validate(input_data):
            raise ValueError("输入数据不能为空")

        try:
            import pandas as pd
        except ImportError:
            raise ImportError("使用FileInputAdapter需要安装pandas: pip install pandas")

        # 检测文件格式
        detected_format = file_format or self._detect_file_format(input_data)

        if detected_format not in self._supported_formats:
            raise ValueError(f"不支持的文件格式: {detected_format}")

        try:
            # 根据输入类型和数据格式读取数据
            if isinstance(input_data, (str, Path)):
                df = self._read_from_path(input_data, detected_format, **kwargs)
                file_path = str(input_data)
                file_size = os.path.getsize(input_data) if os.path.exists(input_data) else 0
            elif isinstance(input_data, bytes):
                df = self._read_from_bytes(input_data, detected_format, **kwargs)
                file_path = None
                file_size = len(input_data)
            else:
                raise ValueError(f"不支持的输入数据类型: {type(input_data).__name__}")

            # 转换为结构化数据
            headers = df.columns.tolist()
            records = df.to_dict("records")
            rows = df.values.tolist()

            return {
                "type": "file",
                "content": {
                    "headers": headers,
                    "rows": rows,
                    "records": records,
                    "dataframe": df,
                },
                "metadata": {
                    **self.get_metadata(input_data),
                    "file_path": file_path,
                    "file_size": file_size,
                    "file_format": detected_format,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                },
                "format": detected_format,
            }

        except Exception as e:
            raise ValueError(f"解析文件时发生错误: {str(e)}")

    def validate(self, input_data: Any) -> bool:
        """
        验证文件输入数据是否有效

        Args:
            input_data: 待验证的输入数据

        Returns:
            bool: 数据是否为有效的文件输入
        """
        if input_data is None:
            return False

        # 检查是否为文件路径
        if isinstance(input_data, (str, Path)):
            path = Path(input_data)
            return path.exists() and path.is_file()

        # 检查是否为字节流
        if isinstance(input_data, bytes):
            return len(input_data) > 0

        return False

    def _detect_file_format(self, input_data: Union[str, bytes, Path]) -> str:
        """
        自动检测文件格式

        Args:
            input_data: 文件路径或字节流

        Returns:
            str: 检测到的文件格式
        """
        # 如果是路径，从扩展名检测
        if isinstance(input_data, (str, Path)):
            path = Path(input_data)
            suffix = path.suffix.lower()

            if suffix in [".csv"]:
                return "csv"
            elif suffix in [".xlsx"]:
                return "xlsx"
            elif suffix in [".xls"]:
                return "xls"

        # 如果是字节流，尝试从内容检测
        if isinstance(input_data, bytes):
            # Excel文件以特定字节开头
            if input_data.startswith(b"PK"):
                return "xlsx"
            elif input_data.startswith(b"\xd0\xcf\x11\xe0"):
                return "xls"
            else:
                return "csv"

        # 默认返回csv
        return "csv"

    def _read_from_path(
        self, file_path: Union[str, Path], file_format: str, **kwargs
    ) -> "pandas.DataFrame":
        """
        从文件路径读取数据

        Args:
            file_path: 文件路径
            file_format: 文件格式
            **kwargs: 传递给pandas读取函数的额外参数

        Returns:
            pandas.DataFrame: 读取的数据框
        """
        import pandas as pd

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if file_format == "csv":
            return pd.read_csv(path, **kwargs)
        elif file_format in ["xlsx", "xls", "excel"]:
            return pd.read_excel(path, **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")

    def _read_from_bytes(
        self, data: bytes, file_format: str, **kwargs
    ) -> "pandas.DataFrame":
        """
        从字节流读取数据

        Args:
            data: 文件字节流
            file_format: 文件格式
            **kwargs: 传递给pandas读取函数的额外参数

        Returns:
            pandas.DataFrame: 读取的数据框
        """
        import io

        import pandas as pd

        if file_format == "csv":
            return pd.read_csv(io.BytesIO(data), **kwargs)
        elif file_format in ["xlsx", "xls", "excel"]:
            return pd.read_excel(io.BytesIO(data), **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")

    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名列表

        Returns:
            List[str]: 支持的文件扩展名列表
        """
        return [".csv", ".xlsx", ".xls"]

    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 文件信息字典
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        stat = path.stat()

        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": stat.st_size,
            "extension": path.suffix.lower(),
            "format": self._detect_file_format(path),
            "modified_time": stat.st_mtime,
        }
