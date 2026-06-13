# UI 改进方案

基于 PPT 设计原则 + 全项目 UI 审计，制定以下改进方案。

---

## 一、问题总览

### 核心问题：三套设计系统并存

| 前缀 | 页面/组件 | 来源 |
|------|-----------|------|
| `--yt-*` | Home, Vocabulary, Favorites, Profile, LearningCenter, EnglishCards, Materials | 旧系统 |
| `--sf-*` | Learn, DictationMode, FilterChip, VideoCard | 新系统 |
| `--primary/--accent/--background` | Login, Register | shadcn 默认 |
| 硬编码 | Admin 全部页面 | 无设计系统 |

**这违反了 PPT 原则：配色先克制**——颜色变量应该有且只有一套。

### Emoji 污染（违反"素材统一"原则）

| 页面 | Emoji | 应替换 |
|------|-------|--------|
| VocabularyReview | 😵 🤔 💡 😊 🎯 | Lucide 图标 |
| LearningCenter | 🔥 | Flame 图标 |
| EnglishCards | 💡 | Lightbulb 图标 |
| Home | 🔥 🌱 💪 ⭐ 🏆 👑 🎯 ✨ | 各对应图标 |

### HTML Entity 作为图标

| 页面 | Entity | 应替换 |
|------|--------|--------|
| AnnouncementBanner | `&#9888;` `&#10003;` `&#128640;` `&#8505;` | Lucide 图标 |

### 组件混用问题

- Element Plus: `el-pagination`, `el-form`, `el-input` 散落在多个页面
- 应统一为 Sf* 组件

---

## 二、改进优先级

```
P0 立即修复（不影响功能）
├── 统一 CSS 变量命名体系
├── 替换 emoji → Lucide 图标
├── 替换 HTML entity → Lucide 图标
└── Admin 页面硬编码颜色纳入变量

P1 短期（1-2天）
├── 按钮层级标准化
├── 圆角系统化
├── 间距 4px 网格化
├── Loading 状态统一
└── Hover 效果统一

P2 中期（1周）
├── 暗色模式配色优化
├── 组件库统一（移除 Element Plus）
├── 操作反馈 Toast 机制
└── 动画时长标准化

P3 长期（品牌升级）
├── 设计规范文档 / Figma
└── 组件 Storybook
```

---

## 三、设计令牌重构

### 新变量体系（统一为 `--sf-*` 前缀）

```css
/* ========== 颜色 ========== */
--sf-primary           /* 主色：品牌蓝 #6366f1 */
--sf-primary-hover
--sf-primary-subtle
--sf-accent            /* 强调色：青色 #06b6d4 */
--sf-success           /* 成功：#10b981 */
--sf-warning           /* 警告：#f59e0b */
--sf-danger            /* 危险：#ef4444 */
--sf-info              /* 信息：#6366f1 */

/* 文字 */
--sf-text-primary      /* #111827 */
--sf-text-secondary    /* #6b7280 */
--sf-text-muted        /* #9ca3af */

/* 背景 */
--sf-bg-base           /* #f9fafb */
--sf-bg-card           /* #ffffff */
--sf-bg-elevated       /* #f3f4f6 */

/* 边框 */
--sf-border            /* #e5e7eb */

/* ========== 圆角 ========== */
--sf-radius-sm   6px   /* 标签、小徽章 */
--sf-radius-md   10px  /* 输入框、下拉框 */
--sf-radius-lg   14px  /* 卡片 */
--sf-radius-xl   20px  /* 大卡片、弹窗 */
--sf-radius-full 9999px /* 药丸按钮、筛选标签 */

/* ========== 间距 ========== */
--sf-space-1   4px
--sf-space-2   8px
--sf-space-3   12px
--sf-space-4   16px
--sf-space-5   20px
--sf-space-6   24px
--sf-space-8   32px
--sf-space-10  40px

/* ========== 阴影 ========== */
--sf-shadow-sm
--sf-shadow-md
--sf-shadow-lg

/* ========== 动画 ========== */
--sf-ease-standard  cubic-bezier(0.4, 0, 0.2, 1)
--sf-ease-bounce    cubic-bezier(0.34, 1.56, 0.64, 1)
--sf-duration-fast   150ms
--sf-duration-normal 200ms
--sf-duration-slow   300ms
```

---

## 四、各页面改进清单

### 4.1 Home.vue

| 问题 | 改进方案 |
|------|---------|
| 侧边栏 stat 卡片使用 emoji 🔥 | 替换为 Lucide `Flame` 图标 |
| 里程碑数据使用多个 emoji | 统一替换为对应 Lucide 图标 |
| 卡片 hover 效果已有 | 保持 |

### 4.2 Login.vue / Register.vue

| 问题 | 改进方案 |
|------|---------|
| Login 用 `--primary/--accent`，Register 用 `--color-*` | 统一迁移到 `--sf-*` |
| Login.vue 硬编码 `rgba(99,102,241,0.3)` | 纳入 `--sf-shadow-lg` |
| 渐变光球动画 | 保留，效果好 |

### 4.3 Learn.vue ⚠️ 改动最多

| 问题 | 改进方案 |
|------|---------|
| 同时混用 `--sf-*` 和 `--yt-*` | 统一为 `--sf-*` |
| 注解颜色硬编码 `#ff0000` `#2196f3` `#ff9800` | 纳入设计令牌 |
| 多处 inline style 属性 | 提取为 CSS 类 |
| 三栏布局信息密度可能过高 | 优化间距和留白 |
| 暗色模式下颜色参考方案 | 见下方暗色模式改进 |

### 4.4 Vocabulary.vue

| 问题 | 改进方案 |
|------|---------|
| 使用 `--yt-*` 变量 | 迁移到 `--sf-*` |
| 硬编码 `rgba(16,185,129,0.08)` hover | 纳入变量 |
| 卡片展开动画 | 保持 |

### 4.5 VocabularyReview.vue

| 问题 | 改进方案 |
|------|---------|
| Rating 按钮使用 emoji 😵🤔💡😊🎯 | 替换为 Lucide 图标 + 文字标签 |
| 翻牌动画 | 保持（效果好） |
| 错题 shake 动画 | 保持 |
| 空状态 🎉 | 替换为 Lucide `PartyPopper` 图标 |

### 4.6 EnglishCards.vue

| 问题 | 改进方案 |
|------|---------|
| 语法分析用 💡 emoji | 替换为 Lucide `Lightbulb` |
| 硬编码 `#ef4444` 未知卡片 | 迁移到 `--sf-danger` |
| 左侧素材列表无边框分隔 | 添加分隔线 |
| 卡片网格间距 | 标准化 |

### 4.7 DictationMode.vue

| 问题 | 改进方案 |
|------|---------|
| 整体使用 `--sf-*`，一致性较好 | 保持，只需迁移变量名 |
| 音频播放脉冲动画 | 保持 |
| 进度条颜色 | 标准化 |

### 4.8 Favorites.vue

| 问题 | 改进方案 |
|------|---------|
| 使用 `--yt-*` | 迁移到 `--sf-*` |
| 硬编码 `#fff` 多处 | 替换为 CSS 变量 |
| Tab 切换样式 | 统一按钮/标签样式 |

### 4.9 Profile.vue

| 问题 | 改进方案 |
|------|---------|
| 使用 `--yt-*` | 迁移到 `--sf-*` |
| 头像背景 `rgba(255,255,255,0.3)` | 标准化 |
| Banner 渐变背景 | 保留，但颜色纳入变量 |

### 4.10 LearningCenter.vue

| 问题 | 改进方案 |
|------|---------|
| 🔥 streak emoji | 替换为 Lucide `Flame` |
| 统计卡片硬编码颜色 `#f59e0b` `#8b5cf6` | 纳入语义变量 |
| 使用 Element Plus 分页 | 统一为 SfPagination |

### 4.11 Materials.vue

| 问题 | 改进方案 |
|------|---------|
| `sf-dropdown-item` 硬编码样式 | 提取为正式 CSS 类 |
| 下拉激活用硬编码 `#fff` | 替换为 `--sf-text-primary` |
| 玻璃态效果 | 保留 |

### 4.12 Admin 页面 ⚠️ 问题最严重

| 问题 | 改进方案 |
|------|---------|
| AdminLayout 完全硬编码 `#0f172a` `#1e293b` | 纳入 `--sf-*` 暗色模式变量 |
| 侧边栏深色主题与主站不一致 | 统一设计系统 |
| Dashboard stat 颜色硬编码 `#2563eb` 等 | 迁移到语义变量 |
| 图表颜色硬编码 | 统一为 `--sf-chart-*` 变量 |
| **建议**：Admin 使用独立深色主题变量（`--sf-admin-*`），避免与主站浅色主题冲突 | |

### 4.13 AnnouncementBanner.vue

| 问题 | 改进方案 |
|------|---------|
| HTML entity 图标 `&#9888;` `&#10003;` 等 | 替换为 Lucide 图标 |
| 渐变背景 | 保留，颜色纳入变量 |

---

## 五、暗色模式配色优化（参考 PPT 深灰风格）

当前暗色模式：`#0f172a`（接近纯黑），建议调整为：

```
/* Light 模式 */
--sf-bg-base: #ffffff
--sf-bg-card: #ffffff
--sf-bg-elevated: #f3f4f6
--sf-text-primary: #111827

/* Dark 模式（优化后） */
--sf-bg-base: #1a1a2e        /* PPT 参考: #1E1E1E / #2D2D2D */
--sf-bg-card: #252540
--sf-bg-elevated: #2d2d4a
--sf-text-primary: #e2e8f0
--sf-text-secondary: #94a3b8
--sf-border: rgba(255,255,255,0.08)
```

关键改动：
- 背景从 `#0f172a` → `#1a1a2e`（没那么黑，更现代）
- 卡片有微妙渐变感
- 边框使用 rgba 透明色

---

## 六、组件库统一

### 移除 Element Plus

以下 Element Plus 组件应替换为 Sf* 组件：

| Element Plus | 替换为 | 影响页面 |
|-------------|--------|---------|
| `el-pagination` | `SfPagination` | Materials, Vocabulary, LearningCenter |
| `el-form` | `SfForm/SfFormItem` | Profile, MaterialsManage |
| `el-input` | `SfInput` | 多处 |

### 统一图标

全部使用 `lucide-vue-next`，禁止 emoji/html entity。

---

## 七、文件改动清单

| 阶段 | 文件 | 改动 |
|------|------|------|
| P0 | `styles/design-tokens.css` | 重构为完整 `--sf-*` 令牌 |
| P0 | `styles/global.css` | 迁移所有变量引用 |
| P0 | `views/Home.vue` | 替换 emoji |
| P0 | `views/VocabularyReview.vue` | 替换 emoji → Lucide |
| P0 | `views/LearningCenter.vue` | 替换 🔥 emoji |
| P0 | `views/EnglishCards.vue` | 替换 💡 emoji |
| P0 | `views/AnnouncementBanner.vue` | 替换 HTML entity |
| P0 | `views/admin/AdminLayout.vue` | 硬编码颜色变量化 |
| P0 | `views/admin/Dashboard.vue` | 硬编码颜色变量化 |
| P1 | `components/ui/SfButton.vue` | 按钮层级标准化 |
| P1 | `components/common/FilterChip.vue` | hover 效果统一 |
| P1 | `styles/responsive.css` | 间距系统化 |
| P2 | `App.vue` | 暗色模式配色更新 |
| P2 | `views/Learn.vue` | 变量统一 + 样式优化 |
| P2 | 其余所有 view 文件 | 变量迁移 |
| P3 | 文档 | 设计规范 + Storybook |

---

## 八、预期效果

| 改进项 | 效果 |
|--------|------|
| CSS 变量统一 | 消除三套系统混用的混乱 |
| 替换 emoji | 专业度大幅提升 |
| 组件统一 | UI 一致性提升 |
| 暗色模式优化 | 现代感+护眼 |
| Admin 统一 | 管理后台不再像另一个项目 |
| Hover/Loading 统一 | 交互体验提升 |

---

> **核心原则**：配色克制、排版分层、素材统一、交互好用。UI 的目的不是做成艺术品，是**不劝退用户**。

---

## 附录：设计资源

**参考设计方向（来自 PPT）：**
- 深灰背景 (#1E1E1E / #2D2D2D) + 高对比色文字
- 模块化卡片布局，清晰的层级
- 主/次/危险按钮三色体系（蓝/灰/红）
- 步骤流程式设计

**图标资源：**
- `lucide-vue-next`（已安装）

**素材网站（来自 PPT）：**
- 花瓣网
- 站酷网