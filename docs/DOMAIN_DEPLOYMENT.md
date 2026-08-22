# Fluenty 英语学习平台 - 域名部署与备案文档

## 📋 项目概览

- **项目名称**：Fluenty 英语口语学习平台
- **域名**：fluenty.cn
- **服务器**：阿里云 ECS（华东1-杭州）
- **公网 IP**：101.37.181.33
- **内网 IP**：172.18.134.107
- **部署目录**：/opt/english-learning

---

## 🌐 域名信息

### 域名注册
- **域名**：fluenty.cn
- **注册时间**：2026-03-04
- **注册商**：阿里云（万网）
- **订单号**：D20261R0OXG61874
- **费用**：￥38.00/年

### DNS 解析配置

| 记录类型 | 主机记录 | 解析线路 | 记录值 | TTL | 状态 |
|---------|---------|---------|--------|-----|------|
| A | @ | 默认 | 101.37.181.33 | 600 | ⏸️ 暂停（备案中） |
| A | www | 默认 | 101.37.181.33 | 600 | ⏸️ 暂停（备案中） |
| A | api | 默认 | 101.37.181.33 | 600 | ⏸️ 暂停（备案中） |

**域名控制台**：https://dc.console.aliyun.com/

---

## 🏗️ 服务器架构

### 部署架构
```
用户请求
    ↓
阿里云安全组（80, 443, 8000, 3306）
    ↓
Nginx 容器（80, 443）
    ├─→ 前端容器（内部 80）
    └─→ 后端容器（8000）
            ↓
        MySQL 容器（3306）
```

### Docker 容器列表

| 容器名称 | 镜像 | 端口映射 | 状态 |
|---------|------|---------|------|
| english_learning_nginx | nginx:alpine | 80:80, 443:443 | ✅ 运行中 |
| english_learning_frontend | english-learning-frontend:latest | 80（内部） | ✅ 运行中 |
| english_learning_backend | english-learning-backend:latest | 8000:8000 | ✅ 运行中 |
| english_learning_mysql | mysql:8.0 | 3306:3306 | ✅ 运行中 |

### 目录结构
```
/opt/english-learning/
├── docker-compose.yml          # Docker 编排配置
├── deploy/
│   ├── nginx/
│   │   ├── nginx.conf          # Nginx 配置文件
│   │   └── ssl/                # SSL 证书目录（待配置）
│   └── mysql/
│       └── my.cnf              # MySQL 配置
├── data/
│   └── materials/              # 学习语料数据
├── logs/                       # 日志目录
├── english-learning-backend.tar
└── english-learning-frontend.tar
```

---

## ⚙️ Nginx 配置

### 当前配置（支持域名）

**配置文件位置**：`/opt/english-learning/deploy/nginx/nginx.conf`

#### 前端服务（fluenty.cn, www.fluenty.cn）
```nginx
server {
    listen 80;
    server_name fluenty.cn www.fluenty.cn localhost;

    # API 代理
    location /api {
        proxy_pass http://backend:8000;
        # ... 代理配置
    }

    # 视频流代理
    location /video {
        proxy_pass http://backend:8000;
        # ... 视频流配置
    }

    # 前端页面
    location / {
        proxy_pass http://frontend:80;
        # ... 前端代理
    }
}
```

#### API 服务（api.fluenty.cn）
```nginx
server {
    listen 80;
    server_name api.fluenty.cn;

    location / {
        proxy_pass http://backend:8000;
        # ... API 代理配置
    }
}
```

### 特性支持
- ✅ HTTP/1.1 和 WebSocket 支持
- ✅ Gzip 压缩
- ✅ 大文件上传（500MB）
- ✅ 视频流传输
- ✅ 静态资源缓存
- ⏳ HTTPS（待备案后配置）

---

## 📝 ICP 备案信息

### 备案状态
- **状态**：⏳ 审核中
- **提交时间**：2026-03-04
- **备案主体**：个人/企业
- **网站名称**：Fluenty英语口语学习平台
- **域名**：fluenty.cn
- **服务器地域**：华东1（杭州）

### 备案流程
```
✅ 1. 准备材料（身份证、域名证书）
✅ 2. 暂停域名解析
✅ 3. 提交备案申请
⏳ 4. 阿里云初审（1-2 工作日）
⏳ 5. 短信核验（24小时内完成）
⏳ 6. 管局审核（7-20 工作日）
⏳ 7. 备案成功，恢复域名解析
```

### 备案系统
- **备案控制台**：https://beian.aliyun.com/
- **客服电话**：95187

### 备案材料清单
- ✅ 身份证正反面照片
- ✅ 域名证书（在域名控制台下载）
- ✅ 手机号和邮箱
- ⏳ 幕布照片（等待邮寄）

### 预计时间表
```
第 1-2 天：阿里云初审
第 3-5 天：短信核验
第 5-25 天：管局审核
第 25+ 天：备案成功
```

---

## 🌍 访问地址

### 备案期间（当前）
- **前端访问**：http://101.37.181.33
- **API 访问**：http://101.37.181.33/api
- **后端直连**：http://101.37.181.33:8000

### 备案成功后
- **前端访问**：http://fluenty.cn 或 http://www.fluenty.cn
- **API 访问**：http://api.fluenty.cn
- **HTTPS 访问**：https://fluenty.cn（待配置）

---

## 🔐 安全配置

### 阿里云安全组规则

| 方向 | 端口 | 协议 | 授权对象 | 说明 |
|-----|------|------|---------|------|
| 入方向 | 22 | TCP | 0.0.0.0/0 | SSH 访问 |
| 入方向 | 80 | TCP | 0.0.0.0/0 | HTTP 访问 |
| 入方向 | 443 | TCP | 0.0.0.0/0 | HTTPS 访问 |
| 入方向 | 3306 | TCP | 0.0.0.0/0 | MySQL（建议限制） |
| 入方向 | 8000 | TCP | 0.0.0.0/0 | 后端直连（建议限制） |

**安全建议**：
- ⚠️ 3306 和 8000 端口建议限制访问 IP
- ✅ 建议只开放 80 和 443 端口给外网

---

## 🚀 常用操作命令

### Docker 服务管理
```bash
# 进入项目目录
cd /opt/english-learning

# 查看容器状态
docker ps

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart nginx

# 查看日志
docker logs english_learning_nginx --tail 100
docker logs english_learning_backend --tail 100
docker logs english_learning_frontend --tail 100

# 停止所有服务
docker-compose down

# 启动所有服务
docker-compose up -d
```

### Nginx 配置
```bash
# 查看 Nginx 配置
cat /opt/english-learning/deploy/nginx/nginx.conf

# 测试配置语法
docker exec english_learning_nginx nginx -t

# 重新加载配置
docker exec english_learning_nginx nginx -s reload
```

### 测试访问
```bash
# 测试前端
curl -I http://localhost

# 测试 API
curl http://localhost/api/materials

# 测试外网 IP
curl -I http://101.37.181.33
```

---

## 📋 待办事项

### 备案期间（优先级：高）
- [x] 提交 ICP 备案申请
- [ ] 等待阿里云初审（1-2 工作日）
- [ ] 收到短信后完成核验（24小时内）
- [ ] 等待管局审核
- [ ] 收到备案号

### 备案成功后（优先级：高）
- [ ] 恢复域名解析（在域名控制台启用记录）
- [ ] 测试域名访问
- [ ] 申请 SSL 证书（Let's Encrypt）
- [ ] 配置 HTTPS
- [ ] 配置 HTTP 自动跳转 HTTPS
- [ ] 网站底部添加备案号

### 功能完善（优先级：中）
- [ ] 添加学习语料数据
- [ ] 完善用户功能
- [ ] 优化性能
- [ ] 移动端适配

### 优化提升（优先级：低）
- [ ] 配置 CDN 加速
- [ ] 配置 OSS 存储
- [ ] SEO 优化
- [ ] 监控和告警

---

## 🔧 故障排查

### 常见问题

#### 1. 域名无法访问（403 Forbidden）
**原因**：域名未备案
**解决**：完成 ICP 备案

#### 2. Nginx 容器无法启动
**原因**：nginx.conf 是目录而不是文件
**解决**：
```bash
cd /opt/english-learning
rm -rf deploy/nginx/nginx.conf
# 重新创建 nginx.conf 文件
```

#### 3. 端口被占用
**原因**：前端容器直接暴露了 80 端口
**解决**：
```bash
docker-compose down
docker-compose up -d
```

#### 4. API 无法访问
**原因**：后端服务未启动或端口未开放
**解决**：
```bash
docker ps  # 检查后端容器状态
docker logs english_learning_backend  # 查看日志
```

---

## 📞 联系方式

### 阿里云支持
- **客服电话**：95187
- **工单系统**：https://workorder.console.aliyun.com/
- **备案咨询**：https://beian.aliyun.com/

### 技术支持
- **项目文档**：`PRD.md`, `DEPLOY_GUIDE.md`
- **部署指南**：`DEPLOYMENT.md`
- **HTTPS 配置**：`HTTPS_CONFIG_GUIDE.md`

---

## 📊 项目状态

| 模块 | 状态 | 进度 |
|-----|------|------|
| 服务器部署 | ✅ 完成 | 100% |
| 域名申请 | ✅ 完成 | 100% |
| DNS 配置 | ✅ 完成 | 100% |
| Nginx 配置 | ✅ 完成 | 100% |
| ICP 备案 | ⏳ 进行中 | 10% |
| HTTPS 配置 | ⏸️ 待备案 | 0% |
| 功能开发 | 🔄 进行中 | 60% |
| 内容填充 | 🔄 进行中 | 20% |

---

## 🎯 里程碑

- ✅ **2026-03-01**：项目启动
- ✅ **2026-03-03**：服务器部署完成
- ✅ **2026-03-04**：域名申请成功
- ✅ **2026-03-04**：提交 ICP 备案
- ⏳ **预计 2026-03-25**：备案完成
- ⏳ **预计 2026-03-26**：配置 HTTPS
- ⏳ **预计 2026-03-27**：网站正式上线

---

## 📝 更新日志

### 2026-03-04
- ✅ 申请域名 fluenty.cn
- ✅ 配置 DNS 解析
- ✅ 配置 Nginx 支持域名
- ✅ 提交 ICP 备案申请
- ✅ 暂停域名解析（备案要求）
- ✅ 测试 IP 访问正常
- ✅ 创建部署文档

### 2026-03-03
- ✅ 服务器部署完成
- ✅ Docker 服务启动
- ✅ 基础功能测试

---

**文档版本**：v1.0
**最后更新**：2026-03-04
**维护者**：开发团队
