"""调试 MCP 配置和工具缓存"""

import os
import sys
from pathlib import Path

# 检查环境变量
if not os.environ.get("KIMI_API_KEY"):
    print("需要 kimi_api_key")
    sys.exit(1)

# 设置项目路径
sys.path.insert(0, str(Path(__file__).parent))

from flood_decision_agent.mcp.clients.base import MCPClientManager

def main():
    print("=" * 60)
    print("调试 MCP 配置和工具缓存")
    print("=" * 60)
    
    # 1. 检查配置文件
    config_path = Path("configs/mcp/servers.yaml")
    print(f"\n[1] 配置文件路径: {config_path}")
    print(f"    配置文件存在: {config_path.exists()}")
    
    # 2. 创建 MCP 客户端管理器
    print("\n[2] 创建 MCP 客户端管理器...")
    manager = MCPClientManager(auto_load_config=True)
    
    # 3. 检查已连接的客户端
    print(f"\n[3] 已连接的 MCP 客户端: {list(manager.clients.keys())}")
    
    # 4. 检查工具缓存
    print(f"\n[4] 缓存的工具:")
    for server_name, client in manager.clients.items():
        tools = client.get("tools", []) if isinstance(client, dict) else []
        if hasattr(client, 'tools'):
            tools = client.tools
        print(f"    {server_name}: {len(tools)} 个工具")
        if tools:
            for tool in tools[:5]:  # 只显示前5个
                if isinstance(tool, dict):
                    print(f"      - {tool.get('name', 'unknown')}")
                else:
                    print(f"      - {tool}")
    
    # 5. 列出所有工具
    print(f"\n[5] 所有可用工具:")
    for server_name, client in manager.clients.items():
        try:
            # 尝试列出工具
            if hasattr(client, 'list_tools'):
                tools = client.list_tools()
                print(f"    {server_name}: {tools}")
            elif hasattr(client, 'tools'):
                print(f"    {server_name}: {client.tools}")
            else:
                print(f"    {server_name}: (无法获取工具列表)")
        except Exception as e:
            print(f"    {server_name}: 获取工具列表失败 - {e}")

    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
