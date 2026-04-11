"""FastAPI Web服务入口.

提供Web端AI工作流服务，支持RESTful API和WebSocket通信。
"""

from __future__ import annotations

import os
import sys
import io
import platform
import re
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import date
from pathlib import Path

_original_stderr = sys.__stderr__

class AsyncGenErrorFilter(io.TextIOBase):
    """过滤异步生成器关闭时的错误输出（Windows兼容）"""
    
    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._buffer = ""
        self._filter_patterns = [
            "async_generator",
            "error occurred during closing",
            "Attempted to exit cancel scope",
            "RuntimeError: Attempted to exit cancel scope",
            "stdio_client",
            "cancel scope in a different task",
        ]
    
    def write(self, s):
        if not s:
            return 0
        self._buffer += s
        if "\n" in self._buffer:
            lines = self._buffer.split("\n")
            self._buffer = lines[-1]
            full_text = "\n".join(lines[:-1])
            if any(p in full_text for p in self._filter_patterns):
                return len(s)
        return self._wrapped.write(s)
    
    def flush(self):
        if self._buffer and any(p in self._buffer for p in self._filter_patterns):
            self._buffer = ""
        return self._wrapped.flush()
    
    @property
    def encoding(self):
        return self._wrapped.encoding
    
    @property
    def mode(self):
        return self._wrapped.mode
    
    @property
    def name(self):
        return self._wrapped.name

original_stderr = sys.stderr
filtered_stderr = AsyncGenErrorFilter(original_stderr)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(filtered_stderr, encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from loguru import logger

LOG_DIR = Path("f:/college/sophomore/academic/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

from flood_decision_agent.infrastructure.logging import CONSOLE_FORMAT, FILE_FORMAT

logger.remove()
logger.add(
    sink=str(LOG_DIR / f"web-{date.today().isoformat()}.log"),
    level="DEBUG",
    format=FILE_FORMAT,
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
)
logger.add(
    sink=sys.stdout,
    level="DEBUG",
    format=CONSOLE_FORMAT,
    backtrace=True,
    diagnose=True,
)

import logging
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("anyio").setLevel(logging.WARNING)
logging.getLogger("mcp").setLevel(logging.WARNING)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from web.backend.api.chat import router as chat_router
from web.backend.api.conversations import router as conversations_router
from web.backend.api.mode import router as mode_router
from web.backend.api.data_acquisition import router as data_acquisition_router
from web.backend.api.plans import router as plans_router
from web.backend.api.specs import router as specs_router
from web.backend.api.sessions import router as sessions_router
from web.backend.api.chain_generation import router as chain_generation_router
from web.backend.websocket.chat_ws import router as ws_router


def check_kimi_api_key() -> None:
    """检查KIMI_API_KEY环境变量."""
    from flood_decision_agent.infrastructure.config_loader import get_api_key
    try:
        get_api_key("KIMI_API_KEY")
    except ValueError:
        logger.critical("需要kimi_api_key")
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理."""
    from flood_decision_agent.mcp.clients import initialize_mcp_services
    import asyncio
    
    # 启动时检查
    check_kimi_api_key()
    logger.info("[OK] KIMI_API_KEY 已配置")
    
    # 创建停止事件
    stop_event = asyncio.Event()
    app.state.stop_event = stop_event
    
    # 启动后台任务等待停止信号
    async def wait_for_shutdown():
        try:
            await stop_event.wait()
        except asyncio.CancelledError:
            pass
    
    # 在 yield 之前启动后台任务
    shutdown_task = asyncio.create_task(wait_for_shutdown())
    
    # 启动 MCP 服务（在后台任务之后启动）
    logger.info("[INFO] 正在初始化 MCP 服务...")
    try:
        health_results = await initialize_mcp_services()
        healthy_count = sum(1 for r in health_results.values() if r.healthy)
        total_count = len(health_results)
        logger.info(f"[OK] MCP 服务初始化完成: {healthy_count}/{total_count} 个服务健康")
        
        for name, result in health_results.items():
            status_icon = "✓" if result.healthy else "✗"
            logger.info(f"  {status_icon} {name}: {result.message}")
    except Exception as e:
        logger.warning(f"[WARN] MCP 服务初始化部分失败: {e}")
        import traceback
        logger.warning(f"[WARN] 详细堆栈: {traceback.format_exc()}")
    
    logger.info("[OK] Web服务启动成功")
    
    yield  # 应用运行中
    
    # 设置停止事件
    stop_event.set()
    
    # 等待后台任务完成
    await shutdown_task
    
    # 关闭时清理 MCP 服务
    from flood_decision_agent.mcp.clients import get_mcp_health_manager
    try:
        mcp_manager = get_mcp_health_manager()
        await mcp_manager.close()
        logger.info("[OK] MCP 服务已关闭")
    except Exception as e:
        logger.warning(f"[WARN] 关闭 MCP 服务时出错: {e}")
    
    logger.info("[OK] Web服务已关闭")


app = FastAPI(
    title="水利智脑 Web服务",
    description="AI工作流Web端服务",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> dict:
    """健康检查接口.

    Returns:
        服务状态信息
    """
    from flood_decision_agent.mcp.clients import get_mcp_health_manager
    
    mcp_status = {}
    try:
        mcp_manager = get_mcp_health_manager()
        mcp_status = mcp_manager.get_health_status()
    except Exception:
        pass
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "水利智脑 Web服务",
        "mcp_services": mcp_status
    }


# 注册API路由（必须在静态文件之前注册）
app.include_router(chat_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(mode_router, prefix="/api")
app.include_router(data_acquisition_router)
app.include_router(plans_router, prefix="/api")
app.include_router(specs_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(chain_generation_router, prefix="/api")
app.include_router(ws_router)

# 挂载静态文件（前端构建产物）
# 注意：静态文件挂载在根路径会拦截所有请求，包括WebSocket
# 解决方案：只在存在静态文件目录且不是开发环境时挂载
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir) and os.getenv("DEV_MODE") != "1":
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("web.backend.main:app", host="127.0.0.1", port=port)
