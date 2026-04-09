"""水利规划文档生成测试（使用真实API）

使用环境变量中的 KIMI_API_KEY 生成真实的水利项目规划文档，
并验证规划文档的质量和完整性。
"""

import os
import sys
import unittest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent
from flood_decision_agent.agents.prompts import WaterDomainPrompts


class TestWaterPlanGenerationWithAPI(unittest.TestCase):
    """使用真实API生成水利规划文档的测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.api_key = os.environ.get("KIMI_API_KEY")
        cls.has_api_key = bool(cls.api_key)
        
        if cls.has_api_key:
            print("\n" + "=" * 70)
            print(" " * 15 + "水利规划文档生成测试（使用真实API）")
            print("=" * 70)
            print(f"\n✓ API Key 已配置: {cls.api_key[:10]}...")
            cls.agent = DecisionChainGeneratorAgent()
        else:
            print("\n" + "=" * 70)
            print(" " * 20 + "API Key 未配置")
            print("=" * 70)
            print("\n⚠ 跳过API测试，请设置环境变量 KIMI_API_KEY")

    @unittest.skipUnless(
        bool(os.environ.get("KIMI_API_KEY")),
        "需要 KIMI_API_KEY 环境变量"
    )
    def test_01_generate_flood_warning_plan(self):
        """测试1: 生成洪水预警系统规划文档"""
        print("\n" + "-" * 70)
        print("【测试1】生成洪水预警系统规划文档")
        print("-" * 70)
        
        user_input = """开发一个洪水预警系统，实现以下功能：
1. 实时接入流域内雨量站、水位站监测数据
2. 基于水文模型进行洪水预报，预见期24小时
3. 根据预警等级自动发布预警信息
4. 支持多渠道预警发布（短信、APP、广播）
"""
        
        result = self.agent.generate_water_plan(
            user_input=user_input,
            water_business_type="flood_warning",
            constraints={
                "预报预见期": "24小时",
                "预警发布时间": "5分钟内",
                "数据更新频率": "5分钟"
            },
            references=[
                "《洪水预报规范》SL 250",
                "《洪水预警发布管理办法》",
                "《水文监测数据通信规约》SL 651"
            ]
        )
        
        # 验证结果
        self.assertTrue(result["plan_document"], "规划文档不应为空")
        self.assertEqual(result["metadata"]["water_business_type"], "flood_warning")
        self.assertTrue(result["metadata"]["domain_knowledge_used"])
        self.assertGreater(result["metadata"]["section_count"], 0)
        
        # 保存规划文档
        output_file = project_root / "tests" / "output" / "flood_warning_plan.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["plan_document"])
        
        print(f"\n✓ 规划文档生成成功")
        print(f"  - 章节数: {result['metadata']['section_count']}")
        print(f"  - 文档长度: {len(result['plan_document'])} 字符")
        print(f"  - 保存路径: {output_file}")
        
        # 打印规划文档预览
        print("\n  规划文档预览（前1500字符）:")
        print("  " + "=" * 66)
        preview = result["plan_document"][:1500]
        for line in preview.split("\n"):
            print(f"  {line}")
        print("  ...")
        
        return result

    @unittest.skipUnless(
        bool(os.environ.get("KIMI_API_KEY")),
        "需要 KIMI_API_KEY 环境变量"
    )
    def test_02_generate_reservoir_dispatch_plan(self):
        """测试2: 生成水库调度系统规划文档"""
        print("\n" + "-" * 70)
        print("【测试2】生成水库调度系统规划文档")
        print("-" * 70)
        
        user_input = """开发一个水库优化调度系统，实现以下功能：
1. 实时监测水库水位、入库流量、出库流量
2. 基于洪水预报进行防洪调度决策
3. 综合考虑防洪、发电、供水等多目标优化
4. 提供调度方案推荐和风险评估
"""
        
        result = self.agent.generate_water_plan(
            user_input=user_input,
            water_business_type="reservoir_dispatch",
            constraints={
                "调度响应时间": "10分钟内",
                "多目标优化": "防洪+发电+供水",
                "安全约束": "不超设计洪水位"
            },
            references=[
                "《水库调度规程编制导则》SL 319",
                "《水库大坝安全管理条例》",
                "《洪水预报规范》SL 250"
            ]
        )
        
        # 验证结果
        self.assertTrue(result["plan_document"], "规划文档不应为空")
        self.assertEqual(result["metadata"]["water_business_type"], "reservoir_dispatch")
        
        # 保存规划文档
        output_file = project_root / "tests" / "output" / "reservoir_dispatch_plan.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["plan_document"])
        
        print(f"\n✓ 规划文档生成成功")
        print(f"  - 章节数: {result['metadata']['section_count']}")
        print(f"  - 文档长度: {len(result['plan_document'])} 字符")
        print(f"  - 保存路径: {output_file}")
        
        # 打印规划文档预览
        print("\n  规划文档预览（前1500字符）:")
        print("  " + "=" * 66)
        preview = result["plan_document"][:1500]
        for line in preview.split("\n"):
            print(f"  {line}")
        print("  ...")
        
        return result

    @unittest.skipUnless(
        bool(os.environ.get("KIMI_API_KEY")),
        "需要 KIMI_API_KEY 环境变量"
    )
    def test_03_generate_chain_from_plan(self):
        """测试3: 从规划文档生成决策链"""
        print("\n" + "-" * 70)
        print("【测试3】从规划文档生成决策链")
        print("-" * 70)
        
        # 首先生成规划文档
        user_input = "开发一个洪水预警系统，实现实时监测和预警发布"
        plan_result = self.agent.generate_water_plan(
            user_input=user_input,
            water_business_type="flood_warning",
        )
        
        self.assertTrue(plan_result["plan_document"], "规划文档生成失败")
        print(f"\n  规划文档已生成，包含 {plan_result['metadata']['section_count']} 个章节")
        
        # 从规划文档生成决策链
        task_graph, metadata = self.agent.generate_chain_from_plan(
            plan_document=plan_result["plan_document"],
            user_input=user_input,
        )
        
        # 验证决策链
        self.assertIsNotNone(task_graph)
        self.assertGreater(metadata["node_count"], 0)
        self.assertEqual(metadata["source"], "plan_document")
        
        print(f"\n✓ 决策链生成成功")
        print(f"  - 提取步骤: {metadata['steps_extracted']}")
        print(f"  - 生成节点: {metadata['node_count']}")
        print(f"  - 可靠性评分: {metadata['reliability_score']:.2f}")
        
        # 打印节点详情
        all_nodes = task_graph.get_all_nodes()
        print(f"\n  决策链节点详情:")
        for node_id, node in list(all_nodes.items())[:5]:  # 只显示前5个
            deps = task_graph.get_dependencies(node_id)
            print(f"    [{node_id}] {node.task_type}")
            if deps:
                print(f"        -> 依赖: {', '.join(deps)}")
        
        if len(all_nodes) > 5:
            print(f"    ... 还有 {len(all_nodes) - 5} 个节点")

    @unittest.skipUnless(
        bool(os.environ.get("KIMI_API_KEY")),
        "需要 KIMI_API_KEY 环境变量"
    )
    def test_04_complete_workflow(self):
        """测试4: 完整工作流测试"""
        print("\n" + "-" * 70)
        print("【测试4】完整工作流：输入 -> 规划文档 -> 决策链")
        print("-" * 70)
        
        user_input = """开发一个流域洪水预报预警系统，要求：
- 覆盖整个流域，包括干流和主要支流
- 预报预见期24-48小时
- 预警等级分为蓝黄橙红四级
- 支持多源数据融合（地面监测+卫星遥感+气象预报）
"""
        
        result = self.agent.generate_complete_workflow(
            user_input=user_input,
            water_business_type="flood_warning",
            constraints={
                "覆盖范围": "全流域",
                "预报预见期": "24-48小时",
                "预警等级": "蓝黄橙红四级",
                "数据源": "地面+卫星+气象"
            },
            references=[
                "《洪水预报规范》SL 250",
                "《洪水预警发布管理办法》"
            ]
        )
        
        # 验证完整工作流结果
        self.assertTrue(result["success"], "工作流执行失败")
        self.assertTrue(result["plan_result"]["plan_document"], "规划文档生成失败")
        self.assertIsNotNone(result["task_graph"], "决策链生成失败")
        
        workflow_summary = result["workflow_summary"]
        
        print(f"\n✓ 完整工作流执行成功")
        print(f"\n  工作流摘要:")
        print(f"    - 用户输入: {workflow_summary['user_input'][:50]}...")
        print(f"    - 业务类型: {workflow_summary['water_business_type']}")
        print(f"    - 规划章节数: {workflow_summary['plan_sections']}")
        print(f"    - 决策链节点数: {workflow_summary['chain_nodes']}")
        print(f"    - 决策链边数: {workflow_summary['chain_edges']}")
        print(f"    - 可靠性评分: {workflow_summary['reliability_score']:.2f}")
        
        # 保存完整结果
        output_dir = project_root / "tests" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存规划文档
        plan_file = output_dir / "complete_workflow_plan.md"
        with open(plan_file, "w", encoding="utf-8") as f:
            f.write(result["plan_result"]["plan_document"])
        
        print(f"\n  输出文件:")
        print(f"    - 规划文档: {plan_file}")

    @unittest.skipUnless(
        bool(os.environ.get("KIMI_API_KEY")),
        "需要 KIMI_API_KEY 环境变量"
    )
    def test_05_plan_quality_check(self):
        """测试5: 规划文档质量检查"""
        print("\n" + "-" * 70)
        print("【测试5】规划文档质量检查")
        print("-" * 70)
        
        user_input = "开发一个水库防洪调度决策支持系统"
        result = self.agent.generate_water_plan(
            user_input=user_input,
            water_business_type="reservoir_dispatch",
        )
        
        plan_doc = result["plan_document"]
        
        # 质量检查项
        quality_checks = {
            "包含概述章节": "## 概述" in plan_doc or "# 概述" in plan_doc,
            "包含目标章节": "## 目标" in plan_doc or "# 目标" in plan_doc,
            "包含数据处理链条": "数据处理链条" in plan_doc,
            "包含实施步骤": "实施步骤" in plan_doc or "## 步骤" in plan_doc,
            "包含验收标准": "验收标准" in plan_doc,
            "引用法规标准": any(code in plan_doc for code in ["SL 250", "SL 319", "SL 651"]),
            "引用专家经验": "经验" in plan_doc or "案例" in plan_doc,
            "包含风险分析": "风险" in plan_doc,
        }
        
        print(f"\n  质量检查结果:")
        passed = 0
        for check_name, check_result in quality_checks.items():
            status = "✓" if check_result else "✗"
            print(f"    {status} {check_name}")
            if check_result:
                passed += 1
        
        print(f"\n  质量评分: {passed}/{len(quality_checks)} ({passed/len(quality_checks)*100:.1f}%)")
        
        # 断言关键检查项
        self.assertTrue(quality_checks["包含实施步骤"], "规划文档应包含实施步骤")
        self.assertTrue(quality_checks["引用法规标准"], "规划文档应引用法规标准")

    @unittest.skipUnless(
        bool(os.environ.get("KIMI_API_KEY")),
        "需要 KIMI_API_KEY 环境变量"
    )
    def test_06_compare_with_without_domain_knowledge(self):
        """测试6: 对比使用/不使用领域知识的效果"""
        print("\n" + "-" * 70)
        print("【测试6】对比使用/不使用领域知识的效果")
        print("-" * 70)
        
        user_input = "开发一个洪水预警系统"
        
        # 使用领域知识生成
        print("\n  使用水利领域知识生成...")
        result_with = self.agent.generate_water_plan(
            user_input=user_input,
            water_business_type="flood_warning",
            constraints={},
            references=[],
        )
        
        # 检查是否包含水利专业术语
        plan_with = result_with["plan_document"]
        water_terms = ["面雨量", "洪峰流量", "汛限水位", "警戒水位", "SL ", "水库调度"]
        term_count_with = sum(1 for term in water_terms if term in plan_with)
        
        print(f"\n  使用领域知识生成的文档:")
        print(f"    - 文档长度: {len(plan_with)} 字符")
        print(f"    - 水利专业术语: {term_count_with}/{len(water_terms)} 个")
        print(f"    - 包含术语: {[t for t in water_terms if t in plan_with]}")
        
        # 保存对比结果
        output_dir = project_root / "tests" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "plan_with_domain_knowledge.md", "w", encoding="utf-8") as f:
            f.write(plan_with)
        
        print(f"\n  文档已保存到: {output_dir / 'plan_with_domain_knowledge.md'}")
        
        # 验证包含足够多的专业术语
        self.assertGreaterEqual(term_count_with, 3, 
                               f"使用领域知识的文档应包含至少3个水利专业术语，实际只有{term_count_with}个")


def run_api_tests():
    """运行API测试"""
    # 检查API Key
    api_key = os.environ.get("KIMI_API_KEY")
    
    if not api_key:
        print("\n" + "=" * 70)
        print(" " * 20 + "API Key 未配置")
        print("=" * 70)
        print("\n请设置环境变量 KIMI_API_KEY 后重新运行测试")
        print("\n设置方法:")
        print("  Windows PowerShell:")
        print("    $env:KIMI_API_KEY=\"your-api-key\"")
        print("  Windows CMD:")
        print("    set KIMI_API_KEY=your-api-key")
        print("  Linux/Mac:")
        print("    export KIMI_API_KEY=your-api-key")
        return False
    
    print("\n" + "=" * 70)
    print(" " * 15 + "水利规划文档生成测试（使用真实API）")
    print("=" * 70)
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    print(f"✓ 开始运行测试...\n")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestWaterPlanGenerationWithAPI))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 70)
    print(" " * 25 + "测试总结")
    print("=" * 70)
    print(f"\n  运行测试: {result.testsRun}")
    print(f"  通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n  ✓ 所有测试通过！")
        print("\n  生成的文档保存在: tests/output/")
    else:
        print("\n  ✗ 部分测试未通过")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
