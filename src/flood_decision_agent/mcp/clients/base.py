"""MCP Client 基础管理器

提供统一的 MCP Client 管理和工具调用接口。
针对 Windows 环境进行了优化。
"""

import asyncio
import io
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool as MCPTool

from flood_decision_agent.infrastructure.config_loader import ConfigLoader
from flood_decision_agent.infrastructure.logging import get_logger
from flood_decision_agent.shared.utils.timeout_utils import (
    with_timeout,
    TimeoutManager,
)

try:
    from flood_decision_agent.mcp.log import get_mcp_logger
    from flood_decision_agent.mcp.log.error_formatter import format_error as format_error_dict
    MCP_LOG_AVAILABLE = True
except ImportError:
    MCP_LOG_AVAILABLE = False

def _is_stderr_fileno_supported() -> bool:
    """检查当前环境的 stderr 是否支持 fileno()

    注意：使用 sys.__stderr__ 而不是 sys.stderr，因为某些情况下
    sys.stderr 可能是被包装的 io.TextIOWrapper，不支持 fileno()
    """
    try:
        # 使用 __stderr__ 检查原始 stderr
        sys.__stderr__.fileno()
        return True
    except (io.UnsupportedOperation, AttributeError):
        return False

def _create_safe_stderr() -> Any:
    """创建一个安全的 stderr 目标，适用于 Windows 子进程

    在 Windows 环境下，如果 stderr 被重定向（如 IDE 控制台）
    或者被 io.TextIOWrapper 包装，subprocess 可能无法获取有效的文件描述符。
    """
    if platform.system() != "Windows":
        return sys.stderr

    # 检查当前 stderr 是否支持 fileno
    if _is_stderr_fileno_supported():
        return sys.stderr

    # 如果不支持 fileno（IDE 环境或被包装），使用 os.devnull 打开的文件
    # 注意：这里不能使用 subprocess.DEVNULL，因为它在 Python 3.13+ 返回整数
    # 而 MCP 库期望 TextIO 对象
    try:
        devnull_file = open(os.devnull, 'w')
        return devnull_file
    except Exception:
        pass

    # 最后的回退方案：使用 sys.__stderr__（原始 stderr）
    return sys.__stderr__

# MCP客户端超时管理器
mcp_timeout_manager = TimeoutManager({
    "mcp_connect": 30.0,
    "mcp_call_tool": 30.0,
    "mcp_fetch_tools": 15.0,
})


@dataclass
class MCPToolInfo:
    """MCP 工具信息"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str


class MCPClientConnection:
    """单个 MCP Client 连接"""
    
    # 重试配置
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_BASE = 1.0  # 基础延迟（秒）
    
    def __init__(self, name: str, server_params: StdioServerParameters):
        self.name = name
        self.server_params = server_params
        self.session: Optional[ClientSession] = None
        self.client = None
        self.read = None
        self.write = None
        self.tools: List[MCPToolInfo] = []
        self._connected = False
        self._logger = None
        
    def _get_logger(self):
        """延迟获取 logger（避免在 __init__ 时可能的问题）"""
        if self._logger is None and MCP_LOG_AVAILABLE:
            try:
                from flood_decision_agent.mcp.log import get_mcp_logger
                self._logger = get_mcp_logger(f"client-{self.name}")
            except Exception:
                pass
        return self._logger
        
    async def connect(self):
        """建立连接（带重试机制，Windows 优化版）"""
        last_error = None
        
        for attempt in range(1, self.MAX_RETRY_ATTEMPTS + 1):
            if self._logger:
                self._logger.info(f"尝试连接 MCP Server: {self.name} (尝试 {attempt}/{self.MAX_RETRY_ATTEMPTS})")
            
            success = await self._try_connect()
            if success:
                return True
            
            last_error = "连接失败"
            if attempt < self.MAX_RETRY_ATTEMPTS:
                delay = self.RETRY_DELAY_BASE * (2 ** (attempt - 1))
                if self._logger:
                    self._logger.info(f"等待 {delay:.1f}秒后重试...")
                await asyncio.sleep(delay)
        
        if self._logger:
            self._logger.error(f"MCP Server {self.name} 连接失败，已尝试 {self.MAX_RETRY_ATTEMPTS} 次")
        return False
    
    async def _try_connect(self) -> bool:
        """尝试建立连接"""
        start_time = time.perf_counter()

        if self._logger:
            self._logger.info(f"正在连接 MCP Server: {self.name}")

        try:
            if platform.system() == "Windows":
                if isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsSelectorEventLoopPolicy):
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

            if self._logger:
                self._logger.debug(f"创建 stdio_client，参数: command={self.server_params.command}, args={self.server_params.args}")

            stderr_target = _create_safe_stderr()
            if self._logger:
                is_fileno_ok = _is_stderr_fileno_supported()
                self._logger.debug(f"stderr fileno 支持: {is_fileno_ok}, stderr 类型: {type(stderr_target)}")

            try:
                self.client = stdio_client(self.server_params, errlog=stderr_target)
                self.read, self.write = await self.client.__aenter__()
            except io.UnsupportedOperation as e:
                if "fileno" in str(e):
                    if self._logger:
                        self._logger.warning(f"检测到 fileno 错误，尝试使用 DEVNULL 作为 stderr")
                    self.client = stdio_client(self.server_params, errlog=subprocess.DEVNULL)
                    self.read, self.write = await self.client.__aenter__()
                else:
                    raise
            
            if self._logger:
                self._logger.debug(f"stdio_client 已创建，read={type(self.read)}, write={type(self.write)}")
            
            self.session = await ClientSession(self.read, self.write).__aenter__()
            
            await asyncio.wait_for(
                self.session.initialize(),
                timeout=30.0
            )
            
            self._connected = True
            
            await self._fetch_tools()
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            if self._logger:
                self._logger.info(f"成功连接 MCP Server: {self.name} | 耗时: {duration_ms:.2f}ms | 工具数: {len(self.tools)}")
            
            return True
            
        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if self._logger:
                self._logger.error(f"连接 MCP Server 超时: {self.name} | 耗时: {duration_ms:.2f}ms")
            await self._cleanup()
            return False
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            import traceback
            tb = traceback.format_exc()
            if self._logger:
                self._logger.error(f"连接 MCP Server 失败: {self.name} | 耗时: {duration_ms:.2f}ms | 错误: {e}")
                self._logger.error(f"详细堆栈:\n{tb}")
            await self._cleanup()
            return False
    
    async def _cleanup(self):
        """清理资源（Windows 兼容版）"""
        if platform.system() == "Windows":
            import warnings
            warnings.filterwarnings("ignore", category=RuntimeWarning)
        
        try:
            if self.session:
                try:
                    await self.session.__aexit__(None, None, None)
                except (GeneratorExit, StopAsyncIteration, RuntimeError) as e:
                    if "cancel scope" not in str(e).lower():
                        raise
        except Exception:
            pass
        try:
            if self.client:
                try:
                    await self.client.__aexit__(None, None, None)
                except (GeneratorExit, StopAsyncIteration, RuntimeError) as e:
                    if "cancel scope" not in str(e).lower():
                        raise
        except Exception:
            pass
        self._connected = False
    
    async def _fetch_tools(self):
        """获取服务器工具列表"""
        if not self.session:
            return
        
        try:
            tools_response = await self.session.list_tools()
            self.tools = [
                MCPToolInfo(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema,
                    server_name=self.name
                )
                for tool in tools_response.tools
            ]
        except Exception as e:
            get_logger().warning(f"获取工具列表失败: {e}")
    
    # 工具调用重试配置
    TOOL_MAX_RETRY_ATTEMPTS = 3
    TOOL_RETRY_DELAY_BASE = 0.5
    
    @mcp_timeout_manager.decorator_for("mcp_call_tool")
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具（带重试机制和30秒超时）"""
        last_error = None
        
        for attempt in range(1, self.TOOL_MAX_RETRY_ATTEMPTS + 1):
            try:
                result = await self._try_call_tool(tool_name, arguments)
                return result
            except Exception as e:
                last_error = e
                if attempt < self.TOOL_MAX_RETRY_ATTEMPTS:
                    delay = self.TOOL_RETRY_DELAY_BASE * (2 ** (attempt - 1))
                    if self._logger:
                        self._logger.warning(f"工具 {self.name}.{tool_name} 调用失败: {e}, {delay:.1f}秒后重试...")
                    await asyncio.sleep(delay)
        
        raise RuntimeError(f"工具 {self.name}.{tool_name} 调用失败，已尝试 {self.TOOL_MAX_RETRY_ATTEMPTS} 次: {last_error}")
    
    async def _try_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """尝试调用工具"""
        if not self.session or not self._connected:
            raise RuntimeError(f"MCP Client '{self.name}' 未连接")

        start_time = time.perf_counter()
        
        logger = self._get_logger()
        if logger:
            logger.info(f"调用工具: {self.name}.{tool_name} | 参数: {arguments}")

        result = await self.session.call_tool(tool_name, arguments)

        duration_ms = (time.perf_counter() - start_time) * 1000

        if result.content:
            content = result.content[0]
            if content.type == "text":
                try:
                    response = json.loads(content.text)
                    if self._logger:
                        if response.get("success"):
                            self._logger.info(f"工具调用成功: {self.name}.{tool_name} | 耗时: {duration_ms:.2f}ms")
                        else:
                            self._logger.warning(f"工具调用失败: {self.name}.{tool_name} | 耗时: {duration_ms:.2f}ms | 错误: {response.get('error')}")
                    return response
                except json.JSONDecodeError:
                    if self._logger:
                        self._logger.info(f"工具调用成功: {self.name}.{tool_name} | 耗时: {duration_ms:.2f}ms")
                    return {"text": content.text, "success": True}
            elif content.type == "image":
                if self._logger:
                    self._logger.info(f"工具调用成功: {self.name}.{tool_name} | 返回图像 | 耗时: {duration_ms:.2f}ms")
                return {"image_data": content.data, "success": True}

        if self._logger:
            if not result.isError:
                self._logger.info(f"工具调用成功: {self.name}.{tool_name} | 耗时: {duration_ms:.2f}ms")
            else:
                self._logger.warning(f"工具调用返回错误: {self.name}.{tool_name} | 耗时: {duration_ms:.2f}ms")

        return {"success": not result.isError}
    
    async def close(self):
        """关闭连接"""
        await self._cleanup()


class MCPClientManager:
    """MCP Client 管理器

    管理多个 MCP Client 连接，提供统一的工具调用接口。
    针对 Windows 环境进行了优化。
    """

    def __init__(self, auto_load_config: bool = True):
        self.clients: Dict[str, MCPClientConnection] = {}
        self.logger = get_logger().bind(name="MCPClientManager")

        # Windows 环境设置
        if platform.system() == "Windows":
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                self.logger.debug("已设置 WindowsProactorEventLoopPolicy")
            except Exception as e:
                self.logger.warning(f"设置 EventLoopPolicy 失败: {e}")

        # 加载 .env.local 到环境变量
        _config_loader = ConfigLoader()

        # 自动加载配置文件
        if auto_load_config:
            self.load_from_config()

    def load_from_config(self, config_path: Optional[str] = None):
        """从配置文件加载 MCP Servers"""
        if config_path is None:
            base_path = Path(__file__).parent.parent.parent.parent.parent
            config_path = base_path / "configs" / "mcp" / "servers.yaml"

        config_file = Path(config_path)

        if not config_file.exists():
            self.logger.warning(f"MCP 配置文件不存在: {config_path}")
            return

        self.logger.info(f"开始加载配置文件: {config_file}")
        
        try:
            # 根据文件扩展名选择解析方式
            if config_file.suffix in ['.yaml', '.yml']:
                import yaml
                self.logger.info("正在解析 YAML 配置...")
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            else:
                # JSON 格式
                self.logger.info("正在解析 JSON 配置...")
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            self.logger.info(f"配置解析完成: {list(config.keys())}")

            # 支持多种键名格式 (mcp_servers 或 mcpServers)
            servers = config.get("mcp_servers") or config.get("mcpServers", {})
            
            self.logger.info(f"MCP 服务器配置: {servers.keys() if servers else 'None'}")

            for name, server_config in servers.items():
                self.logger.info(f"处理服务器配置: {name}, 配置内容: {server_config}")
                
                if not server_config.get("enabled", True):
                    self.logger.info(f"跳过禁用的 MCP Server: {name}")
                    continue

                command = server_config.get("command")
                args = server_config.get("args", [])
                env = server_config.get("env", {})
                
                self.logger.info(f"服务器 {name}: command={command}, args={args}")
                
                # 替换环境变量占位符 ${VAR}
                self.logger.debug(f"开始解析环境变量: {env}")
                env = self._resolve_env_vars(env)
                self.logger.debug(f"环境变量解析完成: {env}")

                if command and args:
                    self.logger.debug(f"准备注册服务器: {name}")
                    try:
                        self.register_server(name, command, args, env)
                        self.logger.info(f"从配置加载 MCP Server: {name}")
                    except Exception as e:
                        self.logger.error(f"加载 MCP Server {name} 失败: {e}，继续处理其他服务器")
                        import traceback
                        self.logger.error(traceback.format_exc())
                else:
                    self.logger.warning(f"MCP Server {name} 缺少 command 或 args 配置")

            self.logger.info(f"已加载 {len(self.clients)} 个 MCP Server")

        except Exception as e:
            self.logger.error(f"加载 MCP 配置失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def _resolve_env_vars(self, env: Dict[str, str]) -> Dict[str, str]:
        """替换环境变量占位符 ${VAR}（使用统一的配置读取入口）"""
        from flood_decision_agent.infrastructure.config_loader import get_api_key
        
        resolved = {}
        for key, value in env.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                try:
                    resolved[key] = get_api_key(var_name)
                except Exception:
                    resolved[key] = os.environ.get(var_name, value)
            else:
                resolved[key] = value
        return resolved

    def register_server(self, name: str, command: str, args: List[str], env: Optional[Dict] = None):
        """注册 MCP Server"""
        self.logger.debug(f"register_server: 开始注册 {name}")
        try:
            from flood_decision_agent.infrastructure.config_loader import _load_env_file
            _load_env_file()
            self.logger.debug(f"register_server: 环境变量加载完成")
        except Exception as e:
            self.logger.warning(f"加载环境变量失败: {e}，继续使用现有环境变量")
        
        merged_env = dict(os.environ)
        if env:
            merged_env.update(env)

        # Windows 环境添加必要变量
        if platform.system() == "Windows":
            merged_env["PYTHONIOENCODING"] = merged_env.get("PYTHONIOENCODING", "utf-8")
            merged_env["PYTHONUNBUFFERED"] = "1"

        # 添加项目根目录到 PYTHONPATH（用于正确导入 flood_decision_agent 模块）
        project_root = Path(__file__).parent.parent.parent.parent.parent
        current_pythonpath = merged_env.get("PYTHONPATH", "")
        if current_pythonpath:
            merged_env["PYTHONPATH"] = f"{project_root}{os.pathsep}{current_pythonpath}"
        else:
            merged_env["PYTHONPATH"] = str(project_root)
        
        self.logger.debug(f"register_server: PYTHONPATH 设置完成")

        params = StdioServerParameters(
            command=command,
            args=args,
            env=merged_env
        )
        
        self.logger.debug(f"register_server: StdioServerParameters 创建完成")
        
        if self.logger:
            self.logger.debug(f"注册服务器 [{name}]: command={command}, args={args}")
            self.logger.debug(f"环境变量: PYTHONPATH={merged_env.get('PYTHONPATH')}, QWEATHER_API_KEY={'已设置' if merged_env.get('QWEATHER_API_KEY') else '未设置'}")
        
        self.logger.debug(f"register_server: 准备创建 MCPClientConnection")
        try:
            self.clients[name] = MCPClientConnection(name, params)
            self.logger.info(f"已注册 MCP Server: {name}, 当前客户端数: {len(self.clients)}")
        except Exception as e:
            self.logger.error(f"注册 MCP Server {name} 失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
    async def connect_all(self):
        """连接所有 Server"""
        if not self.clients:
            self.logger.warning("没有注册的 MCP Server")
            return 0
        
        results = await asyncio.gather(
            *[client.connect() for client in self.clients.values()],
            return_exceptions=True
        )
        
        connected = 0
        for name, result in zip(self.clients.keys(), results):
            if isinstance(result, Exception):
                self.logger.error(f"连接 {name} 失败: {result}")
            elif result:
                connected += 1
                self.logger.info(f"已连接: {name}")
        
        self.logger.info(f"MCP 连接完成: {connected}/{len(self.clients)}")
        return connected
    
    def list_all_tools(self) -> List[MCPToolInfo]:
        """列出所有可用工具"""
        all_tools = []
        for client in self.clients.values():
            all_tools.extend(client.tools)
        return all_tools
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定 Server 的工具"""
        if server_name not in self.clients:
            raise ValueError(f"未知的 MCP Server: {server_name}")
        
        client = self.clients[server_name]
        return await client.call_tool(tool_name, arguments)
    
    async def call_tool_auto(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """自动查找并调用工具"""
        for client in self.clients.values():
            if any(t.name == tool_name for t in client.tools):
                return await client.call_tool(tool_name, arguments)
        
        raise ValueError(f"未找到工具: {tool_name}")
    
    async def close_all(self):
        """关闭所有连接（Windows 兼容版）"""
        if platform.system() == "Windows":
            import warnings
            warnings.filterwarnings("ignore", category=RuntimeWarning)
        
        async def safe_close(client):
            try:
                await client.close()
            except (GeneratorExit, StopAsyncIteration, RuntimeError) as e:
                if "cancel scope" not in str(e).lower():
                    raise
            except Exception:
                pass
        
        await asyncio.gather(
            *[safe_close(client) for client in self.clients.values()],
            return_exceptions=True
        )
        self.logger.info("所有 MCP 连接已关闭")


# 全局管理器实例
_global_mcp_manager: Optional[MCPClientManager] = None


def get_mcp_manager() -> MCPClientManager:
    """获取全局 MCP 管理器"""
    global _global_mcp_manager
    if _global_mcp_manager is None:
        _global_mcp_manager = MCPClientManager()
    return _global_mcp_manager