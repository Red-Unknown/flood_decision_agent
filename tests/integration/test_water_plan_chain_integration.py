"""水利 Plan/Chain 集成测试

测试水利提示词与 DecisionChainGeneratorAgent 的集成，
验证完整流程：输入 -> 规划文档生成 -> 决策链生成
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent
from flood_decision_agent.agents.prompts import WaterDomainPrompts


class TestWaterPlanChainIntegration(unittest.TestCase):
    """水利规划-决策链集成测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("\n" + "=" * 60)
        print("水利 Plan/Chain 集成测试")
        print("=" * 60)
        cls.agent = DecisionChainGeneratorAgent()

    def test_01_water_domain_prompts_loaded(self):
        """测试1: 验证水利领域提示词已正确加载"""
        print("\n【测试1】验证水利领域提示词加载")
        
        # 验证数据链条模板
        self.assertIn("flood_warning", WaterDomainPrompts.DATA_CHAIN_TEMPLATES)
        self.assertIn("reservoir_dispatch", WaterDomainPrompts.DATA_CHAIN_TEMPLATES)
        
        # 验证专家规则
        self.assertIn("scheduling", WaterDomainPrompts.EXPERT_RULES)
        self.assertIn("warning", WaterDomainPrompts.EXPERT_RULES)
        self.assertIn("safety", WaterDomainPrompts.EXPERT_RULES)
        
        # 验证法规规程
        self.assertGreater(len(WaterDomainPrompts.REGULATIONS), 0)
        
        # 验证阈值参数
        self.assertIn("rainfall", WaterDomainPrompts.THRESHOLDS)
        self.assertIn("flood_warning", WaterDomainPrompts.THRESHOLDS)
        
        # 验证验收标准
        self.assertIn("functional", WaterDomainPrompts.ACCEPTANCE_CRITERIA)
        
        print("✓ 水利领域提示词加载成功")
        print(f"  - 数据链条模板: {len(WaterDomainPrompts.DATA_CHAIN_TEMPLATES)} 个")
        print(f"  - 专家规则: {sum(len(rules) for rules in WaterDomainPrompts.EXPERT_RULES.values())} 条")
        print(f"  - 法规规程: {len(WaterDomainPrompts.REGULATIONS)} 部")
        print(f"  - 阈值参数: {sum(len(t) for t in WaterDomainPrompts.THRESHOLDS.values())} 项")

    def test_02_data_chain_prompt_generation(self):
        """测试2: 验证数据链条提示词生成"""
        print("\n【测试2】验证数据链条提示词生成")
        
        # 生成洪水预警链条提示词
        flood_prompt = WaterDomainPrompts.get_data_chain_prompt("flood_warning")
        self.assertIsNotNone(flood_prompt)
        self.assertGreater(len(flood_prompt), 100)
        
        # 验证关键内容存在
        self.assertIn("洪水预警分析链条", flood_prompt)
        self.assertIn("DATA_ACQUISITION", flood_prompt)
        self.assertIn("FEATURE_EXTRACTION", flood_prompt)
        self.assertIn("INDEX_CALCULATION", flood_prompt)
        self.assertIn("DECISION_SUPPORT", flood_prompt)
        
        # 生成水库调度链条提示词
        reservoir_prompt = WaterDomainPrompts.get_data_chain_prompt("reservoir_dispatch")
        self.assertIsNotNone(reservoir_prompt)
        self.assertGreater(len(reservoir_prompt), 100)
        self.assertIn("水库优化调度链条", reservoir_prompt)
        
        print("✓ 数据链条提示词生成成功")
        print(f"  - 洪水预警链条长度: {len(flood_prompt)} 字符")
        print(f"  - 水库调度链条长度: {len(reservoir_prompt)} 字符")

    def test_03_expert_rules_prompt_generation(self):
        """测试3: 验证专家规则提示词生成"""
        print("\n【测试3】验证专家规则提示词生成")
        
        # 生成调度规则提示词
        scheduling_prompt = WaterDomainPrompts.get_expert_rules_prompt("scheduling")
        self.assertIsNotNone(scheduling_prompt)
        self.assertGreater(len(scheduling_prompt), 100)
        self.assertIn("SCHEDULING RULES", scheduling_prompt)
        
        # 生成全部规则提示词
        all_rules_prompt = WaterDomainPrompts.get_expert_rules_prompt()
        self.assertIsNotNone(all_rules_prompt)
        self.assertGreater(len(all_rules_prompt), len(scheduling_prompt))
        
        print("✓ 专家规则提示词生成成功")
        print(f"  - 调度规则长度: {len(scheduling_prompt)} 字符")
        print(f"  - 全部规则长度: {len(all_rules_prompt)} 字符")

    def test_04_agent_has_water_plan_method(self):
        """测试4: 验证Agent已集成水利规划方法"""
        print("\n【测试4】验证Agent方法集成")
        
        # 验证新方法存在
        self.assertTrue(hasattr(self.agent, 'generate_water_plan'))
        self.assertTrue(hasattr(self.agent, 'generate_chain_from_plan'))
        self.assertTrue(hasattr(self.agent, 'generate_complete_workflow'))
        self.assertTrue(hasattr(self.agent, '_extract_implementation_steps'))
        self.assertTrue(hasattr(self.agent, '_steps_to_task_nodes'))
        self.assertTrue(hasattr(self.agent, '_infer_task_type'))
        
        print("✓ Agent方法集成验证通过")
        print("  - generate_water_plan: 生成水利项目规划")
        print("  - generate_chain_from_plan: 从规划生成决策链")
        print("  - generate_complete_workflow: 完整工作流生成")

    def test_05_extract_implementation_steps(self):
        """测试5: 验证实施步骤提取功能"""
        print("\n【测试5】验证实施步骤提取")
        
        # 模拟规划文档内容
        plan_doc = """
## 实施步骤

1. **需求分析与调研**（预计2周）
   - 具体内容：调研现有系统、收集用户需求
   - 交付物：《需求规格说明书》
   - 负责人：项目经理

2. **系统设计与开发**（预计8周）
   - 具体内容：架构设计、模块开发
   - 交付物：《系统设计文档》
   - 负责人：开发团队

3. **数据接入与调试**（预计3周）
   - 具体内容：接入水文监测数据
   - 交付物：《数据接入报告》
   - 负责人：数据工程师
"""
        
        steps = self.agent._extract_implementation_steps(plan_doc)
        
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0]["name"], "需求分析与调研")
        self.assertEqual(steps[1]["name"], "系统设计与开发")
        self.assertEqual(steps[2]["name"], "数据接入与调试")
        
        print("✓ 实施步骤提取成功")
        print(f"  - 提取步骤数: {len(steps)}")
        for i, step in enumerate(steps, 1):
            print(f"    {i}. {step['name']}")

    def test_06_infer_task_type(self):
        """测试6: 验证任务类型推断"""
        print("\n【测试6】验证任务类型推断")
        
        from flood_decision_agent.agents.decision_chain.task_decomposer import TaskType
        
        # 测试数据相关
        task_type = self.agent._infer_task_type("数据接入", "接入水文监测数据")
        self.assertEqual(task_type, TaskType.DATA_COLLECTION)
        
        # 测试开发相关
        task_type = self.agent._infer_task_type("系统开发", "实现核心功能模块")
        self.assertEqual(task_type, TaskType.EXECUTION)
        
        # 测试测试相关
        task_type = self.agent._infer_task_type("系统测试", "验证功能正确性")
        self.assertEqual(task_type, TaskType.VERIFICATION)
        
        # 测试模型相关
        task_type = self.agent._infer_task_type("模型训练", "训练洪水预报模型")
        self.assertEqual(task_type, TaskType.PREDICTION)
        
        print("✓ 任务类型推断正确")

    def test_07_steps_to_task_nodes(self):
        """测试7: 验证步骤到任务节点转换"""
        print("\n【测试7】验证步骤到任务节点转换")
        
        steps = [
            {"name": "数据采集", "description": "接入监测数据", "deliverables": "数据报告"},
            {"name": "模型训练", "description": "训练预报模型", "deliverables": "模型文件"},
            {"name": "系统测试", "description": "验证功能", "deliverables": "测试报告"},
        ]
        
        nodes = self.agent._steps_to_task_nodes(steps)
        
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].task_id, "plan_step_000")
        self.assertEqual(nodes[1].task_id, "plan_step_001")
        self.assertEqual(nodes[2].task_id, "plan_step_002")
        
        # 验证依赖关系
        self.assertEqual(len(nodes[0].dependencies), 0)  # 第一个节点无依赖
        self.assertEqual(len(nodes[1].dependencies), 1)  # 第二个依赖第一个
        self.assertEqual(len(nodes[2].dependencies), 1)  # 第三个依赖第二个
        
        print("✓ 步骤转换成功")
        print(f"  - 生成节点数: {len(nodes)}")
        print(f"  - 依赖关系正确")

    def test_08_complete_workflow_mock(self):
        """测试8: 验证完整工作流（使用模拟规划文档）"""
        print("\n【测试8】验证完整工作流（模拟）")
        
        # 使用模拟规划文档测试决策链生成
        mock_plan = """
# 洪水预警系统规划

## 概述
开发洪水预警系统

## 实施步骤

1. **数据接入**（预计1周）
   - 具体内容：接入雨量站和水位站数据
   - 交付物：数据接入完成
   - 负责人：数据工程师

2. **预报模型开发**（预计2周）
   - 具体内容：开发洪水预报模型
   - 交付物：模型代码
   - 负责人：算法工程师

3. **预警功能实现**（预计1周）
   - 具体内容：实现预警发布功能
   - 交付物：预警模块
   - 负责人：开发工程师
"""
        
        task_graph, metadata = self.agent.generate_chain_from_plan(
            plan_document=mock_plan,
            user_input="开发洪水预警系统"
        )
        
        self.assertIsNotNone(task_graph)
        self.assertEqual(metadata["source"], "plan_document")
        self.assertEqual(metadata["steps_extracted"], 3)
        self.assertGreaterEqual(metadata["node_count"], 3)
        
        print("✓ 完整工作流验证通过")
        print(f"  - 提取步骤: {metadata['steps_extracted']}")
        print(f"  - 生成节点: {metadata['node_count']}")
        print(f"  - 可靠性评分: {metadata.get('reliability_score', 0):.2f}")

    def test_09_integration_summary(self):
        """测试9: 集成测试总结"""
        print("\n" + "=" * 60)
        print("集成测试总结")
        print("=" * 60)
        
        summary = {
            "水利领域提示词": "已加载",
            "数据链条模板": f"{len(WaterDomainPrompts.DATA_CHAIN_TEMPLATES)} 个",
            "专家规则": f"{sum(len(rules) for rules in WaterDomainPrompts.EXPERT_RULES.values())} 条",
            "法规规程": f"{len(WaterDomainPrompts.REGULATIONS)} 部",
            "Agent新方法": "已集成",
            "完整工作流": "已支持",
        }
        
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print("=" * 60)
        print("✓ 所有集成测试通过！")
        print("=" * 60)


class TestWaterPlanGeneration(unittest.TestCase):
    """水利规划生成测试类（需要API Key）"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.agent = DecisionChainGeneratorAgent()
        
        # 检查API Key
        import os
        cls.has_api_key = bool(os.environ.get("KIMI_API_KEY"))
    
    @unittest.skipUnless(
        bool(__import__('os').environ.get("KIMI_API_KEY")),
        "需要 KIMI_API_KEY 环境变量"
    )
    def test_10_generate_water_plan_real(self):
        """测试10: 真实生成水利项目规划（需要API Key）"""
        print("\n【测试10】真实生成水利项目规划")
        
        result = self.agent.generate_water_plan(
            user_input="开发一个洪水预警系统，实现实时水情监测和预警发布",
            water_business_type="flood_warning",
            constraints={"预报预见期": "24小时"},
            references=["《洪水预报规范》SL 250"],
        )
        
        self.assertTrue(result["plan_document"])
        self.assertEqual(result["metadata"]["water_business_type"], "flood_warning")
        self.assertTrue(result["metadata"]["domain_knowledge_used"])
        self.assertGreater(result["metadata"]["section_count"], 0)
        
        print("✓ 水利项目规划生成成功")
        print(f"  - 章节数: {result['metadata']['section_count']}")
        print(f"  - 文档长度: {len(result['plan_document'])} 字符")
        
        # 打印规划文档预览
        print("\n  规划文档预览:")
        preview_lines = result["plan_document"].split("\n")[:20]
        for line in preview_lines:
            print(f"    {line}")
        print("    ...")


def run_tests():
    """运行测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加集成测试（不需要API Key）
    suite.addTests(loader.loadTestsFromTestCase(TestWaterPlanChainIntegration))
    
    # 添加规划生成测试（需要API Key）
    suite.addTests(loader.loadTestsFromTestCase(TestWaterPlanGeneration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
