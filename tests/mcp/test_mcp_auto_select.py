"""测试MCP工具自动选择功能

验证UnitTaskExecutor是否能自动选择并执行MCP工具。
MCP Server是按需启动的，通过stdio与主程序通信。
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flood_decision_agent.agents.task_executor.executor import UnitTaskExecutionAgent
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.infra.logging import setup_logging

# 配置日志
setup_logging()


async def test_mcp_initialization():
    """测试MCP初始化 - MCPClientManager会自动按需启动服务器"""
    print("\n" + "=" * 70)
    print("测试1: MCP初始化")
    print("=" * 70)

    executor = UnitTaskExecutionAgent(enable_mcp=True)

    print("\n[1/2] 初始化MCP客户端管理器...")
    print("      (MCP Server将按需自动启动)")
    success = await executor.initialize_mcp()

    if success:
        print(f"✓ MCP初始化成功")
        print(f"  缓存的MCP工具数: {len(executor._mcp_tools_cache)}")

        # 显示缓存的工具
        if executor._mcp_tools_cache:
            print("\n[2/2] 可用的MCP工具:")
            for tool_name, tool_info in list(executor._mcp_tools_cache.items())[:10]:
                server = tool_info.get('server_name', 'unknown')
                print(f"  - {tool_name} (服务器: {server})")
        else:
            print("\n[2/2] 未找到可用的MCP工具")
            print("      可能原因: 服务器启动失败或配置问题")
    else:
        print("✗ MCP初始化失败")
        print("  检查: configs/mcp/servers.yaml 配置")

    return executor


def test_mcp_tool_selection(executor):
    """测试MCP工具自动选择"""
    print("\n" + "=" * 70)
    print("测试2: MCP工具自动选择")
    print("=" * 70)

    test_cases = [
        {
            "name": "数据收集任务",
            "task_type": "data_collection",
            "context": {
                "description": "收集降雨数据",
                "user_input": "查询北京未来3天降雨预报",
            },
        },
        {
            "name": "水文模拟任务",
            "task_type": "simulation",
            "context": {
                "description": "洪水演进模拟",
                "user_input": "模拟洪水演进过程",
            },
        },
        {
            "name": "调度决策任务",
            "task_type": "decision",
            "context": {
                "description": "制定泄洪方案",
                "user_input": "制定水库调度方案",
            },
        },
        {
            "name": "洪水调度任务",
            "task_type": "flood_dispatch",
            "context": {
                "description": "洪水调度分析",
                "user_input": "分析入库流量并制定调度方案",
            },
        },
    ]

    for case in test_cases:
        print(f"\n测试: {case['name']}")
        print(f"  任务类型: {case['task_type']}")

        # 查找MCP工具
        mcp_tools = executor._find_mcp_tools_for_task(
            case['task_type'],
            case['context']
        )

        if mcp_tools:
            print(f"  ✓ 找到 {len(mcp_tools)} 个匹配的MCP工具:")
            for tool in mcp_tools[:3]:
                print(f"    - {tool['tool_name']} (匹配: {tool['matched_keyword']})")
        else:
            print(f"  - 未找到匹配的MCP工具")


async def test_mcp_tool_execution(executor):
    """测试MCP工具执行"""
    print("\n" + "=" * 70)
    print("测试3: MCP工具执行")
    print("=" * 70)

    if not executor._mcp_manager:
        print("✗ MCP管理器未初始化，跳过执行测试")
        return

    data_pool = SharedDataPool()
    data_pool.set("city", "北京")

    # 查找降雨相关工具
    mcp_tools = executor._find_mcp_tools_for_task(
        "data_collection",
        {"description": "查询降雨数据", "user_input": "北京降雨预报"}
    )

    rainfall_tools = [t for t in mcp_tools if 'rain' in t['tool_name'].lower()]

    if not rainfall_tools:
        print("未找到降雨工具，尝试执行第一个可用MCP工具")
        if executor._mcp_tools_cache:
            first_tool_name = list(executor._mcp_tools_cache.keys())[0]
            first_tool_info = executor._mcp_tools_cache[first_tool_name]
            rainfall_tools = [{
                'tool_name': first_tool_name,
                'server_name': first_tool_info.get('server_name', ''),
            }]
        else:
            print("✗ 没有可用的MCP工具")
            return

    tool_spec = {
        "tool_name": rainfall_tools[0]['tool_name'],
        "tool_config": {},
        "server_name": rainfall_tools[0]['server_name'],
    }

    print(f"\n执行工具: {tool_spec['tool_name']}")
    print(f"服务器: {tool_spec['server_name']}")

    try:
        result = await executor._execute_mcp_tool(tool_spec, data_pool)

        if result.get('success'):
            print(f"✓ 工具执行成功")
            print(f"  结果: {str(result.get('data', {}))[:200]}...")
        else:
            print(f"✗ 工具执行失败: {result.get('error')}")
    except Exception as e:
        print(f"✗ 执行异常: {e}")


def test_full_task_execution_with_mcp(executor):
    """测试完整的任务执行流程（带MCP自动选择）"""
    print("\n" + "=" * 70)
    print("测试4: 完整任务执行（带MCP自动选择）")
    print("=" * 70)

    data_pool = SharedDataPool()
    data_pool.set("city", "北京")
    data_pool.set("station", "北京站")

    # 测试数据收集任务
    print("\n执行任务: data_collection (数据收集)")
    print("上下文: 查询北京降雨数据")

    start_time = time.time()
    result = executor.execute_task(
        node_id="test_node_001",
        task_type="data_collection",
        data_pool=data_pool,
        context={
            "description": "收集降雨数据",
            "user_input": "查询北京未来3天降雨预报",
            "allow_auto_select": True,
        },
        execution_strategy="auto",
    )
    elapsed = (time.time() - start_time) * 1000

    print(f"\n执行结果:")
    print(f"  状态: {result.get('status')}")
    print(f"  使用工具: {result.get('metrics', {}).get('tools_used', [])}")
    print(f"  执行策略: {result.get('metrics', {}).get('execution_strategy')}")
    print(f"  耗时: {elapsed:.2f} ms")

    if result.get('status') == 'success':
        output = result.get('output', {})
        print(f"\n  输出数据:")
        if isinstance(output, dict):
            for key, value in list(output.items())[:3]:
                print(f"    {key}: {str(value)[:100]}...")
        else:
            print(f"    {str(output)[:200]}...")


async def test_mcp_manager_directly():
    """直接测试MCPClientManager"""
    print("\n" + "=" * 70)
    print("测试5: 直接测试MCPClientManager")
    print("=" * 70)

    from flood_decision_agent.mcp.clients.base import MCPClientManager

    manager = MCPClientManager()

    # 加载配置
    print("\n[1/3] 加载MCP配置...")
    config_path = "configs/mcp/servers.yaml"
    if os.path.exists(config_path):
        print(f"  配置文件存在: {config_path}")
        manager.load_from_config(config_path)
        print(f"  已注册 {len(manager.clients)} 个服务器")
    else:
        print(f"  ✗ 配置文件不存在: {config_path}")
        return

    # 连接所有服务器（按需启动）
    print("\n[2/3] 连接MCP服务器（按需启动）...")
    try:
        connected = await manager.connect_all()
        print(f"  ✓ 已连接 {connected} 个服务器")

        # 显示每个服务器的状态
        for name, client in manager.clients.items():
            status = "✓ 已连接" if client._connected else "✗ 未连接"
            tool_count = len(client.tools) if hasattr(client, 'tools') and client.tools else 0
            print(f"    {status}: {name} ({tool_count} 个工具)")

    except Exception as e:
        print(f"  ✗ 连接失败: {e}")

    # 关闭所有连接
    print("\n[3/3] 关闭MCP连接...")
    await manager.close_all()
    print("  ✓ 已关闭所有连接")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("MCP工具自动选择功能测试")
    print("=" * 70)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("\n注意: MCP Server是按需启动的，通过stdio与主程序通信")
    print("      不需要手动启动，MCPClientManager会自动管理")
    print("=" * 70)

    # 检查API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("\n✗ 错误: 需要设置 KIMI_API_KEY 环境变量")
        print("  请运行: $env:KIMI_API_KEY='your-api-key'")
        sys.exit(1)

    try:
        # 1. 直接测试MCPClientManager
        asyncio.run(test_mcp_manager_directly())

        # 2. 测试MCP初始化
        executor = asyncio.run(test_mcp_initialization())

        # 3. 测试MCP工具选择
        test_mcp_tool_selection(executor)

        # 4. 测试MCP工具执行
        asyncio.run(test_mcp_tool_execution(executor))

        # 5. 测试完整任务执行
        test_full_task_execution_with_mcp(executor)

        # 6. 关闭MCP连接
        if executor._mcp_manager:
            print("\n" + "=" * 70)
            print("关闭MCP连接")
            print("=" * 70)
            asyncio.run(executor._mcp_manager.close_all())
            print("✓ 所有MCP连接已关闭")

        print("\n" + "=" * 70)
        print("所有测试完成！")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
