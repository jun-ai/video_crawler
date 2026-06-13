# SpeakFlow - 英语口语学习平台

基于视频的英语口语学习系统，支持字幕同步、跟读练习、听写训练、AI词汇卡片和间隔重复复习。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Tailwind CSS 4 + Pinia + Vue Router |
| 后端 | FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 |
| 数据库 | MySQL 8 (aiomysql) |
| AI | DeepSeek API (词汇/短语/语法卡片生成) |
| 音频 | Whisper (语音识别) + 讯飞语音 |
| 存储 | 本地 / 阿里云 OSS / 腾讯云 COS |

## 项目结构

```
video_crawler/
├── frontend/               # Vue 3 前端 (端口 3000)
│   ├── src/
│   │   ├── views/          # 页面组件 (Learn.vue, Vocabulary.vue 等)
│   │   ├── components/     # UI 组件 (learn/, common/, ui/)
│   │   ├── composables/    # 组合式函数 (useTTS.js 等)
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── router/         # 路由配置
│   │   └── styles/         # 全局样式、设计令牌
│   ├── package.json
│   └── vite.config.js
├── backend/               # FastAPI 后端 (端口 8001)
│   ├── app/
│   │   ├── routers/        # API 路由 (auth, materials, learning, admin 等)
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── services/       # 业务服务 (DeepSeek, Storage, 字幕解析等)
│   │   ├── main.py         # FastAPI 入口
│   │   └── config.py       # 配置管理
│   ├── requirements.txt
│   ├── run.sh / run.bat    # 后端启动脚本
│   └── .env                # 环境变量
├── data/materials/         # 视频/字幕文件存储
├── docker-compose.yml      # 开发环境 Docker 配置
├── docker-compose.prod.yml # 生产环境 Docker 配置
├── PRD.md                  # 产品需求文档
├── DEPLOYMENT.md           # 部署指南
└── AGENTS.md               # 设计规范
```

## 快速启动

### 方式一：本地开发

**前置条件**
- Node.js 18+
- Python 3.10+
- MySQL 8.0

**1. 启动 MySQL**

确保 MySQL 服务运行中，数据库 `english_learning` 已创建。

**2. 启动后端**

```bash
# Windows (CMD)
cd backend
run.bat

# Windows (Git Bash / WSL)
cd backend
./run.bat

# 或直接运行 (不使用虚拟环境脚本)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

服务启动后：
- API 地址: http://localhost:8001
- API 文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/health

**3. 启动前端**

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:3000，会自动代理 `/api` `/static` `/video` 请求到后端 (8001)。

> 注意：前端 vite.config.js 中代理指向 `127.0.0.1:8001`，后端默认端口为 **8001** 而非 8000。

**4. 访问应用**

浏览器打开 http://localhost:3000

---

### 方式二：Docker 开发环境

```bash
# 构建并启动所有服务 (MySQL + 后端 + 前端 + Nginx)
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

访问 http://localhost (Nginx 反向代理)

---

## 核心功能

### 学习页面 (`/learn/:id`)
- 视频播放 (支持倍速、循环播放)
- 字幕同步 (点击字幕跳转播放位置)
- 跟读练习 (录音 + AI 发音评估)
- 听写模式 (听写并检查准确率)
- 生词收藏 (点击单词添加到生词本)
- AI 解读抽屉 (单词/短语/语法卡片)

### 生词本 (`/vocabulary`)
- SM-2 间隔重复算法复习
- 按时间/字母/复习次数排序
- TTS 单词发音
- 生词详情查看 (音标、释义、例句)

### AI 词汇卡片 (`/english-cards`)
- DeepSeek AI 自动生成单词/短语/语法/习语卡片
- 标记已知/模糊/未知状态

### 管理后台 (`/admin`)
- 素材上传 (视频 + 字幕 + 封面)
- 标签管理、激活码管理、公告管理

## API 路由概览

| 前缀 | 说明 |
|------|------|
| `/api/auth/*` | 注册、登录、个人信息 |
| `/api/materials/*` | 素材 CRUD、字幕、分类 |
| `/api/learning/*` | 学习进度、生词、听写、跟读 |
| `/api/favorites/*` | 收藏 |
| `/api/admin/*` | 管理功能 |
| `/api/tags/*` | 标签管理 |
| `/api/announcements/*` | 公告 |

## 环境变量

后端 `.env` 关键配置：

```env
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/english_learning
SECRET_KEY=your-secret-key
STORAGE_TYPE=local                  # local | aliyun_oss | tencent_cos
DEEPSEEK_API_KEY=your-deepseek-key
```

## 常用命令

```bash
# 前端
cd frontend
npm install
npm run dev      # 开发服务器 (localhost:3000)
npm run build    # 生产构建

# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# Docker
docker-compose up -d
docker-compose -f docker-compose.prod.yml build

# 进入后端容器
docker exec -it english_learning_backend /bin/sh
```

## 端口汇总

| 服务 | 端口 |
|------|------|
| 前端 (开发) | 3000 |
| 后端 (开发) | 8001 |