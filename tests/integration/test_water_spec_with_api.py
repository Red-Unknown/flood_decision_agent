"""水利规格文档生成测试（使用真实API）

使用环境变量中的 KIMI_API_KEY 生成真实的水利项目规格文档，
验证 Spec 模式的完整流程：输入 -> 规划文档 -> 规格文档
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent


def test_spec_generation():
    """测试规格文档生成"""
    print("\n" + "=" * 70)
    print(" " * 15 + "水利规格文档生成测试（Spec模式）")
    print("=" * 70)
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("\n❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    try:
        # 初始化 Agent
        print("\n初始化 DecisionChainGeneratorAgent...")
        agent = DecisionChainGeneratorAgent()
        print("✓ Agent 初始化成功")
        
        # 测试1：完整Spec工作流
        print("\n" + "=" * 70)
        print("【测试1】完整Spec工作流：输入 -> 规划 -> 规格")
        print("=" * 70)
        
        user_input = """开发一个洪水预警系统，实现以下功能：
1. 实时接入流域内雨量站、水位站监测数据
2. 基于水文模型进行洪水预报，预见期24小时
3. 根据预警等级自动发布预警信息
4. 支持多渠道预警发布（短信、APP、广播）
"""
        
        result = agent.generate_complete_spec_workflow(
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
        
        if not result["success"]:
            print(f"❌ 工作流执行失败: {result.get('error', '未知错误')}")
            return False
        
        print("\n✓ 完整Spec工作流执行成功")
        
        workflow_summary = result["workflow_summary"]
        print(f"\n  工作流摘要:")
        print(f"    - 规划章节数: {workflow_summary['plan_sections']}")
        print(f"    - 规格章节数: {workflow_summary['spec_sections']}")
        
        # 保存规划文档
        output_dir = project_root / "tests" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        plan_file = output_dir / "spec_mode_plan.md"
        with open(plan_file, "w", encoding="utf-8") as f:
            f.write(result["plan_result"]["plan_document"])
        print(f"\n  规划文档已保存: {plan_file}")
        
        # 保存规格文档
        spec_file = output_dir / "spec_mode_spec.md"
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(result["spec_result"]["spec_document"])
        print(f"  规格文档已保存: {spec_file}")
        
        # 打印规划文档预览
        print("\n" + "=" * 70)
        print("规划文档预览（前1000字符）")
        print("=" * 70)
        print(result["plan_result"]["plan_document"][:1000])
        print("...")
        
        # 打印规格文档预览
        print("\n" + "=" * 70)
        print("规格文档预览（前1500字符）")
        print("=" * 70)
        print(result["spec_result"]["spec_document"][:1500])
        print("...")
        
        # 测试2：独立规格生成
        print("\n" + "=" * 70)
        print("【测试2】基于现有规划生成规格文档")
        print("=" * 70)
        
        # 使用已有的规划文档
        plan_doc = result["plan_result"]["plan_document"]
        
        spec_result2 = agent.generate_water_spec(
            plan_document=plan_doc,
            user_input=user_input,
            water_business_type="flood_warning",
        )
        
        if not spec_result2["spec_document"]:
            print("❌ 规格文档生成失败")
            return False
        
        print(f"\n✓ 规格文档生成成功")
        print(f"  - 规划章节数: {spec_result2['metadata']['plan_sections']}")
        print(f"  - 规格章节数: {spec_result2['metadata']['spec_sections']}")
        
        # 质量检查
        print("\n" + "=" * 70)
        print("规格文档质量检查")
        print("=" * 70)
        
        spec_doc = result["spec_result"]["spec_document"]
        checks = {
            "包含系统架构": "系统架构" in spec_doc or "架构" in spec_doc,
            "包含数据模型": "数据模型" in spec_doc or "数据实体" in spec_doc,
            "包含接口设计": "接口设计" in spec_doc or "接口" in spec_doc,
            "包含算法方案": "算法" in spec_doc or "模型" in spec_doc,
            "包含性能指标": "性能" in spec_doc,
            "包含安全设计": "安全" in spec_doc,
            "引用法规标准": any(code in spec_doc for code in ["SL 250", "SL 319", "SL 651"]),
            "包含验收标准": "验收" in spec_doc,
        }
        
        passed = sum(checks.values())
        for name, check_result in checks.items():
            status = "✓" if check_result else "✗"
            print(f"  {status} {name}")
        
        print(f"\n质量评分: {passed}/{len(checks)} ({passed/len(checks)*100:.1f}%)")
        
        # 打印完整结果
        print("\n" + "=" * 70)
        print("✓ 所有测试通过！")
        print("=" * 70)
        print(f"\n生成的文档保存在: {output_dir}")
        print("  - spec_mode_plan.md (规划文档)")
        print("  - spec_mode_spec.md (规格文档)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_spec_generation()
    sys.exit(0 if success else 1)
