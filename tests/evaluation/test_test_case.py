"""测试用例模块测试."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from flood_decision_agent.evaluation.test_case import (
    ExpectedResult,
    TestCase,
    TestCaseType,
    TestPriority,
    TestSuite,
    create_default_flood_dispatch_test_suite,
)


class TestExpectedResult:
    """测试预期结果类."""

    def test_default_values(self):
        """测试默认值."""
        expected = ExpectedResult()
        assert expected.success is True
        assert expected.expected_intent is None
        assert expected.expected_outputs == []
        assert expected.expected_node_count_range == (0, 100)
        assert expected.min_reliability_score == 0.0
        assert expected.max_response_time_ms == 30000.0

    def test_custom_values(self):
        """测试自定义值."""
        expected = ExpectedResult(
            success=False,
            expected_intent="flood_dispatch",
            expected_outputs=["plan", "order"],
            min_reliability_score=0.8,
        )
        assert expected.success is False
        assert expected.expected_intent == "flood_dispatch"
        assert expected.expected_outputs == ["plan", "order"]
        assert expected.min_reliability_score == 0.8


class TestTestCase:
    """测试测试用例类."""

    def test_default_creation(self):
        """测试默认创建."""
        case = TestCase(id="TEST_001", name="测试用例")
        assert case.id == "TEST_001"
        assert case.name == "测试用例"
        assert case.case_type == TestCaseType.POSITIVE
        assert case.priority == TestPriority.MEDIUM
        assert case.input_type == "natural_language"

    def test_full_creation(self):
        """测试完整创建."""
        case = TestCase(
            id="TEST_002",
            name="完整测试",
            description="详细描述",
            case_type=TestCaseType.NEGATIVE,
            priority=TestPriority.HIGH,
            input_text="测试输入",
            input_type="natural_language",
            expected=ExpectedResult(success=False),
            tags=["tag1", "tag2"],
        )
        assert case.description == "详细描述"
        assert case.case_type == TestCaseType.NEGATIVE
        assert case.priority == TestPriority.HIGH
        assert case.input_text == "测试输入"
        assert case.tags == ["tag1", "tag2"]

    def test_to_dict(self):
        """测试转换为字典."""
        case = TestCase(
            id="TEST_003",
            name="字典测试",
            input_text="输入",
            expected=ExpectedResult(expected_intent="intent"),
        )
        data = case.to_dict()
        assert data["id"] == "TEST_003"
        assert data["name"] == "字典测试"
        assert data["input_text"] == "输入"
        assert data["expected"]["expected_intent"] == "intent"

    def test_from_dict(self):
        """测试从字典创建."""
        data = {
            "id": "TEST_004",
            "name": "反序列化测试",
            "case_type": "boundary",
            "priority": 1,
            "input_text": "输入文本",
            "input_type": "structured",
            "structured_input": {"key": "value"},
            "expected": {
                "success": True,
                "expected_task_type": "flood",
                "min_reliability_score": 0.7,
            },
            "tags": ["boundary", "test"],
        }
        case = TestCase.from_dict(data)
        assert case.id == "TEST_004"
        assert case.case_type == TestCaseType.BOUNDARY
        assert case.priority == TestPriority.CRITICAL
        assert case.input_type == "structured"
        assert case.structured_input == {"key": "value"}
        assert case.expected.expected_task_type == "flood"


class TestTestSuite:
    """测试测试集类."""

    def test_creation(self):
        """测试创建."""
        suite = TestSuite(name="my_suite")
        assert suite.name == "my_suite"
        assert len(suite) == 0

    def test_add_test_case(self):
        """测试添加测试用例."""
        suite = TestSuite()
        case = TestCase(id="T001", name="测试1")
        suite.add_test_case(case)
        assert len(suite) == 1

    def test_add_test_cases(self):
        """测试批量添加."""
        suite = TestSuite()
        cases = [
            TestCase(id="T001", name="测试1"),
            TestCase(id="T002", name="测试2"),
        ]
        suite.add_test_cases(cases)
        assert len(suite) == 2

    def test_get_by_type(self):
        """测试按类型获取."""
        suite = TestSuite()
        suite.add_test_case(TestCase(id="P001", name="正向", case_type=TestCaseType.POSITIVE))
        suite.add_test_case(TestCase(id="N001", name="反向", case_type=TestCaseType.NEGATIVE))
        suite.add_test_case(TestCase(id="P002", name="正向2", case_type=TestCaseType.POSITIVE))

        positive_cases = suite.get_by_type(TestCaseType.POSITIVE)
        assert len(positive_cases) == 2

        negative_cases = suite.get_by_type(TestCaseType.NEGATIVE)
        assert len(negative_cases) == 1

    def test_get_by_priority(self):
        """测试按优先级获取."""
        suite = TestSuite()
        suite.add_test_case(TestCase(id="C001", name="关键", priority=TestPriority.CRITICAL))
        suite.add_test_case(TestCase(id="H001", name="高", priority=TestPriority.HIGH))

        critical_cases = suite.get_by_priority(TestPriority.CRITICAL)
        assert len(critical_cases) == 1
        assert critical_cases[0].id == "C001"

    def test_get_by_tags(self):
        """测试按标签获取."""
        suite = TestSuite()
        suite.add_test_case(TestCase(id="T001", name="测试1", tags=["flood", "basic"]))
        suite.add_test_case(TestCase(id="T002", name="测试2", tags=["drought"]))
        suite.add_test_case(TestCase(id="T003", name="测试3", tags=["flood", "advanced"]))

        flood_cases = suite.get_by_tags(["flood"])
        assert len(flood_cases) == 2

    def test_get_balanced_suite(self):
        """测试获取平衡测试集."""
        suite = TestSuite()

        # 添加不同类型测试用例
        for i in range(10):
            suite.add_test_case(TestCase(id=f"P{i:03d}", name=f"正向{i}", case_type=TestCaseType.POSITIVE))
        for i in range(5):
            suite.add_test_case(TestCase(id=f"N{i:03d}", name=f"反向{i}", case_type=TestCaseType.NEGATIVE))
        for i in range(3):
            suite.add_test_case(TestCase(id=f"B{i:03d}", name=f"边界{i}", case_type=TestCaseType.BOUNDARY))

        balanced = suite.get_balanced_suite(
            positive_ratio=0.5,
            negative_ratio=0.3,
            boundary_ratio=0.2,
        )

        # 总共18个用例
        # 正向: 18 * 0.5 = 9
        # 反向: 18 * 0.3 = 5
        # 边界: 18 * 0.2 = 3
        assert len(balanced) == 17  # 9 + 5 + 3

    def test_save_and_load(self):
        """测试保存和加载."""
        suite = TestSuite(name="test_suite")
        suite.add_test_case(TestCase(id="T001", name="测试1", input_text="输入1"))
        suite.add_test_case(TestCase(id="T002", name="测试2", input_text="输入2"))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            # 保存
            suite.save_to_file(temp_path)
            assert Path(temp_path).exists()

            # 加载
            loaded_suite = TestSuite.load_from_file(temp_path)
            assert loaded_suite.name == "test_suite"
            assert len(loaded_suite) == 2

            # 验证内容
            case_ids = [tc.id for tc in loaded_suite.test_cases]
            assert "T001" in case_ids
            assert "T002" in case_ids
        finally:
            Path(temp_path).unlink()

    def test_iteration(self):
        """测试迭代."""
        suite = TestSuite()
        suite.add_test_case(TestCase(id="T001", name="测试1"))
        suite.add_test_case(TestCase(id="T002", name="测试2"))

        ids = [case.id for case in suite]
        assert ids == ["T001", "T002"]


class TestDefaultSuite:
    """测试默认测试集."""

    def test_create_default_suite(self):
        """测试创建默认测试集."""
        suite = create_default_flood_dispatch_test_suite()

        assert suite.name == "flood_dispatch_default"
        assert len(suite) > 0

        # 验证包含各类测试
        assert len(suite.get_by_type(TestCaseType.POSITIVE)) > 0
        assert len(suite.get_by_type(TestCaseType.NEGATIVE)) > 0
        assert len(suite.get_by_type(TestCaseType.BOUNDARY)) > 0
        assert len(suite.get_by_type(TestCaseType.SAFETY)) > 0
        assert len(suite.get_by_type(TestCaseType.ROBUSTNESS)) > 0

    def test_default_suite_content(self):
        """测试默认测试集内容."""
        suite = create_default_flood_dispatch_test_suite()

        # 验证关键测试用例存在
        case_ids = [tc.id for tc in suite.test_cases]
        assert "POS_001" in case_ids  # 标准洪水调度
        assert "NEG_001" in case_ids  # 无效流量值
        assert "BND_001" in case_ids  # 流量边界
        assert "SAF_001" in case_ids  # 安全规则


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
