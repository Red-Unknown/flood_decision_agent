---
name: "mcp-server-workflow"
description: "创建自定义 MCP Server 的标准化工作流程。Invoke when user wants to create a new MCP server, add tool capabilities to agents, or integrate external services via MCP protocol."
---

# 自定义 MCP Server 标准化工作流程

本 Skill 提供创建、开发、测试和部署自定义 MCP Server 的完整标准化流程。

## 何时使用

- 需要创建新的 MCP Server 扩展 Agent 能力
- 需要集成外部服务（数据库、API、模型等）到 Agent 系统
- 需要为特定业务场景（如水利模型、文件处理）创建工具服务
- 需要替换或升级现有的本地工具为 MCP 服务

## 前置条件

- Python 3.11+
- 已安装 `mcp` 包: `pip install mcp`
- 了解项目 MCP 模块架构 (`src/flood_decision_agent/mcp/`)

---

## 阶段一：环境配置

### 1.1 检查环境

```bash
# 检查 mcp 安装
python -c "import mcp; print(mcp.__version__)"

# 检查项目 MCP 模块
python -c "from flood_decision_agent.mcp import MCPClientManager; print('OK')"
```

### 1.2 创建 Server 目录结构

```
src/flood_decision_agent/mcp/servers/
├── __init__.py
├── {your_server}_server.py    # 主服务文件
└── README.md                   # 服务文档
```

---

## 阶段二：模块开发

### 2.1 创建基础 Server 框架（Windows 兼容版）

**重要：Windows 环境必须使用以下规范**

```python
"""{ServerName} MCP Server

{服务描述}
"""

import asyncio
import json
import platform
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

from flood_decision_agent.infra.logging import get_logger

# 创建 MCP Server
server = Server("{server-name}")
logger = get_logger().bind(name="{ServerName}Server")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="{tool_name}",
            description="{工具描述}",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "参数1描述"
                    },
                    "param2": {
                        "type": "number",
                        "description": "参数2描述"
                    }
                },
                "required": ["param1"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "{tool_name}":
            return await _handle_tool(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    except Exception as e:
        logger.error(f"工具执行失败: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
        )]


async def _handle_tool(args: Dict[str, Any]) -> List[TextContent]:
    """处理具体工具逻辑"""
    # 实现工具逻辑
    result = {"success": True, "data": {}}
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def main():
    """启动 MCP Server（Windows 兼容版）"""
    # Windows 环境设置
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 关键：使用正确的导入方式
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    
    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### 2.2 Windows stdio 规范检查清单

创建 MCP Server 时，必须确认以下事项：

| 检查项 | 要求 | 说明 |
|--------|------|------|
| **EventLoopPolicy** | ✅ 必须设置 | Windows 必须使用 `WindowsProactorEventLoopPolicy` |
| **stdio_server 导入** | ✅ 局部导入 | 必须在 `main()` 函数内导入 `mcp_stdio_server` |
| **编码环境变量** | ✅ 必须设置 | `PYTHONIOENCODING=utf-8` |
| **无缓冲输出** | ✅ 建议设置 | `PYTHONUNBUFFERED=1` |
| **console.log** | ❌ 禁止 | 移除所有 `print` 调试语句（除非必要） |
| **stdin 读取** | ❌ 禁止 | 不要直接读取 `sys.stdin` |

### 2.3 定义工具接口

遵循以下规范：

1. **工具命名**: 使用 `snake_case`，如 `write_planning_markdown`
2. **参数定义**: 使用 JSON Schema 格式，明确类型和描述
3. **返回格式**: 统一返回 JSON，包含 `success` 字段
4. **错误处理**: 捕获异常并返回结构化错误信息

### 2.4 实现业务逻辑

```python
# 示例：数据查询工具
async def _handle_query_data(args: Dict[str, Any]) -> List[TextContent]:
    data_source = args.get("source")
    query = args.get("query")
    
    try:
        # 执行业务查询
        data = await fetch_data(data_source, query)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "data": data,
                "count": len(data),
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }, ensure_ascii=False)
        )]
```

---

## 阶段三：接口定义

### 3.1 添加到 MCP 配置（Windows 环境变量）

编辑 `src/flood_decision_agent/mcp/configs/mcp_servers.json`：

```json
{
  "mcpServers": {
    "{your_server}": {
      "command": "python",
      "args": [
        "-m",
        "flood_decision_agent.mcp.servers.{your_server}_server"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      },
      "description": "{服务描述}",
      "enabled": true
    }
  }
}
```

**关键环境变量说明：**

- `PYTHONIOENCODING=utf-8`: 确保标准输入输出使用 UTF-8 编码，避免中文乱码
- `PYTHONUNBUFFERED=1`: 禁用输出缓冲，确保实时通信

### 3.2 创建 Client 封装（Windows 优化版）

如需简化调用，创建 Client 封装：

```python
# src/flood_decision_agent/mcp/clients/{your_server}.py

import platform
import asyncio
from flood_decision_agent.mcp.clients.base import MCPClientManager

class {YourServer}MCPClient:
    """{YourServer} MCP 客户端"""
    
    SERVER_NAME = "{your_server}"
    
    def __init__(self, manager: MCPClientManager):
        self.manager = manager
        
        # Windows 环境设置
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    async def {tool_name}(self, param1: str, param2: int) -> Dict:
        """调用 {tool_name} 工具"""
        return await self.manager.call_tool(
            self.SERVER_NAME,
            "{tool_name}",
            {"param1": param1, "param2": param2}
        )
```

---

## 阶段四：测试验证

### 4.1 Windows 环境测试检查清单

在 Windows 上测试 MCP Server 前，请确认：

- [ ] 已设置 `PYTHONIOENCODING=utf-8`
- [ ] 已设置 `PYTHONUNBUFFERED=1`
- [ ] Server 代码中设置了 `WindowsProactorEventLoopPolicy`
- [ ] `stdio_server` 是在 `main()` 函数内局部导入的
- [ ] 没有直接调用 `sys.stdin.read()`
- [ ] 没有使用 `print()` 进行调试输出

### 4.2 独立测试 Server

```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUNBUFFERED="1"
python -m flood_decision_agent.mcp.servers.{your_server}_server

# 预期结果：命令会"挂起"等待输入（这是正常的 stdio 服务器状态）
# 按 Ctrl+C 可以终止
```

### 4.3 集成测试（Windows 兼容版）

创建测试文件 `tests/test_mcp_{your_server}.py`：

```python
import pytest
import asyncio
import platform
from flood_decision_agent.mcp.clients.base import MCPClientManager

@pytest.mark.asyncio
async def test_{your_server}_connection():
    """测试 MCP Server 连接（Windows 兼容版）"""
    # Windows 环境设置
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    manager = MCPClientManager()
    manager.register_server(
        name="{your_server}",
        command="python",
        args=["-m", "flood_decision_agent.mcp.servers.{your_server}_server"]
    )
    
    # 使用超时避免无限等待
    connected = await asyncio.wait_for(
        manager.connect_all(),
        timeout=15.0
    )
    assert connected == 1
    
    # 测试工具调用
    result = await asyncio.wait_for(
        manager.call_tool(
            "{your_server}",
            "{tool_name}",
            {"param1": "test"}
        ),
        timeout=10.0
    )
    
    assert result["success"] is True
    
    await manager.close_all()
```

### 4.4 手动验证 stdio 服务器状态

在终端运行以下命令，验证 Server 是否正常挂起：

```powershell
# PowerShell
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUNBUFFERED="1"
python -m flood_decision_agent.mcp.servers.{your_server}_server

# 如果看到光标闪烁但没有输出，说明 Server 正常运行，等待 MCP 协议输入
# 这是正确的状态！
```

---

## 阶段五：Windows 常见问题排查

### 问题 1: `TypeError: 'async for' requires an object with __aiter__ method`

**原因**: `stdio_server` 导入或使用方式不正确

**解决**:
```python
# ❌ 错误：全局导入
from mcp.server.stdio import stdio_server

# ✅ 正确：局部导入
async def main():
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    async with mcp_stdio_server() as ...
```

### 问题 2: 连接超时或无法连接

**原因**: Windows 默认 EventLoop 不支持 stdio

**解决**:
```python
# 在 main() 函数开头添加
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

### 问题 3: 中文乱码

**原因**: Windows 默认编码不是 UTF-8

**解决**:
```json
// mcp_servers.json
"env": {
    "PYTHONIOENCODING": "utf-8"
}
```

### 问题 4: 输出被缓冲导致延迟

**原因**: Python 默认缓冲 stdout

**解决**:
```json
// mcp_servers.json
"env": {
    "PYTHONUNBUFFERED": "1"
}
```

---

## 阶段六：部署上线

### 6.1 Windows 部署检查清单

- [ ] Server 代码遵循 Windows stdio 规范
- [ ] 已设置 `WindowsProactorEventLoopPolicy`
- [ ] 已配置 `PYTHONIOENCODING=utf-8`
- [ ] 已配置 `PYTHONUNBUFFERED=1`
- [ ] 工具接口文档完整
- [ ] 错误处理完善
- [ ] 日志记录充分
- [ ] 单元测试通过（Windows 环境）

### 6.2 部署步骤

1. **提交代码**
   ```bash
   git add src/flood_decision_agent/mcp/servers/{your_server}_server.py
   git add src/flood_decision_agent/mcp/configs/mcp_servers.json
   git commit -m "feat: add {your_server} MCP server (Windows compatible)"
   ```

2. **更新文档**
   - 更新 `src/flood_decision_agent/mcp/README.md`
   - 添加 Windows 部署注意事项

3. **验证部署（Windows）**
   ```powershell
   # PowerShell
   $env:PYTHONIOENCODING="utf-8"
   $env:PYTHONUNBUFFERED="1"
   python -c "
   from flood_decision_agent.mcp.clients import get_mcp_manager
   import asyncio
   import platform
   
   if platform.system() == 'Windows':
       asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
   
   manager = get_mcp_manager()
   # 注册并连接
   # 验证工具调用
   "
   ```

---

## 最佳实践

### Windows 开发原则

1. **始终设置 EventLoopPolicy**: Windows 必须使用 `ProactorEventLoop`
2. **使用局部导入**: `stdio_server` 在函数内导入
3. **配置环境变量**: 始终设置编码和无缓冲
4. **使用超时**: 所有异步操作添加超时控制
5. **测试在 Windows**: 必须在 Windows 环境测试通过

### 性能优化

1. **连接复用**: MCP Client 连接可复用，避免频繁创建
2. **异步处理**: 使用 `async/await` 处理 I/O 操作
3. **超时控制**: 设置合理的超时时间（建议 10-15 秒）

### 错误处理

```python
# 标准错误格式
{
    "success": False,
    "error": "用户友好的错误信息",
    "error_type": "ExceptionClassName",
    "details": {}  # 可选的详细错误信息
}
```

---

## 参考资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [项目 MCP 模块 README](../../src/flood_decision_agent/mcp/README.md)
- [filesystem_server.py](../../src/flood_decision_agent/mcp/servers/filesystem_server.py) - Windows 兼容完整示例
- [hydrology_server.py](../../src/flood_decision_agent/mcp/servers/hydrology_server.py) - 复杂业务示例
- [document_server.py](../../src/flood_decision_agent/mcp/servers/document_server.py) - 文档处理示例

---

## Windows 快速开始模板

复制以下代码作为新 Server 的起点：

```python
"""Windows 兼容的 MCP Server 模板"""

import asyncio
import json
import platform
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="my_tool",
            description="My tool description",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                },
                "required": ["param"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "my_tool":
        result = {"success": True, "data": arguments}
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]
    raise ValueError(f"Unknown tool: {name}")


async def main():
    """Windows 兼容的启动函数"""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    
    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```