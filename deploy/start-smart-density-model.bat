@echo off
setlocal

set "MODEL_ROOT=D:\金海泽地\代码\管控平台\python-services\smart-density"
set "MODEL_PORT=6789"
set "MODEL_HOST=0.0.0.0"
set "PYTHON_BIN=python"

if not exist "%MODEL_ROOT%\main.py" (
  echo [ERROR] 未找到智能密控服务入口: %MODEL_ROOT%\main.py
  exit /b 1
)

echo [INFO] 启动智能密控模型服务
echo [INFO] 路径: %MODEL_ROOT%
echo [INFO] 地址: http://%MODEL_HOST%:%MODEL_PORT%

pushd "%MODEL_ROOT%"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
%PYTHON_BIN% -c "from pathlib import Path; p=Path('cfg/console.yaml'); s=p.read_text(encoding='utf-8', errors='ignore'); s=s.replace('host: 127.0.0.1','host: %MODEL_HOST%').replace('host: localhost','host: %MODEL_HOST%'); import re; s=re.sub(r'port:\\s*\\d+','port: %MODEL_PORT%',s); p.write_text(s,encoding='utf-8')"
%PYTHON_BIN% main.py
popd

endlocal
