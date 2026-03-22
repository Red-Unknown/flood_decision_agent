$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$conda = Get-Command conda -ErrorAction SilentlyContinue
if (-not $conda) {
  Write-Host "未找到 conda，请先安装 Anaconda/Miniconda 并确保 conda 在 PATH 中"
  exit 1
}

$envName = "intelligent_decision"
$pythonVersion = "3.11"

$envExists = (conda env list | Select-String -Pattern "^\s*$envName\s") -ne $null
if (-not $envExists) {
  conda create -n $envName "python=$pythonVersion" -y
}

conda run -n $envName python -m pip install --upgrade pip
conda run -n $envName python -m pip install -r requirements.txt
conda run -n $envName python -m pip install -e .
conda run -n $envName pre-commit install

conda env export -n $envName --no-builds | Out-File -FilePath environment.yml -Encoding utf8

Write-Host "环境已就绪：$envName"
