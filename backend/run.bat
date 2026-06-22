@echo off
echo ========================================
echo   英语口语学习 API - 启动脚本
echo ========================================
echo.

cd /d %~dp0

echo [1/2] 检查虚拟环境...
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)

echo [2/2] 激活虚拟环境并安装依赖...
call .venv\Scripts\activate
pip install -r requirements.txt -q

echo.
echo ========================================
echo   启动服务...
echo ========================================
echo   API 文档: http://localhost:8001/docs
echo   健康检查: http://localhost:8001/health
echo ========================================
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
