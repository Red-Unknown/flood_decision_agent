"""
测试所有 MCP Server 连接
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.clients.base import MCPClientManager


async def test_all_servers():
    """测试所有 MCP Server"""
    
    print("=" * 70)
    print("测试所有 MCP Server 连接")
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
        
        success_count = 0
        fail_count = 0
        
        # 检查每个服务器的连接状态
        for name, client in manager.clients.items():
            try:
                # 尝试调用 list_tools 检查连接
                tools = await client.list_tools()
                print(f"\n[OK] {name:15s} - {len(tools):2d} 个工具")
                for tool in tools[:3]:
                    print(f"       - {tool.name}")
                if len(tools) > 3:
                    print(f"       ... 还有 {len(tools) - 3} 个")
                success_count += 1
            except Exception as e:
                print(f"\n[FAIL] {name:15s} - {str(e)[:50]}")
                fail_count += 1
        
        # 快速功能测试
        print("\n" + "=" * 70)
        print("快速功能测试")
        print("=" * 70)
        
        # 测试 rainfall
        if "rainfall" in manager.clients:
            print("\n[rainfall] 检查API状态...", end=" ")
            try:
                result = await manager.clients["rainfall"].call_tool("check_api_status", {})
                if result.get("success"):
                    providers = result.get("providers", {})
                    available = [p for p, s in providers.items() if s.get("available")]
                    print(f"[OK] 可用: {', '.join(available) if available else '无'}")
                else:
                    print(f"[WARN] {result.get('warning', '未配置')[:30]}")
            except Exception as e:
                print(f"[FAIL] {e}")
        
        # 测试 decision_chain
        if "decision_chain" in manager.clients:
            print("\n[decision_chain] 列出Plans...", end=" ")
            try:
                result = await manager.clients["decision_chain"].call_tool("list_plans", {})
                if result.get("success"):
                    print(f"[OK] {result.get('count', 0)} 个 Plan")
                else:
                    print(f"[INFO] 无数据")
            except Exception as e:
                print(f"[FAIL] {e}")
        
        # 测试 filesystem
        if "filesystem" in manager.clients:
            print("\n[filesystem] 列出根目录...", end=" ")
            try:
                result = await manager.clients["filesystem"].call_tool("list_directory", {"path": "./"})
                if result.get("success"):
                    print(f"[OK] {len(result.get('entries', []))} 个条目")
                else:
                    print(f"[INFO] 无数据")
            except Exception as e:
                print(f"[FAIL] {e}")
        
        # 测试 hydrology
        if "hydrology" in manager.clients:
            print("\n[hydrology] 列出工具...", end=" ")
            try:
                tools = await manager.clients["hydrology"].list_tools()
                print(f"[OK] {len(tools)} 个工具")
            except Exception as e:
                print(f"[FAIL] {e}")
        
        # 测试 document
        if "document" in manager.clients:
            print("\n[document] 列出工具...", end=" ")
            try:
                tools = await manager.clients["document"].list_tools()
                print(f"[OK] {len(tools)} 个工具")
            except Exception as e:
                print(f"[FAIL] {e}")
        
        # 测试 yolo_vision
        if "yolo_vision" in manager.clients:
            print("\n[yolo_vision] 检查依赖...", end=" ")
            try:
                result = await manager.clients["yolo_vision"].call_tool("get_model_info", {})
                if result.get("success"):
                    print(f"[OK] {result.get('device', 'unknown')}")
                else:
                    print(f"[WARN] 依赖未安装")
            except Exception as e:
                print(f"[FAIL] {e}")
        
        print("\n" + "=" * 70)
        print(f"测试结果: {success_count} 成功, {fail_count} 失败")
        print("=" * 70)
        
        return fail_count == 0
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n断开所有连接...")
        await manager.close_all()
        print("[OK] 所有连接已关闭")


if __name__ == "__main__":
    # 检查 API Key
    if not os.environ.get("KIMI_API_KEY"):
        print("需要kimi_api_key")
        sys.exit(1)
    
    success = asyncio.run(test_all_servers())
    sys.exit(0 if success else 1)
