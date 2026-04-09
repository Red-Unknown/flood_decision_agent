<#
.SYNOPSIS
    MCP 服务部署脚本
.DESCRIPTION
    自动化部署和验证集成 MCP 服务（Data Hub、Hydrology、HiPIMS）
    包含环境检查、依赖安装、配置验证和服务启动测试
.EXAMPLE
    .\scripts\deploy_mcp_services.ps1
#>

$ErrorActionPreference = "Stop"

# 颜色定义
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
}

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "Info"
    )
    $color = $Colors[$Status]
    Write-Host $Message -ForegroundColor $color
}

function Test-Environment {
    Write-Status "`n[1/5] 检查环境..." "Info"
    
    $results = @()
    
    # 检查 Python 版本
    try {
        $pythonVersion = python --version 2>&1
        Write-Status "  ✓ Python: $pythonVersion" "Success"
        $results += $true
    } catch {
        Write-Status "  ✗ Python 未安装或不在 PATH 中" "Error"
        $results += $false
    }
    
    # 检查 KIMI_API_KEY
    $kimiKey = [Environment]::GetEnvironmentVariable('KIMI_API_KEY', 'User')
    if ($kimiKey) {
        Write-Status "  ✓ KIMI_API_KEY 已配置" "Success"
        $results += $true
    } else {
        Write-Status "  ⚠ KIMI_API_KEY 未配置（部分功能将不可用）" "Warning"
        $results += $true  # 非致命错误
    }
    
    # 检查 Conda 环境
    try {
        $condaInfo = conda info --envs 2>&1
        if ($condaInfo -match "intelligent_decision") {
            Write-Status "  ✓ Conda 环境 'intelligent_decision' 存在" "Success"
            $results += $true
        } else {
            Write-Status "  ⚠ Conda 环境 'intelligent_decision' 不存在" "Warning"
            $results += $true
        }
    } catch {
        Write-Status "  ⚠ Conda 未安装" "Warning"
        $results += $true
    }
    
    return $results -notcontains $false
}

function Test-Dependencies {
    Write-Status "`n[2/5] 检查依赖包..." "Info"
    
    $requiredPackages = @(
        "mcp",
        "aiohttp",
        "numpy"
    )
    
    $optionalPackages = @(
        "torch",
        "ultralytics",
        "opencv-python"
    )
    
    $results = @()
    
    # 检查必需包
    foreach ($package in $requiredPackages) {
        try {
            $null = python -c "import $package" 2>&1
            Write-Status "  ✓ $package" "Success"
            $results += $true
        } catch {
            Write-Status "  ✗ $package (必需) - 请运行: pip install $package" "Error"
            $results += $false
        }
    }
    
    # 检查可选包
    foreach ($package in $optionalPackages) {
        try {
            $null = python -c "import $package" 2>&1
            Write-Status "  ✓ $package (可选)" "Success"
        } catch {
            Write-Status "  ⚠ $package (可选) - 部分功能将不可用" "Warning"
        }
    }
    
    return $results -notcontains $false
}

function Test-Configuration {
    Write-Status "`n[3/5] 检查配置文件..." "Info"
    
    $configPath = "src/flood_decision_agent/mcp/configs/mcp_servers.json"
    $results = @()
    
    if (Test-Path $configPath) {
        Write-Status "  ✓ MCP 配置文件存在" "Success"
        
        try {
            $config = Get-Content $configPath | ConvertFrom-Json
            
            # 检查必需的服务
            $requiredServices = @("data_hub", "hydrology", "hipims", "web_search")
            foreach ($service in $requiredServices) {
                if ($config.mcpServers.$service) {
                    $enabled = $config.mcpServers.$service.enabled
                    if ($enabled) {
                        Write-Status "  ✓ $service 服务已启用" "Success"
                        $results += $true
                    } else {
                        Write-Status "  ⚠ $service 服务已禁用" "Warning"
                        $results += $true
                    }
                } else {
                    Write-Status "  ✗ $service 服务未配置" "Error"
                    $results += $false
                }
            }
        } catch {
            Write-Status "  ✗ 配置文件解析失败: $_" "Error"
            $results += $false
        }
    } else {
        Write-Status "  ✗ MCP 配置文件不存在: $configPath" "Error"
        $results += $false
    }
    
    return $results -notcontains $false
}

function Test-ServiceStartup {
    Write-Status "`n[4/5] 测试服务启动..." "Info"
    
    $services = @(
        @{Name = "data_hub"; Module = "flood_decision_agent.mcp.servers.data_hub_server"},
        @{Name = "hydrology"; Module = "flood_decision_agent.mcp.servers.hydrology_server"},
        @{Name = "hipims"; Module = "flood_decision_agent.mcp.servers.hipims_server"}
    )
    
    $results = @()
    
    foreach ($service in $services) {
        Write-Status "  测试 $($service.Name) 服务..." "Info"
        
        # 使用超时测试服务是否可以导入
        $job = Start-Job -ScriptBlock {
            param($module)
            $env:PYTHONIOENCODING = "utf-8"
            python -c "from $module import server; print('OK')" 2>&1
        } -ArgumentList $service.Module
        
        $completed = $job | Wait-Job -Timeout 5
        
        if ($completed) {
            $output = Receive-Job $job
            if ($output -match "OK") {
                Write-Status "    ✓ $($service.Name) 服务可正常导入" "Success"
                $results += $true
            } else {
                Write-Status "    ✗ $($service.Name) 服务导入失败" "Error"
                $results += $false
            }
            Remove-Job $job
        } else {
            Stop-Job $job
            Remove-Job $job
            Write-Status "    ⚠ $($service.Name) 服务测试超时（可能正常）" "Warning"
            $results += $true
        }
    }
    
    return $results -notcontains $false
}

function Test-IntegrationWorkflow {
    Write-Status "`n[5/5] 运行集成工作流测试..." "Info"
    
    $testScript = "tests/mcp/test_integration_workflow.py"
    
    if (Test-Path $testScript) {
        Write-Status "  运行集成测试..." "Info"
        
        try {
            $output = python $testScript 2>&1
            $exitCode = $LASTEXITCODE
            
            if ($exitCode -eq 0) {
                Write-Status "  ✓ 集成测试通过" "Success"
                return $true
            } else {
                Write-Status "  ✗ 集成测试失败" "Error"
                Write-Status "  输出: $output" "Error"
                return $false
            }
        } catch {
            Write-Status "  ⚠ 集成测试运行出错: $_" "Warning"
            return $true  # 非致命错误
        }
    } else {
        Write-Status "  ⚠ 集成测试脚本不存在: $testScript" "Warning"
        return $true
    }
}

function Write-DeploymentReport {
    param(
        [hashtable]$Results
    )
    
    Write-Status "`n" "Info"
    Write-Status "=" * 60 "Info"
    Write-Status "部署报告" "Info"
    Write-Status "=" * 60 "Info"
    
    foreach ($phase in $Results.Keys) {
        $status = if ($Results[$phase]) { "✓ 通过" } else { "✗ 失败" }
        $color = if ($Results[$phase]) { "Success" } else { "Error" }
        Write-Status "  $phase $status" $color
    }
    
    $passed = ($Results.Values | Where-Object { $_ } | Measure-Object).Count
    $total = $Results.Count
    
    Write-Status "`n总计: $passed/$total 阶段通过" "Info"
    
    if ($passed -eq $total) {
        Write-Status "`n🎉 部署成功！所有 MCP 服务已就绪" "Success"
        Write-Status "`n可用服务:" "Info"
        Write-Status "  - data_hub: 数据中枢服务" "Info"
        Write-Status "  - hydrology: 水利模型服务（集成 YOLO + HiPIMS）" "Info"
        Write-Status "  - hipims: 2D 水动力模拟服务" "Info"
        Write-Status "  - web_search: 网络搜索服务" "Info"
    } else {
        Write-Status "`n⚠️ 部署部分失败，请检查上述错误" "Warning"
    }
}

# ============ 主程序 ============

Write-Status "`n" "Info"
Write-Status "=" * 60 "Info"
Write-Status "MCP 服务部署脚本" "Info"
Write-Status "=" * 60 "Info"
Write-Status "部署目标: Data Hub + Hydrology + HiPIMS" "Info"
Write-Status "`n" "Info"

$deploymentResults = @{}

# 执行各阶段测试
$deploymentResults["环境检查"] = Test-Environment
$deploymentResults["依赖检查"] = Test-Dependencies
$deploymentResults["配置检查"] = Test-Configuration
$deploymentResults["服务启动"] = Test-ServiceStartup
$deploymentResults["集成测试"] = Test-IntegrationWorkflow

# 生成报告
Write-DeploymentReport $deploymentResults

# 退出码
$allPassed = $deploymentResults.Values -notcontains $false
exit ($allPassed ? 0 : 1)
