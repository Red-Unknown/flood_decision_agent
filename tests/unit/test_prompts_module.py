"""Prompts 模块测试脚本

测试 prompts 模块的正确性和向后兼容性
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_new_prompts_import():
    """测试新的 prompts 模块导入"""
    print("测试新的 prompts 模块导入...")
    
    from flood_decision_agent.agents.prompts import (
        BasePrompts,
        IntentParserPrompts,
        TaskDecomposerPrompts,
        DecisionGeneratorPrompts,
        PlanSpecPrompts,
        DocumentType,
        PromptContext,
        AgentRole,
    )
    
    # 测试 BasePrompts
    system_prompt = BasePrompts.get_system_prompt("intent_parser")
    assert len(system_prompt) > 0, "系统提示词不应为空"
    print("✓ BasePrompts 工作正常")
    
    # 测试 IntentParserPrompts
    prompt = IntentParserPrompts.get_intent_parser_prompt("测试输入", [])
    assert "测试输入" in prompt, "提示词应包含用户输入"
    print("✓ IntentParserPrompts 工作正常")
    
    # 测试 TaskDecomposerPrompts
    prompt = TaskDecomposerPrompts.get_task_decomposer_prompt(
        {"task": "测试"}, ["type1", "type2"]
    )
    assert "测试" in prompt, "提示词应包含任务意图"
    print("✓ TaskDecomposerPrompts 工作正常")
    
    # 测试 DecisionGeneratorPrompts
    prompt = DecisionGeneratorPrompts.get_decision_generator_prompt(
        {}, ["目标1"], {}
    )
    assert "目标1" in prompt, "提示词应包含目标"
    print("✓ DecisionGeneratorPrompts 工作正常")
    
    # 测试 PlanSpecPrompts
    context = PromptContext(user_input="测试规划")
    prompt = PlanSpecPrompts.get_plan_generation_prompt(context)
    assert "测试规划" in prompt, "提示词应包含用户输入"
    print("✓ PlanSpecPrompts 工作正常")
    
    # 测试枚举
    assert DocumentType.PLAN.value == "plan", "DocumentType 应正确"
    print("✓ DocumentType 枚举工作正常")
    
    print("新的 prompts 模块测试通过！\n")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("测试向后兼容性...")
    
    import warnings
    
    # 捕获弃用警告
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        from flood_decision_agent.agents.decision_chain.prompts import (
            PromptTemplates,
            get_system_prompt,
        )
        
        # 测试 PromptTemplates（别名）
        system_prompt = PromptTemplates.get_system_prompt("intent_parser")
        assert len(system_prompt) > 0, "PromptTemplates 应工作"
        print("✓ PromptTemplates 向后兼容")
        
        # 测试 get_system_prompt 函数
        system_prompt = get_system_prompt("task_decomposer")
        assert len(system_prompt) > 0, "get_system_prompt 应工作"
        print("✓ get_system_prompt 向后兼容")
        
        # 检查是否有弃用警告
        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        if deprecation_warnings:
            print(f"✓ 正确发出 {len(deprecation_warnings)} 个弃用警告")
    
    print("向后兼容性测试通过！\n")


def test_prompt_content():
    """测试提示词内容"""
    print("测试提示词内容...")
    
    from flood_decision_agent.agents.prompts import BasePrompts
    
    # 测试各个角色的系统提示词
    roles = [
        "intent_parser",
        "task_decomposer",
        "decision_generator",
        "plan_generator",
        "spec_generator",
    ]
    
    for role in roles:
        prompt = BasePrompts.get_system_prompt(role)
        assert len(prompt) > 100, f"{role} 的系统提示词应足够长"
        assert "【" in prompt, f"{role} 的系统提示词应包含格式标记"
        print(f"✓ {role} 系统提示词内容正确")
    
    print("提示词内容测试通过！\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Prompts 模块测试")
    print("=" * 60 + "\n")
    
    try:
        test_new_prompts_import()
        test_backward_compatibility()
        test_prompt_content()
        
        print("=" * 60)
        print("所有测试通过！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
