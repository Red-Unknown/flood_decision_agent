"""MCP 健康检查与初始化管理器

提供 MCP 服务的健康检查、初始化和生命周期管理功能。
在后端启动时执行健康检查，后续调用无需再次初始化。
"""

import asyncio
import platform
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flood_decision_agent.infra.logging import get_logger
from flood_decision_agent.mcp.clients.base import MCPClientManager, MCPClientConnection

logger = get_logger().bind(name="MCPHealthManager")


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    service_name: str
    status: str
    healthy: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ServiceHealthConfig:
    """服务健康检查配置"""
    service_name: str
    health_check_tool: str
    health_check_args: Dict[str, Any] = field(default_factory=dict)
    required: bool = True


SERVICE_HEALTH_CONFIGS: Dict[str, ServiceHealthConfig] = {
    "rainfall": ServiceHealthConfig(
        service_name="rainfall",
        health_check_tool="get_current_rainfall",
        health_check_args={"city": "北京"},
        required=True
    ),
    "data_hub": ServiceHealthConfig(
        service_name="data_hub",
        health_check_tool="get_rainfall_data",
        health_check_args={"city": "北京", "use_cache": False},
        required=True
    ),
    "hydrology": ServiceHealthConfig(
        service_name="hydrology",
        health_check_tool="run_rainfall_runoff",
        health_check_args={"rainfall": [5.0, 10.0, 8.0], "catchment_area": 50},
        required=True
    ),
    "hipims": ServiceHealthConfig(
        service_name="hipims",
        health_check_tool="check_gpu_availability",
        health_check_args={},
        required=False
    ),
    "filesystem": ServiceHealthConfig(
        service_name="filesystem",
        health_check_tool="health_check",
        health_check_args={},
        required=True
    ),
    "document": ServiceHealthConfig(
        service_name="document",
        health_check_tool="health_check",
        health_check_args={},
        required=False
    ),
    "web_search": ServiceHealthConfig(
        service_name="web_search",
        health_check_tool="check_api_status",
        health_check_args={},
        required=False
    ),
    "yolo_vision": ServiceHealthConfig(
        service_name="yolo_vision",
        health_check_tool="get_model_info",
        health_check_args={},
        required=False
    ),
}


class MCPHealthCheckManager:
    """MCP 健康检查与初始化管理器
    
    功能：
    1. 启动时连接所有 MCP 服务
    2. 对每个服务执行真实健康检查
    3. 维护全局单例，后续调用无需重复初始化
    """

    _instance: Optional["MCPHealthCheckManager"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if MCPHealthCheckManager._initialized:
            return
        
        self.mcp_manager: Optional[MCPClientManager] = None
        self.health_results: Dict[str, HealthCheckResult] = {}
        self._initialized_at: Optional[datetime] = None
        self._lock = asyncio.Lock()
        
        MCPHealthCheckManager._initialized = True

    async def initialize(self, config_path: Optional[str] = None) -> Dict[str, HealthCheckResult]:
        """初始化 MCP 服务并执行健康检查
        
        Args:
            config_path: MCP 配置文件路径
            
        Returns:
            每个服务的健康检查结果
        """
        async with self._lock:
            if self.mcp_manager is not None:
                logger.info("MCP 服务已初始化，跳过重复初始化")
                return self.health_results
            
            logger.info("开始初始化 MCP 服务...")
            logger.info("正在创建 MCPClientManager...")
            
            if platform.system() == "Windows":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                logger.info("已设置 WindowsProactorEventLoopPolicy")
            
            try:
                self.mcp_manager = MCPClientManager(auto_load_config=True)
                logger.info(f"MCPClientManager 已创建，已注册 {len(self.mcp_manager.clients)} 个客户端")
            except Exception as e:
                logger.error(f"创建 MCPClientManager 失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                raise
            
            if config_path:
                base_path = Path(config_path).parent.parent
                sys_path = str(base_path / "src")
                if sys_path not in sys.path:
                    sys.path.insert(0, sys_path)
            
            logger.info("开始连接 MCP 服务...")
            try:
                connected = await self.mcp_manager.connect_all()
                logger.info(f"MCP 服务连接完成: {connected}/{len(self.mcp_manager.clients)} 个服务已连接")
            except Exception as e:
                logger.error(f"连接 MCP 服务失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                raise
            
            await self._run_health_checks()
            
            self._initialized_at = datetime.now()
            logger.info(f"MCP 初始化完成于 {self._initialized_at.isoformat()}")
            
            return self.health_results

    async def _run_health_checks(self):
        """对所有已连接的服务执行健康检查"""
        if not self.mcp_manager:
            return
        
        logger.info("开始执行健康检查...")
        
        health_tasks = []
        for service_name, config in SERVICE_HEALTH_CONFIGS.items():
            if service_name in self.mcp_manager.clients:
                health_tasks.append(
                    self._check_service_health(service_name, config)
                )
            else:
                logger.warning(f"服务 {service_name} 未在配置中找到，跳过健康检查")
        
        results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"健康检查异常: {result}")
        
        healthy_count = sum(1 for r in self.health_results.values() if r.healthy)
        total_count = len(self.health_results)
        
        logger.info(f"健康检查完成: {healthy_count}/{total_count} 个服务健康")

    async def _check_service_health(
        self,
        service_name: str,
        config: ServiceHealthConfig
    ) -> HealthCheckResult:
        """检查单个服务的健康状态
        
        Args:
            service_name: 服务名称
            config: 健康检查配置
            
        Returns:
            健康检查结果
        """
        try:
            client = self.mcp_manager.clients.get(service_name)
            if not client:
                result = HealthCheckResult(
                    service_name=service_name,
                    status="not_found",
                    healthy=False,
                    message=f"服务 {service_name} 未找到",
                )
                self.health_results[service_name] = result
                return result
            
            if not client.session or not client._connected:
                result = HealthCheckResult(
                    service_name=service_name,
                    status="disconnected",
                    healthy=False,
                    message=f"服务 {service_name} 未连接",
                )
                self.health_results[service_name] = result
                return result
            
            tool_name = config.health_check_tool
            tool_args = config.health_check_args
            
            logger.debug(f"正在执行健康检查: {service_name}.{tool_name}, 参数: {tool_args}")
            response = await client.call_tool(tool_name, tool_args)
            logger.debug(f"健康检查响应: {response}")
            
            is_healthy = response.get("success", False) if isinstance(response, dict) else False
            
            result = HealthCheckResult(
                service_name=service_name,
                status="healthy" if is_healthy else "unhealthy",
                healthy=is_healthy,
                message=f"健康检查{'成功' if is_healthy else '失败'}",
                details={
                    "tool": tool_name,
                    "args": tool_args,
                    "response": response
                }
            )
            
            self.health_results[service_name] = result
            
            status_str = "✓" if is_healthy else "✗"
            logger.info(f"  {status_str} {service_name}: {result.message}")
            
            return result
            
        except Exception as e:
            result = HealthCheckResult(
                service_name=service_name,
                status="error",
                healthy=False,
                message=f"健康检查失败: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__}
            )
            self.health_results[service_name] = result
            import traceback
            logger.error(f"  ✗ {service_name}: {result.message}")
            logger.error(f"详细堆栈:\n{traceback.format_exc()}")
            return result

    def get_health_status(self) -> Dict[str, Any]:
        """获取当前健康状态
        
        Returns:
            健康状态摘要
        """
        healthy_services = [name for name, r in self.health_results.items() if r.healthy]
        unhealthy_services = [name for name, r in self.health_results.items() if not r.healthy]
        
        return {
            "initialized": self._initialized_at is not None,
            "initialized_at": self._initialized_at.isoformat() if self._initialized_at else None,
            "total_services": len(self.health_results),
            "healthy_count": len(healthy_services),
            "unhealthy_count": len(unhealthy_services),
            "healthy_services": healthy_services,
            "unhealthy_services": unhealthy_services,
            "details": {
                name: {
                    "status": result.status,
                    "healthy": result.healthy,
                    "message": result.message,
                    "timestamp": result.timestamp
                }
                for name, result in self.health_results.items()
            }
        }

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用 MCP 工具（自动初始化）
        
        Args:
            server_name: 服务名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具调用结果
        """
        if not self.mcp_manager:
            await self.initialize()
        
        if server_name not in self.mcp_manager.clients:
            raise ValueError(f"未知的服务: {server_name}")
        
        client = self.mcp_manager.clients[server_name]
        
        if not client._connected:
            await client.connect()
        
        return await client.call_tool(tool_name, arguments)

    async def close(self):
        """关闭所有连接"""
        if self.mcp_manager:
            await self.mcp_manager.close_all()
            self.mcp_manager = None
            logger.info("MCP 服务连接已关闭")


async def get_mcp_health_manager() -> MCPHealthCheckManager:
    """获取 MCP 健康检查管理器的单例实例
    
    Returns:
        MCPHealthCheckManager 实例
    """
    return MCPHealthCheckManager()


async def initialize_mcp_services(config_path: Optional[str] = None) -> Dict[str, HealthCheckResult]:
    """便捷函数：初始化 MCP 服务并执行健康检查
    
    Args:
        config_path: MCP 配置文件路径
        
    Returns:
        健康检查结果
    """
    manager = await get_mcp_health_manager()
    return await manager.initialize(config_path)
