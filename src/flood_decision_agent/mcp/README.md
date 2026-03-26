# MCP 模块 - Model Context Protocol 集成

## 架构概述

本模块实现了基于 MCP (Model Context Protocol) 的分布式工具服务架构，替代原有的本地工具注册表模式。

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Application                            │
├─────────────────────────────────────────────────────────────────┤
│  DecisionChainGeneratorMCPAgent  │  UnitTaskExecutionAgent     │
│         (MCP增强版)               │      (保持兼容)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MCP Client Manager                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Filesystem  │  │  Hydrology  │  │    Other MCP Servers    │ │
│  │   Client    │  │   Client    │  │                         │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
│         └─────────────────┴─────────────────────┘               │
│                         MCP Protocol                            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Filesystem   │    │   Hydrology   │    │    SQLite     │
│    Server     │    │    Server     │    │    Server     │
│               │    │               │    │   (Optional)  │
│ - 规划文件读写 │    │ - 降雨径流模型 │    │               │
│ - JSON数据   │    │ - 洪水演进    │    │               │
│               │    │ - 水库调度    │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 目录结构

```
mcp/
├── __init__.py              # 模块入口
├── README.md                # 本文档
├── configs/
│   └── mcp_servers.json     # MCP Server 配置
├── servers/
│   ├── __init__.py
│   ├── filesystem_server.py # 文件系统服务
│   └── hydrology_server.py  # 水利模型服务
├── clients/
│   ├── __init__.py
│   ├── base.py             # MCP Client 管理器
│   └── filesystem.py       # 文件系统客户端封装
└── adapters/
    ├── __init__.py
    └── tool_adapter.py     # 工具适配器（兼容旧接口）
```

## 快速开始

### 1. 配置 MCP Servers

编辑 `configs/mcp_servers.json`：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["-m", "flood_decision_agent.mcp.servers.filesystem_server"],
      "enabled": true
    },
    "hydrology": {
      "command": "python",
      "args": ["-m", "flood_decision_agent.mcp.servers.hydrology_server"],
      "enabled": true
    }
  }
}
```

### 2. 使用 MCP 增强版 Agent

```python
from flood_decision_agent.agents.decision_chain_generator_mcp import (
    DecisionChainGeneratorMCPAgent,
    DecisionPipelineMCP
)

# 创建 Agent
agent = DecisionChainGeneratorMCPAgent(
    enable_mcp=True,
    auto_save_plans=True
)

# 初始化 MCP 连接
await agent.initialize()

# 使用
message = BaseMessage(
    content={"input": "生成洪水调度方案"}
)
response = await agent.async_execute(message)

# 关闭连接
await agent.close()
```

### 3. 直接使用 MCP Client

```python
from flood_decision_agent.mcp.clients import get_mcp_manager

# 获取管理器
manager = get_mcp_manager()

# 注册 Server
manager.register_server(
    name="filesystem",
    command="python",
    args=["-m", "flood_decision_agent.mcp.servers.filesystem_server"]
)

# 连接
await manager.connect_all()

# 调用工具
result = await manager.call_tool(
    server_name="filesystem",
    tool_name="write_planning_markdown",
    arguments={
        "plan_name": "test_plan",
        "content": "# 测试规划"
    }
)

# 关闭
await manager.close_all()
```

## 可用工具

### Filesystem Server

| 工具名 | 描述 |
|--------|------|
| `write_planning_markdown` | 写入规划文件 |
| `read_planning_file` | 读取规划文件 |
| `list_plans` | 列出规划文件 |
| `append_to_plan` | 追加内容到规划 |
| `write_data_json` | 写入 JSON 数据 |
| `read_data_json` | 读取 JSON 数据 |

### Hydrology Server

| 工具名 | 描述 |
|--------|------|
| `list_hydrology_models` | 列出水利模型 |
| `get_model_info` | 获取模型信息 |
| `run_rainfall_runoff` | 运行降雨径流模型 |
| `run_flood_routing` | 运行洪水演进模型 |
| `run_reservoir_dispatch` | 运行水库调度模型 |
| `calculate_dispatch_plan` | 生成调度方案 |
| `validate_dispatch_safety` | 验证方案安全性 |

## 架构转变说明

### 原有架构（已弃用）

```python
# 本地工具注册表模式
from flood_decision_agent.tools.registry import get_tool_registry

registry = get_tool_registry()
registry.register("my_tool", handler, metadata)
result = registry.execute("my_tool", data_pool, config)
```

### 新架构（推荐）

```python
# MCP 分布式服务模式
from flood_decision_agent.mcp.adapters import MCPToolAdapter

adapter = MCPToolAdapter()
result = await adapter.execute("my_tool", data_pool, config)
```

## 迁移指南

1. **Agent 迁移**: 使用 `DecisionChainGeneratorMCPAgent` 替代 `DecisionChainGeneratorAgent`
2. **工具调用**: 使用 `MCPToolAdapter` 替代 `ToolRegistry`
3. **配置文件**: 在 `mcp/configs/mcp_servers.json` 中配置 MCP Servers

## 注意事项

- MCP Servers 作为独立进程运行，通过 stdio 与 Client 通信
- 确保 Python 环境已安装 `mcp` 包: `pip install mcp`
- 文件系统服务默认限制访问 `./plans` 和 `./data` 目录
- 水利模型服务当前为模拟实现，可替换为真实模型