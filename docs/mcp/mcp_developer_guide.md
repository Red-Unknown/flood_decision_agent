# MCP 服务开发者指南

本文档面向开发者，介绍如何扩展和维护 MCP 服务。

## 目录

- [架构概述](#架构概述)
- [项目结构](#项目结构)
- [日志系统](#日志系统)
- [结果包装器](#结果包装器)
- [创建新服务](#创建新服务)
- [服务间通信](#服务间通信)
- [错误处理](#错误处理)
- [测试规范](#测试规范)
- [部署流程](#部署流程)

## 架构概述

### MCP 协议

Model Context Protocol (MCP) 是一种标准化的协议，用于 AI 模型与外部工具的交互。我们的 MCP 服务实现遵循以下架构：

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Agent      │────▶│  MCP Client     │────▶│  MCP Server     │
│                 │◀────│  (Manager)      │◀────│  (Service)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │   Wrappers/     │
                        │   Prompts       │
                        └─────────────────┘
```

### 分层职责

| 层级 | 职责 | 说明 |
|------|------|------|
| **Server 层** | 模型计算，返回原始数据 | 保持单一职责，不做任何解释 |
| **Client 层** | 结果包装，LLM 解释 | 根据工具类型选择是否包装 |
| **调度层** | 选择合适的 Client 包装器 | 复杂任务用包装版，简单任务用透传版 |

### 服务依赖关系

```
hydrology (水利模型服务)
    ├── data_hub (数据获取)
    └── hipims (2D模拟)
        └── 内部集成

其他独立服务:
    ├── web_search (网络搜索)
    ├── rainfall (降雨数据)
    └── document (文档处理)
```

## 项目结构

```
src/flood_decision_agent/mcp/
├── adapters/           # 工具适配器
│   └── tool_adapter.py
├── clients/            # 客户端实现
│   ├── base.py        # MCPClientManager
│   ├── filesystem.py  # 文件系统客户端
│   ├── prompts.py     # 提示词模板
│   └── wrappers.py    # 结果包装器
├── configs/            # 配置文件
│   └── mcp_servers.json
├── core/              # 核心协议实现
│   ├── client.py
│   ├── server.py
│   ├── session.py
│   └── transport.py
├── log/               # 日志系统
│   ├── __init__.py
│   ├── logger.py      # 日志记录器
│   ├── formatters.py  # 格式化器
│   ├── handlers.py     # 处理器
│   ├── contexts.py    # 上下文管理器
│   └── error_formatter.py # 错误格式化
├── tools/             # 工具基类和装饰器
│   ├── __init__.py
│   ├── base.py       # MCPToolBase
│   └── decorators.py  # 装饰器
├── protocol/          # 协议定义
│   ├── constants.py
│   ├── messages.py
│   └── types.py
├── servers/           # 服务实现
│   ├── data_hub_server.py
│   ├── hydrology_server.py
│   ├── rainfall_server.py
│   └── ...
└── utils/             # 工具函数
    └── error_handler.py
```

## 日志系统

### 概述

MCP 服务使用统一的日志系统，记录所有工具调用和错误信息。日志文件存储在 `logs/mcp/{server_name}/` 目录下。

### 使用日志记录器

```python
from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
from src.flood_decision_agent.mcp.log.error_formatter import format_error as format_error_dict

SERVER_NAME = "my_server"
logger = get_mcp_logger(SERVER_NAME)

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    with ToolCallContext(SERVER_NAME, name, arguments, logger):
        try:
            # 业务逻辑
            result = await handle_tool(name, arguments)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"工具 {name} 执行失败: {e}")
            error_dict = format_error_dict(e, SERVER_NAME, name, arguments)
            return [TextContent(
                type="text",
                text=fast_json_dumps(error_dict, ensure_ascii=False)
            )]
```

### 日志级别规范

| 场景 | 级别 |
|------|------|
| Server 启动/关闭 | INFO |
| 工具调用开始 | INFO |
| 工具调用成功 | INFO |
| 工具调用失败 | ERROR |
| API 请求 | DEBUG |
| API 响应 | DEBUG |
| API 错误 | ERROR |

### 标准化错误格式

所有 MCP Server 返回以下格式的错误信息：

```json
{
    "success": false,
    "error": "错误描述信息",
    "error_type": "异常类名",
    "timestamp": "2024-01-01T12:00:00",
    "server_name": "server名称",
    "tool_name": "工具名称",
    "details": {
        "arguments": {}
    }
}
```

### 使用工具基类

```python
from src.flood_decision_agent.mcp.tools import MCPToolBase, ToolResult

class MyTool(MCPToolBase):
    """自定义工具"""
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        # 业务逻辑
        return ToolResult(success=True, data={"result": "ok"})

# 使用
tool = MyTool("my_server", "my_tool")
result = await tool.call(arguments, data_pool)
```

### 使用装饰器

```python
from src.flood_decision_agent.mcp.tools import with_logging, auto_write_to_pool

@with_logging("my_server")
async def my_tool(args):
    return await process(args)

# 自动写入数据池
@auto_write_to_pool(lambda: get_data_pool())
async def another_tool(args):
    return await fetch_data(args)
```

## 结果包装器

### 设计原则

Server 层保持纯净（只返回原始数据），Client 层负责根据工具类型选择是否使用 LLM 进行结果包装和解释。

### 工具分类

| 工具 | 复杂度 | 包装策略 | 说明 |
|------|--------|----------|------|
| HiPIMS | 高 | ComplexClientWrapper | 2D模拟结果需要专业解释 |
| Hydrology | 高 | ComplexClientWrapper | 水利模型结果需要解释 |
| Dispatch | 高 | ComplexClientWrapper | 调度方案需要解释 |
| Data Hub | 低 | SimpleClientWrapper | 天气查询直接返回 |
| Rainfall | 低 | SimpleClientWrapper | 降雨数据直接返回 |
| Filesystem | 低 | SimpleClientWrapper | 文件操作直接返回 |

### 使用包装器

```python
from flood_decision_agent.mcp.clients import (
    MCPWrappedClientManager,
    SimpleClientWrapper,
    ComplexClientWrapper,
)

# 方式1: 使用带包装器的管理器
wrapped_manager = MCPWrappedClientManager()

# 自动判断是否需要包装
result = await wrapped_manager.call_tool(
    server_name="hydrology",
    tool_name="run_rainfall_runoff",
    arguments={"rainfall": [10, 20, 30], "catchment_area": 50}
)
# 返回: {raw_data, explanation, summary, wrapped: True}

# 强制不包装
result = await wrapped_manager.call_tool(
    server_name="data_hub",
    tool_name="get_rainfall_data",
    arguments={"city": "北京"},
    wrap_result=False
)
# 返回: 原始数据
```

## 创建新服务

### 1. 创建服务文件

在 `src/flood_decision_agent/mcp/servers/` 目录下创建新的服务文件：

```python
# my_service_server.py
"""My Service MCP Server

描述服务功能...

环境变量:
    MY_API_KEY: API Key
"""

import asyncio
import os
import platform
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps
from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
from src.flood_decision_agent.mcp.log.error_formatter import format_error as format_error_dict

SERVER_NAME = "my_service"
logger = get_mcp_logger(SERVER_NAME)

server = Server("flood-agent-my-service")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="my_tool",
            description="工具描述",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "参数1描述"
                    }
                },
                "required": ["param1"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    with ToolCallContext(SERVER_NAME, name, arguments, logger):
        try:
            if name == "my_tool":
                return await _handle_my_tool(arguments)
            else:
                raise ValueError(f"未知工具: {name}")
        except Exception as e:
            logger.error(f"工具 {name} 执行失败: {e}")
            error_dict = format_error_dict(e, SERVER_NAME, name, arguments)
            return [TextContent(
                type="text",
                text=fast_json_dumps(error_dict, ensure_ascii=False)
            )]


async def _handle_my_tool(args: Dict[str, Any]) -> List[TextContent]:
    """处理 my_tool 请求"""
    param1 = args.get("param1")
    
    result = {"message": f"处理完成: {param1}"}
    
    return [TextContent(
        type="text",
        text=fast_json_dumps({
            "success": True,
            "data": result
        }, ensure_ascii=False, indent=2)
    )]


async def main():
    """启动 MCP Server（Windows 兼容版）"""
    logger.info(f"MCP Server [{SERVER_NAME}] 启动中...")
    
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    from mcp.server.stdio import stdio_server as mcp_stdio_server

    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
    
    logger.info(f"MCP Server [{SERVER_NAME}] 已关闭")


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. 注册服务配置

在 `configs/mcp_servers.json` 中添加服务配置：

```json
{
  "mcpServers": {
    "my_service": {
      "command": "python",
      "args": ["-m", "flood_decision_agent.mcp.servers.my_service_server"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      },
      "description": "我的服务描述",
      "enabled": true
    }
  }
}
```

## 服务间通信

### 使用 MCPServiceClient

`hydrology_server.py` 中实现了 `MCPServiceClient` 类用于服务间调用：

```python
from flood_decision_agent.mcp.servers.hydrology_server import service_client

# 调用 data_hub 服务
result = await service_client.call_data_hub(
    "get_rainfall_data",
    {"city": "北京", "provider": "auto"}
)

# 调用 hipims 服务
result = await service_client.call_hipims(
    "run_2d_simulation",
    {
        "terrain_path": "data/terrain.asc",
        "boundary_conditions": {...}
    }
)
```

## 错误处理

### 使用统一错误处理

MCP 服务使用统一的错误格式：

```python
from src.flood_decision_agent.mcp.log.error_formatter import format_error

try:
    result = await process_data(args)
except Exception as e:
    error_dict = format_error(e, "my_server", "my_tool", args)
    return [TextContent(
        type="text",
        text=fast_json_dumps(error_dict, ensure_ascii=False)
    )]
```

## 测试规范

### 运行完整测试

```bash
# 运行所有 MCP 工具测试
python tests/mcp/test_mcp_tools_all.py

# 运行日志系统测试
python tests/mcp/test_mcp_logging.py

# 运行错误格式测试
python tests/mcp/test_mcp_error_format.py
```

### 测试结构

```python
# tests/mcp/test_my_service.py
import asyncio
import pytest
from flood_decision_agent.mcp.clients import MCPClientManager

async def test_my_service():
    manager = MCPClientManager()
    await manager.connect_all()
    
    # 测试工具调用
    result = await manager.call_tool(
        server_name="my_service",
        tool_name="my_tool",
        arguments={"param1": "test"}
    )
    
    assert result["success"] is True
    assert "data" in result
    
    await manager.close_all()

if __name__ == "__main__":
    asyncio.run(test_my_service())
```

## 部署流程

### 1. 环境检查

```powershell
# 检查环境变量
$env:KIMI_API_KEY
$env:QWEATHER_API_KEY

# 检查依赖
pip list | findstr mcp
pip list | findstr aiohttp
```

### 2. 运行服务

```powershell
# 启动后端
python -m web.backend.main

# 或使用脚本
.\scripts\start_web_simple.ps1
```

### 3. 验证服务

```bash
# 运行完整测试
python tests/mcp/test_mcp_tools_all.py

# 测试单个服务
python tests/mcp/test_rainfall_mcp.py
python tests/mcp/test_hydrology_enhanced.py
```

### 4. 监控日志

```powershell
# 查看服务日志
Get-Content logs/mcp/rainfall/mcp-rainfall-2026-04-08.log -Tail 100

# 实时监控
Get-Content logs/mcp/rainfall/mcp-rainfall-2026-04-08.log -Wait
```

## 最佳实践

1. **使用统一日志系统**: 所有 Server 使用 `get_mcp_logger()` 记录日志
2. **返回标准化错误格式**: 使用 `format_error_dict()` 生成错误响应
3. **Server 保持纯净**: 只做模型计算，不处理解释逻辑
4. **Client 灵活组合**: 不同工具用不同包装策略
5. **提示词可配置**: 每个复杂工具有自己的提示词模板
6. **返回格式统一**: 复杂任务返回 `{raw, explanation}`，简单任务直接返回数据
7. **测试覆盖**: 为每个工具编写测试用例
