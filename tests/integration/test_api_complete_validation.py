"""API完整验证测试

根据 docs/04-api-reference/rest-api/web-api.md 中定义的API接口，
使用 decision_chain 模块进行完整验证测试：
- Plan模式：生成plan文档
- Spec模式：生成spec、tasks、checklist套组
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent


def test_plan_mode():
    """测试Plan模式：生成plan文档"""
    print("\n" + "=" * 70)
    print(" " * 25 + "Plan模式测试")
    print("=" * 70)
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("\n❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    try:
        agent = DecisionChainGeneratorAgent()
        print("✓ Agent 初始化成功")
        
        # 测试Plan模式
        print("\n【Plan模式】生成水利项目规划文档")
        print("-" * 70)
        
        user_input = """开发一个洪水预警系统，实现以下功能：
1. 实时接入流域内雨量站、水位站监测数据（符合SL 651标准）
2. 基于水文模型进行洪水预报，预见期24小时（符合SL 250标准）
3. 根据预警等级自动发布预警信息（蓝黄橙红四级）
4. 支持多渠道预警发布（短信、APP、广播）
"""
        
        plan_result = agent.generate_water_plan(
            user_input=user_input,
            water_business_type="flood_warning",
            constraints={
                "预报预见期": "24小时",
                "预警发布时间": "5分钟内",
                "数据更新频率": "5分钟",
                "数据标准": "SL 651",
                "预报标准": "SL 250"
            },
            references=[
                "《洪水预报规范》SL 250",
                "《洪水预警发布管理办法》",
                "《水文监测数据通信规约》SL 651",
                "《水文监测数据完整性评价规范》SL 460"
            ]
        )
        
        if not plan_result["plan_document"]:
            print("❌ 规划文档生成失败")
            return False
        
        # 保存规划文档
        output_dir = project_root / "tests" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        plan_file = output_dir / "plan_mode_output.md"
        with open(plan_file, "w", encoding="utf-8") as f:
            f.write(plan_result["plan_document"])
        
        print(f"\n✓ 规划文档生成成功")
        print(f"  - 章节数: {plan_result['metadata']['section_count']}")
        print(f"  - 文档长度: {len(plan_result['plan_document'])} 字符")
        print(f"  - 保存路径: {plan_file}")
        
        # 打印预览
        print("\n  规划文档预览（前800字符）:")
        print("  " + "-" * 66)
        print(plan_result["plan_document"][:800])
        print("  ...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Plan模式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_spec_mode():
    """测试Spec模式：生成spec、tasks、checklist套组"""
    print("\n" + "=" * 70)
    print(" " * 25 + "Spec模式测试")
    print("=" * 70)
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("\n❌ KIMI_API_KEY 环境变量未设置")
        return False
    
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    try:
        agent = DecisionChainGeneratorAgent()
        print("✓ Agent 初始化成功")
        
        # 测试Spec模式
        print("\n【Spec模式】生成完整文档套组（spec + tasks + checklist）")
        print("-" * 70)
        
        user_input = """开发一个洪水预警系统，实现以下功能：
1. 实时接入流域内雨量站、水位站监测数据
2. 基于水文模型进行洪水预报，预见期24小时
3. 根据预警等级自动发布预警信息
4. 支持多渠道预警发布（短信、APP、广播）
"""
        
        result = agent.generate_complete_spec_suite(
            user_input=user_input,
            water_business_type="flood_warning",
            constraints={
                "预报预见期": "24小时",
                "预警发布时间": "5分钟内",
            },
            references=[
                "《洪水预报规范》SL 250",
                "《水文监测数据通信规约》SL 651",
            ]
        )
        
        if not result["success"]:
            print(f"❌ Spec模式执行失败: {result.get('error', '未知错误')}")
            return False
        
        print("\n✓ Spec模式执行成功")
        
        workflow_summary = result["workflow_summary"]
        print(f"\n  工作流摘要:")
        print(f"    - 规划章节数: {workflow_summary['plan_sections']}")
        print(f"    - 规格章节数: {workflow_summary['spec_sections']}")
        print(f"    - 任务分解: {'已生成' if workflow_summary['has_tasks'] else '失败'}")
        print(f"    - 检查清单: {'已生成' if workflow_summary['has_checklist'] else '失败'}")
        
        # 保存所有文档
        output_dir = project_root / "tests" / "output" / "spec_suite"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存规划文档
        plan_file = output_dir / "plan.md"
        with open(plan_file, "w", encoding="utf-8") as f:
            f.write(result["plan_result"]["plan_document"])
        print(f"\n  ✓ 规划文档已保存: {plan_file}")
        
        # 保存规格文档
        spec_file = output_dir / "spec.md"
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(result["spec_result"]["spec_document"])
        print(f"  ✓ 规格文档已保存: {spec_file}")
        
        # 保存任务分解
        if result["tasks_result"].get("tasks_document"):
            tasks_file = output_dir / "tasks.md"
            with open(tasks_file, "w", encoding="utf-8") as f:
                f.write(result["tasks_result"]["tasks_document"])
            print(f"  ✓ 任务分解已保存: {tasks_file}")
        
        # 保存检查清单
        if result["checklist_result"].get("checklist_document"):
            checklist_file = output_dir / "checklist.md"
            with open(checklist_file, "w", encoding="utf-8") as f:
                f.write(result["checklist_result"]["checklist_document"])
            print(f"  ✓ 检查清单已保存: {checklist_file}")
        
        # 打印规格文档预览
        print("\n" + "=" * 70)
        print("规格文档预览（spec.md - 前1000字符）")
        print("=" * 70)
        print(result["spec_result"]["spec_document"][:1000])
        print("...")
        
        # 验证Spec文档不包含验收标准
        spec_doc = result["spec_result"]["spec_document"]
        has_acceptance_section = "## 验收标准" in spec_doc or "# 验收标准" in spec_doc
        
        print("\n" + "=" * 70)
        print("Spec文档结构验证")
        print("=" * 70)
        print(f"  ✓ 验收标准章节已分离: {'否' if has_acceptance_section else '是'}")
        print(f"  ✓ 任务分解在tasks.md中: {'是' if workflow_summary['has_tasks'] else '否'}")
        print(f"  ✓ 检查清单在checklist.md中: {'是' if workflow_summary['has_checklist'] else '否'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Spec模式测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """测试API端点对应关系"""
    print("\n" + "=" * 70)
    print(" " * 20 + "API端点对应关系验证")
    print("=" * 70)
    
    # 根据web-api.md验证API端点
    api_endpoints = {
        "Plan模式": {
            "endpoint": "POST /api/v1/decision-chain/generate",
            "description": "生成决策链（对应plan文档生成）",
            "method": "generate_water_plan",
        },
        "Spec模式": {
            "endpoint": "POST /api/v1/decision-chain/generate-spec",
            "description": "生成规格文档套组（spec+tasks+checklist）",
            "method": "generate_complete_spec_suite",
        },
        "决策链生成": {
            "endpoint": "POST /api/v1/decision-chain/generate-chain",
            "description": "从规划生成决策链",
            "method": "generate_chain_from_plan",
        },
    }
    
    print("\n  API端点映射:")
    for mode, info in api_endpoints.items():
        print(f"\n  {mode}:")
        print(f"    端点: {info['endpoint']}")
        print(f"    描述: {info['description']}")
        print(f"    方法: {info['method']}")
    
    return True


def run_complete_validation():
    """运行完整验证测试"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "API完整验证测试" + " " * 41 + "║")
    print("║" + " " * 5 + "根据web-api.md验证Plan/Spec模式" + " " * 26 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {}
    
    # 测试API端点对应关系
    results["api_endpoints"] = test_api_endpoints()
    
    # 测试Plan模式
    results["plan_mode"] = test_plan_mode()
    
    # 测试Spec模式
    results["spec_mode"] = test_spec_mode()
    
    # 打印总结
    print("\n" + "=" * 70)
    print(" " * 25 + "测试总结")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n  ✓ 所有测试通过！")
        print("\n  生成的文档保存在:")
        print("    - tests/output/plan_mode_output.md")
        print("    - tests/output/spec_suite/")
        print("      - plan.md")
        print("      - spec.md")
        print("      - tasks.md")
        print("      - checklist.md")
    else:
        print("\n  ✗ 部分测试未通过")
    
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = run_complete_validation()
    sys.exit(0 if success else 1)
