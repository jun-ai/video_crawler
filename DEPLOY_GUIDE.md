# 英语学习平台 - 生产环境部署指南

> 基于本地打包镜像上传服务器的方式部署

---

## 目录

- [一、服务器环境要求](#一服务器环境要求)
- [二、本地打包镜像](#二本地打包镜像)
- [三、上传文件到服务器](#三上传文件到服务器)
- [四、服务器部署流程](#四服务器部署流程)
- [五、验证部署](#五验证部署)
- [六、日常运维](#六日常运维)
- [七、更新部署](#七更新部署)
- [八、常见问题](#八常见问题)

---

## 一、服务器环境要求

### 1.1 硬件配置

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核 | 4核 |
| 内存 | 4GB | 8GB |
| 硬盘 | 50GB | 100GB |
| 带宽 | 5Mbps | 10Mbps+ |

### 1.2 软件环境

| 软件 | 版本要求 |
|------|----------|
| 操作系统 | Ubuntu 20.04 / CentOS 7+ / Debian 10+ |
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

### 1.3 安装 Docker 环境

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 启动 Docker 并设置开机自启
systemctl start docker
systemctl enable docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

---

## 二、本地打包镜像

### 2.1 项目目录结构

```
video_crawler/
├── backend/                    # 后端代码
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # 前端代码
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── deploy/                     # 部署配置
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── frontend.conf
│   └── mysql/
│       └── my.cnf
├── data/                       # 数据目录
│   └── materials/
├── docker-compose.yml
└── .env                        # 环境变量配置
```

### 2.2 构建镜像

在项目根目录执行：

```bash
# Windows (PowerShell)
cd D:\PythonTools\PythonProject\video_crawler

# 构建所有镜像
docker-compose build

# 或者单独构建
docker build -t english-learning-backend:latest ./backend
docker build -t english-learning-frontend:latest ./frontend
```

### 2.3 导出镜像文件

```bash
# 导出后端镜像
docker save -o english-learning-backend.tar english-learning-backend:latest

# 导出前端镜像
docker save -o english-learning-frontend.tar english-learning-frontend:latest

# 查看导出的文件
ls -lh *.tar
```

### 2.4 准备部署文件

需要上传到服务器的文件：

| 文件/目录 | 必须 | 说明 |
|-----------|------|------|
| `docker-compose.yml` | ✅ | Docker 编排配置 |
| `.env` | ✅ | 环境变量配置 |
| `english-learning-backend.tar` | ✅ | 后端镜像文件 |
| `english-learning-frontend.tar` | ✅ | 前端镜像文件 |
| `deploy/` | ✅ | 部署配置目录 |
| `data/` | ⚠️ | 数据目录（首次部署需要） |

---

## 三、上传文件到服务器

### 3.1 创建服务器目录

```bash
# SSH 登录服务器
ssh root@your-server-ip

# 创建部署目录
mkdir -p /opt/english-learning
mkdir -p /opt/english-learning/data/materials
mkdir -p /opt/english-learning/deploy/nginx
mkdir -p /opt/english-learning/deploy/mysql
mkdir -p /opt/english-learning/deploy/nginx/ssl
```

### 3.2 上传文件

**方式一：使用 scp**

```bash
# 在本地执行，上传所有文件
scp docker-compose.yml root@your-server-ip:/opt/english-learning/
scp .env root@your-server-ip:/opt/english-learning/
scp english-learning-backend.tar root@your-server-ip:/opt/english-learning/
scp english-learning-frontend.tar root@your-server-ip:/opt/english-learning/

# 上传配置目录
scp -r deploy/nginx/* root@your-server-ip:/opt/english-learning/deploy/nginx/
scp -r deploy/mysql/* root@your-server-ip:/opt/english-learning/deploy/mysql/
```

**方式二：使用 WinSCP / FileZilla 等工具**

直接拖拽上传以下文件到 `/opt/english-learning/` 目录。

### 3.3 确认服务器文件

```bash
# 服务器上查看文件结构
cd /opt/english-learning
ls -la

# 预期输出：
# docker-compose.yml
# .env
# english-learning-backend.tar
# english-learning-frontend.tar
# data/
# deploy/
```

---

## 四、服务器部署流程

### 4.1 配置环境变量

```bash
cd /opt/english-learning

# 编辑环境变量
nano .env
```

**必须修改的配置项：**

```env
# ==================== 数据库配置 ====================
MYSQL_ROOT_PASSWORD=your-strong-password-here

# ==================== JWT配置 ====================
SECRET_KEY=your-random-secret-key-at-least-32-characters

# ==================== 存储配置 ====================
# 存储类型: local, aliyun_oss, tencent_cos
STORAGE_TYPE=aliyun_oss

# 阿里云OSS配置（如果使用OSS）
ALIYUN_OSS_ACCESS_KEY_ID=your-access-key-id
ALIYUN_OSS_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_BUCKET_NAME=your-bucket-name

# CDN域名（可选）
CDN_DOMAIN=cdn.yourdomain.com

# ==================== AI API配置 ====================
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 4.2 加载镜像

```bash
cd /opt/english-learning

# 加载后端镜像
echo "正在加载后端镜像..."
docker load -i english-learning-backend.tar

# 加载前端镜像
echo "正在加载前端镜像..."
docker load -i english-learning-frontend.tar

# 验证镜像已加载
docker images | grep english-learning
```

### 4.3 拉取基础镜像（如果需要）

```bash
# 拉取 MySQL 镜像
docker pull mysql:8.0

# 如果使用 Nginx 反向代理
docker pull nginx:alpine
```

### 4.4 启动服务

```bash
cd /opt/english-learning

# 启动所有服务
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 4.5 初始化数据库

数据库会自动创建表结构，如需手动初始化：

```bash
# 进入后端容器
docker-compose exec backend bash

# 手动初始化数据库
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

# 退出容器
exit
```

---

## 五、验证部署

### 5.1 检查服务状态

```bash
# 查看所有容器状态
docker-compose ps

# 预期输出：
# NAME                        STATUS    PORTS
# english_learning_backend    Up        0.0.0.0:8000->8000/tcp
# english_learning_frontend   Up        0.0.0.0:80->80/tcp
# english_learning_mysql      Up        0.0.0.0:3306->3306/tcp
```

### 5.2 健康检查

```bash
# 检查后端 API
curl http://localhost:8000/health

# 检查前端
curl http://localhost:80

# 查看后端日志
docker-compose logs backend | tail -50
```

### 5.3 访问测试

- **前端页面**: http://your-server-ip
- **API 文档**: http://your-server-ip:8000/docs
- **健康检查**: http://your-server-ip:8000/health

---

## 六、日常运维

### 6.1 服务管理

```bash
cd /opt/english-learning

# 查看服务状态
docker-compose ps

# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql

# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 启动所有服务
docker-compose up -d
```

### 6.2 数据库备份与恢复

```bash
# 备份数据库
docker-compose exec mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} english_learning > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} english_learning < backup_20240101_120000.sql
```

### 6.3 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看 Docker 磁盘使用
docker system df
```

### 6.4 日志管理

```bash
# 清理 Docker 日志
docker-compose down
rm -rf /var/lib/docker/containers/*/*-json.log
docker-compose up -d

# 或者设置日志轮转（在 docker-compose.yml 中添加）
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 七、更新部署

### 7.1 更新流程

**本地操作：**

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose build

# 3. 导出新镜像
docker save -o english-learning-backend.tar english-learning-backend:latest
docker save -o english-learning-frontend.tar english-learning-frontend:latest

# 4. 上传到服务器
scp english-learning-backend.tar root@your-server-ip:/opt/english-learning/
scp english-learning-frontend.tar root@your-server-ip:/opt/english-learning/
```

**服务器操作：**

```bash
cd /opt/english-learning

# 1. 加载新镜像
docker load -i english-learning-backend.tar
docker load -i english-learning-frontend.tar

# 2. 停止旧服务
docker-compose down

# 3. 启动新服务
docker-compose up -d

# 4. 查看日志确认
docker-compose logs -f
```

### 7.2 快速更新脚本

创建更新脚本 `update.sh`：

```bash
#!/bin/bash
cd /opt/english-learning

echo ">>> 加载新镜像..."
docker load -i english-learning-backend.tar
docker load -i english-learning-frontend.tar

echo ">>> 重启服务..."
docker-compose down
docker-compose up -d

echo ">>> 查看服务状态..."
docker-compose ps

echo ">>> 更新完成！"
```

---

## 八、常见问题

### 8.1 容器无法启动

```bash
# 查看详细错误日志
docker-compose logs backend

# 检查端口占用
netstat -tlnp | grep 8000
netstat -tlnp | grep 3306

# 检查 Docker 网络
docker network ls
docker network inspect english_learning_network
```

### 8.2 数据库连接失败

```bash
# 检查 MySQL 容器状态
docker-compose ps mysql

# 进入 MySQL 容器测试
docker-compose exec mysql mysql -u root -p

# 检查数据库是否创建
docker-compose exec mysql mysql -u root -p -e "SHOW DATABASES;"

# 检查后端环境变量
docker-compose exec backend env | grep DATABASE
```

### 8.3 前端无法访问后端 API

```bash
# 检查后端是否正常
curl http://localhost:8000/health

# 检查防火墙
ufw status
iptables -L

# 开放端口
ufw allow 80
ufw allow 443
ufw allow 8000
```

### 8.4 文件上传失败

```bash
# 检查存储配置
docker-compose exec backend env | grep STORAGE

# 检查本地存储目录权限
ls -la /opt/english-learning/data/materials

# 测试 OSS 连接
docker-compose exec backend curl http://localhost:8000/api/admin/storage/test
```

### 8.5 镜像加载失败

```bash
# 检查镜像文件完整性
md5sum english-learning-backend.tar

# 重新下载/上传镜像文件
```

### 8.6 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理无用镜像
docker image prune -a

# 清理无用容器
docker container prune

# 清理无用卷
docker volume prune
```

---

## 九、安全建议

### 9.1 基础安全

- [ ] 修改默认数据库密码
- [ ] 修改 JWT 密钥为随机字符串
- [ ] 开启防火墙，只开放必要端口 (80, 443)
- [ ] 定期更新系统补丁

### 9.2 网络安全

```bash
# 配置防火墙
ufw enable
ufw allow 22      # SSH
ufw allow 80      # HTTP
ufw allow 443     # HTTPS
ufw deny 8000     # 禁止外部直接访问后端
ufw deny 3306     # 禁止外部直接访问数据库
```

### 9.3 SSL 配置（推荐）

```bash
# 安装 certbot
apt install certbot

# 申请证书
certbot certonly --standalone -d yourdomain.com

# 复制证书
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/english-learning/deploy/nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/english-learning/deploy/nginx/ssl/

# 启用 Nginx 服务
docker-compose up -d nginx
```

---

## 十、联系与支持

如有问题，请检查日志文件或联系技术支持。

**常用命令速查：**

| 操作 | 命令 |
|------|------|
| 查看状态 | `docker-compose ps` |
| 查看日志 | `docker-compose logs -f` |
| 重启服务 | `docker-compose restart` |
| 停止服务 | `docker-compose down` |
| 启动服务 | `docker-compose up -d` |
| 进入容器 | `docker-compose exec backend bash` |
| 备份数据库 | `docker-compose exec mysql mysqldump -u root -p english_learning > backup.sql` |
