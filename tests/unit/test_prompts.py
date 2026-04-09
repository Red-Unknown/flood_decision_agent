"""Prompts 模块单元测试

测试 prompts 模块的各个组件
"""

import pytest
from flood_decision_agent.agents.prompts import (
    BasePrompts,
    IntentParserPrompts,
    TaskDecomposerPrompts,
    DecisionGeneratorPrompts,
    PlanSpecPrompts,
    DocumentType,
    PromptContext,
    AgentRole,
    get_system_prompt,
)


class TestBasePrompts:
    """测试 BasePrompts 类"""

    def test_get_system_prompt_intent_parser(self):
        """测试获取意图解析器系统提示词"""
        prompt = BasePrompts.get_system_prompt("intent_parser")
        assert len(prompt) > 100
        assert "水利智脑" in prompt
        assert "【你的职责】" in prompt

    def test_get_system_prompt_task_decomposer(self):
        """测试获取任务分解器系统提示词"""
        prompt = BasePrompts.get_system_prompt("task_decomposer")
        assert len(prompt) > 100
        assert "任务规划师" in prompt

    def test_get_system_prompt_decision_generator(self):
        """测试获取决策生成器系统提示词"""
        prompt = BasePrompts.get_system_prompt("decision_generator")
        assert len(prompt) > 100
        assert "调度决策专家" in prompt

    def test_get_system_prompt_plan_generator(self):
        """测试获取规划生成器系统提示词"""
        prompt = BasePrompts.get_system_prompt("plan_generator")
        assert len(prompt) > 100
        assert "规划专家" in prompt

    def test_get_system_prompt_spec_generator(self):
        """测试获取规格生成器系统提示词"""
        prompt = BasePrompts.get_system_prompt("spec_generator")
        assert len(prompt) > 100
        assert "规格设计专家" in prompt

    def test_get_system_prompt_unknown(self):
        """测试获取未知类型的系统提示词"""
        prompt = BasePrompts.get_system_prompt("unknown_type")
        assert prompt == "你是一个专业的 AI 助手。"


class TestIntentParserPrompts:
    """测试 IntentParserPrompts 类"""

    def test_get_intent_parser_prompt_basic(self):
        """测试基本的意图解析提示词生成"""
        user_input = "分析北江洪水情况"
        templates = []
        prompt = IntentParserPrompts.get_intent_parser_prompt(user_input, templates)
        
        assert user_input in prompt
        assert "【任务】" in prompt
        assert "【用户输入】" in prompt
        assert "【输出要求】" in prompt

    def test_get_intent_parser_prompt_with_templates(self):
        """测试带模板的意图解析提示词生成"""
        user_input = "设计洪水预警系统"
        templates = [
            {"name": "洪水预警", "description": "设计洪水预警系统"}
        ]
        prompt = IntentParserPrompts.get_intent_parser_prompt(user_input, templates, use_template_context=True)
        
        assert "【参考模板】" in prompt
        assert "洪水预警" in prompt


class TestTaskDecomposerPrompts:
    """测试 TaskDecomposerPrompts 类"""

    def test_get_task_decomposer_prompt(self):
        """测试任务分解提示词生成"""
        intent = {"task": "洪水预警系统设计", "type": "plan"}
        execution_types = ["analysis", "design", "implementation"]
        prompt = TaskDecomposerPrompts.get_task_decomposer_prompt(intent, execution_types)
        
        assert "洪水预警系统设计" in prompt
        assert "analysis" in prompt
        assert "【分解要求】" in prompt
        assert "【输出格式】" in prompt


class TestDecisionGeneratorPrompts:
    """测试 DecisionGeneratorPrompts 类"""

    def test_get_decision_generator_prompt(self):
        """测试决策生成提示词"""
        data_summary = {"water_level": 165.5, "inflow": 20000}
        objectives = ["防洪安全", "发电效益"]
        constraints = {"max_outflow": 25000}
        
        prompt = DecisionGeneratorPrompts.get_decision_generator_prompt(
            data_summary, objectives, constraints
        )
        
        assert "165.5" in prompt
        assert "防洪安全" in prompt
        assert "max_outflow" in prompt

    def test_get_risk_assessment_prompt(self):
        """测试风险评估提示词"""
        scenario = {"location": "北江", "rainfall": 100}
        risk_factors = ["洪水风险", "溃坝风险"]
        
        prompt = DecisionGeneratorPrompts.get_risk_assessment_prompt(scenario, risk_factors)
        
        assert "北江" in prompt
        assert "洪水风险" in prompt

    def test_get_report_generator_prompt(self):
        """测试报告生成提示词"""
        task_results = [{"task": "数据分析", "result": "完成"}]
        prompt = DecisionGeneratorPrompts.get_report_generator_prompt(task_results, "测试报告")
        
        assert "数据分析" in prompt
        assert "测试报告" in prompt


class TestPlanSpecPrompts:
    """测试 PlanSpecPrompts 类"""

    def test_get_plan_generation_prompt(self):
        """测试规划生成提示词"""
        context = PromptContext(user_input="设计洪水预警系统")
        prompt = PlanSpecPrompts.get_plan_generation_prompt(context)
        
        assert "设计洪水预警系统" in prompt
        assert "【任务】" in prompt

    def test_get_spec_generation_prompt(self):
        """测试规格生成提示词"""
        context = PromptContext(user_input="实现洪水预警模块")
        prompt = PlanSpecPrompts.get_spec_generation_prompt(context)
        
        assert "实现洪水预警模块" in prompt
        assert "【任务】" in prompt


class TestDocumentType:
    """测试 DocumentType 枚举"""

    def test_document_type_values(self):
        """测试文档类型枚举值"""
        assert DocumentType.PLAN.value == "plan"
        assert DocumentType.SPEC.value == "spec"
        assert DocumentType.TASKS.value == "tasks"
        assert DocumentType.CHECKLIST.value == "checklist"


class TestPromptContext:
    """测试 PromptContext 类"""

    def test_prompt_context_creation(self):
        """测试 PromptContext 创建"""
        context = PromptContext(
            user_input="测试输入",
            domain="水利调度",
            existing_content="已有内容",
            constraints={"time": "1个月"},
            references=["参考1", "参考2"],
        )
        
        assert context.user_input == "测试输入"
        assert context.domain == "水利调度"
        assert context.existing_content == "已有内容"
        assert context.constraints == {"time": "1个月"}
        assert len(context.references) == 2


class TestAgentRole:
    """测试 AgentRole 枚举"""

    def test_agent_role_values(self):
        """测试 Agent 角色枚举值"""
        assert AgentRole.INTENT_PARSER.value == "intent_parser"
        assert AgentRole.TASK_DECOMPOSER.value == "task_decomposer"
        assert AgentRole.DECISION_GENERATOR.value == "decision_generator"


class TestGetSystemPromptFunction:
    """测试 get_system_prompt 便捷函数"""

    def test_get_system_prompt_function(self):
        """测试模块级别的 get_system_prompt 函数"""
        prompt = get_system_prompt("intent_parser")
        assert len(prompt) > 100
        assert "水利智脑" in prompt
