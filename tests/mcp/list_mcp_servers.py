"""
列出所有已配置的 MCP Server
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flood_decision_agent.mcp.clients.base import MCPClientManager


def list_servers():
    """列出所有 MCP Server"""
    
    print("=" * 70)
    print("已配置的 MCP Server 列表")
    print("=" * 70)
    
    # 初始化客户端管理器
    manager = MCPClientManager()
    
    print(f"\n共 {len(manager.clients)} 个 MCP Server:\n")
    
    for i, (name, client) in enumerate(manager.clients.items(), 1):
        print(f"{i}. {name}")
        print(f"   命令: {client.server_params.command}")
        print(f"   参数: {' '.join(client.server_params.args)}")
        print()
    
    print("=" * 70)
    print("使用说明:")
    print("=" * 70)
    print("""
启动单个 MCP Server:
  python -m flood_decision_agent.mcp.servers.filesystem_server
  python -m flood_decision_agent.mcp.servers.hydrology_server
  python -m flood_decision_agent.mcp.servers.document_server
  python -m flood_decision_agent.mcp.servers.decision_chain_server
  python -m flood_decision_agent.mcp.servers.yolo_vision_server
  python -m flood_decision_agent.mcp.servers.rainfall_server

测试所有 MCP Server:
  python scripts/test_all_mcp_servers.py
""")


if __name__ == "__main__":
    list_servers()
