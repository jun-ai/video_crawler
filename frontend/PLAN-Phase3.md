# UI 精细化改进计划 - 对标 SpeakVlog 截图（第三阶段）

## Context
前两阶段已完成：配色迁移蓝+去侧边栏+两栏布局、登录页居中卡片+渐变、绿色辅助色、词汇卡片优化、首页侧栏。
用户提供了 11 张 SpeakVlog 截图（包括 6 张新截图：英语卡片页x3、收藏页、学习记录页、最新学习页），对照后发现仍有 6 大差距需要补齐。

---

## Phase 1: Learn.vue 学习页细节增强（低风险高收益）

### 1A. 活跃字幕黄色高亮
**文件**: `src/views/Learn.vue` (CSS ~L3255)

当前活跃字幕用红色左边框 `border-left-color: var(--yt-red)` + 浅红背景。SpeakVlog 用黄色背景。

- `.subtitle-item.active` background 改为 `var(--yt-highlight-bg, #fef3c7)` (琥珀黄)
- border-left 改为琥珀色 `var(--yt-highlight-border, #f59e0b)`
- `.subtitle-item.active .sub-text` font-weight 提升到 700
- `.subtitle-item.active .sub-text-cn` 使用琥珀色调
- 暗色模式新增变量 `--yt-highlight-bg: rgba(251, 191, 36, 0.15)`

### 1B. 字幕中解读词汇绿色高亮
**文件**: `src/views/Learn.vue` (JS getAnnotatedText + CSS)

当前 `getAnnotatedText()` 只处理用户标注。需要额外高亮解读面板中的单词/短语。

- 扩展 `getAnnotatedText()`：在渲染前，查找 `interpretation.value.words` + `interpretation.value.phrases` 中出现在字幕文本中的词汇
- 匹配到的词汇包裹 `<span class="interp-word-highlight">` 样式：
  - `border-bottom: 2px solid var(--yt-study-green)`
  - `background: var(--yt-study-green-softer)`
- 优先级：用户标注 > 自动解读高亮（避免冲突）
- 点击高亮词跳转到对应字幕时间戳

### 1C. 播放模式下拉菜单
**文件**: `src/views/Learn.vue` (模板+脚本+CSS)

SpeakVlog 有播放模式选择器，我们没有。

- 新增 ref: `const playMode = ref('single')`
- 4 种模式：`single`(单次播放) / `single-loop`(单集循环) / `continuous`(连续播放) / `sentence-loop`(单句循环)
- 字幕面板 header 区域新增 `el-dropdown`，显示当前模式图标+文字
- 修改 `onTimeUpdate` 和 video `@ended` 事件：
  - `single`: 默认（播完停止）
  - `single-loop`: `video.currentTime = 0; video.play()`
  - `continuous`: 自动播放下一句字幕
  - `sentence-loop`: 循环当前活跃字幕段（回跳到 `sub.start_time`）

---

## Phase 2: 新页面「英语卡片」(EnglishCards.vue)

这是最大的新功能。SpeakVlog 有独立的词汇浏览页。

### 2A. 新建 `src/views/EnglishCards.vue`

**页面布局**（复用 Home.vue 侧栏模式）：
```
+----------------------------------------------------------+
| PageHeader: "English Cards"       [Hide Chinese toggle]  |
+----------------------------------------------------------+
| LEFT SIDEBAR (280px)    | RIGHT MAIN (flex: 1)           |
| - Search input          | - Tabs: Words/Phrases/         |
| - Video list scrollable |   Idiomatic Expressions+counts |
|   - Each video item     | - Filter chips: All/Unmarked   |
|     with camera icon    |   /Known/Unknown + counts      |
|     + title             | - 4-column card grid           |
|     - Active: selected  |   (responsive to 2-col mobile) |
+----------------------------------------------------------+
```

**左侧栏 (.ec-sidebar)**:
- 搜索框（按视频标题过滤）
- 可滚动视频列表：缩略图(48px) + 标题 + 词汇数 badge
- 选中项高亮（蓝色背景 + 右侧强调线）
- 点击设置 `selectedMaterialId`

**右侧主区 (.ec-main)**:
- Tab 栏：Words(N) / Phrases(N) / Idiomatic Expressions(N) — 下划线风格
- Filter chips：All(N) / Unmarked(N) / Known(N) / Unknown(N)
- "隐藏中文" 开关按钮
- 卡片网格：CSS Grid `grid-template-columns: repeat(4, 1fr)`

**单词/短语卡片 (.ec-vocab-card)**:
- 第一行：粗体单词(18px) + 音标(italic) + 词性标签(vt./vi./phr.)
- 中文 + 英英释义
- 例句在绿色边框块中
- 选中卡片：`background: var(--yt-study-green-softer)`

**地道表达卡片（更丰富）**:
- "字幕原文" 区：英文原句
- "中文翻译" 区：中文翻译
- "表达分析" 区（灯泡图标）：
  - 结构解析 (`structure_analysis`)
  - 举一反三 (`similar_expressions`)
  - 使用场景 (`usage_scenario`)
  - 相似表达 (`alternative_phrasings`)

**数据流**:
- `materialAPI.getList({ limit: 100 })` → 加载视频列表
- `materialAPI.getInterpretation(selectedMaterialId)` → 加载解读
- `interpretationAPI.getStatus(selectedMaterialId)` → 加载学习状态

### 2B. 路由注册
**文件**: `src/router/index.js`
- 新增 `/english-cards` 路由

### 2C. 导航更新
**文件**: `src/App.vue`
- navItems / mobileNavItems 添加"英语卡片"入口
- 考虑将原"词汇"入口替换为"英语卡片"

---

## Phase 3: 收藏页重设计

**文件**: `src/views/Favorites.vue`

### 当前 vs 目标
- 当前：视频卡片网格
- SpeakVlog：双 Tab（字幕收藏 + 词汇收藏）+ 纵向列表

### 3A. 模板重设计

**Tab 栏**（绿色下划线指示器）:
- "字幕" Tab
- "词汇" Tab

**字幕 Tab 内容**:
- 按日期分组（"今天"、"昨天"、"更早"）
- 纵向卡片列表：
  - 英文短语（粗体）
  - 中文翻译（引号包裹）
  - 类别标签 + 时长
  - "去练习"按钮（绿色圆角）
  - 三点菜单（删除）

**词汇 Tab 内容**:
- 纵向卡片或网格
- 单词 + 音标 + 翻译 + 来源视频

**API 注意**: 字幕级收藏需后端支持。若无 API，字幕 Tab 显示空状态。

---

## Phase 4: 学习中心增强

**文件**: `src/views/LearningCenter.vue`

### 4A. Tab 导航替代多 Section
当前有 3 个独立区域，改为 Tab 导航：
- "最近学习" | "已完成" | "收藏"
- 下划线风格 Tab

### 4B. 视频卡片增强
**文件**: `src/components/common/VideoCard.vue`

新增 props:
- `showPlayIcon: Boolean` — 缩略图中央半透明播放图标
- `completed: Boolean` — 绿色"已完成"徽章
- `progressText: String` — 进度文字（"学习于今天，看至57%"）

---

## Phase 5: Learn.vue 词汇卡片增强

**文件**: `src/views/Learn.vue`

### 5A. 地道表达卡片富字段
当前语法卡片展开只有 explanation。需增加：
- 字幕原文 (`context_sentence`)
- 中文翻译 (`context_translation`)
- 表达分析：结构解析、举一反三、使用场景、相似表达
- 所有字段 `v-if` 降级，后端缺失时隐藏

### 5B. 卡片选中状态
- 展开卡片添加浅绿背景 + 绿色边框

### 5C. 音标显示增强
- 字号 12→13px，颜色更明显

---

## Phase 6: 设计系统更新

### 6A. design-tokens.css 新增变量
```css
:root {
  --yt-highlight-bg: #fef3c7;
  --yt-highlight-border: #f59e0b;
}
[data-theme="dark"] {
  --yt-highlight-bg: rgba(251, 191, 36, 0.15);
  --yt-highlight-border: rgba(251, 191, 36, 0.5);
}
```

### 6B. FilterChip 计数显示
- 新增 prop `count: Number`
- count 不为 null 时标签后显示小圆角数字徽章

---

## 执行顺序

| 步骤 | 任务 | Phase | 复杂度 | 文件 |
|------|------|-------|--------|------|
| 1 | design-tokens 新增变量 | 6A | 极小 | design-tokens.css |
| 2 | 活跃字幕黄色高亮 | 1A | 小 | Learn.vue CSS |
| 3 | FilterChip 计数显示 | 6B | 小 | FilterChip.vue |
| 4 | VideoCard 播放图标+完成徽章 | 4B | 小 | VideoCard.vue |
| 5 | 解读词汇绿色高亮 | 1B | 中 | Learn.vue JS+CSS |
| 6 | 播放模式下拉菜单 | 1C | 中 | Learn.vue 全部 |
| 7 | 地道表达富字段卡片 | 5A | 中 | Learn.vue 模板+CSS |
| 8 | 卡片选中态+音标增强 | 5B+5C | 小 | Learn.vue CSS |
| 9 | 学习中心 Tab 重设计 | 4A | 中 | LearningCenter.vue |
| 10 | 英语卡片新页面 | 2A | 大 | EnglishCards.vue + router + App.vue |
| 11 | 收藏页重设计 | 3A | 中大 | Favorites.vue |

## 关键文件清单

| 文件 | 改动级别 |
|------|---------|
| `src/views/Learn.vue` | 中改（黄色高亮+绿色词汇高亮+播放模式+富卡片） |
| `src/views/EnglishCards.vue` | **新建**（完整页面） |
| `src/views/Favorites.vue` | 重写（双Tab+纵向列表） |
| `src/views/LearningCenter.vue` | 中改（Tab导航+增强卡片） |
| `src/components/common/VideoCard.vue` | 小改（播放图标+完成徽章） |
| `src/components/common/FilterChip.vue` | 小改（计数显示） |
| `src/styles/design-tokens.css` | 小改（高亮变量） |
| `src/router/index.js` | 小改（新路由） |
| `src/App.vue` | 小改（导航入口） |

## 风险与注意事项

1. **后端数据**: 地道表达富字段需后端 AI prompt 更新。前端 `v-if` 降级。
2. **字幕级收藏 API**: 收藏页需后端支持。若无，字幕 Tab 显示空状态。
3. **Learn.vue 行数**: 已 4800 行，新增约 150 行。
4. **暗色模式**: 所有新 CSS 必须用 `--yt-*` 变量。
5. **响应式**: 覆盖 1280/1024/768/480 断点。

## 验证方式
每步完成后：
1. `cd frontend && npm run build`
2. 对比 SpeakVlog 11 张截图
3. 测试 1280px / 768px / 480px 断点
4. 测试暗色模式
