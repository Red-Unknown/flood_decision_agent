"""ModeDetector 集成测试.

测试 ModeDetector 与 DecisionChainGeneratorAgent 的集成功能。
"""

import os
import sys
import unittest
from typing import Any, Dict

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flood_decision_agent.agents.decision_chain import (
    DecisionChainGeneratorAgent,
    ModeDetector,
    ModeType,
)
from flood_decision_agent.core.task_graph import TaskGraph


class TestModeDetectorIntegration(unittest.TestCase):
    """ModeDetector 集成测试类."""

    def setUp(self):
        """测试前置准备."""
        self.agent = DecisionChainGeneratorAgent()
        self.mode_detector = ModeDetector()

    def test_mode_detector_initialization(self):
        """测试 ModeDetector 正确初始化."""
        self.assertIsNotNone(self.agent.mode_detector)
        self.assertIsInstance(self.agent.mode_detector, ModeDetector)

    def test_mode_detector_detect_simple(self):
        """测试 ModeDetector 识别 simple 模式."""
        simple_input = "什么是洪水预警？"
        mode = self.mode_detector.detect(simple_input)
        self.assertEqual(mode, ModeType.SIMPLE.value)

    def test_mode_detector_detect_plan(self):
        """测试 ModeDetector 识别 plan 模式."""
        plan_input = "设计一个洪水预警系统架构，需要包含数据采集模块和处理模块"
        mode = self.mode_detector.detect(plan_input)
        self.assertEqual(mode, ModeType.PLAN.value)

    def test_mode_detector_detect_spec(self):
        """测试 ModeDetector 识别 spec 模式."""
        spec_input = """设计一个完整的洪水预警系统，需要包含以下模块：
        1. 数据采集模块：负责从多个传感器收集水位、降雨量等数据
        2. 数据处理模块：对采集的数据进行清洗、分析和存储
        3. 预警模块：根据分析结果生成预警信息并推送给用户
        4. 可视化模块：展示实时数据和历史趋势
        系统需要支持高并发、高可用，并能够处理海量数据。"""
        mode = self.mode_detector.detect(spec_input)
        self.assertEqual(mode, ModeType.SPEC.value)

    def test_generate_with_mode_auto(self):
        """测试 generate_with_mode 自动检测模式."""
        simple_input = "什么是洪水预警？"
        task_graph, metadata = self.agent.generate_with_mode(simple_input, preferred_mode="auto")

        self.assertIsInstance(task_graph, TaskGraph)
        self.assertIn("mode", metadata)
        self.assertEqual(metadata["mode_source"], "auto")

    def test_generate_with_mode_simple(self):
        """测试 generate_with_mode 指定 simple 模式."""
        user_input = "查询今天的天气"
        task_graph, metadata = self.agent.generate_with_mode(user_input, preferred_mode="simple")

        self.assertIsInstance(task_graph, TaskGraph)
        self.assertEqual(metadata["mode"], "simple")
        self.assertEqual(metadata["mode_source"], "specified")
        self.assertEqual(metadata["optimization"]["mode"], "simple")

    def test_generate_with_mode_plan(self):
        """测试 generate_with_mode 指定 plan 模式."""
        user_input = "设计一个数据处理流程"
        task_graph, metadata = self.agent.generate_with_mode(user_input, preferred_mode="plan")

        self.assertIsInstance(task_graph, TaskGraph)
        self.assertEqual(metadata["mode"], "plan")
        self.assertEqual(metadata["mode_source"], "specified")

    def test_generate_with_mode_spec(self):
        """测试 generate_with_mode 指定 spec 模式."""
        user_input = "设计一个完整的系统架构，包含多个模块和详细的技术规范"
        task_graph, metadata = self.agent.generate_with_mode(user_input, preferred_mode="spec")

        self.assertIsInstance(task_graph, TaskGraph)
        self.assertEqual(metadata["mode"], "spec")
        self.assertEqual(metadata["mode_source"], "specified")
        self.assertIn("alternatives_count", metadata["optimization"])

    def test_generate_with_mode_invalid(self):
        """测试 generate_with_mode 处理无效模式."""
        user_input = "测试输入"
        task_graph, metadata = self.agent.generate_with_mode(user_input, preferred_mode="invalid_mode")

        self.assertIsInstance(task_graph, TaskGraph)
        # 无效模式应该回退到 auto 检测
        self.assertIn("mode", metadata)

    def test_generate_chain_uses_auto_mode(self):
        """测试 generate_chain 方法使用 auto 模式."""
        user_input = "什么是洪水预警？"
        task_graph, metadata = self.agent.generate_chain(user_input)

        self.assertIsInstance(task_graph, TaskGraph)
        self.assertIn("mode", metadata)
        self.assertEqual(metadata["mode_source"], "auto")

    def test_simple_mode_single_node(self):
        """测试 simple 模式只生成单个节点."""
        user_input = "简单查询"
        task_graph, metadata = self.agent.generate_with_mode(user_input, preferred_mode="simple")

        nodes = task_graph.get_all_nodes()
        # simple 模式应该只生成一个节点
        self.assertEqual(len(nodes), 1)

    def test_mode_detector_get_metrics(self):
        """测试 ModeDetector 获取指标功能."""
        user_input = "设计一个系统架构，包含数据采集和处理模块"
        metrics = self.mode_detector.get_metrics(user_input)

        self.assertGreater(metrics.char_count, 0)
        self.assertGreaterEqual(metrics.technical_term_count, 0)

    def test_mode_detector_get_detection_details(self):
        """测试 ModeDetector 获取检测详情功能."""
        user_input = "设计一个系统架构，包含数据采集和处理模块"
        details = self.mode_detector.get_detection_details(user_input)

        self.assertIn("mode", details)
        self.assertIn("metrics", details)
        self.assertIn("scores", details)
        self.assertIn("reason", details)


class TestModeIntegrationWithDifferentInputs(unittest.TestCase):
    """使用不同输入测试 Mode 集成."""

    def setUp(self):
        """测试前置准备."""
        self.agent = DecisionChainGeneratorAgent()

    def test_chinese_simple_query(self):
        """测试中文简单查询."""
        inputs = [
            "什么是洪水？",
            "怎么预警？",
            "告诉我天气",
            "为什么下雨？",
        ]
        for user_input in inputs:
            with self.subTest(input=user_input):
                task_graph, metadata = self.agent.generate_with_mode(user_input, preferred_mode="simple")
                self.assertIsInstance(task_graph, TaskGraph)
                self.assertEqual(metadata["mode"], "simple")

    def test_chinese_plan_query(self):
        """测试中文计划类查询."""
        inputs = [
            "设计一个预警系统架构",
            "如何构建微服务系统",
        ]
        for user_input in inputs:
            with self.subTest(input=user_input):
                mode = self.agent.mode_detector.detect(user_input)
                # 这些输入应该被识别为 plan 或 spec
                self.assertIn(mode, [ModeType.PLAN.value, ModeType.SPEC.value])

    def test_english_queries(self):
        """测试英文查询."""
        inputs = [
            ("What is flood warning?", ModeType.SIMPLE.value),
            ("How to design a system architecture?", ModeType.PLAN.value),
        ]
        for user_input, expected_mode in inputs:
            with self.subTest(input=user_input):
                mode = self.agent.mode_detector.detect(user_input)
                self.assertEqual(mode, expected_mode)


if __name__ == "__main__":
    # 检查环境变量
    if not os.environ.get("KIMI_API_KEY"):
        print("需要kimi_api_key")
        sys.exit(1)

    # 运行测试
    unittest.main(verbosity=2)
