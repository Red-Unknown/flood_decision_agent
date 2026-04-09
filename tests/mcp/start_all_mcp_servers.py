"""
启动所有 MCP Server 并测试连接
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.clients.base import MCPClientManager


async def start_and_test_all_servers():
    """启动并测试所有 MCP Server"""
    
    print("=" * 70)
    print("启动所有 MCP Server")
    print("=" * 70)
    
    # 初始化客户端管理器
    manager = MCPClientManager()
    
    print(f"\n已注册 {len(manager.clients)} 个 MCP Server:")
    for name in manager.clients.keys():
        print(f"  - {name}")
    
    # 连接到所有服务器
    print("\n" + "-" * 70)
    print("正在连接所有 MCP Server...")
    print("-" * 70)
    
    try:
        await manager.connect_all()
        
        print("\n" + "=" * 70)
        print("连接状态检查")
        print("=" * 70)
        
        # 检查每个服务器的连接状态
        for name, client in manager.clients.items():
            try:
                # 尝试调用 list_tools 检查连接
                tools = await client.list_tools()
                print(f"\n[OK] {name}")
                print(f"     可用工具: {len(tools)} 个")
                for tool in tools[:3]:  # 只显示前3个工具
                    print(f"       - {tool.name}")
                if len(tools) > 3:
                    print(f"       ... 还有 {len(tools) - 3} 个")
            except Exception as e:
                print(f"\n[FAIL] {name}")
                print(f"       错误: {e}")
        
        # 测试特定功能
        print("\n" + "=" * 70)
        print("功能测试")
        print("=" * 70)
        
        # 测试 rainfall
        if "rainfall" in manager.clients:
            print("\n[1] 测试 rainfall - 检查API状态...")
            try:
                result = await manager.clients["rainfall"].call_tool("check_api_status", {})
                if result.get("success"):
                    print("     [OK] API 状态正常")
                    providers = result.get("providers", {})
                    for provider, status in providers.items():
                        if status.get("available"):
                            print(f"       - {provider}: 可用")
                else:
                    print(f"     [WARN] {result.get('warning', '未知状态')}")
            except Exception as e:
                print(f"     [FAIL] {e}")
        
        # 测试 decision_chain
        if "decision_chain" in manager.clients:
            print("\n[2] 测试 decision_chain - 列出Plans...")
            try:
                result = await manager.clients["decision_chain"].call_tool("list_plans", {})
                if result.get("success"):
                    print(f"     [OK] 找到 {result.get('count', 0)} 个 Plan")
                else:
                    print(f"     [INFO] {result.get('message', '无数据')}")
            except Exception as e:
                print(f"     [FAIL] {e}")
        
        # 测试 filesystem
        if "filesystem" in manager.clients:
            print("\n[3] 测试 filesystem - 列出目录...")
            try:
                result = await manager.clients["filesystem"].call_tool("list_directory", {
                    "path": "./"
                })
                if result.get("success"):
                    entries = result.get("entries", [])
                    print(f"     [OK] 目录包含 {len(entries)} 个条目")
                else:
                    print(f"     [INFO] {result.get('error', '无数据')}")
            except Exception as e:
                print(f"     [FAIL] {e}")
        
        print("\n" + "=" * 70)
        print("所有 MCP Server 已启动并测试完成")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 保持连接运行，等待用户中断
        print("\n按 Ctrl+C 停止所有服务...")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\n正在停止所有服务...")
            await manager.close_all()
            print("[OK] 所有服务已停止")


if __name__ == "__main__":
    # 检查 API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("需要kimi_api_key")
        sys.exit(1)
    
    try:
        asyncio.run(start_and_test_all_servers())
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(0)
