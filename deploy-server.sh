#!/bin/bash

# ========================================
#  英语学习平台 - 服务器部署脚本
# ========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
DEPLOY_DIR="/opt/english-learning"
BACKEND_IMAGE="english-learning-backend"
FRONTEND_IMAGE="english-learning-frontend"

echo ""
echo "========================================"
echo "  英语学习平台 - 服务器部署脚本"
echo "========================================"
echo ""

# 切换到部署目录
cd $DEPLOY_DIR

# 检查镜像文件是否存在
echo -e "${YELLOW}[1/5] 检查镜像文件...${NC}"
if [ ! -f "${BACKEND_IMAGE}.tar" ]; then
    echo -e "${RED}错误: 找不到 ${BACKEND_IMAGE}.tar${NC}"
    exit 1
fi
if [ ! -f "${FRONTEND_IMAGE}.tar" ]; then
    echo -e "${RED}错误: 找不到 ${FRONTEND_IMAGE}.tar${NC}"
    exit 1
fi
echo -e "${GREEN}完成: 镜像文件检查通过${NC}"
echo ""

# 加载镜像
echo -e "${YELLOW}[2/5] 加载后端镜像...${NC}"
docker load -i ${BACKEND_IMAGE}.tar
echo -e "${GREEN}完成: 后端镜像加载成功${NC}"
echo ""

echo -e "${YELLOW}[3/5] 加载前端镜像...${NC}"
docker load -i ${FRONTEND_IMAGE}.tar
echo -e "${GREEN}完成: 前端镜像加载成功${NC}"
echo ""

# 停止旧服务
echo -e "${YELLOW}[4/5] 重启服务...${NC}"
docker-compose down
echo ""

# 启动新服务
docker-compose up -d
echo -e "${GREEN}完成: 服务启动成功${NC}"
echo ""

# 检查服务状态
echo -e "${YELLOW}[5/5] 检查服务状态...${NC}"
sleep 5
docker-compose ps
echo ""

# 健康检查
echo -e "${YELLOW}健康检查...${NC}"
sleep 3
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}后端服务: 正常${NC}"
else
    echo -e "${RED}后端服务: 异常${NC}"
fi

if curl -s http://localhost:80 > /dev/null; then
    echo -e "${GREEN}前端服务: 正常${NC}"
else
    echo -e "${RED}前端服务: 异常${NC}"
fi

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "  访问地址:"
echo "  - 前端: http://$(hostname -I | awk '{print $1}')"
echo "  - API文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "  常用命令:"
echo "  - 查看日志: docker-compose logs -f"
echo "  - 重启服务: docker-compose restart"
echo "  - 停止服务: docker-compose down"
echo ""
echo "========================================"
