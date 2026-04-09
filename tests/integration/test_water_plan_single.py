"""单一水利规划文档生成测试（使用真实API）"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent


def test_single_plan_generation():
    """测试单一规划文档生成"""
    print("\n" + "=" * 70)
    print(" " * 15 + "单一水利规划文档生成测试")
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
        
        # 生成规划文档
        print("\n生成洪水预警系统规划文档...")
        print("-" * 70)
        
        user_input = """开发一个洪水预警系统，实现以下功能：
1. 实时接入流域内雨量站、水位站监测数据
2. 基于水文模型进行洪水预报，预见期24小时
3. 根据预警等级自动发布预警信息
"""
        
        result = agent.generate_water_plan(
            user_input=user_input,
            water_business_type="flood_warning",
            constraints={
                "预报预见期": "24小时",
                "预警发布时间": "5分钟内",
            },
            references=[
                "《洪水预报规范》SL 250",
                "《洪水预警发布管理办法》",
            ]
        )
        
        # 验证结果
        if not result["plan_document"]:
            print("❌ 规划文档生成失败")
            return False
        
        print("\n✓ 规划文档生成成功")
        print(f"  - 章节数: {result['metadata']['section_count']}")
        print(f"  - 文档长度: {len(result['plan_document'])} 字符")
        
        # 保存规划文档
        output_dir = project_root / "tests" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "flood_warning_plan_single.md"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["plan_document"])
        
        print(f"  - 保存路径: {output_file}")
        
        # 打印规划文档预览
        print("\n" + "=" * 70)
        print("规划文档预览")
        print("=" * 70)
        preview = result["plan_document"][:2000]
        print(preview)
        print("...")
        
        # 质量检查
        print("\n" + "=" * 70)
        print("质量检查")
        print("=" * 70)
        
        plan_doc = result["plan_document"]
        checks = {
            "包含概述章节": "## 概述" in plan_doc or "# 概述" in plan_doc,
            "包含目标章节": "## 目标" in plan_doc or "# 目标" in plan_doc,
            "包含实施步骤": "实施步骤" in plan_doc,
            "引用法规标准": any(code in plan_doc for code in ["SL 250", "SL 319"]),
            "引用专家经验": "经验" in plan_doc or "案例" in plan_doc,
        }
        
        passed = sum(checks.values())
        for name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {name}")
        
        print(f"\n质量评分: {passed}/{len(checks)} ({passed/len(checks)*100:.1f}%)")
        
        # 从规划文档生成决策链
        print("\n" + "=" * 70)
        print("从规划文档生成决策链")
        print("=" * 70)
        
        task_graph, metadata = agent.generate_chain_from_plan(
            plan_document=plan_doc,
            user_input=user_input,
        )
        
        print(f"\n✓ 决策链生成成功")
        print(f"  - 提取步骤: {metadata['steps_extracted']}")
        print(f"  - 生成节点: {metadata['node_count']}")
        print(f"  - 可靠性评分: {metadata['reliability_score']:.2f}")
        
        # 打印节点详情
        all_nodes = task_graph.get_all_nodes()
        print(f"\n  决策链节点:")
        for node_id, node in list(all_nodes.items())[:5]:
            deps = task_graph.get_dependencies(node_id)
            print(f"    [{node_id}] {node.task_type}")
            if deps:
                print(f"        -> 依赖: {', '.join(deps)}")
        
        print("\n" + "=" * 70)
        print("✓ 所有测试通过！")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_single_plan_generation()
    sys.exit(0 if success else 1)
