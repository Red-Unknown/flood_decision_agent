# 水利智脑 Web服务启动脚本 (Windows)
# 一键启动前后端服务

param(
    [int]$Port = 8000,
    [switch]$SkipBuild,
    [switch]$DevMode
)

$ErrorActionPreference = "Stop"

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WebDir = Split-Path -Parent $ScriptDir
$ProjectRoot = Split-Path -Parent $WebDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  水利智脑 Web服务启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查KIMI_API_KEY
if (-not $env:KIMI_API_KEY) {
    Write-Host "✗ KIMI_API_KEY 环境变量未设置" -ForegroundColor Red
    Write-Host "  请先设置: `$env:KIMI_API_KEY='your-api-key'" -ForegroundColor Yellow
    exit 1
}

# 检查端口是否可用
function Test-PortAvailable {
    param([int]$Port)
    $listener = $null
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $Port)
        $listener.Start()
        return $true
    } catch {
        return $false
    } finally {
        if ($listener) {
            $listener.Stop()
        }
    }
}

# 查找可用端口
$AvailablePort = $Port
while ($AvailablePort -le 8010) {
    if (Test-PortAvailable -Port $AvailablePort) {
        break
    }
    $AvailablePort++
}

if ($AvailablePort -gt 8010) {
    Write-Host "✗ 端口 8000-8010 均被占用，请手动指定端口" -ForegroundColor Red
    exit 1
}

if ($AvailablePort -ne $Port) {
    Write-Host "⚠ 端口 $Port 被占用，使用端口 $AvailablePort" -ForegroundColor Yellow
}

# 检查Node.js
try {
    $NodeVersion = node --version
    Write-Host "✓ Node.js版本: $NodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js未安装，请先安装Node.js 18+" -ForegroundColor Red
    exit 1
}

# 安装前端依赖
$FrontendDir = Join-Path $WebDir "frontend"
Set-Location $FrontendDir

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    Write-Host "`n正在安装前端依赖..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ 前端依赖安装失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ 前端依赖安装完成" -ForegroundColor Green
}

# 构建前端
if (-not $SkipBuild -and -not $DevMode) {
    Write-Host "`n正在构建前端..." -ForegroundColor Cyan
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ 前端构建失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ 前端构建完成" -ForegroundColor Green
}

# 检查Python依赖
Write-Host "`n检查Python依赖..." -ForegroundColor Cyan
Set-Location $ProjectRoot

try {
    python -c "import fastapi, uvicorn" 2>$null
    Write-Host "✓ Python依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "⚠ 缺少Python依赖，尝试安装..." -ForegroundColor Yellow
    pip install fastapi uvicorn
}

# 启动服务
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  启动Web服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务地址:" -ForegroundColor Yellow
Write-Host "  - Web界面: http://localhost:$AvailablePort" -ForegroundColor White
Write-Host "  - API文档: http://localhost:$AvailablePort/docs" -ForegroundColor White
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

# 设置环境变量并启动
$env:PORT = $AvailablePort

# 启动浏览器
Start-Process "http://localhost:$AvailablePort"

# 启动后端服务
python -m web.backend.main
