$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$envFile = Join-Path $rootDir ".env.docker"
$envExample = Join-Path $rootDir ".env.docker.example"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "未找到 docker 命令，请先安装 Docker Desktop 或 Docker Engine。"
}

if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
    Write-Host "已生成 .env.docker，请先检查账号、密码和现场地址配置：" -ForegroundColor Yellow
    Write-Host "  $envFile" -ForegroundColor Yellow
}

Push-Location $rootDir
try {
    $env:SMART_DENSITY_ENABLED = "true"
    $env:SMART_DENSITY_BASE_URL = "http://smart-density:6789"
    $env:SMART_REAGENT_ENABLED = "true"
    $env:SMART_REAGENT_BASE_URL = "http://smart-reagent:6788"
    if (-not $env:SMART_DENSITY_RHO_SOURCE) {
        $env:SMART_DENSITY_RHO_SOURCE = "param"
    }
    if (-not $env:SMART_DENSITY_DB_HOST) {
        $env:SMART_DENSITY_DB_HOST = "smart-density-mysql"
    }

    docker compose --env-file .env.docker --profile models up -d --build
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose 启动失败"
    }

    Write-Host ""
    Write-Host "容器已启动，当前状态：" -ForegroundColor Green
    docker compose ps
    Write-Host ""
    Write-Host "访问地址：" -ForegroundColor Green
    Write-Host "  前端: http://localhost" -ForegroundColor Green
    Write-Host "  后端: http://localhost:8080" -ForegroundColor Green
    Write-Host ""
    Write-Host "如需查看日志：" -ForegroundColor Green
    Write-Host "  docker compose logs -f server" -ForegroundColor Green
    Write-Host "  docker compose logs -f smart-density" -ForegroundColor Green
    Write-Host "  docker compose logs -f smart-reagent" -ForegroundColor Green
}
finally {
    Pop-Location
}
