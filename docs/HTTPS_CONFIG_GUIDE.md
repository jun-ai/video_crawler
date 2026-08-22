# 域名购买与 HTTPS 配置指南

> 服务器IP: 101.37.181.33

---

## 一、购买域名

### 1.1 推荐域名服务商

| 服务商 | 价格(.com) | 特点 |
|--------|-----------|------|
| [阿里云](https://wanwang.aliyun.com) | ¥55/年 | 国内推荐，和服务器同平台，解析快 |
| [腾讯云](https://dnspod.cloud.tencent.com) | ¥55/年 | DNSPod 解析稳定 |
| [Cloudflare](https://www.cloudflare.com) | $9.99/年 | 免费SSL，CDN加速 |
| [Namecheap](https://www.namecheap.com) | $8.88/年 | 国外便宜，隐私保护免费 |

### 1.2 域名选择建议

```
推荐格式:
- english-learn.com
- learnenglish.com
- speak-fluent.com
- 你的品牌名.com

注意事项:
- 选择 .com / .cn 等主流后缀
- 避免特殊字符和数字
- 尽量简短好记
```

---

## 二、域名解析配置

### 2.1 添加 DNS 解析记录

购买域名后，在域名控制台添加以下解析记录：

| 记录类型 | 主机记录 | 记录值 | 说明 |
|----------|----------|--------|------|
| A | @ | 101.37.181.33 | 主域名访问 |
| A | www | 101.37.181.33 | www 子域名 |
| A | api | 101.37.181.33 | API 子域名（可选） |

### 2.2 阿里云解析配置步骤

1. 登录 [阿里云域名控制台](https://dc.console.aliyun.com)
2. 点击域名进入「解析设置」
3. 添加记录：
   ```
   记录类型: A
   主机记录: @
   记录值: 101.37.181.33
   TTL: 10分钟
   ```
4. 再添加 www 记录：
   ```
   记录类型: A
   主机记录: www
   记录值: 101.37.181.33
   TTL: 10分钟
   ```

### 2.3 验证解析生效

```bash
# 在本地命令行执行
ping yourdomain.com
# 应该返回 101.37.181.33

# 或使用 nslookup
nslookup yourdomain.com
```

> 解析生效时间：通常 10分钟 - 2小时

---

## 三、SSL 证书配置

### 3.1 方式一：Let's Encrypt 免费证书（推荐）

**在服务器上执行：**

```bash
# 1. 安装 certbot
apt update
apt install certbot -y

# 2. 先临时停止 80 端口服务
cd /opt/english-learning
docker-compose stop frontend nginx

# 3. 申请证书（替换 yourdomain.com 为你的域名）
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 按提示输入邮箱，同意条款

# 4. 复制证书到部署目录
mkdir -p /opt/english-learning/deploy/nginx/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/english-learning/deploy/nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/english-learning/deploy/nginx/ssl/

# 5. 设置自动续期
crontab -e
# 添加以下行（每月1号凌晨3点自动续期）：
0 3 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/yourdomain.com/*.pem /opt/english-learning/deploy/nginx/ssl/ && cd /opt/english-learning && docker-compose restart nginx
```

### 3.2 方式二：阿里云免费证书

1. 登录 [阿里云 SSL 证书控制台](https://yundunnext.console.aliyun.com/?p=cas)
2. 点击「免费证书」→「创建证书」
3. 填写域名信息，选择「DNS 验证」
4. 按提示添加 TXT 记录验证
5. 下载 Nginx 格式证书
6. 上传到服务器：
   ```bash
   # 重命名文件
   mv yourdomain.com.pem fullchain.pem
   mv yourdomain.com.key privkey.pem

   # 上传到服务器
   scp fullchain.pem privkey.pem root@101.37.181.33:/opt/english-learning/deploy/nginx/ssl/
   ```

---

## 四、Nginx HTTPS 配置

### 4.1 更新 nginx.conf

在服务器上创建新的 nginx 配置：

```bash
nano /opt/english-learning/deploy/nginx/nginx.conf
```

内容如下（替换 `yourdomain.com` 为你的域名）：

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Let's Encrypt 验证路径
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # 其他请求重定向到 HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS 服务
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书配置
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # API 代理
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 视频流代理（支持 Range 请求）
    location /video {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Range $http_range;
        proxy_set_header If-Range $http_if_range;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # 静态文件代理
    location /static {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # 前端页面
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/x-javascript
        application/xml
        application/json
        application/pdf
        image/svg+xml;
    gzip_comp_level 6;
}
```

### 4.2 更新 docker-compose.yml

```bash
nano /opt/english-learning/docker-compose.yml
```

确保 nginx 服务配置正确：

```yaml
  # Nginx 反向代理（HTTPS）
  nginx:
    image: nginx:alpine
    container_name: english_learning_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./deploy/nginx/ssl:/etc/nginx/ssl
      - /var/www/certbot:/var/www/certbot  # Let's Encrypt 验证目录
    depends_on:
      - backend
      - frontend
    networks:
      - english_learning_network
```

---

## 五、应用配置

### 5.1 重启服务

```bash
cd /opt/english-learning

# 重启所有服务
docker-compose down
docker-compose up -d

# 查看状态
docker-compose ps
```

### 5.2 验证 HTTPS

```bash
# 检查 SSL 证书
curl -I https://yourdomain.com

# 或使用在线工具
# https://www.ssllabs.com/ssltest/
```

---

## 六、完整操作清单

### 6.1 首次配置流程

```bash
# === 步骤1: 购买域名 ===
# 去阿里云/腾讯云购买域名

# === 步骤2: 配置 DNS 解析 ===
# 添加 A 记录指向 101.37.181.33

# === 步骤3: 等待解析生效 ===
ping yourdomain.com

# === 步骤4: 服务器申请 SSL 证书 ===
# 停止 80 端口
cd /opt/english-learning
docker-compose stop frontend nginx

# 安装 certbot
apt update && apt install certbot -y

# 申请证书
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 复制证书
mkdir -p /opt/english-learning/deploy/nginx/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/english-learning/deploy/nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/english-learning/deploy/nginx/ssl/

# === 步骤5: 更新 nginx 配置 ===
# 按上面的配置更新 nginx.conf 和 docker-compose.yml

# === 步骤6: 重启服务 ===
docker-compose down
docker-compose up -d

# === 步骤7: 验证 ===
curl https://yourdomain.com
```

### 6.2 设置自动续期

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每月1号凌晨3点执行）
0 3 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/yourdomain.com/*.pem /opt/english-learning/deploy/nginx/ssl/ && cd /opt/english-learning && docker-compose restart nginx
```

---

## 七、常用命令

```bash
# 查看证书有效期
certbot certificates

# 手动续期测试
certbot renew --dry-run

# 强制续期
certbot renew --force-renewal

# 查看 nginx 日志
docker-compose logs -f nginx

# 测试 nginx 配置
docker-compose exec nginx nginx -t

# 重新加载 nginx 配置
docker-compose exec nginx nginx -s reload
```

---

## 八、访问地址

配置完成后：

| 地址 | 说明 |
|------|------|
| https://yourdomain.com | 前端页面（HTTPS） |
| https://yourdomain.com/api | API 接口 |
| http://yourdomain.com | 自动跳转到 HTTPS |

---

## 九、故障排查

### 9.1 证书申请失败

```bash
# 检查 80 端口是否被占用
netstat -tlnp | grep :80

# 确保停止了前端服务
docker-compose stop frontend nginx
```

### 9.2 HTTPS 访问失败

```bash
# 检查证书文件
ls -la /opt/english-learning/deploy/nginx/ssl/

# 检查 nginx 配置语法
docker-compose exec nginx nginx -t

# 查看 nginx 错误日志
docker-compose logs nginx
```

### 9.3 浏览器提示不安全

- 检查证书是否过期
- 检查域名是否匹配
- 清除浏览器缓存

---

> 配置完成后，你的网站将通过 HTTPS 安全访问！
