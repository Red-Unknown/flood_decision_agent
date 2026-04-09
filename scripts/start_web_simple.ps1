﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿# Start Web Services Script - Simple Version
# 功能：
# 1. 自动获取环境变量中的API_KEY
# 2. 查询后端8001端口是否占用，占用则停止并重启后端
# 3. 前端3001端口是否被占用，占用则停止并重启前端

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Water Resources AI - Web Service Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$backendPort = 8001
$frontendPort = 3001

# 1. 自动获取环境变量中的API_KEY
Write-Host ""
Write-Host "Checking KIMI_API_KEY..."
$apiKey = $env:KIMI_API_KEY

if ([string]::IsNullOrWhiteSpace($apiKey) -or $apiKey -eq "test-key") {
    Write-Host "[WARN] KIMI_API_KEY not set or invalid" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please enter your KIMI API Key:" -ForegroundColor Cyan
    $apiKey = Read-Host -AsSecureString "KIMI API Key"
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
    $apiKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
    
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        Write-Host "[ERROR] API Key is required" -ForegroundColor Red
        exit 1
    }
    
    $env:KIMI_API_KEY = $apiKey
    Write-Host "[OK] API Key configured" -ForegroundColor Green
} else {
    Write-Host "[OK] KIMI_API_KEY is set" -ForegroundColor Green
}

# 2. 检查并释放后端8001端口
Write-Host ""
Write-Host "Checking backend port $backendPort..."
$backendConnection = netstat -ano | Select-String ":$backendPort"
if ($backendConnection) {
    Write-Host "[WARN] Port $backendPort is in use" -ForegroundColor Yellow
    $backendPid = ($backendConnection -split '\s+')[-1]
    Write-Host "[INFO] Found process using port $backendPort, PID: $backendPid" -ForegroundColor Cyan
    try {
        Stop-Process -Id $backendPid -Force -ErrorAction Stop
        Write-Host "[OK] Stopped process PID: $backendPid" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "[ERROR] Failed to stop process: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Port $backendPort is available" -ForegroundColor Green
}

# 3. 检查并释放前端3001端口
Write-Host ""
Write-Host "Checking frontend port $frontendPort..."
$frontendConnection = netstat -ano | Select-String ":$frontendPort"
if ($frontendConnection) {
    Write-Host "[WARN] Port $frontendPort is in use" -ForegroundColor Yellow
    $frontendPid = ($frontendConnection -split '\s+')[-1]
    Write-Host "[INFO] Found process using port $frontendPort, PID: $frontendPid" -ForegroundColor Cyan
    try {
        Stop-Process -Id $frontendPid -Force -ErrorAction Stop
        Write-Host "[OK] Stopped process PID: $frontendPid" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "[ERROR] Failed to stop process: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Port $frontendPort is available" -ForegroundColor Green
}

# 更新前端配置
Write-Host ""
Write-Host "Updating frontend WebSocket config..."
$websocketJsPath = Join-Path $ProjectRoot "web\frontend\src\services\websocket.js"
if (Test-Path $websocketJsPath) {
    $content = Get-Content $websocketJsPath -Raw -Encoding UTF8
    $content = $content -replace "ws://localhost:\d+", "ws://localhost:$backendPort"
    Set-Content $websocketJsPath $content -Encoding UTF8 -NoNewline
    Write-Host "[OK] WebSocket config updated to port $backendPort" -ForegroundColor Green
}

$viteConfigPath = Join-Path $ProjectRoot "web\frontend\vite.config.js"
if (Test-Path $viteConfigPath) {
    $content = Get-Content $viteConfigPath -Raw -Encoding UTF8
    $content = $content -replace "target:\s*'http://localhost:\d+'", "target: 'http://localhost:$backendPort'"
    $content = $content -replace "target:\s*'ws://localhost:\d+'", "target: 'ws://localhost:$backendPort'"
    Set-Content $viteConfigPath $content -Encoding UTF8 -NoNewline
    Write-Host "[OK] Vite proxy config updated to port $backendPort" -ForegroundColor Green
}

# 启动后端服务
Write-Host ""
Write-Host "Starting backend service on port $backendPort..."
$backendDir = $ProjectRoot
$env:KIMI_API_KEY = $apiKey
$env:PORT = $backendPort
$backendProcess = Start-Process python -ArgumentList "-m", "web.backend.main" -WorkingDirectory $backendDir -WindowStyle Hidden -PassThru
Write-Host "[OK] Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green

Write-Host "Waiting for backend ready..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $client = [System.Net.Sockets.TcpClient]::new()
        $client.Connect("localhost", $backendPort)
        $client.Close()
        $ready = $true
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}
if ($ready) {
    Write-Host "[OK] Backend ready: http://localhost:$backendPort" -ForegroundColor Green
} else {
    Write-Host "[WARN] Backend timeout" -ForegroundColor Yellow
}

# 启动前端服务
Write-Host ""
Write-Host "Starting frontend service on port $frontendPort..."
$frontendDir = Join-Path $ProjectRoot "web\frontend"
$env:PORT = $frontendPort
$frontendProcess = Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory $frontendDir -WindowStyle Hidden -PassThru
Write-Host "[OK] Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green

Write-Host "Waiting for frontend ready..."
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $client = [System.Net.Sockets.TcpClient]::new()
        $client.Connect("localhost", $frontendPort)
        $client.Close()
        $ready = $true
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}
if ($ready) {
    Write-Host "[OK] Frontend ready: http://localhost:$frontendPort" -ForegroundColor Green
} else {
    Write-Host "[WARN] Frontend timeout" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# 显示服务信息
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Services started successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:$frontendPort" -ForegroundColor Yellow
Write-Host "Backend:  http://localhost:$backendPort" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:$backendPort/docs" -ForegroundColor Yellow
Write-Host "WebSocket: ws://localhost:$backendPort/ws/chat/{conversation_id}" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 保存PID信息
$pidInfo = @{
    backend_pid = $backendProcess.Id
    frontend_pid = $frontendProcess.Id
    backend_port = $backendPort
    frontend_port = $frontendPort
    start_time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
} | ConvertTo-Json

$pidFile = Join-Path $ScriptDir ".web_pids.json"
Set-Content $pidFile $pidInfo -Encoding UTF8
Write-Host ""
Write-Host "[INFO] PID info saved to: $pidFile"

# 监控进程
Write-Host ""
Write-Host "Monitoring services... (Press Ctrl+C to stop)" -ForegroundColor Cyan

for ($i = 0; $i -lt 999999; $i++) {
    Start-Sleep -Seconds 2
    if ($backendProcess.HasExited) {
        Write-Host ""
        Write-Host "[WARN] Backend stopped (exit code: $($backendProcess.ExitCode))" -ForegroundColor Yellow
        break
    }
    if ($frontendProcess.HasExited) {
        Write-Host ""
        Write-Host "[WARN] Frontend stopped (exit code: $($frontendProcess.ExitCode))" -ForegroundColor Yellow
        break
    }
}

# 清理
Write-Host ""
Write-Host "Stopping services..." -ForegroundColor Cyan

if (-not $backendProcess.HasExited) {
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Backend stopped" -ForegroundColor Green
}

if (-not $frontendProcess.HasExited) {
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Frontend stopped" -ForegroundColor Green
}

if (Test-Path $pidFile) { 
    Remove-Item $pidFile -Force 
}

Write-Host "[OK] All services stopped" -ForegroundColor Green
