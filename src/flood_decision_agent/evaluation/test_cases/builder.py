"""测试用例构建器.

提供流式API和预设模板用于快速创建测试用例。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from flood_decision_agent.evaluation.test_cases.base import (
    ExpectedResult,
    TestCase,
    TestCaseType,
    TestPriority,
    TestSuite,
)


class TestCaseBuilder:
    """测试用例构建器.

    提供流式API构建测试用例：

    Example:
        case = (TestCaseBuilder()
            .with_id("POS_001")
            .with_name("标准请求")
            .with_input("调整流量到10000")
            .expect_success()
            .with_min_reliability(0.7)
            .build())
    """

    def __init__(self):
        self._id = ""
        self._name = ""
        self._description = ""
        self._case_type = TestCaseType.POSITIVE
        self._priority = TestPriority.MEDIUM
        self._input_text = ""
        self._structured_input: Optional[Dict[str, Any]] = None
        self._input_type = "natural_language"
        self._expected = ExpectedResult()
        self._reference_solution: Optional[Dict[str, Any]] = None
        self._tags: List[str] = []

    def with_id(self, id: str) -> "TestCaseBuilder":
        """设置ID."""
        self._id = id
        return self

    def with_name(self, name: str) -> "TestCaseBuilder":
        """设置名称."""
        self._name = name
        return self

    def with_description(self, description: str) -> "TestCaseBuilder":
        """设置描述."""
        self._description = description
        return self

    def with_type(self, case_type: TestCaseType) -> "TestCaseBuilder":
        """设置类型."""
        self._case_type = case_type
        return self

    def with_priority(self, priority: TestPriority) -> "TestCaseBuilder":
        """设置优先级."""
        self._priority = priority
        return self

    def with_input(self, text: str) -> "TestCaseBuilder":
        """设置自然语言输入."""
        self._input_text = text
        self._input_type = "natural_language"
        return self

    def with_structured_input(self, data: Dict[str, Any]) -> "TestCaseBuilder":
        """设置结构化输入."""
        self._structured_input = data
        self._input_type = "structured"
        return self

    def expect_success(self) -> "TestCaseBuilder":
        """期望成功."""
        self._expected.success = True
        return self

    def expect_failure(self) -> "TestCaseBuilder":
        """期望失败."""
        self._expected.success = False
        return self

    def with_expected_task_type(self, task_type: str) -> "TestCaseBuilder":
        """设置期望任务类型."""
        self._expected.expected_task_type = task_type
        return self

    def with_expected_outputs(self, outputs: List[str]) -> "TestCaseBuilder":
        """设置期望输出."""
        self._expected.expected_outputs = outputs
        return self

    def with_min_reliability(self, score: float) -> "TestCaseBuilder":
        """设置最小可靠性评分."""
        self._expected.min_reliability_score = score
        return self

    def with_max_response_time(self, ms: float) -> "TestCaseBuilder":
        """设置最大响应时间."""
        self._expected.max_response_time_ms = ms
        return self

    def with_required_rules(self, rules: List[str]) -> "TestCaseBuilder":
        """设置必需规则."""
        self._expected.required_rules = rules
        return self

    def with_reference_solution(self, solution: Dict[str, Any]) -> "TestCaseBuilder":
        """设置参考解法."""
        self._reference_solution = solution
        return self

    def with_tags(self, tags: List[str]) -> "TestCaseBuilder":
        """设置标签."""
        self._tags = tags
        return self

    def add_tag(self, tag: str) -> "TestCaseBuilder":
        """添加标签."""
        self._tags.append(tag)
        return self

    def build(self) -> TestCase:
        """构建测试用例."""
        if not self._id:
            raise ValueError("测试用例ID不能为空")
        if not self._name:
            raise ValueError("测试用例名称不能为空")

        return TestCase(
            id=self._id,
            name=self._name,
            description=self._description,
            case_type=self._case_type,
            priority=self._priority,
            input_text=self._input_text,
            structured_input=self._structured_input,
            input_type=self._input_type,
            expected=self._expected,
            reference_solution=self._reference_solution,
            tags=self._tags,
        )


class TestSuiteBuilder:
    """测试集构建器."""

    def __init__(self, name: str = "default"):
        self._name = name
        self._description = ""
        self._version = "1.0"
        self._cases: List[TestCase] = []

    def with_metadata(self, description: str, version: str = "1.0") -> "TestSuiteBuilder":
        """设置元数据."""
        self._description = description
        self._version = version
        return self

    def add_case(self, case: TestCase) -> "TestSuiteBuilder":
        """添加测试用例."""
        self._cases.append(case)
        return self

    def add_cases(self, cases: List[TestCase]) -> "TestSuiteBuilder":
        """批量添加测试用例."""
        self._cases.extend(cases)
        return self

    def build(self) -> TestSuite:
        """构建测试集."""
        suite = TestSuite(name=self._name)
        suite.metadata = {
            "version": self._version,
            "description": self._description,
        }
        suite.test_cases = self._cases
        return suite


class TestTemplates:
    """测试用例模板.

    提供常用测试场景的预设模板。
    """

    @staticmethod
    def flood_dispatch(
        case_id: str,
        name: str,
        target_flow: int,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> TestCase:
        """创建洪水调度测试用例模板."""
        builder = (
            TestCaseBuilder()
            .with_id(case_id)
            .with_name(name)
            .with_type(TestCaseType.POSITIVE)
            .with_priority(TestPriority.CRITICAL)
            .with_input(f"调整出库流量到{target_flow}立方米每秒")
            .expect_success()
            .with_expected_task_type("flood_dispatch")
            .with_expected_outputs(["dispatch_plan", "dispatch_order"])
            .with_min_reliability(0.7)
            .add_tag("flood")
        )

        if constraints:
            builder.with_structured_input({
                "task_type": "flood_dispatch",
                "target": {"outflow": target_flow},
                "constraints": constraints,
            })

        return builder.build()

    @staticmethod
    def invalid_input(
        case_id: str,
        name: str,
        input_text: str,
        expected_error: str = "",
    ) -> TestCase:
        """创建无效输入测试用例模板."""
        return (
            TestCaseBuilder()
            .with_id(case_id)
            .with_name(name)
            .with_type(TestCaseType.NEGATIVE)
            .with_priority(TestPriority.HIGH)
            .with_input(input_text)
            .expect_failure()
            .add_tag("validation")
            .build()
        )

    @staticmethod
    def boundary_value(
        case_id: str,
        name: str,
        input_text: str,
        boundary_type: str = "min",
    ) -> TestCase:
        """创建边界值测试用例模板."""
        return (
            TestCaseBuilder()
            .with_id(case_id)
            .with_name(name)
            .with_type(TestCaseType.BOUNDARY)
            .with_priority(TestPriority.HIGH)
            .with_input(input_text)
            .expect_success()
            .add_tag("boundary")
            .add_tag(boundary_type)
            .build()
        )

    @staticmethod
    def safety_check(
        case_id: str,
        name: str,
        input_text: str,
        required_rule: str,
    ) -> TestCase:
        """创建安全检查测试用例模板."""
        return (
            TestCaseBuilder()
            .with_id(case_id)
            .with_name(name)
            .with_type(TestCaseType.SAFETY)
            .with_priority(TestPriority.CRITICAL)
            .with_input(input_text)
            .expect_success()
            .with_required_rules([required_rule])
            .add_tag("safety")
            .build()
        )

    @staticmethod
    def robustness_test(
        case_id: str,
        name: str,
        input_text: str,
        scenario: str = "network_delay",
    ) -> TestCase:
        """创建鲁棒性测试用例模板."""
        return (
            TestCaseBuilder()
            .with_id(case_id)
            .with_name(name)
            .with_type(TestCaseType.ROBUSTNESS)
            .with_priority(TestPriority.MEDIUM)
            .with_input(input_text)
            .expect_success()
            .with_max_response_time(60000.0)
            .add_tag("robustness")
            .add_tag(scenario)
            .build()
        )
