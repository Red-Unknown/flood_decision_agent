# MCP 服务使用文档

本文档介绍如何使用集成 MCP 服务（Data Hub、Hydrology、HiPIMS）以及结果包装器功能。

## 目录

- [服务概览](#服务概览)
- [快速开始](#快速开始)
- [健康检查与初始化](#健康检查与初始化)
- [MCP 服务器配置](#mcp-服务器配置)
- [结果包装器](#结果包装器)
- [Data Hub 服务](#data-hub-服务)
- [Hydrology 服务](#hydrology-服务)
- [HiPIMS 服务](#hipims-服务)
- [Rainfall 服务](#rainfall-服务)
- [YOLO Vision 服务](#yolo-vision-服务)
- [Filesystem 服务](#filesystem-服务)
- [Document 服务](#document-服务)
- [总结智能体](#总结智能体)
- [完整工作流示例](#完整工作流示例)
- [错误处理](#错误处理)
- [故障排除](#故障排除)

## 服务概览

| 服务名 | 功能描述 | 复杂度 | 包装策略 | 状态 | 健康检查 |
|--------|----------|--------|----------|------|----------|
| `data_hub` | 数据中枢 - 统一数据获取、聚合 | 低 | SimpleClientWrapper | ✅ 可用 | 查询北京降雨 |
| `hydrology` | 水利模型 - 降雨径流、洪水演进、水库调度 | 高 | ComplexClientWrapper | ✅ 可用 | 运行测试模型 |
| `hipims` | 2D 水动力模拟 - GPU 加速洪水演进 | 高 | ComplexClientWrapper | ✅ 可用 | 检查GPU |
| `web_search` | 网络搜索 - KIMI API 联网查询 | 低 | SimpleClientWrapper | ✅ 可用 | 检查API状态 |
| `rainfall` | 降雨数据 - 实时/预报降雨 | 低 | SimpleClientWrapper | ✅ 可用 | 查询北京天气 |
| `filesystem` | 文件系统 - 文件操作 | 低 | SimpleClientWrapper | ✅ 可用 | 目录检查 |
| `document` | 文档处理 - 文档解析 | 低 | SimpleClientWrapper | ✅ 可用 | 依赖检查 |
| `decision_chain` | 决策链生成 - 智能体决策链优化 | 高 | ComplexClientWrapper | ✅ 可用 | - |
| `yolo_vision` | 视觉检测 - YOLO 洪水区域检测 | 高 | ComplexClientWrapper | ✅ 可用 | 模型信息 |

## 快速开始

### 1. 环境准备

确保已配置环境变量：

```powershell
# Windows PowerShell
$env:KIMI_API_KEY="your-kimi-api-key"
$env:OPENWEATHER_API_KEY="your-openweather-key"  # 可选
$env:QWEATHER_API_KEY="your-qweather-key"        # 推荐
```

### 2. 启动后端服务

```powershell
python -m web.backend.main
```

后端启动时会自动：
1. 连接所有 MCP 服务
2. 执行健康检查（真实 API 调用/模型测试）
3. 后续直接使用，无需初始化

### 3. 查看服务状态

访问健康检查接口：

```bash
curl http://localhost:8001/api/health
```

返回示例：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "水利智脑 Web服务",
  "mcp_services": {
    "initialized": true,
    "total_services": 9,
    "healthy_count": 8,
    "unhealthy_count": 1,
    "healthy_services": ["rainfall", "data_hub", "hydrology", ...],
    "details": {...}
  }
}
```

## 健康检查与初始化

### 什么是健康检查？

健康检查是 MCP 服务在启动时执行的**真实验证**，确保：
- API 可正常调用
- 模型可加载运行
- 依赖可用

不再是 mock 数据，而是**真实的 API 调用**和**小数据量测试**。

### 各服务健康检查详情

| 服务 | 健康检查工具 | 检查内容 | 必需 |
|------|-------------|----------|------|
| `rainfall` | `get_current_rainfall` | 查询北京实时天气 | 是 |
| `data_hub` | `get_rainfall_data` | 查询北京降雨数据 | 是 |
| `hydrology` | `run_rainfall_runoff` | 运行小数据量降雨径流模型 | 是 |
| `hipims` | `check_gpu_availability` | 检查 GPU 可用性 | 否 |
| `filesystem` | `health_check` | 验证目录和文件可用性 | 是 |
| `document` | `health_check` | 验证 python-docx 依赖 | 否 |
| `web_search` | `check_api_status` | 检查 KIMI API 状态 | 否 |
| `yolo_vision` | `get_model_info` | 检查 YOLO 模型信息 | 否 |

### 使用 MCPHealthCheckManager

```python
from flood_decision_agent.mcp.clients import (
    MCPHealthCheckManager,
    initialize_mcp_services,
    get_mcp_health_manager
)

# 方式1：初始化并获取结果（后端启动时自动调用）
health_results = await initialize_mcp_services()

# 查看结果
for name, result in health_results.items():
    status = "✓" if result.healthy else "✗"
    print(f"{status} {name}: {result.message}")

# 方式2：获取管理器单例（后续直接使用）
manager = await get_mcp_health_manager()

# 获取健康状态
status = manager.get_health_status()
print(f"健康服务: {status['healthy_services']}")

# 直接调用工具（服务已就绪，无需初始化）
result = await manager.call_tool(
    "rainfall",
    "get_current_rainfall",
    {"city": "北京"}
)
```

### 启动日志示例

```
[INFO] 正在初始化 MCP 服务...
[OK] MCP 服务初始化完成: 8/9 个服务健康
  ✓ rainfall: 健康检查成功
  ✓ data_hub: 健康检查成功
  ✓ hydrology: 健康检查成功
  ✓ hipims: 健康检查成功
  ✓ filesystem: 健康检查成功
  ✓ document: 健康检查成功
  ✓ yolo_vision: 健康检查成功
  ✗ web_search: 健康检查失败: 未配置 KIMI_API_KEY
[OK] Web服务启动成功
```

### 后端生命周期集成

MCP 服务初始化已集成到 FastAPI 的 `lifespan` 中：

```python
from fastapi import FastAPI
from flood_decision_agent.mcp.clients import initialize_mcp_services

app = FastAPI()

@app.on_event("startup")
async def startup():
    # 启动时自动初始化
    await initialize_mcp_services()

@app.on_event("shutdown")
async def shutdown():
    # 关闭时清理连接
    from flood_decision_agent.mcp.clients import get_mcp_health_manager
    manager = get_mcp_health_manager()
    await manager.close()
```

## MCP 服务器配置

### 配置文件位置

MCP 服务器配置位于 `configs/mcp/servers.yaml`。

### 启用/禁用服务

```yaml
mcp_servers:
  rainfall:
    command: python
    args:
      - "-m"
      - "flood_decision_agent.mcp.servers.rainfall_server"
    env:
      PYTHONIOENCODING: "utf-8"
      PYTHONUNBUFFERED: "1"
      OPENWEATHER_API_KEY: "${OPENWEATHER_API_KEY}"
      QWEATHER_API_KEY: "${QWEATHER_API_KEY}"
    description: "降雨数据服务 - 实时和历史降雨数据查询"
    enabled: true  # 设置为 false 可禁用服务
```

### 工具复杂度分类

配置中的 `tool_complexity` 部分用于结果包装器：

```yaml
settings:
  tool_complexity:
    complex_tools:
      - hydrology
      - hipims
      - decision_chain
    simple_tools:
      - rainfall
      - data_hub
      - web_search
      - filesystem
      - document
```

复杂工具会使用 LLM 生成专业解释，简单工具直接透传原始结果。

## 结果包装器

### 什么是结果包装器？

结果包装器是 Client 层的功能，用于根据工具类型自动选择是否使用 LLM 对结果进行专业解释：

- **简单工具**（如数据查询）：直接透传原始结果
- **复杂工具**（如洪水模拟）：使用 LLM 生成专业解释

### 使用包装器

```python
from flood_decision_agent.mcp.clients import MCPWrappedClientManager

# 创建带包装器的管理器
manager = MCPWrappedClientManager()
await manager.connect_all()

# 调用复杂工具（自动使用 LLM 解释）
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="run_rainfall_runoff",
    arguments={
        "rainfall": [10, 20, 30, 25, 15],
        "catchment_area": 100
    }
)

print(result)
# {
#     "success": True,
#     "raw_data": {...},           # 原始计算结果
#     "explanation": "...",         # LLM 生成的专业解释
#     "summary": "...",             # 一句话摘要
#     "wrapped": True,
#     "server": "hydrology",
#     "tool": "run_rainfall_runoff"
# }

# 调用简单工具（直接透传）
result = await manager.call_tool(
    server_name="data_hub",
    tool_name="get_rainfall_data",
    arguments={"city": "北京"}
)

print(result)
# {
#     "success": True,
#     "raw_data": {...},           # 原始数据
#     "wrapped": False,
#     "server": "data_hub",
#     "tool": "get_rainfall_data"
# }
```

### 强制控制包装行为

```python
# 强制包装（即使工具被分类为简单工具）
result = await manager.call_tool(
    server_name="data_hub",
    tool_name="get_rainfall_data",
    arguments={"city": "北京"},
    wrap_result=True
)

# 强制不包装（即使工具被分类为复杂工具）
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="run_rainfall_runoff",
    arguments={...},
    wrap_result=False
)
```

### 使用底层包装器

```python
from flood_decision_agent.mcp.clients import (
    SimpleClientWrapper,
    ComplexClientWrapper,
    MCPClientManager,
)

manager = MCPClientManager()
await manager.connect_all()

# 简单包装器 - 直接透传
simple = SimpleClientWrapper(manager)
result = await simple.execute(
    server_name="filesystem",
    tool_name="list_directory",
    arguments={"path": "."}
)

# 复杂包装器 - 带 LLM 解释
from flood_decision_agent.infrastructure.llm.kimi_client import get_kimi_client

llm_client = get_kimi_client()
complex_wrapper = ComplexClientWrapper(manager, llm_client)

result = await complex_wrapper.execute(
    server_name="hydrology",
    tool_name="run_reservoir_dispatch",
    arguments={
        "inflow": [100, 200, 350, 400, 300, 200, 150],
        "initial_level": 100.0,
        "target_level": 95.0,
        "max_outflow": 500.0
    }
)

print(result["explanation"])
# 输出: 水库调度方案解释...
```

### 提示词管理

```python
from flood_decision_agent.mcp.clients import PromptManager

# 判断工具复杂度
is_complex = PromptManager.is_complex_tool("hydrology")  # True
is_simple = PromptManager.is_simple_tool("data_hub")     # True

# 获取提示词模板
prompt = PromptManager.get_prompt("hipims")

# 格式化提示词
formatted = PromptManager.format_prompt(
    "hipims",
    simulation_results=json.dumps(simulation_data)
)
```

## Data Hub 服务

### 获取降雨数据

```python
result = await manager.call_tool(
    server_name="data_hub",
    tool_name="get_rainfall_data",
    arguments={
        "city": "北京",
        "provider": "openweather",  # 或 "qweather"
        "use_cache": True
    }
)
```

### 聚合多数据源

```python
result = await manager.call_tool(
    server_name="data_hub",
    tool_name="aggregate_data_sources",
    arguments={
        "sources": ["rainfall", "hydrology"],
        "location": "北京",
        "use_cache": False
    }
)
```

## Hydrology 服务

### 降雨径流模拟

```python
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="run_rainfall_runoff",
    arguments={
        "rainfall": [10, 20, 30, 25, 15, 10, 5],
        "catchment_area": 50  # km²
    }
)

# 结果包含 LLM 解释
print(result["explanation"])
# 输出: 结果解读、当前状况、趋势预测、预警级别
```

### 洪水演进模拟

```python
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="run_flood_routing",
    arguments={
        "inflow": [100, 150, 200, 180, 140, 100, 80, 60],
        "k": 3.0,  # 蓄量常数
        "x": 0.3   # 权重系数
    }
)
```

### 水库调度

```python
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="run_reservoir_dispatch",
    arguments={
        "inflow": [100, 200, 350, 400, 300, 200, 150],
        "initial_level": 100.0,
        "target_level": 95.0,
        "max_outflow": 500.0
    }
)

# 结果包含调度方案解释
print(result["explanation"])
# 输出: 方案核心、预期效果、注意事项、执行建议
```

### YOLO 洪水检测

```python
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="detect_flood_from_image",
    arguments={
        "image_path": "path/to/flood_image.jpg",
        "confidence": 0.5,
        "save_result": True
    }
)
```

### 集成工作流

```python
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="run_integrated_workflow",
    arguments={
        "location": "北京",
        "data_source": "openweather",
        "catchment_area": 100,
        "simulation_duration": 3600,
        "use_gpu": False
    }
)
```

## HiPIMS 服务

### 检查 GPU 可用性

```python
result = await manager.call_tool(
    server_name="hipims",
    tool_name="check_gpu_availability",
    arguments={}
)
```

### 运行 2D 洪水模拟

```python
result = await manager.call_tool(
    server_name="hipims",
    tool_name="run_2d_simulation",
    arguments={
        "terrain_path": "data/terrain.asc",
        "boundary_conditions": {
            "inflow_points": [{"i": 0, "j": 50, "discharge": 10.0}],
            "outflow_points": [],
            "initial_water_level": 0.5
        },
        "rainfall_data": {
            "type": "uniform",
            "intensity": 50.0,
            "duration": 3600
        },
        "simulation_duration": 3600,
        "time_step": 1.0,
        "use_gpu": True
    }
)

# 结果包含专业解释
print(result["explanation"])
# 输出:
# 一句话总结: ...
# 主要风险: ...
# 建议行动: ...
# 数据可靠性: ...
```

### 获取模拟状态

```python
result = await manager.call_tool(
    server_name="hipims",
    tool_name="get_simulation_status",
    arguments={
        "simulation_id": "HIPIMS_20250402_..."
    }
)
```

## Rainfall 服务

Rainfall 服务提供实时降雨数据和天气预报功能，支持多个数据源（OpenWeatherMap、和风天气）。

### 城市名称支持

Rainfall 服务支持多种城市名称格式，包括：
- 标准名称：如 "北京"、"上海"
- 区县级：如 "金坛区"、"常州市"
- 别名：如 "金坛" → "金坛区"

```python
# 以下调用都能正确工作
"金坛"      # 自动解析为金坛区
"金坛区"    # 直接匹配
"常州市"    # 标准格式
```

### 获取实时降雨数据

```python
result = await manager.call_tool(
    server_name="rainfall",
    tool_name="get_current_rainfall",
    arguments={
        "city": "金坛",
        "provider": "qweather"  # 推荐使用和风天气
    }
)

# 返回数据示例
# {
#     "success": True,
#     "provider": "qweather",
#     "city": "金坛",
#     "current": {
#         "temperature": "19",
#         "humidity": "47",
#         "weather": "阴",
#         "precipitation": "0.0",
#         "wind_speed": "21",
#         "wind_direction": "东南风"
#     }
# }
```

### 获取逐小时预报

```python
result = await manager.call_tool(
    server_name="rainfall",
    tool_name="get_hourly_rainfall",
    arguments={
        "city": "金坛",
        "hours": 24
    }
)
```

### 获取天气预报

```python
result = await manager.call_tool(
    server_name="rainfall",
    tool_name="get_rainfall_forecast",
    arguments={
        "city": "金坛",
        "days": 3
    }
)
```

## YOLO Vision 服务

YOLO Vision 服务提供基于 YOLO11n 的水利视觉检测功能。

### 健康检查

服务启动时会调用 `get_model_info` 检查模型是否可加载。

### 获取模型信息

```python
result = await manager.call_tool(
    server_name="yolo_vision",
    tool_name="get_model_info",
    arguments={}
)
```

### 检测洪水区域

```python
result = await manager.call_tool(
    server_name="yolo_vision",
    tool_name="detect_flood_areas",
    arguments={
        "image_path": "path/to/flood_image.jpg",
        "confidence": 0.25,
        "save_result": True
    }
)
```

### 检测水体

```python
result = await manager.call_tool(
    server_name="yolo_vision",
    tool_name="detect_water_bodies",
    arguments={
        "image_path": "path/to/water_image.jpg",
        "confidence": 0.3
    }
)
```

## Filesystem 服务

Filesystem 服务提供规划文件的标准化读写操作。

### 健康检查

服务启动时会检查 `./plans` 和 `./data` 目录是否可访问。

### 写入规划文件

```python
result = await manager.call_tool(
    server_name="filesystem",
    tool_name="write_planning_markdown",
    arguments={
        "plan_name": "2024年防汛预案",
        "content": "# 防汛预案\n\n内容..."
    }
)
```

### 读取规划文件

```python
result = await manager.call_tool(
    server_name="filesystem",
    tool_name="read_planning_file",
    arguments={
        "plan_id": "plan_20240101_xxx.md"
    }
)
```

### 写入 JSON 数据

```python
result = await manager.call_tool(
    server_name="filesystem",
    tool_name="write_data_json",
    arguments={
        "filename": "rainfall_data.json",
        "data": {"city": "北京", "precipitation": 25.5}
    }
)
```

## Document 服务

Document 服务提供文档格式转换功能。

### 健康检查

服务启动时会检查 `python-docx` 依赖是否可用。

### Docx 转 Markdown

```python
result = await manager.call_tool(
    server_name="document",
    tool_name="docx_to_markdown",
    arguments={
        "input_file": "report.docx",
        "include_metadata": True
    }
)
```

### 读取 Docx 内容

```python
result = await manager.call_tool(
    server_name="document",
    tool_name="read_docx_content",
    arguments={
        "input_file": "report.docx"
    }
)
```

### 创建示例文档

```python
result = await manager.call_tool(
    server_name="document",
    tool_name="create_sample_docx",
    arguments={
        "filename": "test.docx",
        "title": "测试文档"
    }
)
```

## 总结智能体

### 什么是总结智能体？

总结智能体（SummarizerAgent）是任务执行完成后的智能总结组件，能够：
- 分析任务执行过程和结果
- 提取关键数据发现
- 生成专业的总结报告
- 提供调度建议和行动指南

### 在 WebSocket 中使用

当用户通过 WebSocket 发送聊天消息时，系统会自动：

1. 接收并解析用户请求
2. 生成决策链和任务图
3. 执行各个任务节点
4. **调用总结智能体生成专业总结**
5. 返回给前端

```python
# WebSocket 消息流程示例
# 
# 1. 发送用户消息
# {"type": "chat_message", "content": "分析金坛降雨情况"}
#
# 2. 接收执行完成消息
# {
#     "type": "execution_complete",
#     "success": true,
#     "summary": {"total_tasks": 3, "completed_tasks": 3, ...},
#     "results": [...]
# }
#
# 3. 接收 AI 回复（包含总结智能体输出）
# {
#     "type": "assistant_message",
#     "content": "## 一、任务执行概况\n...\n## 二、关键数据发现\n..."
# }
```

### 提示词模板

总结智能体使用专业的提示词模板，包含：

```python
# 总结报告结构
SUMMARIZER_SYSTEM_PROMPT = """你是一位水利调度专家，需要对任务执行过程和结果进行专业总结。

输出要求：
- 使用专业的水利术语
- 数据准确、逻辑清晰
- 建议具有可操作性"""

# 报告模板包含：
# 1. 任务执行概况
# 2. 关键数据发现
# 3. 趋势预测和风险评估
# 4. 调度建议和行动指南
```

### 直接调用总结智能体

```python
from flood_decision_agent.agents.summarizer import SummarizerAgent
from flood_decision_agent.core.message import BaseMessage, MessageType

# 创建总结智能体
summarizer = SummarizerAgent(enable_streaming=False)

# 构建执行信息
execution_info = {
    "task_request": {
        "input": "分析金坛降雨情况",
        "type": "data_query",
    },
    "execution_summary": {
        "total_tasks": 3,
        "completed_tasks": 3,
        "failed_tasks": 0,
    },
    "data_pool_snapshot": {"rainfall": 25.5},
    "task_graph": {"total_tasks": 3},
    "node_results": [...],
}

# 调用总结智能体
message = BaseMessage(
    type=MessageType.EVENT,
    sender="test",
    payload=execution_info
)
result = summarizer._process(message)

print(result["summary"])
# 输出专业总结报告
```

## 完整工作流示例

```python
from flood_decision_agent.mcp.clients import MCPWrappedClientManager

async def flood_decision_workflow():
    # 创建带包装器的管理器
    manager = MCPWrappedClientManager()
    await manager.connect_all()
    
    try:
        # 1. 获取降雨数据（简单工具 - 直接透传）
        rainfall_result = await manager.call_tool(
            server_name="data_hub",
            tool_name="get_rainfall_data",
            arguments={"location": "北京"}
        )
        print(f"降雨数据: {rainfall_result['raw_data']}")
        
        # 2. 运行降雨径流模型（复杂工具 - 带 LLM 解释）
        runoff_result = await manager.call_tool(
            server_name="hydrology",
            tool_name="run_rainfall_runoff",
            arguments={
                "rainfall": [10, 20, 30, 25, 15],
                "catchment_area": 100
            }
        )
        print(f"径流解释: {runoff_result['explanation']}")
        print(f"摘要: {runoff_result['summary']}")
        
        # 3. 运行 HiPIMS 2D 模拟（复杂工具 - 带 LLM 解释）
        peak_discharge = runoff_result['raw_data']['data']['peak_discharge']
        
        flood_result = await manager.call_tool(
            server_name="hipims",
            tool_name="run_2d_simulation",
            arguments={
                "boundary_conditions": {
                    "inflow_points": [{"i": 0, "j": 50, 
                        "discharge": peak_discharge}]
                },
                "simulation_duration": 3600
            }
        )
        print(f"洪水模拟解释: {flood_result['explanation']}")
        
        # 4. 生成调度方案（复杂工具 - 带 LLM 解释）
        dispatch_result = await manager.call_tool(
            server_name="hydrology",
            tool_name="run_reservoir_dispatch",
            arguments={
                "inflow": runoff_result['raw_data']['data']['outflow Hydrograph'],
                "initial_level": 100.0,
                "target_level": 95.0,
                "max_outflow": 500.0
            }
        )
        print(f"调度方案: {dispatch_result['explanation']}")
        
        return {
            "rainfall": rainfall_result,
            "runoff": runoff_result,
            "flood": flood_result,
            "dispatch": dispatch_result,
        }
        
    finally:
        await manager.close_all()

# 运行工作流
import asyncio
results = asyncio.run(flood_decision_workflow())
```

## 错误处理

所有服务返回统一格式的错误信息：

```json
{
    "success": false,
    "error": "错误描述",
    "error_type": "ExceptionClassName",
    "timestamp": "2026-04-02T10:30:00"
}
```

包装器错误处理：

```python
result = await manager.call_tool(
    server_name="hydrology",
    tool_name="run_rainfall_runoff",
    arguments={"invalid_param": "value"}
)

if not result["success"]:
    print(f"错误: {result['error']}")
    # 如果没有 LLM 解释，explanation 为 None
    print(f"解释: {result.get('explanation', 'N/A')}")
```

## 工具类型映射

### 概述

系统使用工具类型映射来智能匹配合适的 MCP 工具与任务类型，确保任务执行时能够自动选用正确的专业工具。

### 任务类型到 MCP 工具映射

| 任务类型 | 映射的 MCP 工具 | 说明 |
|----------|----------------|------|
| `data_query` | `get_rainfall_data`, `get_current_rainfall`, `get_hydrological_data` | 数据查询 |
| `data_collection` | `get_rainfall_data`, `get_current_rainfall`, `get_hourly_rainfall`, `get_rainfall_forecast` | 数据收集 |
| `rainfall_analysis` | `get_rainfall_data`, `get_current_rainfall`, `get_hourly_rainfall`, `aggregate_data_sources` | 降雨分析 |
| `hydrological_simulation` | `run_hydrological_model` | 水文模拟 |
| `flood_simulation` | `run_flood_simulation`, `run_hydrological_model` | 洪水模拟 |
| `flood_forecast` | `run_flood_simulation`, `get_rainfall_forecast` | 洪水预报 |
| `dispatch_decision` | `create_plan`, `update_plan` | 调度决策 |
| `scheduling` | `create_plan`, `update_plan` | 调度计划 |
| `document_processing` | `docx_to_markdown`, `read_docx_content` | 文档处理 |
| `file_operation` | `read_planning_file`, `write_planning_markdown`, `read_data_json`, `write_data_json` | 文件操作 |
| `web_search` | `web_search`, `search` | 网络搜索 |

### 任务类型友好名称

用于前端显示的友好名称：

| 任务类型 | 友好名称 |
|----------|----------|
| `data_query` | 数据查询 |
| `data_collection` | 数据收集 |
| `data_processing` | 数据处理 |
| `rainfall_analysis` | 降雨分析 |
| `hydrological_simulation` | 水文模拟 |
| `flood_simulation` | 洪水模拟 |
| `flood_forecast` | 洪水预报 |
| `dispatch_decision` | 调度决策 |
| `scheduling` | 调度计划 |
| `reporting` | 报告生成 |
| `document_processing` | 文档处理 |
| `file_operation` | 文件操作 |
| `web_search` | 网络搜索 |

### MCP 工具友好名称

| MCP 工具名 | 友好名称 |
|------------|----------|
| `get_rainfall_data` | 获取降雨数据 |
| `get_current_rainfall` | 获取当前降雨 |
| `get_rainfall_forecast` | 获取降雨预报 |
| `get_hourly_rainfall` | 获取逐小时降雨 |
| `get_hydrological_data` | 获取水文数据 |
| `aggregate_data_sources` | 聚合数据源 |
| `run_hydrological_model` | 运行水文模型 |
| `run_flood_simulation` | 运行洪水模拟 |
| `create_plan` | 创建方案 |
| `update_plan` | 更新方案 |

### 前端消息示例

任务更新消息现在包含友好名称：

```json
{
    "type": "task_update",
    "task_id": "data_query_001",
    "friendly_task_name": "数据查询 #001",
    "task_type": "data_query",
    "friendly_task_type": "数据查询",
    "status": "completed",
    "result": {...},
    "duration_ms": 150.5
}
```

## 故障排除

### 服务无法启动

1. 检查环境变量 `KIMI_API_KEY` 是否配置
2. 检查依赖包是否安装：`pip install mcp aiohttp numpy`
3. 检查配置文件 `configs/mcp/servers.yaml` 是否正确

### GPU 不可用

- HiPIMS 会自动回退到 CPU 模式
- 如需 GPU 加速，请安装 CUDA 和 PyTorch

### API 调用失败

- 检查网络连接
- 检查 API Key 是否有效
- 查看服务日志获取详细信息

### LLM 解释失败

- 检查 `KIMI_API_KEY` 是否有效
- 检查 LLM 客户端是否正确初始化
- 复杂工具在没有 LLM 时会回退到原始数据返回

```python
# 检查 LLM 客户端
from flood_decision_agent.infrastructure.llm.kimi_client import get_kimi_client

try:
    llm_client = get_kimi_client()
    print("LLM 客户端初始化成功")
except Exception as e:
    print(f"LLM 客户端初始化失败: {e}")
```
