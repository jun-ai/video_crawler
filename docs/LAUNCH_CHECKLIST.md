# Fluenty 商业化上线 Checklist

> 状态: 2026-06-29 prod 实测
> ECS: 101.37.181.33 / 域 fluenty.cn

---

## ✅ 已完成 (P0 全部上线)

### 1. 商业化安全
- [x] **关闭 /docs /openapi.json /redoc** (ENV `ENABLE_API_DOCS=false`)
- [x] **修激活码 TOCTOU race condition** (原子 `UPDATE ... WHERE use_count < max_uses`)
- [x] **登录端 bcrypt 异常加固** (Invalid salt 不再返 500)
- [x] **CORS 严格限制** (`CORS_ORIGINS=https://fluenty.cn,https://www.fluenty.cn,https://api.fluenty.cn`)
- [x] **DEBUG=false** (生产环境)
- [x] **/docs 公开 (公网 200) → 404** ✓
- [x] **5xx 错误率 24h = 0%** ✓
- [x] **端到端 14/14 测试通过** ✓

### 2. 激活码 + 注册/登录
- [x] **POST /api/auth/register** 验证激活码 + 原子扣减 use_count
- [x] **POST /api/auth/login** (手机号+密码 + rate limit 5/min)
- [x] **POST /api/auth/forgot-password** 用激活码当重置凭证 (免短信)
- [x] **/register** 5 字段表单 (用户名/手机/激活码/密码/确认密码)
- [x] **/login** + 底部"忘记密码？"链接
- [x] **/forgot-password** 4 字段表单

### 3. 商业化合规 (中国法律)
- [x] **/terms** 用户协议 10 章节 (激活码机制 / 账号使用 / 退换条款)
- [x] **/privacy** 隐私政策 8 章节 (最小化收集 / bcrypt / 阿里云杭州 / 第三方)
- [x] **/refund** 退换政策 7 章节 (7 天无理由 / 已激活按比例 / 24h 客服)
- [x] **App.vue footer** "关于" 列: 3 个合规链接
- [x] **SPA 动态 title** (`/terms` -> "用户协议 - Fluenty")
- [x] **SEO noindex** (login/register/forgot-password)

### 4. 用户体验
- [x] **首页激活码引导 banner** (v-if 未登录, 暖色系, 移动端自适应)
- [x] **Profile 激活信息 section** (激活码 ID / 状态 / 激活时间)
- [x] **激活码 admin 管理** 5 个端点 (生成/列表/删除/批量删除/全删未用)
- [x] **生成对话框默认 365 天** (1 年过期)
- [x] **复制 / 复制全部** 按钮

### 5. 部署 + 监控
- [x] **3 容器跑 prod** (backend 32min / mysql 27h / frontend 13min)
- [x] **nginx 0 警告** (babyname.asia 旧冲突清理)
- [x] **GitHub push** 到 `deploy/prod-snapshot-20260629` (48ad03b + ee41a51)

---

## 🚨 商业化前 **俊哥必须手动** 处理

### 🔴 #1 OSS AccessKey rotate
- **当前状态**: 仍用 6-28 泄漏事故的旧 key `LTAI5t6kw4sWThfBJuE2PdbB`
- **步骤**:
  1. 阿里云控制台 → 访问 RAM → AccessKey → 找到 `LTAI5t6kw4sWThfBJuE2PdbB` → **Disable**
  2. 创建新 AccessKey (记录 ID + Secret)
  3. ECS 上 `vim /opt/english-learning/.env` 改 `ALIYUN_OSS_ACCESS_KEY_ID/SECRET`
  4. `docker compose up -d --no-deps --force-recreate backend` (env 改了需 force-recreate)
  5. 验证: `docker exec english_learning_backend python3 -c "import os; print(os.environ.get('ALIYUN_OSS_ACCESS_KEY_ID','MISSING')[:10])"`
  6. 上传一个视频测试 OSS 写入正常

### 🟡 商业运营准备 (建议)
- [ ] 小红书账号发首条引流 (引导用户到 https://fluenty.cn/register)
- [ ] 客服小红书私信话术 (激活码怎么用 / 忘记密码 / 退款)
- [ ] 激活码批量生成脚本 (admin 端手动生成, 5 个一批)
- [ ] 定价策略 (年卡 / 终身卡 / 团购, 在 Refund 页 "7 天无理由" 是基础)
- [ ] 支付收款 (小红书私信付款, 手动发激活码; 或接 Creem/Stripe, 但俊哥纯个人无公司实体)

---

## 🔄 已知限制 (商业化跑起来后视情况优化)

### P2
- [ ] 激活码格式 8 位 hex (4.3 亿空间) → 12 位字母数字 (4.7 万亿) 更安全
- [ ] JWT 24h 偏长 → 60-120 min + refresh token
- [ ] admin 操作审计日志 (谁在何时生成了几个码 / 删了哪个)
- [ ] 手机号短信验证 (用户量上来有纠纷再做)

### P3
- [ ] PRD.md 仍是 v1.0 2026-02-28 旧版, 跟实际项目严重脱节 → 弃用或重写
- [ ] CI/CD 自动化部署 (目前 scp + restart 手动)
- [ ] 监控告警 (Prometheus + Grafana, 目前 24h manual grep logs)

---

## 📊 prod 24h 健康基线 (2026-06-29)

| 指标 | 值 |
|---|---|
| 后端容器 | Up 32 min (restart) |
| MySQL 容器 | Up 27 h |
| 前端容器 | Up 13 min (restart) |
| 24h 请求数 | 1032 |
| 5xx 错误数 | **0** |
| bcrypt Invalid salt | **0** |
| nginx warning | **0** |
| 端口监听 | 80/443/3306/8000/8080 全 OK |
| 业务数据 | 1 user (admin) / 3 codes / 29 materials / 7695 subtitles |
| 翻译覆盖 | 7424/7695 = **96.5%** |

---

## 🎯 小红书发布前 1 天再确认

```
□ OSS key 已 rotate (俊哥操作) + ECS env 改完 + 验证
□ 客服小红书账号准备 + 私信话术 ready
□ 首批 10-20 个激活码 admin 生成 + 复制到小红书私信话术
□ 自己登录 + 完整跑一遍 买码 → 注册 → 学习 流程
□ 隐身浏览器实测手机端首页引导 banner
□ robots.txt 没把注册页排除? (确认下)
```

---

## 🆘 出问题怎么办

| 问题 | 排查 |
|---|---|
| 用户说"激活码无效" | `mysql -e "SELECT id, use_count, max_uses, expires_at FROM activation_codes WHERE code='<code>'"` |
| 用户说"忘记密码" | 引导到 /forgot-password, 用手机号 + 激活码重置 |
| 用户说"网站打不开" | 让用户关 Clash 重试 (Win 开发机 6 月踩坑) |
| 5xx 突发 | `docker logs --since 5m english_learning_backend \| grep -E "ERROR\|5[0-9][0-9]"` |
| nginx warning | `nginx -t 2>&1 \| grep -i warn` |
| 视频加载慢 | ECS→OSS 杭州单 `put_object` ~5Mbps, 200MB 视频 5-8min; 用 multipart 并行优化 (P2) |
