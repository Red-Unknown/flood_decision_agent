"""测试用例模块 - 基于Anthropic第一步：从手动测试开始.

定义测试用例结构和测试集管理，支持：
1. 正向测试用例（正常场景）
2. 反向测试用例（异常场景）
3. 边界测试用例
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestCaseType(Enum):
    """测试用例类型."""

    POSITIVE = "positive"  # 正向测试：验证正常功能
    NEGATIVE = "negative"  # 反向测试：验证异常处理
    BOUNDARY = "boundary"  # 边界测试：验证边界条件
    SAFETY = "safety"  # 安全测试：验证合规性
    ROBUSTNESS = "robustness"  # 鲁棒性测试：验证容错能力


class TestPriority(Enum):
    """测试优先级."""

    CRITICAL = 1  # 关键测试，必须通过
    HIGH = 2  # 高优先级
    MEDIUM = 3  # 中优先级
    LOW = 4  # 低优先级


@dataclass
class ExpectedResult:
    """预期结果定义."""

    success: bool = True
    expected_intent: Optional[str] = None
    expected_task_type: Optional[str] = None
    expected_outputs: List[str] = field(default_factory=list)
    expected_node_count_range: tuple = (0, 100)
    min_reliability_score: float = 0.0
    max_response_time_ms: float = 30000.0
    required_rules: List[str] = field(default_factory=list)
    custom_validators: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TestCase:
    """测试用例数据类.

    每个测试用例包含：
    - 输入数据
    - 预期结果
    - 成功标准
    - 参考解法（用于校准评分器）
    """

    # 基本信息
    id: str
    name: str
    description: str = ""
    case_type: TestCaseType = TestCaseType.POSITIVE
    priority: TestPriority = TestPriority.MEDIUM

    # 输入数据
    input_text: str = ""  # 自然语言输入
    structured_input: Optional[Dict[str, Any]] = None  # 结构化输入
    input_type: str = "natural_language"  # 输入类型

    # 预期结果
    expected: ExpectedResult = field(default_factory=ExpectedResult)

    # 参考解法（用于校准评分器）
    reference_solution: Optional[Dict[str, Any]] = None

    # 元数据
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "case_type": self.case_type.value,
            "priority": self.priority.value,
            "input_text": self.input_text,
            "structured_input": self.structured_input,
            "input_type": self.input_type,
            "expected": {
                "success": self.expected.success,
                "expected_intent": self.expected.expected_intent,
                "expected_task_type": self.expected.expected_task_type,
                "expected_outputs": self.expected.expected_outputs,
                "expected_node_count_range": self.expected.expected_node_count_range,
                "min_reliability_score": self.expected.min_reliability_score,
                "max_response_time_ms": self.expected.max_response_time_ms,
                "required_rules": self.expected.required_rules,
            },
            "reference_solution": self.reference_solution,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCase":
        """从字典创建."""
        expected_data = data.get("expected", {})
        expected = ExpectedResult(
            success=expected_data.get("success", True),
            expected_intent=expected_data.get("expected_intent"),
            expected_task_type=expected_data.get("expected_task_type"),
            expected_outputs=expected_data.get("expected_outputs", []),
            expected_node_count_range=tuple(expected_data.get("expected_node_count_range", [0, 100])),
            min_reliability_score=expected_data.get("min_reliability_score", 0.0),
            max_response_time_ms=expected_data.get("max_response_time_ms", 30000.0),
            required_rules=expected_data.get("required_rules", []),
        )

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            case_type=TestCaseType(data.get("case_type", "positive")),
            priority=TestPriority(data.get("priority", 3)),
            input_text=data.get("input_text", ""),
            structured_input=data.get("structured_input"),
            input_type=data.get("input_type", "natural_language"),
            expected=expected,
            reference_solution=data.get("reference_solution"),
            tags=data.get("tags", []),
        )


class TestSuite:
    """测试集管理类.

    管理一组测试用例，支持：
    - 加载/保存测试集
    - 按类型/优先级筛选
    - 平衡问题集构建
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self.test_cases: List[TestCase] = []
        self.metadata: Dict[str, Any] = {
            "version": "1.0",
            "description": "",
        }

    def add_test_case(self, test_case: TestCase) -> None:
        """添加测试用例."""
        self.test_cases.append(test_case)

    def add_test_cases(self, test_cases: List[TestCase]) -> None:
        """批量添加测试用例."""
        self.test_cases.extend(test_cases)

    def get_by_type(self, case_type: TestCaseType) -> List[TestCase]:
        """按类型获取测试用例."""
        return [tc for tc in self.test_cases if tc.case_type == case_type]

    def get_by_priority(self, priority: TestPriority) -> List[TestCase]:
        """按优先级获取测试用例."""
        return [tc for tc in self.test_cases if tc.priority == priority]

    def get_by_tags(self, tags: List[str]) -> List[TestCase]:
        """按标签获取测试用例."""
        return [tc for tc in self.test_cases if any(tag in tc.tags for tag in tags)]

    def get_balanced_suite(
        self,
        positive_ratio: float = 0.5,
        negative_ratio: float = 0.2,
        boundary_ratio: float = 0.15,
        safety_ratio: float = 0.1,
        robustness_ratio: float = 0.05,
    ) -> List[TestCase]:
        """获取平衡的测试集.

        避免类别不平衡导致的评估偏差。

        Args:
            positive_ratio: 正向测试比例
            negative_ratio: 反向测试比例
            boundary_ratio: 边界测试比例
            safety_ratio: 安全测试比例
            robustness_ratio: 鲁棒性测试比例

        Returns:
            平衡的测试用例列表
        """
        total = len(self.test_cases)
        if total == 0:
            return []

        balanced = []

        # 按比例从各类型中选取
        type_ratios = {
            TestCaseType.POSITIVE: positive_ratio,
            TestCaseType.NEGATIVE: negative_ratio,
            TestCaseType.BOUNDARY: boundary_ratio,
            TestCaseType.SAFETY: safety_ratio,
            TestCaseType.ROBUSTNESS: robustness_ratio,
        }

        for case_type, ratio in type_ratios.items():
            type_cases = self.get_by_type(case_type)
            count = int(total * ratio)
            # 按优先级排序后选取
            sorted_cases = sorted(type_cases, key=lambda x: x.priority.value)
            balanced.extend(sorted_cases[:count])

        return balanced

    def save_to_file(self, filepath: str) -> None:
        """保存测试集到文件."""
        data = {
            "name": self.name,
            "metadata": self.metadata,
            "test_cases": [tc.to_dict() for tc in self.test_cases],
        }
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "TestSuite":
        """从文件加载测试集."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        suite = cls(name=data.get("name", "default"))
        suite.metadata = data.get("metadata", {})

        for tc_data in data.get("test_cases", []):
            suite.add_test_case(TestCase.from_dict(tc_data))

        return suite

    def __len__(self) -> int:
        return len(self.test_cases)

    def __iter__(self):
        return iter(self.test_cases)
