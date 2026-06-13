# 英语口语学习网站 PRD（产品需求文档）

> 版本：v1.0
> 日期：2026-02-28
> 状态：待确认

---

## 一、产品概述

### 1.1 产品定位
基于真实视频语料库的英语口语学习平台，通过视频+字幕+场景化内容，帮助用户提升英语口语能力。

### 1.2 目标用户
- 英语学习者（初中级水平）
- 希望提升日常口语表达能力的人群
- 喜欢通过视频学习的用户

### 1.3 核心价值
- **真实语境**：非教科书式英语，学习地道口语表达
- **场景化学习**：按生活场景分类（旅行、购物、社交等）
- **多模态输入**：视频+字幕+图片，强化记忆

---

## 二、产品路线图

### Phase 1: MVP（4-6周）
| 功能模块 | 功能点 | 优先级 |
|---------|--------|--------|
| 视频播放 | 视频播放器、进度控制 | P0 |
| 字幕同步 | 字幕显示、时间轴同步 | P0 |
| 语料管理 | 语料库CRUD、分类管理 | P0 |
| 用户系统 | 注册、登录、学习记录 | P0 |

### Phase 2: 核心功能（6-8周）
| 功能模块 | 功能点 | 优先级 |
|---------|--------|--------|
| 听写练习 | 逐句听写、答案校验 | P1 |
| 跟读打分 | 录音、语音识别、评分 | P1 |
| 生词本 | 生词收藏、复习提醒 | P1 |
| 学习统计 | 学习时长、进度追踪 | P1 |

### Phase 3: 高级功能（8-12周）
| 功能模块 | 功能点 | 优先级 |
|---------|--------|--------|
| AI对话 | 基于场景的AI口语对话 | P2 |
| 社区功能 | 学习打卡、分享 | P2 |
| 移动端 | 小程序/APP | P2 |
| 付费课程 | VIP会员、精品课程 | P2 |

---

## 三、MVP原型图

### 3.1 页面结构

```
┌─────────────────────────────────────────────────────────────┐
│                        网站导航栏                            │
│  [Logo] 首页 | 语料库 | 我的课程 | 生词本 | 个人中心          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心页面原型

#### 首页
```
┌──────────────────────────────────────────────────────────────┐
│  [Banner: 今日推荐语料]                                       │
├──────────────────────────────────────────────────────────────┤
│  热门场景分类                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                │
│  │ 旅行   │ │ 购物   │ │ 社交   │ │ 工作   │                │
│  │ [图标] │ │ [图标] │ │ [图标] │ │ [图标] │                │
│  └────────┘ └────────┘ └────────┘ └────────┘                │
├──────────────────────────────────────────────────────────────┤
│  最新语料                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ [封面图]    │ │ [封面图]    │ │ [封面图]    │            │
│  │ Day in NYC  │ │ Coffee Shop │ │ Shopping    │            │
│  │ ⭐ 4.8      │ │ ⭐ 4.6      │ │ ⭐ 4.9      │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

#### 视频学习页（核心页面）
```
┌──────────────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────┐  ┌────────────┐ │
│  │                                        │  │ 语料信息   │ │
│  │           视频播放区域                  │  │ 标题: xxx  │ │
│  │                                        │  │ 难度: ⭐⭐  │ │
│  │          [播放/暂停] [进度条]           │  │ 时长: 5:30 │ │
│  │                                        │  │ 场景: 旅行 │ │
│  └────────────────────────────────────────┘  └────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  字幕区域（同步高亮）                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 00:05 "guys it is day one in New York..."             │ │
│  │ 00:09 "I have a kind of a free day today..."          │ │
│  │ 00:12 "my friend tages he recommended..."  [当前]     │ │
│  │ 00:16 "this coffee shop I'm gonna go..."              │ │
│  └────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  功能按钮                                                     │
│  [上一句] [重播] [下一句] | [听写练习] [收藏生词] [分享]       │
└──────────────────────────────────────────────────────────────┘
```

#### 语料库列表页
```
┌──────────────────────────────────────────────────────────────┐
│  筛选: [全部场景 ▼] [难度 ▼] [时长 ▼]     搜索: [_______] [🔍] │
├──────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │ [封面图]  I went to NYC for a boy                     │  │
│  │           场景: 旅行 | 难度: ⭐⭐ | 时长: 5:30         │  │
│  │           简介: 跟随博主探索纽约...                    │  │
│  │           [开始学习]                                   │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ [封面图]  Coffee Shop Conversation                    │  │
│  │           场景: 社交 | 难度: ⭐ | 时长: 3:20           │  │
│  │           简介: 咖啡店点单常用表达...                  │  │
│  │           [开始学习]                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、架构设计蓝图

### 4.1 技术栈选型

| 层级 | 技术选择 | 说明 |
|-----|---------|------|
| **前端** | Vue 3 + TypeScript + Vite | 现代化前端框架，组件化开发 |
| **UI框架** | Element Plus / Naive UI | 成熟的Vue3组件库 |
| **后端** | Python FastAPI | 高性能异步API框架 |
| **数据库** | PostgreSQL + Redis | 关系型 + 缓存 |
| **文件存储** | 本地/MinIO/OSS | 视频图片存储 |
| **部署** | Docker + Nginx | 容器化部署 |

### 4.2 系统架构图

```
                            ┌─────────────────┐
                            │   Nginx (反向代理) │
                            └────────┬────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
     ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
     │   前端服务      │    │   API服务       │    │   静态资源      │
     │   (Vue 3)      │    │   (FastAPI)    │    │   (视频/图片)   │
     └────────────────┘    └───────┬────────┘    └────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
     │   PostgreSQL   │   │     Redis      │   │  File Storage  │
     │   (业务数据)    │   │   (缓存/会话)   │   │  (MinIO/OSS)   │
     └────────────────┘   └────────────────┘   └────────────────┘
```

### 4.3 数据库设计

#### 核心表结构

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(255),
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 语料表
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    video_path VARCHAR(255) NOT NULL,
    subtitle_path VARCHAR(255) NOT NULL,
    cover_path VARCHAR(255) NOT NULL,
    category VARCHAR(50),           -- 场景分类
    difficulty INTEGER DEFAULT 1,   -- 难度等级 1-5
    duration INTEGER,               -- 时长(秒)
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 字幕句子表（解析SRT后存储）
CREATE TABLE subtitles (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(id),
    sequence INTEGER NOT NULL,      -- 句子序号
    start_time INTEGER NOT NULL,    -- 开始时间(毫秒)
    end_time INTEGER NOT NULL,      -- 结束时间(毫秒)
    text_en TEXT NOT NULL,          -- 英文文本
    text_cn TEXT,                   -- 中文翻译(可选)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学习记录表
CREATE TABLE learning_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    material_id INTEGER REFERENCES materials(id),
    progress INTEGER DEFAULT 0,     -- 学习进度(%)
    last_position INTEGER DEFAULT 0,-- 上次播放位置(秒)
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 生词本表
CREATE TABLE vocabulary (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    material_id INTEGER REFERENCES materials(id),
    subtitle_id INTEGER REFERENCES subtitles(id),
    word VARCHAR(100) NOT NULL,
    context TEXT,                   -- 上下文句子
    mastered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.4 目录结构

```
english-learning/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue        # 首页
│   │   │   ├── MaterialList.vue# 语料列表
│   │   │   ├── Learning.vue    # 学习页面
│   │   │   └── Profile.vue     # 个人中心
│   │   ├── components/         # 公共组件
│   │   │   ├── VideoPlayer.vue # 视频播放器
│   │   │   ├── SubtitlePanel.vue# 字幕面板
│   │   │   └── CategoryCard.vue# 分类卡片
│   │   ├── api/                # API接口
│   │   ├── stores/             # 状态管理(Pinia)
│   │   └── utils/              # 工具函数
│   └── package.json
│
├── backend/                     # 后端项目
│   ├── app/
│   │   ├── main.py             # 入口文件
│   │   ├── routers/            # 路由模块
│   │   │   ├── auth.py         # 用户认证
│   │   │   ├── materials.py    # 语料管理
│   │   │   └── learning.py     # 学习记录
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # Pydantic模型
│   │   ├── services/           # 业务逻辑
│   │   │   ├── subtitle_parser.py  # SRT解析
│   │   │   └── file_manager.py     # 文件管理
│   │   └── utils/              # 工具函数
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/                        # 语料数据
│   ├── materials/
│   │   ├── PKOw-FbVXrc/
│   │   │   ├── video.mp4
│   │   │   ├── subtitle.srt
│   │   │   └── cover.jpg
│   │   └── ...
│
├── docker-compose.yml          # Docker编排
└── README.md
```

### 4.5 API设计

#### 核心接口

```
# 用户模块
POST   /api/auth/register        # 注册
POST   /api/auth/login           # 登录
GET    /api/auth/profile         # 获取用户信息

# 语料模块
GET    /api/materials            # 语料列表(支持分页/筛选)
GET    /api/materials/{id}       # 语料详情
GET    /api/materials/{id}/subtitles  # 获取字幕列表
GET    /api/categories           # 场景分类列表

# 学习模块
POST   /api/learning/progress    # 更新学习进度
GET    /api/learning/history     # 学习历史
POST   /api/vocabulary           # 添加生词
GET    /api/vocabulary           # 生词列表
```

---

## 五、语料库规范

### 5.1 数据结构规范

```
data/materials/{material_id}/
├── video.mp4          # 视频文件
├── subtitle.srt       # 字幕文件(SRT格式)
├── cover.jpg          # 封面图片(推荐16:9)
└── meta.json          # 元数据(可选)
```

### 5.2 元数据格式 (meta.json)

```json
{
    "id": "PKOw-FbVXrc",
    "title": "Day in New York City",
    "description": "跟随博主探索纽约的一天",
    "category": "travel",
    "difficulty": 2,
    "tags": ["旅行", "日常对话", "纽约"],
    "source": "YouTube",
    "duration": 330
}
```

---

## 六、下一步计划

- [ ] 确认技术栈选型
- [ ] 确认MVP功能范围
- [ ] 开始数据库建表
- [ ] 搭建项目骨架
- [ ] 实现视频播放+字幕同步

---

> **状态：待确认**
>
> 请确认以上"产品路线图"、"MVP原型图"和"架构设计蓝图"是否符合预期，确认后将进入开发阶段。
