# MCP 子进程数据流实现指南

本文档详细介绍 MCP 服务中子进程数据流的实现原理、架构和注意事项。

## 概述

MCP（Model Context Protocol）服务使用 **Stdio（标准输入/输出）** 方式与子进程进行通信。这种方式允许在本地启动独立的 Python 进程作为 MCP Server，并通过标准输入输出流进行 JSON-RPC 消息传递。

## 架构原理

```
┌─────────────────────────────────────────────────────────────────────┐
│                         主进程 (Backend)                             │
│  ┌─────────────────┐    ┌──────────────────────────────────────┐  │
│  │ MCPClientManager │───▶│ StdioServerParameters               │  │
│  │                 │    │  - command: "python"                 │  │
│  │  • 连接管理      │    │  - args: ["-m", "module_name"]      │  │
│  │  • 工具调用     │    │  - env: {环境变量}                   │  │
│  │  • 会话管理     │    └──────────────────────────────────────┘  │
│  └─────────────────┘                      │                        │
│         │                                  ▼                        │
│         │                    ┌─────────────────────────┐            │
│         │                    │   mcp.client.stdio     │            │
│         │                    │   (stdio_client)       │            │
│         │                    └─────────────────────────┘            │
│         │                               │                           │
│         │                               ▼                           │
│         │                    ┌─────────────────────────┐            │
│         │                    │  子进程 (MCP Server)    │            │
│         │                    │  • rainfall_server      │            │
│         │                    │  • data_hub_server     │            │
│         │                    │  • hydrology_server    │            │
│         └───────────────────▶│  stdin / stdout         │            │
│                              └─────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

## 核心实现

### 1. StdioServerParameters 配置

在 `src/flood_decision_agent/mcp/clients/base.py` 中定义：

```python
from mcp import StdioServerParameters

params = StdioServerParameters(
    command="python",                    # 执行命令
    args=["-m", "module_name"],         # 模块路径
    env={                                # 环境变量
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1",
        "KIMI_API_KEY": "xxx",
        "QWEATHER_API_KEY": "xxx",
    }
)
```

### 2. 环境变量传递

子进程启动时会继承父进程的环境变量，并额外添加以下变量：

```python
# Windows 环境特殊处理
if platform.system() == "Windows":
    merged_env["PYTHONIOENCODING"] = "utf-8"
    merged_env["PYTHONUNBUFFERED"] = "1"

# 添加项目根目录到 PYTHONPATH
project_root = Path(__file__).parent.parent.parent.parent.parent
merged_env["PYTHONPATH"] = str(project_root)
```

### 3. 连接建立过程

```python
async def connect(self):
    """建立与 MCP Server 的连接"""
    from mcp.client.stdio import stdio_client

    # 创建标准输入输出流
    self.client = stdio_client(self.server_params)
    streams = await self.client.__aenter__()

    # 创建会话
    self.session = ClientSession(streams[0], streams[1])
    await self.session.__aenter__()

    # 初始化
    await self.session.initialize()

    # 获取可用工具列表
    response = await self.session.list_tools()
    self.tools = [self._parse_tool(t) for t in response.tools]

    self._connected = True
```

## Windows 特殊处理

### fileno() 兼容性问题

在 Windows 环境下，某些 IDE（如 VS Code）的控制台可能不支持 `fileno()` 系统调用，导致子进程创建失败。

**解决方案**：使用安全的 stderr 处理

```python
def _is_stderr_fileno_supported() -> bool:
    """检查 stderr 是否支持 fileno()"""
    try:
        sys.stderr.fileno()
        return True
    except (AttributeError, UnsupportedOperation):
        return False

def _create_safe_stderr() -> TextIO:
    """创建安全的 stderr 流"""
    if _is_stderr_fileno_supported():
        return sys.stderr
    else:
        # 使用临时文件作为替代
        import tempfile
        return tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
```

### WindowsProactorEventLoopPolicy

Windows 上需要设置事件循环策略：

```python
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

## 配置管理

### 服务配置文件格式

在 `configs/mcp/servers.yaml` 中配置：

```yaml
mcp_servers:
  rainfall:
    command: python
    args:
      - -m
      - flood_decision_agent.mcp.servers.rainfall_server
    env:
      PYTHONIOENCODING: utf-8
      PYTHONUNBUFFERED: "1"
      KIMI_API_KEY: ${KIMI_API_KEY}
      QWEATHER_API_KEY: ${QWEATHER_API_KEY}
    description: 降雨数据服务
    enabled: true
```

### 环境变量占位符替换

```python
def _resolve_env_vars(env: Dict[str, Any]) -> Dict[str, Any]:
    """解析环境变量中的占位符 ${VAR}"""
    resolved = {}
    for key, value in env.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            var_name = value[2:-1]
            resolved[key] = os.environ.get(var_name, value)
        else:
            resolved[key] = value
    return resolved
```

## 注意事项

### 1. 环境变量传递

- **必须传递 API Keys**：确保 `KIMI_API_KEY` 和 `QWEATHER_API_KEY` 等敏感信息正确传递
- **PYTHONPATH**：子进程需要能够导入 `flood_decision_agent` 模块
- **编码设置**：`PYTHONIOENCODING=utf-8` 确保中文正常处理

### 2. Windows 兼容性

- 始终使用 `WindowsProactorEventLoopPolicy`
- 处理 stderr 不支持 fileno 的情况
- 端口占用时等待 TIME_WAIT 状态结束

### 3. 日志输出

- MCP Server 日志必须输出到 **stderr**（MCP 协议要求）
- Client 日志使用 Loguru 输出到 `logs/` 目录
- 避免在子进程中使用 print()，使用 logger

### 4. 性能考虑

- 子进程启动有延迟，建议预热（warm-up）
- 使用缓存避免重复调用 API
- 设置合理的超时时间

### 5. 错误处理

- 子进程异常会导致连接断开，需要实现重连机制
- 检查 `session` 和 `_connected` 状态后再调用工具
- 捕获并记录所有异常信息

## 调试技巧

### 查看子进程通信

可以使用 `python -u` 启动子进程（无缓冲）：

```python
params = StdioServerParameters(
    command="python",
    args=["-u", "-m", "module_name"],  # -u 无缓冲输出
    env={...}
)
```

### 日志级别调整

在开发环境可以启用 DEBUG 级别日志：

```python
import logging
logging.getLogger("mcp").setLevel(logging.DEBUG)
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 连接超时 | 子进程启动慢 | 增加超时时间或预热 |
| fileno 错误 | IDE 控制台不支持 | 使用临时文件替代 stderr |
| 模块导入失败 | PYTHONPATH 未设置 | 确保环境变量正确传递 |
| API 调用失败 | 缺少环境变量 | 检查配置文件和 .env.local |
| 端口占用 | 上次进程未完全关闭 | 等待 TIME_WAIT 结束或使用新端口 |
