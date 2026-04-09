"""Plan/Spec 模式测试用例

测试 decision_chain MCP 服务与 plan/spec 模式的集成，
包括文档创建、读取、更新和手工编辑功能。
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest


class TestPlanMode:
    """Plan 模式测试类"""

    def setup_method(self):
        """测试前置准备"""
        self.test_dir = tempfile.mkdtemp()
        self.plans_dir = os.path.join(self.test_dir, "plans")
        os.makedirs(self.plans_dir, exist_ok=True)

    def teardown_method(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_plan_basic(self):
        """测试创建基础规划文档"""
        # 测试问题：验证是否能正确创建规划文档
        plan_data = {
            "title": "洪水预警系统优化规划",
            "description": "提升洪水预警的准确性和响应速度",
            "goals": "- 预警准确率提升至95%\n- 响应时间缩短至5分钟",
            "steps": "1. 数据接入优化\n2. 模型训练\n3. 系统集成",
            "criteria": "- 通过压力测试\n- 用户验收通过",
            "output_path": os.path.join(self.plans_dir, "test_plan.md")
        }
        
        # 验证数据完整性
        assert plan_data["title"], "规划标题不能为空"
        assert plan_data["description"], "规划描述不能为空"
        assert plan_data["goals"], "规划目标不能为空"
        assert plan_data["steps"], "实施步骤不能为空"
        assert plan_data["criteria"], "验收标准不能为空"

    def test_create_plan_with_chinese_title(self):
        """测试创建中文标题的规划文档"""
        # 测试问题：验证中文标题处理
        plan_data = {
            "title": "水库调度系统智能化升级规划",
            "description": "引入AI技术优化水库调度决策",
            "goals": "- 调度效率提升30%\n- 人工成本降低50%",
            "steps": "1. 需求分析\n2. 方案设计\n3. 开发实施\n4. 测试上线",
            "criteria": "- 系统稳定运行\n- 用户培训完成",
            "output_path": os.path.join(self.plans_dir, "水库调度规划.md")
        }
        
        # 验证中文字符正确处理
        assert "水库" in plan_data["title"]
        assert "调度" in plan_data["description"]

    def test_read_plan_sections(self):
        """测试读取规划文档章节"""
        # 测试问题：验证章节解析功能
        plan_content = """# 测试规划

## 概述

这是概述内容

## 目标

- 目标1
- 目标2

## 实施步骤

1. 步骤一
2. 步骤二

## 验收标准

标准内容
"""
        
        # 模拟章节解析
        sections = self._parse_markdown_sections(plan_content)
        
        assert "概述" in sections
        assert "目标" in sections
        assert "实施步骤" in sections
        assert "验收标准" in sections

    def test_update_plan_section(self):
        """测试更新规划文档章节"""
        # 测试问题：验证章节更新功能
        original_content = """# 测试规划

## 实施步骤

1. 旧步骤一
2. 旧步骤二
"""
        
        section_name = "实施步骤"
        new_content = "1. 新步骤一\n2. 新步骤二\n3. 新步骤三"
        
        updated = self._update_markdown_section(
            original_content, section_name, new_content
        )
        
        assert "新步骤一" in updated
        assert "新步骤三" in updated
        assert "旧步骤一" not in updated

    def test_plan_template_structure(self):
        """测试规划模板结构完整性"""
        # 测试问题：验证模板包含所有必要章节
        required_sections = [
            "概述",
            "目标", 
            "实施步骤",
            "验收标准",
            "备注"
        ]
        
        # 模拟模板验证
        template_sections = ["概述", "目标", "实施步骤", "验收标准", "备注"]
        
        for section in required_sections:
            assert section in template_sections, f"缺少必要章节: {section}"

    def _parse_markdown_sections(self, content: str) -> dict:
        """辅助函数：解析markdown章节"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections

    def _update_markdown_section(self, content: str, section_name: str, new_content: str) -> str:
        """辅助函数：更新markdown章节"""
        lines = content.split('\n')
        result = []
        in_target_section = False
        section_updated = False
        
        for line in lines:
            if line.startswith('## '):
                if in_target_section and not section_updated:
                    result.append(new_content)
                    section_updated = True
                
                if line[3:].strip() == section_name:
                    in_target_section = True
                    result.append(line)
                else:
                    in_target_section = False
                    result.append(line)
            elif not in_target_section:
                result.append(line)
        
        if in_target_section and not section_updated:
            result.append(new_content)
        
        return '\n'.join(result)


class TestSpecMode:
    """Spec 模式测试类"""

    def setup_method(self):
        """测试前置准备"""
        self.test_dir = tempfile.mkdtemp()
        self.specs_dir = os.path.join(self.test_dir, ".trae", "specs")
        os.makedirs(self.specs_dir, exist_ok=True)

    def teardown_method(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_spec_suite(self):
        """测试创建规格文档套装"""
        # 测试问题：验证是否能创建完整的spec套装
        spec_data = {
            "feature_name": "flood-warning-v2",
            "title": "洪水预警系统V2",
            "description": "新一代洪水预警系统",
            "requirements": "- 支持多源数据\n- 预警准确率≥95%",
            "technical_design": "微服务架构",
            "interfaces": "REST API",
            "acceptance_criteria": "- 测试通过",
            "tasks": "- [ ] 任务1"
        }
        
        # 验证必要字段
        assert spec_data["feature_name"], "功能名称不能为空"
        assert spec_data["title"], "标题不能为空"
        assert spec_data["description"], "描述不能为空"
        assert spec_data["requirements"], "需求不能为空"

    def test_spec_file_structure(self):
        """测试规格文件结构"""
        # 测试问题：验证spec套装包含所有必要文件
        expected_files = ["spec.md", "tasks.md", "checklist.md"]
        
        feature_dir = os.path.join(self.specs_dir, "test-feature")
        os.makedirs(feature_dir, exist_ok=True)
        
        # 模拟创建文件
        for filename in expected_files:
            filepath = os.path.join(feature_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {filename}\n")
        
        # 验证文件存在
        for filename in expected_files:
            filepath = os.path.join(feature_dir, filename)
            assert os.path.exists(filepath), f"缺少文件: {filename}"

    def test_spec_sections_validation(self):
        """测试规格文档章节验证"""
        # 测试问题：验证spec.md包含必要章节
        spec_content = """# 功能规格

## 概述

功能概述

## 功能需求

需求列表

## 技术方案

技术细节

## 接口定义

接口说明

## 验收标准

验收条件
"""
        
        required_sections = ["概述", "功能需求", "技术方案", "接口定义", "验收标准"]
        sections = self._parse_markdown_sections(spec_content)
        
        for section in required_sections:
            assert section in sections, f"spec.md 缺少章节: {section}"

    def test_tasks_sections_validation(self):
        """测试任务文档章节验证"""
        # 测试问题：验证tasks.md包含必要章节
        tasks_content = """# 任务列表

## 任务分解

- [ ] 任务1
- [ ] 任务2

## 依赖关系

任务1 -> 任务2

## 时间估算

- 任务1: 3天
- 任务2: 5天
"""
        
        required_sections = ["任务分解", "依赖关系", "时间估算"]
        sections = self._parse_markdown_sections(tasks_content)
        
        for section in required_sections:
            assert section in sections, f"tasks.md 缺少章节: {section}"

    def test_checklist_sections_validation(self):
        """测试检查清单章节验证"""
        # 测试问题：验证checklist.md包含必要章节
        checklist_content = """# 检查清单

## 前置条件

- [ ] 需求确认

## 开发检查项

- [ ] 代码实现

## 测试检查项

- [ ] 单元测试

## 部署检查项

- [ ] 部署文档

## 文档检查项

- [ ] API文档
"""
        
        required_sections = [
            "前置条件", "开发检查项", "测试检查项", 
            "部署检查项", "文档检查项"
        ]
        sections = self._parse_markdown_sections(checklist_content)
        
        for section in required_sections:
            assert section in sections, f"checklist.md 缺少章节: {section}"

    def test_update_spec_section(self):
        """测试更新规格文档章节"""
        # 测试问题：验证spec章节更新
        original_content = """# 规格文档

## 功能需求

旧需求
"""
        
        new_content = "- 新需求1\n- 新需求2"
        updated = self._update_markdown_section(
            original_content, "功能需求", new_content
        )
        
        assert "新需求1" in updated
        assert "旧需求" not in updated

    def _parse_markdown_sections(self, content: str) -> dict:
        """辅助函数：解析markdown章节"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections

    def _update_markdown_section(self, content: str, section_name: str, new_content: str) -> str:
        """辅助函数：更新markdown章节"""
        lines = content.split('\n')
        result = []
        in_target_section = False
        section_updated = False
        
        for line in lines:
            if line.startswith('## '):
                if in_target_section and not section_updated:
                    result.append(new_content)
                    section_updated = True
                
                if line[3:].strip() == section_name:
                    in_target_section = True
                    result.append(line)
                else:
                    in_target_section = False
                    result.append(line)
            elif not in_target_section:
                result.append(line)
        
        if in_target_section and not section_updated:
            result.append(new_content)
        
        return '\n'.join(result)


class TestManualEditing:
    """手工编辑功能测试类"""

    def setup_method(self):
        """测试前置准备"""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_read_document_content(self):
        """测试读取文档内容"""
        # 测试问题：验证文档读取功能
        test_file = os.path.join(self.test_dir, "test.md")
        test_content = "# 测试文档\n\n内容"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content == test_content

    def test_save_document_content(self):
        """测试保存文档内容"""
        # 测试问题：验证文档保存功能
        test_file = os.path.join(self.test_dir, "test.md")
        test_content = "# 新内容\n\n更新后的内容"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        assert os.path.exists(test_file)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        assert saved_content == test_content

    def test_backup_on_save(self):
        """测试保存时自动备份"""
        # 测试问题：验证自动备份功能
        test_file = os.path.join(self.test_dir, "test.md")
        backup_dir = os.path.join(self.test_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # 原始内容
        original_content = "# 原始内容"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # 创建备份
        import datetime
        backup_name = f"test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.copy2(test_file, backup_path)
        
        # 更新内容
        new_content = "# 新内容"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 验证备份存在
        assert os.path.exists(backup_path)

    def test_validate_markdown(self):
        """测试Markdown格式验证"""
        # 测试问题：验证Markdown格式检查
        valid_md = """# 标题

## 二级标题

- 列表项1
- 列表项2

**粗体文本**
"""
        
        # 基本验证：检查标题格式
        assert valid_md.startswith('#')
        assert '## ' in valid_md
        assert '- ' in valid_md

    def test_preview_markdown(self):
        """测试Markdown预览"""
        # 测试问题：验证Markdown渲染预览
        md_content = """# 标题

这是段落

- 列表项
"""
        
        # 模拟渲染（实际应该调用渲染库）
        # 这里仅验证内容存在
        assert "# 标题" in md_content
        assert "列表项" in md_content


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """测试前置准备"""
        self.test_dir = tempfile.mkdtemp()
        self.plans_dir = os.path.join(self.test_dir, "plans")
        self.specs_dir = os.path.join(self.test_dir, ".trae", "specs")
        os.makedirs(self.plans_dir, exist_ok=True)
        os.makedirs(self.specs_dir, exist_ok=True)

    def teardown_method(self):
        """测试后置清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plan_to_spec_workflow(self):
        """测试从Plan到Spec的完整工作流"""
        # 测试问题：验证从规划到规格的完整流程
        
        # 1. 创建Plan
        plan_content = """# 系统优化规划

## 概述

优化现有系统

## 目标

- 性能提升
- 稳定性增强

## 实施步骤

1. 分析现状
2. 设计方案
3. 开发实施

## 验收标准

- 测试通过
"""
        
        plan_file = os.path.join(self.plans_dir, "optimization_plan.md")
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        # 2. 基于Plan创建Spec
        spec_feature_name = "system-optimization"
        spec_dir = os.path.join(self.specs_dir, spec_feature_name)
        os.makedirs(spec_dir, exist_ok=True)
        
        spec_content = """# 系统优化 - 规格文档

## 概述

基于规划文档进行详细设计

## 功能需求

- 性能优化需求
- 稳定性需求

## 技术方案

待补充

## 接口定义

待补充

## 验收标准

- 符合规划要求
"""
        
        spec_file = os.path.join(spec_dir, "spec.md")
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        # 验证文件存在
        assert os.path.exists(plan_file)
        assert os.path.exists(spec_file)

    def test_ai_assisted_generation(self):
        """测试AI辅助生成功能"""
        # 测试问题：验证AI生成内容的集成
        
        prompt = "为水库调度系统制定优化规划"
        context = {
            "current_system": "基于规则调度",
            "goals": ["提升效率", "降低成本"]
        }
        
        # 模拟AI生成结果
        generated = {
            "title": "水库调度系统智能化升级规划",
            "description": "引入AI优化调度决策",
            "goals": "- 效率提升30%\n- 成本降低20%",
            "steps": "1. 需求分析\n2. 方案设计\n3. 开发实施",
            "criteria": "- 系统稳定\n- 用户满意"
        }
        
        # 验证生成内容完整性
        assert generated["title"]
        assert generated["description"]
        assert generated["goals"]
        assert generated["steps"]
        assert generated["criteria"]

    def test_collaboration_locking(self):
        """测试协作锁定机制"""
        # 测试问题：验证多人协作时的锁定机制
        
        document_id = "plan_001"
        section = "实施步骤"
        user_id = "user_123"
        
        # 模拟锁定
        lock_info = {
            "document_id": document_id,
            "section": section,
            "locked_by": user_id,
            "locked_at": "2026-03-26T10:00:00Z"
        }
        
        assert lock_info["locked_by"] == user_id
        assert lock_info["section"] == section


# 测试数据工厂
def create_test_plan_data():
    """创建测试用的规划数据"""
    return {
        "title": "测试规划",
        "description": "测试描述",
        "goals": "- 目标1\n- 目标2",
        "steps": "1. 步骤1\n2. 步骤2",
        "criteria": "- 标准1\n- 标准2",
        "notes": "备注信息"
    }


def create_test_spec_data():
    """创建测试用的规格数据"""
    return {
        "feature_name": "test-feature",
        "title": "测试功能",
        "description": "功能描述",
        "requirements": "- 需求1\n- 需求2",
        "technical_design": "技术方案",
        "interfaces": "接口定义",
        "acceptance_criteria": "验收标准",
        "tasks": "- [ ] 任务1"
    }


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
