"""MCP 文档服务测试脚本

测试内容：
1. 创建示例 docx 文件
2. 使用 MCP 转换为 markdown
3. 验证转换结果
"""

import asyncio
import json
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flood_decision_agent.mcp.clients.base import MCPClientManager
from flood_decision_agent.infra.logging import setup_logging

# 配置日志
setup_logging()


async def test_mcp_document_service():
    """测试 MCP 文档服务"""
    print("=" * 60)
    print("MCP 文档服务测试")
    print("=" * 60)
    
    # 创建 MCP Client Manager
    manager = MCPClientManager()
    
    # 注册 document server
    manager.register_server(
        name="document",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.document_server"]
    )
    
    print("\n[1/4] 连接 MCP Server...")
    try:
        connected = await manager.connect_all()
        print(f"✓ 已连接 {connected} 个 MCP Server")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return
    
    # 列出可用工具
    print("\n[2/4] 列出可用工具...")
    tools = manager.list_all_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # 创建示例 docx 文件
    print("\n[3/4] 创建示例 docx 文件...")
    try:
        result = await manager.call_tool(
            "document",
            "create_sample_docx",
            {
                "filename": "test_document.docx",
                "title": "洪水调度决策文档"
            }
        )
        
        if result.get("success"):
            print(f"✓ {result.get('message')}")
            print(f"  文件: {result.get('filepath')}")
        else:
            print(f"✗ 创建失败: {result.get('error')}")
            if "python-docx" in result.get("error", ""):
                print("\n  提示: 请先安装 python-docx")
                print("  pip install python-docx")
            return
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        return
    
    # 转换为 markdown
    print("\n[4/4] 转换为 markdown...")
    try:
        result = await manager.call_tool(
            "document",
            "docx_to_markdown",
            {
                "input_file": "test_document.docx",
                "output_file": "converted_document.md",
                "include_metadata": True
            }
        )
        
        if result.get("success"):
            print(f"✓ 转换成功")
            print(f"  输入: {result.get('input_file')}")
            print(f"  输出: {result.get('output_file')}")
            print(f"  段落数: {result.get('paragraphs')}")
            print(f"  表格数: {result.get('tables')}")
            print(f"\n  内容预览:")
            print("  " + "-" * 50)
            preview = result.get('content_preview', '')
            for line in preview.split('\n')[:10]:
                print(f"  {line}")
            if len(preview.split('\n')) > 10:
                print("  ...")
            print("  " + "-" * 50)
        else:
            print(f"✗ 转换失败: {result.get('error')}")
    except Exception as e:
        print(f"✗ 转换失败: {e}")
    
    # 关闭连接
    print("\n关闭 MCP 连接...")
    await manager.close_all()
    print("✓ 测试完成")
    print("=" * 60)


async def test_with_unit_task_agent():
    """使用 UnitTaskExecutionAgent 风格测试 MCP"""
    print("\n" + "=" * 60)
    print("UnitTaskExecutionAgent 风格 MCP 测试")
    print("=" * 60)
    
    from flood_decision_agent.mcp.adapters.tool_adapter import MCPToolAdapter
    from flood_decision_agent.core.shared_data_pool import SharedDataPool
    
    # 创建适配器
    adapter = MCPToolAdapter()
    
    # 初始化 MCP 连接
    manager = adapter.manager
    manager.register_server(
        name="document",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.document_server"]
    )
    
    print("\n[1/3] 初始化 MCP 连接...")
    await manager.connect_all()
    print("✓ 连接成功")
    
    # 创建数据池
    data_pool = SharedDataPool()
    
    # 模拟 UnitTaskExecutionAgent 调用方式
    print("\n[2/3] 使用适配器执行工具...")
    
    # 方式1: 直接调用（新方式）
    result1 = await adapter.execute(
        tool_name="create_sample_docx",
        data_pool=data_pool,
        config={
            "filename": "agent_test.docx",
            "title": "Agent 测试文档"
        }
    )
    print(f"  create_sample_docx: {'✓' if result1.get('success') else '✗'}")
    
    # 方式2: 调用转换工具
    result2 = await adapter.execute(
        tool_name="docx_to_markdown",
        data_pool=data_pool,
        config={
            "input_file": "agent_test.docx",
            "output_file": "agent_output.md"
        }
    )
    print(f"  docx_to_markdown: {'✓' if result2.get('success') else '✗'}")
    
    if result2.get("success"):
        print(f"\n  输出文件: {result2.get('output_file')}")
        print(f"  完整路径: {result2.get('output_path')}")
    
    # 列出所有可用工具
    print("\n[3/3] 所有可用 MCP 工具:")
    all_tools = adapter.list_tools()
    for tool_name in all_tools:
        print(f"  - {tool_name}")
    
    # 关闭
    await manager.close_all()
    print("\n✓ Agent 风格测试完成")
    print("=" * 60)


async def main():
    """主函数"""
    # 测试1: 基础 MCP 文档服务
    await test_mcp_document_service()
    
    # 测试2: Agent 风格调用
    await test_with_unit_task_agent()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    print("\n生成的文件:")
    print("  - ./data/test_document.docx")
    print("  - ./plans/converted_document.md")
    print("  - ./data/agent_test.docx")
    print("  - ./plans/agent_output.md")


if __name__ == "__main__":
    asyncio.run(main())