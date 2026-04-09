from typing import Any, Dict, List

from src.flood_decision_agent.application.services.data_acquisition.adapters.base import (
    BaseInputAdapter,
)


class TextInputAdapter(BaseInputAdapter):
    """文本输入适配器 - 处理自然语言文本输入"""

    def __init__(self):
        super().__init__()
        self._supported_formats = ["text", "plain", "string"]

    def parse(self, input_data: Any) -> Dict[str, Any]:
        """
        解析自然语言文本输入

        Args:
            input_data: 文本输入数据（字符串）

        Returns:
            Dict[str, Any]: 解析后的结构化数据

        Raises:
            ValueError: 当输入数据不是字符串类型时
        """
        if not self.validate(input_data):
            raise ValueError("输入数据不能为空")

        if not isinstance(input_data, str):
            raise ValueError(f"期望字符串类型输入，但收到 {type(input_data).__name__}")

        text_content = input_data.strip()

        return {
            "type": "text",
            "content": text_content,
            "metadata": {
                **self.get_metadata(input_data),
                "length": len(text_content),
                "line_count": text_content.count("\n") + 1,
                "word_count": len(text_content.split()),
                "is_empty": len(text_content) == 0,
            },
            "format": "text",
        }

    def validate(self, input_data: Any) -> bool:
        """
        验证文本输入数据是否有效

        Args:
            input_data: 待验证的输入数据

        Returns:
            bool: 数据是否为有效的字符串类型
        """
        return input_data is not None and isinstance(input_data, str)

    def extract_keywords(self, input_data: str, keywords: List[str]) -> List[str]:
        """
        从文本中提取指定的关键词

        Args:
            input_data: 输入文本
            keywords: 要查找的关键词列表

        Returns:
            List[str]: 在文本中找到的关键词列表
        """
        if not isinstance(input_data, str):
            return []

        text_lower = input_data.lower()
        found_keywords = []

        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return found_keywords

    def split_sentences(self, input_data: str) -> List[str]:
        """
        将文本分割成句子列表

        Args:
            input_data: 输入文本

        Returns:
            List[str]: 句子列表
        """
        if not isinstance(input_data, str):
            return []

        import re

        sentences = re.split(r"[。！？.!?\n]+", input_data)
        return [s.strip() for s in sentences if s.strip()]
