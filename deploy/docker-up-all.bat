@echo off
setlocal

powershell -ExecutionPolicy Bypass -File "%~dp0docker-up-all.ps1"

if errorlevel 1 (
  echo.
  echo [ERROR] Docker 一键启动失败
  exit /b 1
)

exit /b 0
