"""MCP与单元任务执行Agent集成测试

测试MCP服务如何接入单元任务执行Agent。
"""

import asyncio
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flood_decision_agent.agents.task_executor.executor import UnitTaskExecutionAgent
from flood_decision_agent.agents.task_executor.mcp_integration import (
    MCPToolIntegration,
    UnitTaskExecutorWithMCP,
    setup_mcp_for_executor,
)
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.infrastructure.logging import setup_logging

# 配置日志
setup_logging()


async def test_mcp_tool_integration():
    """测试MCP工具集成"""
    print("=" * 70)
    print("测试1: MCP工具集成")
    print("=" * 70)
    
    # 创建基础执行器
    print("\n[1/5] 创建基础执行器...")
    executor = UnitTaskExecutionAgent()
    print(f"✓ 执行器创建成功，已有 {len(executor.tool_registry.list_tools())} 个工具")
    
    # 创建MCP集成
    print("\n[2/5] 创建MCP工具集成器...")
    mcp_integration = MCPToolIntegration(
        tool_registry=executor.tool_registry,
    )
    print("✓ MCP集成器创建成功")
    
    # 初始化MCP
    print("\n[3/5] 初始化MCP连接...")
    success = await mcp_integration.initialize()
    if success:
        print("✓ MCP连接成功")
    else:
        print("✗ MCP连接失败")
        return
    
    # 查看注册的MCP工具
    print("\n[4/5] 查看注册的MCP工具...")
    mcp_tools = mcp_integration.get_registered_mcp_tools()
    print(f"✓ 已注册 {len(mcp_tools)} 个MCP工具:")
    for tool in mcp_tools:
        print(f"  - {tool}")
    
    # 执行MCP工具
    print("\n[5/5] 测试执行MCP工具...")
    data_pool = SharedDataPool()
    
    # 测试文档创建工具
    if "mcp_create_sample_docx" in mcp_tools:
        result = await mcp_integration.execute_mcp_tool(
            tool_name="mcp_create_sample_docx",
            data_pool=data_pool,
            config={
                "filename": "mcp_test.docx",
                "title": "MCP集成测试文档"
            }
        )
        
        if result.get("success"):
            print(f"✓ MCP工具执行成功")
            print(f"  结果: {result.get('result', {}).get('message', 'N/A')}")
        else:
            print(f"✗ MCP工具执行失败: {result.get('error')}")
    
    # 关闭连接
    print("\n关闭MCP连接...")
    await mcp_integration.close()
    print("✓ 测试完成")
    print("=" * 70)


async def test_executor_with_mcp():
    """测试支持MCP的执行器包装器"""
    print("\n" + "=" * 70)
    print("测试2: 支持MCP的执行器包装器")
    print("=" * 70)
    
    # 创建基础执行器
    print("\n[1/4] 创建基础执行器...")
    base_executor = UnitTaskExecutionAgent()
    print(f"✓ 基础执行器创建成功")
    
    # 创建支持MCP的包装器
    print("\n[2/4] 创建支持MCP的包装器...")
    executor_with_mcp = UnitTaskExecutorWithMCP(
        base_executor=base_executor,
        enable_mcp=True,
    )
    print("✓ MCP包装器创建成功")
    
    # 初始化MCP
    print("\n[3/4] 初始化MCP...")
    success = await executor_with_mcp.initialize_mcp()
    if success:
        print("✓ MCP初始化成功")
    else:
        print("✗ MCP初始化失败")
        return
    
    # 查看所有可用工具
    print("\n[4/4] 查看所有可用工具...")
    all_tools = executor_with_mcp.get_available_tools()
    base_tools = base_executor.tool_registry.list_tools()
    mcp_tools = [t for t in all_tools if t.startswith("mcp_")]
    
    print(f"✓ 基础工具: {len(base_tools)} 个")
    print(f"✓ MCP工具: {len(mcp_tools)} 个")
    print(f"✓ 总计: {len(all_tools)} 个")
    
    if mcp_tools:
        print("\nMCP工具列表:")
        for tool in mcp_tools[:5]:  # 只显示前5个
            print(f"  - {tool}")
        if len(mcp_tools) > 5:
            print(f"  ... 还有 {len(mcp_tools) - 5} 个")
    
    # 关闭
    print("\n关闭资源...")
    await executor_with_mcp.close()
    print("✓ 测试完成")
    print("=" * 70)


async def test_mcp_tool_via_executor():
    """测试通过执行器调用MCP工具"""
    print("\n" + "=" * 70)
    print("测试3: 通过执行器调用MCP工具")
    print("=" * 70)
    
    # 创建执行器并设置MCP
    print("\n[1/3] 创建执行器并设置MCP...")
    executor = UnitTaskExecutionAgent()
    mcp_integration = await setup_mcp_for_executor(executor)
    print("✓ 设置完成")
    
    # 准备数据池
    print("\n[2/3] 准备数据池...")
    data_pool = SharedDataPool()
    data_pool.set("test_data", {"key": "value"})
    print("✓ 数据池准备完成")
    
    # 获取可用MCP工具
    print("\n[3/3] 尝试执行MCP工具...")
    mcp_tools = mcp_integration.get_registered_mcp_tools()
    
    if mcp_tools:
        # 尝试执行第一个可用的MCP工具
        test_tool = mcp_tools[0]
        print(f"  测试工具: {test_tool}")
        
        try:
            result = await mcp_integration.execute_mcp_tool(
                tool_name=test_tool,
                data_pool=data_pool,
                config={}
            )
            
            if result.get("success"):
                print(f"✓ 工具执行成功")
                print(f"  结果类型: {type(result.get('result'))}")
            else:
                print(f"✗ 工具执行失败: {result.get('error')}")
        except Exception as e:
            print(f"✗ 执行异常: {e}")
    else:
        print("  没有可用的MCP工具")
    
    # 关闭
    print("\n关闭资源...")
    await mcp_integration.close()
    print("✓ 测试完成")
    print("=" * 70)


async def test_tool_registry_integration():
    """测试工具注册表集成"""
    print("\n" + "=" * 70)
    print("测试4: 工具注册表集成")
    print("=" * 70)
    
    # 创建执行器
    print("\n[1/4] 创建执行器...")
    executor = UnitTaskExecutionAgent()
    initial_tools = len(executor.tool_registry.list_tools())
    print(f"✓ 初始工具数: {initial_tools}")
    
    # 创建MCP集成
    print("\n[2/4] 创建MCP集成...")
    mcp_integration = MCPToolIntegration(
        tool_registry=executor.tool_registry,
    )
    
    # 初始化
    print("\n[3/4] 初始化MCP...")
    success = await mcp_integration.initialize()
    if not success:
        print("✗ MCP初始化失败")
        return
    
    # 检查工具注册
    print("\n[4/4] 检查工具注册...")
    final_tools = len(executor.tool_registry.list_tools())
    mcp_tools = mcp_integration.get_registered_mcp_tools()
    
    print(f"✓ 最终工具数: {final_tools}")
    print(f"✓ MCP工具数: {len(mcp_tools)}")
    print(f"✓ 新增工具数: {final_tools - initial_tools}")
    
    # 验证MCP工具是否在注册表中
    all_tools = executor.tool_registry.list_tools()
    registered_count = sum(1 for t in mcp_tools if t in all_tools)
    print(f"✓ 成功注册到工具表: {registered_count}/{len(mcp_tools)}")
    
    # 关闭
    print("\n关闭资源...")
    await mcp_integration.close()
    print("✓ 测试完成")
    print("=" * 70)


async def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("MCP与单元任务执行Agent集成测试")
    print("=" * 70)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # 运行所有测试
        await test_mcp_tool_integration()
        await test_executor_with_mcp()
        await test_mcp_tool_via_executor()
        await test_tool_registry_integration()
        
        print("\n" + "=" * 70)
        print("所有测试完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
