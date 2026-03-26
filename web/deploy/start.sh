#!/bin/bash

# 水利智脑 Web服务启动脚本 (Linux/Mac)
# 一键启动前后端服务

set -e

PORT=8000
SKIP_BUILD=false
DEV_MODE=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$WEB_DIR")"

echo "========================================"
echo "  水利智脑 Web服务启动脚本"
echo "========================================"
echo ""

# 检查KIMI_API_KEY
if [ -z "$KIMI_API_KEY" ]; then
    echo "✗ KIMI_API_KEY 环境变量未设置"
    echo "  请先设置: export KIMI_API_KEY='your-api-key'"
    exit 1
fi

# 检查端口是否可用
find_available_port() {
    local start_port=$1
    local max_port=8010
    local port=$start_port

    while [ $port -le $max_port ]; do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $port
            return
        fi
        ((port++))
    done
    echo -1
}

AVAILABLE_PORT=$(find_available_port $PORT)

if [ "$AVAILABLE_PORT" -eq -1 ]; then
    echo "✗ 端口 8000-8010 均被占用，请手动指定端口"
    exit 1
fi

if [ "$AVAILABLE_PORT" -ne "$PORT" ]; then
    echo "⚠ 端口 $PORT 被占用，使用端口 $AVAILABLE_PORT"
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "✗ Node.js未安装，请先安装Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js版本: $NODE_VERSION"

# 安装前端依赖
FRONTEND_DIR="$WEB_DIR/frontend"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo ""
    echo "正在安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "✗ 前端依赖安装失败"
        exit 1
    fi
    echo "✓ 前端依赖安装完成"
fi

# 构建前端
if [ "$SKIP_BUILD" = false ] && [ "$DEV_MODE" = false ]; then
    echo ""
    echo "正在构建前端..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "✗ 前端构建失败"
        exit 1
    fi
    echo "✓ 前端构建完成"
fi

# 检查Python依赖
echo ""
echo "检查Python依赖..."
cd "$PROJECT_ROOT"

if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "✓ Python依赖已安装"
else
    echo "⚠ 缺少Python依赖，尝试安装..."
    pip install fastapi uvicorn
fi

# 启动服务
echo ""
echo "========================================"
echo "  启动Web服务"
echo "========================================"
echo ""
echo "服务地址:"
echo "  - Web界面: http://localhost:$AVAILABLE_PORT"
echo "  - API文档: http://localhost:$AVAILABLE_PORT/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 设置环境变量并启动
export PORT=$AVAILABLE_PORT

# 启动后端服务
python -m web.backend.main
