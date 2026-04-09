from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseInputAdapter(ABC):
    """多模态输入适配器抽象基类"""

    def __init__(self):
        self._supported_formats: List[str] = []

    @property
    def supported_formats(self) -> List[str]:
        """返回该适配器支持的格式列表"""
        return self._supported_formats

    @abstractmethod
    def parse(self, input_data: Any) -> Dict[str, Any]:
        """
        解析输入数据并返回结构化数据字典

        Args:
            input_data: 输入数据，可以是文本、文件路径、字节流等

        Returns:
            Dict[str, Any]: 解析后的结构化数据，包含以下字段:
                - type: 数据类型标识
                - content: 原始内容或处理后的数据
                - metadata: 元数据信息
                - format: 输入格式
        """
        pass

    def validate(self, input_data: Any) -> bool:
        """
        验证输入数据是否有效

        Args:
            input_data: 待验证的输入数据

        Returns:
            bool: 数据是否有效
        """
        return input_data is not None

    def get_metadata(self, input_data: Any) -> Dict[str, Any]:
        """
        获取输入数据的元数据信息

        Args:
            input_data: 输入数据

        Returns:
            Dict[str, Any]: 元数据字典
        """
        return {
            "adapter": self.__class__.__name__,
            "supported_formats": self.supported_formats,
        }
