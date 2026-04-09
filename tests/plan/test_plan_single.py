"""Plan 单链生成模式单元测试.

测试 generate_plan_single 方法的各个功能，包括：
1. 单一规划文档生成
2. 章节结构提取
3. 可编辑性支持
4. 错误处理
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, patch, MagicMock

from flood_decision_agent.agents.decision_chain.generator import (
    DecisionChainGeneratorAgent,
)
from flood_decision_agent.agents.decision_chain.plan_spec_prompts import (
    PromptContext,
    PlanSpecPrompts,
)


class TestPlanSingleGeneration:
    """测试单一规划文档生成功能."""

    def test_generate_plan_single_basic(self):
        """测试基本的单一规划生成功能."""
        agent = DecisionChainGeneratorAgent()

        # Mock LLMClient
        mock_plan_doc = """# 洪水预警系统建设规划

## 概述

本项目旨在建设一套洪水预警系统，提升洪水灾害的预警能力。

## 目标

- 目标1：建设洪水监测网络，覆盖主要流域
- 目标2：实现预警信息30秒内发布

## 实施步骤

1. **需求分析**（1周）
   - 具体内容：调研现有系统和用户需求
   - 交付物：需求规格说明书
   - 负责人：产品经理

2. **系统设计**（2周）
   - 具体内容：完成系统架构和详细设计
   - 交付物：设计文档
   - 负责人：架构师

## 验收标准

- [ ] 标准1：系统响应时间小于1秒
- [ ] 标准2：预警准确率达到95%以上

## 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 技术风险 | 中 | 高 | 提前进行技术预研 |

## 备注

无
"""

        with patch(
            "flood_decision_agent.agents.decision_chain.generator.LLMClient"
        ) as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.complete.return_value = mock_plan_doc
            mock_llm_class.return_value = mock_llm

            result = agent.generate_plan_single(
                user_input="建设一个洪水预警系统",
                domain="水利调度",
            )

        # 验证结果结构
        assert "plan_document" in result
        assert "metadata" in result
        assert result["metadata"]["editable"] is True
        assert result["metadata"]["user_input"] == "建设一个洪水预警系统"
        assert result["metadata"]["domain"] == "水利调度"

    def test_generate_plan_single_sections(self):
        """测试章节结构提取功能."""
        agent = DecisionChainGeneratorAgent()

        mock_plan_doc = """# 测试规划

## 概述

测试概述内容。

## 目标

- 目标1
- 目标2

## 实施步骤

1. 步骤一
2. 步骤二

## 验收标准

- [ ] 标准1

## 风险与应对

| 风险 | 可能性 |
|------|--------|
| 风险1 | 高 |

## 备注

备注内容
"""

        with patch(
            "flood_decision_agent.agents.decision_chain.generator.LLMClient"
        ) as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.complete.return_value = mock_plan_doc
            mock_llm_class.return_value = mock_llm

            result = agent.generate_plan_single(
                user_input="测试输入",
            )

        # 验证章节列表
        sections = result["metadata"]["sections"]
        assert "概述" in sections
        assert "目标" in sections
        assert "实施步骤" in sections
        assert "验收标准" in sections
        assert "风险与应对" in sections
        assert "备注" in sections
        assert result["metadata"]["section_count"] == 6

    def test_generate_plan_single_with_constraints(self):
        """测试带约束条件的规划生成."""
        agent = DecisionChainGeneratorAgent()

        constraints = {
            "budget": "100万",
            "timeline": "3个月",
            "team_size": 5,
        }

        with patch(
            "flood_decision_agent.agents.decision_chain.generator.LLMClient"
        ) as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.complete.return_value = "# 测试规划\n\n## 概述\n测试"
            mock_llm_class.return_value = mock_llm

            result = agent.generate_plan_single(
                user_input="建设系统",
                constraints=constraints,
            )

        assert result["metadata"]["editable"] is True

    def test_generate_plan_single_with_references(self):
        """测试带参考资料的规划生成."""
        agent = DecisionChainGeneratorAgent()

        references = [
            "《洪水预警系统建设规范》",
            "《水利信息化技术标准》",
        ]

        with patch(
            "flood_decision_agent.agents.decision_chain.generator.LLMClient"
        ) as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.complete.return_value = "# 测试规划\n\n## 概述\n测试"
            mock_llm_class.return_value = mock_llm

            result = agent.generate_plan_single(
                user_input="建设系统",
                references=references,
            )

        assert result["metadata"]["editable"] is True

    def test_generate_plan_single_error_handling(self):
        """测试错误处理."""
        agent = DecisionChainGeneratorAgent()

        with patch(
            "flood_decision_agent.agents.decision_chain.generator.LLMClient"
        ) as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.complete.side_effect = Exception("LLM调用失败")
            mock_llm_class.return_value = mock_llm

            result = agent.generate_plan_single(
                user_input="建设系统",
            )

        # 验证错误处理
        assert result["plan_document"] == ""
        assert "error" in result["metadata"]
        assert result["metadata"]["editable"] is False
        assert "LLM调用失败" in result["metadata"]["error"]


class TestExtractPlanSections:
    """测试章节提取功能."""

    def test_extract_sections_normal(self):
        """测试正常章节提取."""
        agent = DecisionChainGeneratorAgent()

        plan_doc = """# 规划标题

## 概述

概述内容

## 目标

目标内容

## 实施步骤

步骤内容

## 验收标准

验收内容
"""

        sections = agent._extract_plan_sections(plan_doc)

        assert len(sections) == 4
        assert "概述" in sections
        assert "目标" in sections
        assert "实施步骤" in sections
        assert "验收标准" in sections

    def test_extract_sections_empty(self):
        """测试空文档."""
        agent = DecisionChainGeneratorAgent()

        sections = agent._extract_plan_sections("")
        assert sections == []

    def test_extract_sections_no_headers(self):
        """测试无章节标题的文档."""
        agent = DecisionChainGeneratorAgent()

        plan_doc = "这是一段没有章节标题的内容"
        sections = agent._extract_plan_sections(plan_doc)
        assert sections == []

    def test_extract_sections_with_special_chars(self):
        """测试包含特殊字符的章节标题."""
        agent = DecisionChainGeneratorAgent()

        plan_doc = """# 标题

## 目标与指标（2024年）

内容

## 风险 & 应对

内容
"""

        sections = agent._extract_plan_sections(plan_doc)

        assert len(sections) == 2
        assert "目标与指标（2024年）" in sections
        assert "风险 & 应对" in sections


class TestPlanSpecPrompts:
    """测试 PlanSpecPrompts 类."""

    def test_get_plan_single_generation_prompt_structure(self):
        """测试单一规划生成提示词结构."""
        context = PromptContext(
            user_input="测试需求",
            domain="测试领域",
        )

        prompt = PlanSpecPrompts.get_plan_single_generation_prompt(context)

        # 验证提示词包含关键要素
        assert "只生成单一规划方案" in prompt
        assert "可编辑性" in prompt
        assert "章节结构说明" in prompt
        assert "测试需求" in prompt
        assert "测试领域" in prompt

    def test_get_plan_single_generation_prompt_with_constraints(self):
        """测试带约束条件的提示词."""
        context = PromptContext(
            user_input="测试需求",
            constraints={"budget": "100万"},
        )

        prompt = PlanSpecPrompts.get_plan_single_generation_prompt(context)

        assert "约束条件" in prompt
        assert "budget" in prompt

    def test_get_plan_single_generation_prompt_with_references(self):
        """测试带参考资料的提示词."""
        context = PromptContext(
            user_input="测试需求",
            references=["参考资料1", "参考资料2"],
        )

        prompt = PlanSpecPrompts.get_plan_single_generation_prompt(context)

        assert "参考资料" in prompt
        assert "参考资料1" in prompt
        assert "参考资料2" in prompt


class TestPlanSingleIntegration:
    """集成测试."""

    def test_plan_single_end_to_end(self):
        """测试完整的单一规划生成流程."""
        agent = DecisionChainGeneratorAgent()

        mock_plan_doc = """# 水库调度优化系统建设规划

## 概述

建设一套智能水库调度优化系统，提升调度决策的科学性和效率。

## 目标

- 目标1：实现水库调度方案自动生成，响应时间小于5秒
- 目标2：调度方案准确率达到90%以上
- 目标3：支持多目标优化（防洪、发电、生态）

## 实施步骤

1. **需求调研**（2周）
   - 具体内容：调研水库调度业务流程和用户需求
   - 交付物：需求调研报告
   - 负责人：业务分析师

2. **算法设计**（4周）
   - 具体内容：设计多目标优化算法和调度模型
   - 交付物：算法设计文档
   - 负责人：算法工程师

3. **系统开发**（8周）
   - 具体内容：完成系统前后端开发
   - 交付物：可运行的系统
   - 负责人：开发团队

## 验收标准

- [ ] 标准1：系统功能覆盖所有需求点
- [ ] 标准2：性能测试通过，响应时间达标
- [ ] 标准3：用户验收测试通过

## 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 算法精度不达标 | 中 | 高 | 增加数据样本，优化模型 |
| 需求变更 | 高 | 中 | 采用敏捷开发，快速迭代 |

## 备注

项目需在汛期前完成部署。
"""

        with patch(
            "flood_decision_agent.agents.decision_chain.generator.LLMClient"
        ) as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.complete.return_value = mock_plan_doc
            mock_llm_class.return_value = mock_llm

            result = agent.generate_plan_single(
                user_input="建设水库调度优化系统",
                domain="水利调度",
                constraints={"timeline": "3个月"},
                references=["《水库调度规程》"],
            )

        # 验证完整结果
        assert result["plan_document"].strip() == mock_plan_doc.strip()
        assert result["metadata"]["editable"] is True
        assert result["metadata"]["section_count"] == 6
        assert "概述" in result["metadata"]["sections"]
        assert "目标" in result["metadata"]["sections"]
        assert "实施步骤" in result["metadata"]["sections"]
        assert "验收标准" in result["metadata"]["sections"]
        assert "风险与应对" in result["metadata"]["sections"]
        assert "备注" in result["metadata"]["sections"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
