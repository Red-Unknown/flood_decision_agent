"""测试 MCP Server 的 Windows 换行符修复"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.servers.decision_chain_server import (
    _parse_markdown_sections,
    _update_markdown_section,
)


def test_parse_with_unix_line_endings():
    """测试 Unix 换行符 (\n)"""
    print("\n=== 测试 Unix 换行符 (\\n) ===")

    content = "# 标题\n\n## 章节1\n\n内容1\n\n## 章节2\n\n内容2\n"

    sections = _parse_markdown_sections(content)

    assert "章节1" in sections
    assert "章节2" in sections
    assert "内容1" in sections["章节1"]
    assert "内容2" in sections["章节2"]

    print(f"✓ 解析成功，共 {len(sections)} 个章节")


def test_parse_with_windows_line_endings():
    """测试 Windows 换行符 (\r\n)"""
    print("\n=== 测试 Windows 换行符 (\\r\\n) ===")

    content = "# 标题\r\n\r\n## 章节1\r\n\r\n内容1\r\n\r\n## 章节2\r\n\r\n内容2\r\n"

    sections = _parse_markdown_sections(content)

    assert "章节1" in sections, f"章节1 不在结果中: {sections.keys()}"
    assert "章节2" in sections, f"章节2 不在结果中: {sections.keys()}"
    assert "内容1" in sections["章节1"]
    assert "内容2" in sections["章节2"]

    print(f"✓ 解析成功，共 {len(sections)} 个章节")


def test_update_with_unix_line_endings():
    """测试 Unix 换行符下的章节更新"""
    print("\n=== 测试 Unix 换行符下的章节更新 ===")

    content = "# 标题\n\n## 章节1\n\n旧内容1\n\n## 章节2\n\n旧内容2\n"

    updated = _update_markdown_section(content, "章节1", "新内容1")

    assert "新内容1" in updated
    assert "旧内容1" not in updated
    assert "旧内容2" in updated  # 其他章节不应被修改

    print("✓ 更新成功")


def test_update_with_windows_line_endings():
    """测试 Windows 换行符下的章节更新"""
    print("\n=== 测试 Windows 换行符下的章节更新 ===")

    content = "# 标题\r\n\r\n## 章节1\r\n\r\n旧内容1\r\n\r\n## 章节2\r\n\r\n旧内容2\r\n"

    updated = _update_markdown_section(content, "章节1", "新内容1")

    assert "新内容1" in updated, f"新内容1 不在更新后的内容中:\n{updated}"
    assert "旧内容1" not in updated, f"旧内容1 仍然在更新后的内容中:\n{updated}"
    assert "旧内容2" in updated, f"旧内容2 被意外修改:\n{updated}"

    print("✓ 更新成功")


def test_update_last_section():
    """测试更新最后一个章节"""
    print("\n=== 测试更新最后一个章节 ===")

    # Windows 换行符
    content = "# 标题\r\n\r\n## 章节1\r\n\r\n内容1\r\n\r\n## 章节2\r\n\r\n旧内容2\r\n"

    updated = _update_markdown_section(content, "章节2", "新内容2")

    assert "新内容2" in updated
    assert "旧内容2" not in updated
    assert "内容1" in updated  # 第一个章节不应被修改

    print("✓ 最后一个章节更新成功")


def test_mixed_line_endings():
    """测试混合换行符"""
    print("\n=== 测试混合换行符 ===")

    content = "# 标题\n\r\n## 章节1\r\n\n内容1\r\n\r\n## 章节2\n\r\n内容2\n"

    sections = _parse_markdown_sections(content)

    assert "章节1" in sections, f"章节1 不在结果中: {sections.keys()}"
    assert "章节2" in sections, f"章节2 不在结果中: {sections.keys()}"

    print(f"✓ 混合换行符解析成功，共 {len(sections)} 个章节")


def test_chinese_section_names():
    """测试中文章节名"""
    print("\n=== 测试中文章节名 ===")

    # 使用 Unix 换行符测试
    content = "# 规划文档\n\n## 概述\n\n概述内容\n\n## 目标\n\n目标内容\n\n## 实施步骤\n\n旧步骤内容\n"

    sections = _parse_markdown_sections(content)

    assert "概述" in sections
    assert "目标" in sections
    assert "实施步骤" in sections

    # 更新中文章节
    updated = _update_markdown_section(content, "实施步骤", "新内容")
    assert "新内容" in updated
    assert "旧步骤内容" not in updated

    print("✓ 中文章节名处理成功")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("MCP Server Windows 换行符修复测试")
    print("=" * 60)

    tests = [
        test_parse_with_unix_line_endings,
        test_parse_with_windows_line_endings,
        test_update_with_unix_line_endings,
        test_update_with_windows_line_endings,
        test_update_last_section,
        test_mixed_line_endings,
        test_chinese_section_names,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 异常: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
