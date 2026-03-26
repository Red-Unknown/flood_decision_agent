"""FastAPI Web服务入口.

提供Web端AI工作流服务，支持RESTful API和WebSocket通信。
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from web.backend.api.chat import router as chat_router
from web.backend.api.conversations import router as conversations_router
from web.backend.websocket.chat_ws import router as ws_router


def check_kimi_api_key() -> None:
    """检查KIMI_API_KEY环境变量."""
    if not os.getenv("KIMI_API_KEY", "").strip():
        print("需要kimi_api_key")
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理."""
    # 启动时检查
    check_kimi_api_key()
    print("✓ KIMI_API_KEY 已配置")
    print("✓ Web服务启动成功")
    yield
    # 关闭时清理
    print("✓ Web服务已关闭")


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
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "水利智脑 Web服务",
    }


# 注册API路由（必须在静态文件之前注册）
app.include_router(chat_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(ws_router)

# 挂载静态文件（前端构建产物）
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
