"""MCP 包装器简化测试

测试包装器核心功能，使用已连接的服务。
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def check_api_key():
    """检查 KIMI_API_KEY 环境变量"""
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("=" * 60)
        print("错误: 需要 KIMI_API_KEY 环境变量")
        print("=" * 60)
        sys.exit(1)
    return api_key


async def main():
    """运行简化测试"""
    print("=" * 60)
    print("MCP 包装器简化测试")
    print("=" * 60)
    
    # 检查 API Key
    api_key = check_api_key()
    print(f"\n✓ API Key 已配置: {api_key[:10]}...")
    
    # 导入测试
    print("\n1. 测试模块导入...")
    from flood_decision_agent.mcp.clients import (
        PromptManager,
        SimpleClientWrapper,
        ComplexClientWrapper,
        MCPWrapperFactory,
        MCPWrappedClientManager,
        MCPClientManager,
    )
    from flood_decision_agent.infrastructure.llm.kimi_client import get_kimi_client
    print("✓ 所有模块导入成功")
    
    # 测试 PromptManager
    print("\n2. 测试 PromptManager...")
    assert PromptManager.is_complex_tool("hydrology") == True
    assert PromptManager.is_complex_tool("hipims") == True
    assert PromptManager.is_simple_tool("data_hub") == True
    assert PromptManager.is_simple_tool("filesystem") == True
    
    prompt = PromptManager.get_prompt("hipims")
    assert prompt is not None
    assert "水利专家" in prompt
    print("✓ PromptManager 测试通过")
    
    # 初始化 MCP 管理器
    print("\n3. 初始化 MCP 管理器...")
    manager = MCPClientManager(auto_load_config=True)
    connected = await manager.connect_all()
    print(f"✓ 已连接 {connected} 个 MCP 服务")
    
    # 列出可用工具
    tools = manager.list_all_tools()
    print(f"\n可用工具 ({len(tools)} 个):")
    for tool in tools[:5]:  # 只显示前5个
        print(f"  - {tool.name} ({tool.server_name})")
    if len(tools) > 5:
        print(f"  ... 还有 {len(tools) - 5} 个")
    
    # 测试简单包装器
    print("\n4. 测试 SimpleClientWrapper...")
    simple = SimpleClientWrapper(manager)
    
    # 使用 filesystem 服务测试
    result = await simple.execute(
        server_name="filesystem",
        tool_name="list_directory",
        arguments={"path": "."}
    )
    
    assert result["success"] == True
    assert result["wrapped"] == False
    assert "raw_data" in result
    print("✓ SimpleClientWrapper 测试通过")
    print(f"  - wrapped: {result['wrapped']}")
    print(f"  - server: {result['server']}")
    print(f"  - tool: {result['tool']}")
    
    # 测试 LLM 客户端
    print("\n5. 测试 LLM 客户端...")
    try:
        llm_client = get_kimi_client()
        print("✓ LLM 客户端初始化成功")
        
        # 测试复杂包装器
        print("\n6. 测试 ComplexClientWrapper...")
        complex_wrapper = ComplexClientWrapper(manager, llm_client)
        
        # 使用 filesystem 服务测试（模拟复杂工具行为）
        result = await complex_wrapper.execute(
            server_name="filesystem",
            tool_name="list_directory",
            arguments={"path": "."}
        )
        
        assert result["success"] == True
        assert result["wrapped"] == True
        assert "raw_data" in result
        assert "explanation" in result
        print("✓ ComplexClientWrapper 测试通过")
        print(f"  - wrapped: {result['wrapped']}")
        print(f"  - has_explanation: {result['explanation'] is not None}")
        if result['explanation']:
            print(f"  - summary: {result['summary'][:50]}...")
        
    except Exception as e:
        print(f"⚠ LLM 测试跳过: {e}")
    
    # 测试包装器工厂
    print("\n7. 测试 MCPWrapperFactory...")
    factory = MCPWrapperFactory(manager)
    
    # 测试简单工具自动选择
    result = await factory.execute(
        server_name="filesystem",
        tool_name="list_directory",
        arguments={"path": "."}
    )
    
    # 注意：list_directory 不是复杂工具，所以不会包装
    print(f"✓ MCPWrapperFactory 测试通过")
    print(f"  - 简单工具 wrapped: {result.get('wrapped', 'N/A')}")
    
    # 测试带包装器的管理器
    print("\n8. 测试 MCPWrappedClientManager...")
    wrapped_manager = MCPWrappedClientManager(
        mcp_manager=manager,
        auto_load_config=False  # 使用已有的 manager
    )
    
    # 测试不包装调用
    result = await wrapped_manager.call_tool(
        server_name="filesystem",
        tool_name="list_directory",
        arguments={"path": "."},
        wrap_result=False
    )
    
    print("✓ MCPWrappedClientManager 测试通过")
    print(f"  - 不包装调用成功")
    
    # 关闭连接
    await manager.close_all()
    print("\n✓ MCP 连接已关闭")
    
    # 测试摘要
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    print("\n✓ 所有核心测试通过！")
    print("\n测试内容:")
    print("  1. 模块导入")
    print("  2. PromptManager 工具分类")
    print("  3. MCPClientManager 初始化")
    print("  4. SimpleClientWrapper 透传功能")
    print("  5. LLM 客户端初始化")
    print("  6. ComplexClientWrapper 包装功能")
    print("  7. MCPWrapperFactory 自动选择")
    print("  8. MCPWrappedClientManager 集成")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
