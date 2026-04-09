"""水利 Plan/Spec 模式演示

演示如何使用水利领域专用提示词生成规划/规格文档。
"""

import sys
sys.path.insert(0, 'src')

from flood_decision_agent.agents.prompts import (
    PlanSpecPrompts,
    PromptContext,
    WaterDomainPrompts,
    get_prompt_for_mode,
)


def demo_water_domain_prompts():
    """演示水利领域专用提示词"""
    print("=" * 60)
    print("水利领域专用提示词演示")
    print("=" * 60)
    
    # 1. 演示数据处理链条提示词
    print("\n【1. 洪水预警数据处理链条】")
    print("-" * 40)
    chain_prompt = WaterDomainPrompts.get_data_chain_prompt("flood_warning")
    print(chain_prompt[:1500] + "...\n")
    
    # 2. 演示专家规则提示词
    print("\n【2. 调度专家规则】")
    print("-" * 40)
    rules_prompt = WaterDomainPrompts.get_expert_rules_prompt("scheduling")
    print(rules_prompt[:1000] + "...\n")
    
    # 3. 演示法规规程提示词
    print("\n【3. 适用法规规程】")
    print("-" * 40)
    reg_prompt = WaterDomainPrompts.get_regulations_prompt()
    print(reg_prompt[:800] + "...\n")
    
    # 4. 演示阈值参数提示词
    print("\n【4. 关键阈值参数】")
    print("-" * 40)
    threshold_prompt = WaterDomainPrompts.get_thresholds_prompt("flood_warning")
    print(threshold_prompt)
    
    # 5. 演示验收标准提示词
    print("\n【5. 项目验收标准】")
    print("-" * 40)
    acceptance_prompt = WaterDomainPrompts.get_acceptance_criteria_prompt("functional")
    print(acceptance_prompt)


def demo_water_plan_generation():
    """演示水利项目规划生成"""
    print("\n" + "=" * 60)
    print("水利项目规划生成演示")
    print("=" * 60)
    
    # 创建提示词上下文
    context = PromptContext(
        user_input="开发一个洪水预警系统，实现实时水情监测、洪水预报和预警发布功能",
        domain="水利调度",
        water_business_type="flood_warning",  # 指定水利业务类型
        use_water_domain_knowledge=True,       # 使用水利领域知识
        constraints={
            "预报预见期": "24小时",
            "预警发布时间": "5分钟内",
            "覆盖范围": "整个流域"
        },
        references=[
            "《洪水预报规范》SL 250",
            "《洪水预警发布管理办法》"
        ]
    )
    
    # 生成水利项目专用规划提示词
    print("\n【生成水利项目规划提示词】")
    print("-" * 40)
    
    # 方法1：直接使用类方法
    prompts = PlanSpecPrompts()
    plan_prompt = prompts.get_water_plan_generation_prompt(context)
    
    print(f"提示词长度: {len(plan_prompt)} 字符")
    print(f"\n提示词预览（前2000字符）:\n")
    print(plan_prompt[:2000])
    print("...\n")
    
    # 方法2：使用便捷函数
    print("\n【使用便捷函数生成】")
    print("-" * 40)
    
    prompt_from_helper = get_prompt_for_mode(
        mode="water_plan",
        action="generate",
        context={
            "user_input": "开发一个水库优化调度系统",
            "domain": "水利调度",
            "water_business_type": "reservoir_dispatch",
            "use_water_domain_knowledge": True,
        }
    )
    
    print(f"便捷函数生成的提示词长度: {len(prompt_from_helper)} 字符")


def demo_expert_knowledge_access():
    """演示专家知识库访问"""
    print("\n" + "=" * 60)
    print("专家知识库访问演示")
    print("=" * 60)
    
    # 访问各类专家规则
    print("\n【调度规则数量】")
    print(f"调度规则: {len(WaterDomainPrompts.EXPERT_RULES['scheduling'])} 条")
    print(f"预警规则: {len(WaterDomainPrompts.EXPERT_RULES['warning'])} 条")
    print(f"安全规则: {len(WaterDomainPrompts.EXPERT_RULES['safety'])} 条")
    
    # 访问法规规程
    print("\n【法规规程数量】")
    print(f"共 {len(WaterDomainPrompts.REGULATIONS)} 部法规规程")
    for reg in WaterDomainPrompts.REGULATIONS:
        print(f"  - {reg['code']}: {reg['name']}")
    
    # 访问阈值参数
    print("\n【阈值参数类别】")
    for category in WaterDomainPrompts.THRESHOLDS.keys():
        print(f"  - {category}: {len(WaterDomainPrompts.THRESHOLDS[category])} 项")
    
    # 访问验收标准
    print("\n【验收标准类别】")
    for category in WaterDomainPrompts.ACCEPTANCE_CRITERIA.keys():
        count = len(WaterDomainPrompts.ACCEPTANCE_CRITERIA[category])
        print(f"  - {category}: {count} 项")
    
    # 访问历史案例
    print("\n【历史案例】")
    for case in WaterDomainPrompts.HISTORICAL_CASES:
        print(f"  - {case['id']}: {case['name']} ({case['date']})")
        print(f"    决策: {case['decision'][:50]}...")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "水利 Plan/Spec 模式演示" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 运行演示
    demo_water_domain_prompts()
    demo_water_plan_generation()
    demo_expert_knowledge_access()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n提示：")
    print("1. 使用 WaterDomainPrompts 类访问各类水利领域知识")
    print("2. 使用 get_water_plan_generation_prompt() 生成水利项目规划")
    print("3. 使用 mode='water_plan' 调用便捷函数")
    print("4. 所有提示词均符合水利行业规范和标准")
