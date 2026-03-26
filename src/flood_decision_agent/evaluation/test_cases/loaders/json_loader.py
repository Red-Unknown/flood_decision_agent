"""JSON测试加载器."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from flood_decision_agent.evaluation.test_cases.base import TestCase, TestSuite
from flood_decision_agent.infra.logging import get_logger


class JsonTestLoader:
    """JSON格式测试加载器."""

    def __init__(self):
        self.logger = get_logger().bind(name=self.__class__.__name__)

    def load(self, filepath: str) -> TestSuite:
        """从JSON文件加载测试集.

        Args:
            filepath: JSON文件路径

        Returns:
            测试集
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"测试文件不存在: {filepath}")

        self.logger.info(f"加载测试文件: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return self._parse_suite(data)

    def load_multiple(self, filepaths: List[str]) -> TestSuite:
        """加载多个测试文件并合并.

        Args:
            filepaths: 文件路径列表

        Returns:
            合并后的测试集
        """
        combined = TestSuite(name="combined")

        for filepath in filepaths:
            suite = self.load(filepath)
            combined.add_test_cases(suite.test_cases)
            combined.metadata["sources"] = combined.metadata.get("sources", []) + [filepath]

        return combined

    def load_from_directory(self, directory: str, pattern: str = "*.json") -> TestSuite:
        """从目录加载所有测试文件.

        Args:
            directory: 目录路径
            pattern: 文件匹配模式

        Returns:
            合并后的测试集
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")

        files = list(dir_path.glob(pattern))
        if not files:
            self.logger.warning(f"目录中未找到匹配的文件: {directory}/{pattern}")
            return TestSuite(name="empty")

        return self.load_multiple([str(f) for f in files])

    def save(self, suite: TestSuite, filepath: str) -> None:
        """保存测试集到JSON文件.

        Args:
            suite: 测试集
            filepath: 输出文件路径
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "name": suite.name,
            "metadata": suite.metadata,
            "test_cases": [tc.to_dict() for tc in suite.test_cases],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"测试集已保存: {filepath}")

    def _parse_suite(self, data: Dict[str, Any]) -> TestSuite:
        """解析测试集数据."""
        suite = TestSuite(name=data.get("name", "unnamed"))
        suite.metadata = data.get("metadata", {})

        for tc_data in data.get("test_cases", []):
            try:
                test_case = TestCase.from_dict(tc_data)
                suite.add_test_case(test_case)
            except Exception as e:
                self.logger.error(f"解析测试用例失败: {e}")

        self.logger.info(f"已加载 {len(suite)} 个测试用例")
        return suite
