#!/bin/bash

echo "========================================"
echo "  英语口语学习 API - 启动脚本"
echo "========================================"
echo

cd "$(dirname "$0")"

echo "[1/2] 检查虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

echo "[2/2] 激活虚拟环境并安装依赖..."
source .venv/bin/activate
pip install -r requirements.txt -q

echo
echo "========================================"
echo "  启动服务..."
echo "========================================"
echo "  API 文档: http://localhost:8000/docs"
echo "  健康检查: http://localhost:8000/health"
echo "========================================"
echo

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
