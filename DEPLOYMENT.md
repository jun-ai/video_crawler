# 英语学习网站部署指南

## 目录结构

```
video_crawler/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── deploy/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── frontend.conf
│   └── mysql/
│       └── my.cnf
├── data/
│   └── materials/          # 本地存储目录
├── docker-compose.yml
└── .env
```

## 一、环境准备

### 1. 服务器要求
- CPU: 2核+
- 内存: 4GB+
- 硬盘: 50GB+
- 系统: Ubuntu 20.04 / CentOS 7+

### 2. 安装 Docker
```bash
# Ubuntu
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER

# 安装 docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 二、阿里云 OSS 配置

### 1. 创建 Bucket
1. 登录 [阿里云 OSS 控制台](https://oss.console.aliyun.com)
2. 点击"创建 Bucket"
3. 配置：
   - Bucket 名称: `english-learning-media`
   - 地域: 选择离用户最近的区域（如华东-杭州）
   - 存储类型: 标准存储
   - 读写权限: 公共读

### 2. 获取 AccessKey
1. 点击右上角头像 → AccessKey 管理
2. 创建 AccessKey
3. 记录 AccessKey ID 和 Secret

### 3. 配置 CDN（可选但推荐）
1. 进入 [CDN 控制台](https://cdn.console.aliyun.com)
2. 添加域名: `cdn.yourdomain.com`
3. 业务类型: CDN图片小文件
4. 源站信息: OSS域名
5. 配置 CNAME 解析

## 三、配置部署

### 1. 克隆代码
```bash
git clone https://github.com/yourname/english-learning.git
cd english-learning
```

### 2. 配置环境变量
```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件：
```env
# 数据库
MYSQL_ROOT_PASSWORD=your-strong-password

# JWT
SECRET_KEY=your-random-secret-key-at-least-32-characters

# 云存储
STORAGE_TYPE=aliyun_oss
ALIYUN_OSS_ACCESS_KEY_ID=your-access-key-id
ALIYUN_OSS_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_BUCKET_NAME=english-learning-media
CDN_DOMAIN=cdn.yourdomain.com

# AI API
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 3. SSL 证书配置
```bash
# 创建证书目录
mkdir -p deploy/nginx/ssl

# 使用 Let's Encrypt 免费证书
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deploy/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deploy/nginx/ssl/
```

## 四、启动服务

### 1. 构建并启动
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 2. 初始化数据库
```bash
# 进入后端容器
docker-compose exec backend bash

# 数据库会自动初始化，如需手动执行：
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 3. 迁移现有数据（如有）
```bash
docker-compose exec backend python scripts/migrate_to_cloud.py
```

## 五、验证部署

### 1. 健康检查
```bash
# 检查后端
curl http://localhost:8000/health

# 检查前端
curl http://localhost:80
```

### 2. 测试存储
```bash
# 访问管理后台 API
curl http://localhost:8000/api/admin/storage/test
```

### 3. 检查服务状态
```bash
docker-compose ps
```

## 六、日常运维

### 1. 查看日志
```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f backend
docker-compose logs -f mysql
```

### 2. 重启服务
```bash
# 重启所有
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 3. 更新代码
```bash
git pull
docker-compose build
docker-compose up -d
```

### 4. 备份数据库
```bash
# 备份
docker-compose exec mysql mysqldump -u root -p english_learning > backup.sql

# 恢复
docker-compose exec -T mysql mysql -u root -p english_learning < backup.sql
```

### 5. 查看资源使用
```bash
docker stats
```

## 七、监控告警（可选）

### 使用阿里云监控
1. 开通云监控服务
2. 配置主机监控
3. 设置告警规则：
   - CPU 使用率 > 80%
   - 内存使用率 > 85%
   - 磁盘使用率 > 90%

## 八、性能优化建议

### 1. CDN 优化
- 开启 HTTPS
- 配置缓存规则
- 开启 Gzip 压缩

### 2. 数据库优化
- 定期清理日志
- 优化慢查询
- 适当增加连接数

### 3. 应用优化
- 启用 Redis 缓存（可选）
- 配置日志轮转
- 定期清理临时文件

## 九、故障排查

### 常见问题

**1. 容器无法启动**
```bash
# 查看详细错误
docker-compose logs backend

# 检查端口占用
netstat -tlnp | grep 8000
```

**2. 数据库连接失败**
```bash
# 检查 MySQL 状态
docker-compose exec mysql mysql -u root -p

# 检查网络
docker network ls
```

**3. 文件上传失败**
```bash
# 检查存储配置
docker-compose exec backend python -c "from app.services.storage import get_storage_service; print(get_storage_service())"

# 测试 OSS 连接
docker-compose exec backend curl http://localhost:8000/api/admin/storage/test
```

## 十、成本估算

| 资源 | 配置 | 月费用 |
|------|------|--------|
| 云服务器 | 2核4G | ¥100-200 |
| OSS 存储 | 100GB | ¥12 |
| CDN 流量 | 500GB | ¥35 |
| 域名 | .com | ¥55/年 |
| SSL 证书 | Let's Encrypt | 免费 |
| **合计** | | **~¥150-250/月** |

## 十一、安全建议

1. **定期更新密码**
2. **开启防火墙**，只开放 80/443 端口
3. **配置 IP 白名单**（管理后台）
4. **定期备份数据**
5. **开启操作日志**
6. **使用 HTTPS**

---

如有问题，请查看日志或联系技术支持。
