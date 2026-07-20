#!/bin/bash

# ========================================
#  英语学习平台 - 服务器部署脚本
# ========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
DEPLOY_DIR="/opt/english-learning"
BACKEND_IMAGE="english-learning-backend"
FRONTEND_IMAGE="english-learning-frontend"

# SSL 域名 (letsencrypt live dir → nginx ssl 同步)
# 7-20: 历史上 deploy/nginx/ssl 缺 fullchain.pem, 重起 nginx 时 502; 同步 letsencrypt 到 deploy dir 修复
# 格式: "letsencrypt_dir|nginx_ssl_subdir" — nginx.conf 引用路径决定 subdir 名
#   - nginx.conf L57 /etc/nginx/ssl/fullchain.pem → subdir="" (主域, 落顶层)
#   - nginx.conf L196 /etc/nginx/ssl/babyname/fullchain.pem → subdir="babyname"
SSL_DOMAINS=("fluenty.cn|" "api.babyname.asia|babyname")

echo ""
echo "========================================"
echo "  英语学习平台 - 服务器部署脚本"
echo "========================================"
echo ""

# 切换到部署目录
cd $DEPLOY_DIR

# 检查 .env 文件
echo -e "${YELLOW}[1/7] 检查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    echo "请先创建 .env 文件: cp deploy/prod.env .env"
    exit 1
fi
echo -e "${GREEN}完成: .env 配置文件检查通过${NC}"
echo ""

# 检查镜像文件
echo -e "${YELLOW}[2/7] 检查镜像文件...${NC}"
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

# 加载后端镜像
echo -e "${YELLOW}[3/7] 加载后端镜像...${NC}"
docker load -i ${BACKEND_IMAGE}.tar
echo -e "${GREEN}完成: 后端镜像加载成功${NC}"
echo ""

# 加载前端镜像
echo -e "${YELLOW}[4/8] 加载前端镜像...${NC}"
docker load -i ${FRONTEND_IMAGE}.tar
echo -e "${GREEN}完成: 前端镜像加载成功${NC}"
echo ""

# 同步 SSL 证书 (letsencrypt → nginx ssl dir)
echo -e "${YELLOW}[5/8] 同步 SSL 证书...${NC}"
for entry in "${SSL_DOMAINS[@]}"; do
  src_domain="${entry%|*}"
  dst_subdir="${entry#*|}"
  src="/etc/letsencrypt/live/$src_domain"
  dst="$DEPLOY_DIR/deploy/nginx/ssl/${dst_subdir}"
  if [ -f "$src/fullchain.pem" ] && [ -f "$src/privkey.pem" ]; then
    mkdir -p "$dst"
    cp "$src/fullchain.pem" "$dst/"
    cp "$src/privkey.pem" "$dst/"
    echo "  $src_domain → ssl/${dst_subdir}: synced"
  else
    echo -e "${RED}  $src_domain: 跳过 (letsencrypt 缺证书: $src)${NC}"
  fi
done
echo ""

# 停止旧服务
echo -e "${YELLOW}[6/8] 停止旧服务...${NC}"
docker-compose down
echo ""

# 启动新服务
echo -e "${YELLOW}[7/8] 启动服务...${NC}"
docker-compose up -d
echo -e "${GREEN}完成: 服务启动成功${NC}"
echo ""

# 检查服务状态
echo -e "${YELLOW}[8/8] 检查服务状态...${NC}"
sleep 8
docker-compose ps
echo ""

# 健康检查
echo ""
echo -e "${YELLOW}健康检查...${NC}"
sleep 3
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}后端服务: 正常${NC}"
else
    echo -e "${RED}后端服务: 异常，请检查日志: docker-compose logs backend${NC}"
fi

if curl -sf http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}前端服务: 正常${NC}"
else
    echo -e "${RED}前端服务: 异常，请检查日志: docker-compose logs frontend${NC}"
fi

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "  访问地址:"
echo "  - 主站: https://fluenty.cn"
echo "  - API文档: http://localhost:8000/docs"
echo ""
echo "  常用命令:"
echo "  - 查看所有日志: docker-compose logs -f"
echo "  - 查看后端日志: docker-compose logs -f backend"
echo "  - 查看前端日志: docker-compose logs -f frontend"
echo "  - 重启服务: docker-compose restart"
echo "  - 停止服务: docker-compose down"
echo "  - 重建服务: docker-compose up -d --force-recreate"
echo ""
echo "========================================"