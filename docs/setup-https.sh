#!/bin/bash

# ========================================
#  HTTPS 配置脚本 - 阿里云服务器
# ========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DEPLOY_DIR="/opt/english-learning"

echo ""
echo "========================================"
echo "  HTTPS 配置脚本"
echo "========================================"
echo ""

# 获取域名
read -p "请输入你的域名 (例如: example.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}错误: 域名不能为空${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}域名: $DOMAIN${NC}"
echo -e "${YELLOW}请确认域名已解析到本服务器 (101.37.181.33)${NC}"
read -p "确认继续? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "已取消"
    exit 0
fi

cd $DEPLOY_DIR

# 1. 安装 certbot
echo ""
echo -e "${YELLOW}[1/5] 安装 certbot...${NC}"
apt update
apt install certbot -y
echo -e "${GREEN}完成${NC}"

# 2. 停止 80 端口服务
echo ""
echo -e "${YELLOW}[2/5] 停止前端服务...${NC}"
docker-compose stop frontend nginx 2>/dev/null || true
echo -e "${GREEN}完成${NC}"

# 3. 申请 SSL 证书
echo ""
echo -e "${YELLOW}[3/5] 申请 SSL 证书...${NC}"
echo "请按提示输入邮箱并同意条款"
certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN

# 4. 复制证书
echo ""
echo -e "${YELLOW}[4/5] 复制证书文件...${NC}"
mkdir -p $DEPLOY_DIR/deploy/nginx/ssl
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $DEPLOY_DIR/deploy/nginx/ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $DEPLOY_DIR/deploy/nginx/ssl/
echo -e "${GREEN}完成${NC}"

# 5. 生成 nginx 配置
echo ""
echo -e "${YELLOW}[5/5] 生成 nginx 配置...${NC}"

cat > $DEPLOY_DIR/deploy/nginx/nginx.conf << EOF
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

# HTTPS 服务
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /video {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Range \$http_range;
        proxy_set_header If-Range \$http_if_range;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /static {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/x-javascript application/xml application/json;
    gzip_comp_level 6;
}
EOF

# 创建 certbot 验证目录
mkdir -p /var/www/certbot

echo -e "${GREEN}完成${NC}"

# 6. 重启服务
echo ""
echo -e "${YELLOW}重启服务...${NC}"
docker-compose down
docker-compose up -d

echo ""
echo "========================================"
echo -e "${GREEN}  HTTPS 配置完成！${NC}"
echo "========================================"
echo ""
echo "  访问地址:"
echo "  - https://$DOMAIN"
echo "  - https://www.$DOMAIN"
echo ""
echo "  证书有效期: 90天"
echo "  自动续期命令: certbot renew"
echo ""
echo "========================================"

# 7. 设置自动续期
echo ""
read -p "是否设置证书自动续期? (y/n): " AUTO_RENEW

if [ "$AUTO_RENEW" = "y" ]; then
    # 添加 crontab 任务
    (crontab -l 2>/dev/null; echo "0 3 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/*.pem $DEPLOY_DIR/deploy/nginx/ssl/ && cd $DEPLOY_DIR && docker-compose restart nginx") | crontab -
    echo -e "${GREEN}已设置每月自动续期${NC}"
fi

echo ""
echo "配置完成！请访问 https://$DOMAIN 测试"
