# Favorites.vue 深度分析报告

> 模块：我的收藏 / 收藏本
> 路由：`/favorites`（推测，对应文件 `Favorites.vue`）
> 文件：`/root/video_crawler/frontend/src/views/Favorites.vue`（901 行）
> 分析日期：2026-06-18
> 分析范围：UI 布局、功能完整性、后端 API 适配、数据加载性能

---

## 0. 模块现状速览

| 维度 | 现状 |
|---|---|
| Tab | 「字幕」「单词/短语」两个 |
| 字幕收藏数据源 | 走 N+1 循环：先 `favoriteAPI.getList` 拿材料，再逐个材料 `subtitleBookmarkAPI.getList` 拉字幕收藏 |
| 词汇数据源 | 直接 `vocabularyAPI.getList`，支持分页 |
| 收藏的视频（material 级） | **未展示**。虽然后端有 `Favorite` 表和 `favoriteAPI`，但页面只把它当作字幕收藏的"中间查询表" |
| 进入学习 | "去练习"按钮只跳 `/learn/:material_id`，不带 `start_time`，玩家从视频开头播放 |
| 取消收藏 | 字幕：通过右上角 `SfDropdown → 取消收藏`。词汇：通过 `SfDropdown → 删除` |
| 笔记/标签/文件夹 | **全部缺失**。后端 `SubtitleBookmark.note` 字段已存在但前端未暴露 |
| 布局 | 单列卡片列表（无网格/列表切换），按"今天/昨天/近一周/更早"分 4 组 |
| 信息密度 | 字幕卡片：英文+中文+来源 tag+时长+练习次数。词汇卡片：单词+音标+翻译+来源 |
| 空状态 | 两个 Tab 各自有 `EmptyState`，CTA 都是"去学习" |

---

## 1. P0 — 必须立即修复（Bug / 数据丢失 / 性能黑洞）

### P0-1 字幕收藏的分页是"假分页"，数据会被截断

**问题描述**
- 第 206–207 行声明了 `subtitlePage` / `subtitlePageSize`，第 100–108 行渲染了 `<el-pagination>`，点击翻页会触发 `@current-change="loadSubtitleBookmarks"`。
- 但 `loadSubtitleBookmarks`（第 252–305 行）**完全没读** `subtitlePage.value`：
  - 第 258 行硬编码：`favoriteAPI.getList({ page: 1, page_size: 100 })`
  - 第 263–296 行用 `for...of materials` 一次性把所有材料的字幕收藏全部塞进 `subtitleBookmarks.value`
- 结果：
  1. 用户收藏 **>100 个材料** 时，后面收藏的材料的字幕收藏**静默丢失**（永远不显示）。
  2. 第 4 段字幕收藏永远加载不到，"翻页"按钮点 N 次都只显示同一批。
- 词汇 Tab 的分页是真分页（第 334–336 行正确传了 `vocabPage.value`），但**首次进入页面没有重置 page=1**，切换 Tab 时 `vocabPage` 仍是 1，行为勉强对；但用户多次进入页面后 `vocabPage` 会保留上次的值，可能直接跳到上次离开的页。

**怎么改**
- 后端新增 `GET /api/learning/bookmarks?page=1&page_size=20&material_id=&keyword=`：一次性返回当前用户**全部字幕收藏**（join Subtitle + Material），按 `created_at desc` 排序，支持分页、关键字搜索、按 material 过滤。这是治本方案。
- 前端改造 `subtitleBookmarkAPI` 增 `getAll({page, page_size, keyword, material_id})`，`loadSubtitleBookmarks` 改为单次请求 + 真正使用 `subtitlePage.value`。
- 在切换 Tab / 退出登录时把 `subtitlePage = 1`、`vocabPage = 1`。

**预计工作量**：后端 1 人天（新增路由 + schema），前端 0.5 人天（去掉 N+1 循环 + 修分页）。合计 **1.5 人天**。

**影响面**
- 数据完整性：修复后会显式加载所有收藏，符合用户直觉。
- 性能：网络请求从 O(N materials × 2 calls) 降到 O(1)。
- 接口扩展性：未来加搜索、按材料筛选有了落点。

---

### P0-2 N+1 查询：每次进入页面发起几十到几百个请求

**问题描述**
- 第 252–305 行 `loadSubtitleBookmarks` 用了典型的反模式：
  ```js
  for (const mat of materials) {
    const bookmarks = await subtitleBookmarkAPI.getList(mat.id)   // 1 req
    if (!subtitleDetailsMap.value[mat.id]) {
      subtitles = await materialAPI.getSubtitles(mat.id)         // 1 req
      ...
    }
  }
  ```
- 用户收藏 30 个材料 = 60 个 HTTP 请求，全部串行（`for...of await`）。在 4G/弱网下首次加载 5–15 秒非常常见。
- 第 269–276 行的"缓存"是按 `material_id` 缓存的，**只在组件挂载期间有效**——切到「单词/短语」再切回来，缓存还在；但只要页面刷新或 router 重新进入组件就清零。
- "刷新"按钮（第 14–17 行）每次都重新跑这套循环。

**怎么改**
- 同 P0-1，最佳方案就是后端一次性 join 返回。
- 兜底方案（不立刻改后端）：前端 `Promise.all` 改并发，但请求数没变，只是把串行 10s 压到并行 2s——治标不治本。
- 兜底方案 2：用 `Promise.allSettled` 容错，单个材料失败不影响整体，并在末尾给用户提示"X 个材料加载失败"。

**预计工作量**：并入 P0-1，**0 工时**（已被覆盖）。

**影响面**
- 性能与流量，移动端明显。
- 用户感知：当前"刷新"按钮转圈时间长，部分用户会误以为卡死多次点击。

---

### P0-3 "去练习"按钮没有跳转到对应字幕时间点

**问题描述**
- 第 74–82 行卡片右下角"去练习"按钮，点击后调用 `goLearnSubtitle(item)`（第 307–311 行）：
  ```js
  router.push(`/learn/${item.material_id}`)
  ```
- `item.start_time` 拿到了，后端 `SubtitleBookmarkResponse` 也包含 `subtitle_start_time`（learning.py 第 1277 行），但路由里**完全没有传**。
- 用户点击"去练习"，期望"马上跟读这句"，实际落到了视频开头，必须自己拖进度条或者点字幕列表才能定位。
- 这是收藏 → 学习闭环里最关键的一步断裂。

**怎么改**
- 路由改为：`router.push({ path: \`/learn/\${item.material_id}\`, query: { t: item.start_time, bookmark: item.id, sub: item.subtitle_id } })`
- `/learn` 页面（需要看一下 `Learn.vue` 是否支持 query）在 `onMounted` 里读取 query，对 `video.currentTime = t/1000`，并自动定位到当前字幕。
- 学习页如果有"恢复上次位置"的逻辑，要和这次的 `t` 协调优先级——建议 `?t=` 显式最高。

**预计工作量**：Favorites.vue 改动 0.1 人天；`Learn.vue` 适配（如未支持）0.3 人天。合计 **0.4 人天**。

**影响面**
- 收藏 → 学习路径从 4 步（找视频 → 拖进度 → 找字幕 → 开始跟读）压到 1 步。
- 直接拉升**收藏的复访率**和**练习转化率**——这是产品最关键的转化指标。

---

## 2. P1 — 高价值功能 / UX 改进

### P1-1 没有"视频收藏"Tab，material 级收藏不可见不可管理

**问题描述**
- 后端 `Favorite` 表 + `favoriteAPI.add/remove/check/getList`（`/root/video_crawler/backend/app/routers/favorites.py`）存在且完整。
- 但 Favorites.vue 顶上的 Tab 只有"字幕 / 单词/短语"，material 级别收藏**无处显示**，用户也无法在这里取消对整个视频的收藏。
- 用户在某视频页点了星标收藏了视频，进入"我的收藏"看不到，会以为收藏没生效。

**怎么改**
- 加第三个 Tab「视频」，从 `favoriteAPI.getList` 直接拉，复用现有的卡片样式（视频列表卡片已经在 `/materials` 等页面有了，可抽成 `<MaterialCard>` 组件）。
- 同时把第 258 行的 `favoriteAPI.getList` 复用为新 Tab 的数据源，移除中间查询用途。

**预计工作量**：前端 0.5 人天（如果有 MaterialCard 组件则 0.3）。合计 **0.5 人天**。

**影响面**
- 让"我的收藏"语义完整。
- 减少用户在视频详情页和收藏页之间反复跳。

---

### P1-2 不支持笔记 / 标签 / 文件夹

**问题描述**
- 后端 `SubtitleBookmark` 表已有 `note` 字段（models.py 第 288 行），整个 Schema 已就位，前端从未使用。
- 用户收藏一句台词，3 周后回来只看到一句英文，没有任何上下文线索（"这是哪个场景？为什么要收藏？"）。很容易遗忘。
- 词汇也一样：用户只能看到单词+翻译+context（context 字段其实存的是字幕原文句子，命名误导，见 P2-4）。

**怎么改**
- 字幕卡片：右上角 `SfDropdown` 扩出三个动作：**编辑笔记**（弹窗/行内展开）、**复制原句**、**分享**。笔记用单行 `<textarea>`，保存后 `subtitleBookmarkAPI.update(id, {note})`——需要后端补 PATCH 接口。
- 长期：支持**用户自定义标签**（复用现有 `tags` 表，新增 `bookmark_tags` 多对多），或允许把 bookmark 放进**收藏夹**（新增 `FavoriteFolder` 表）。这是 P1 的延伸，可拆 v2。

**预计工作量**：笔记 0.5 人天（前端 + 后端 PATCH）。标签/收藏夹 2 人天起。

**影响面**
- 把"收藏本"从"过期清单"升级为"个人语料库"。
- 与产品"间隔重复"定位契合。

---

### P1-3 词汇 Tab 没有"已掌握"开关、复习队列、SM-2 复习提醒

**问题描述**
- 后端 Vocabulary 模型（models.py 第 123–158 行）已经有：
  - `mastered: Boolean`（第 133 行）
  - `next_review_at: DateTime`（第 135 行，SM-2 间隔重复）
  - `/api/learning/vocabulary?mastered=true` 过滤（第 200 行）
  - `/api/learning/vocabulary/{id}/master` 标记掌握（第 272 行）
- 前端 Vocab 卡片只有一个删除按钮和一个发音按钮，**完全没暴露**这些能力。
- 用户一旦收藏超过 50 个生词，就会变成"收藏即遗忘"。

**怎么改**
- 在 Vocab 卡片左侧/右侧加 ⭐ / ✅ 按钮：`vocabularyAPI.markMastered(id)`，乐观更新 `item.mastered = true`，加 CSS 灰显 + 删除线。
- 头部加 3 个筛选 chip：全部 / 待复习（`next_review_at <= now()`） / 已掌握。后两个是 query param。
- "待复习" Tab 默认置顶，按 `next_review_at asc` 排序，后端 `sort_by=review_count` 已预留。
- 顶栏加一个小红点：`dueCount = vocabList.filter(v => v.next_review_at <= now()).length`。

**预计工作量**：前端 0.8 人天，后端可能要补 `due_count` 聚合接口或前端先做粗筛。合计 **1 人天**。

**影响面**
- 词汇功能从"记事本"升级为"复习系统"，直接呼应英语学习产品核心价值。

---

### P1-4 没有搜索和按视频/标签筛选

**问题描述**
- 字幕卡片数量增长后，列表几百条，找一句特定台词=大海捞针。
- 当前唯一过滤维度是日期分 4 组，对长期用户意义不大。
- 第 213–233 行 `groupedSubtitles` 只有 4 个桶（今天/昨天/近一周/更早），收藏 200 条时"更早"组依然 100+ 条。

**怎么改**
- 顶部加搜索框（icon + input）：input 双向绑 `searchKeyword`，前端 300ms debounce，调 `subtitleBookmarkAPI.getAll({keyword})`（依赖 P0-1 的新接口）。
- 加视频过滤：把 `material_title` 提取成 chip 横向滚动条，点击筛选。
- 日期分组改为按真实日期（`YYYY-MM-DD`），加 sticky header；如果用户日均收藏 >5，再切回"按周"分组。

**预计工作量**：**0.5 人天**（搜索框 + chip 过滤 UI）。

**影响面**
- 信息密度高的页面，搜索是基本盘。
- 让用户感觉"我的收藏真的属于我"。

---

### P1-5 没有批量操作

**问题描述**
- 单条删除只能走 `SfDropdown → 删除`，遇到 30 条过期收藏，30 次确认弹窗，30 次网络请求。
- 没法批量导出（PDF/CSV/有道/扇贝导入格式），没法跨设备迁移。

**怎么改**
- 卡片左上角加 checkbox（淡灰，hover 时显示），选中后顶部出现"已选 N 项"操作条：删除、移入收藏夹（待 P1-2）、复制全部、导出 JSON。
- 至少先把"批量删除"做了，价值最大。
- 导出 JSON 0.5 人天，前端 Blob 下载即可。

**预计工作量**：批量删除 0.5 人天；导出 0.3 人天。合计 **0.8 人天**。

**影响面**
- 重度用户的留存。
- 导出 JSON 是用户信任感的来源（"我的数据属于我"）。

---

### P1-6 「收藏本」标题与导航不一致

**问题描述**
- `<h1 class="fav-page-title">收藏本</h1>`（第 13 行）——「收藏本」是日语式表达，中文母语者第一眼可能觉得别扭。
- 推测路由/面包屑/侧边栏叫"我的收藏"。
- 命名不一致影响可发现性（用户在空状态下点"去学习"再回来，可能找不到回来的入口）。

**怎么改**
- 与产品和设计对齐命名。建议统一为「我的收藏」。
- 如果产品定位就是"口袋本/语料库"风格，可以保留「收藏本」但要在全局导航也统一用这个词。

**预计工作量**：**0.1 人天**。

**影响面**
- 文案一致性 = 品牌一致性。

---

### P1-7 词汇卡片"来源 context"字段命名误导，且渲染像状态徽标

**问题描述**
- 第 129–131 行渲染的是 `item.context`，根据 models.py 第 132 行 `context: 上下文句子`——也就是来源字幕的原文。
- 但前端把"来源：xxx"放进了一个圆角小盒子里（CSS 第 748–756 行 `.vocab-context`），视觉上像状态/标签，不像引文。
- 用户看到"来源：I didn't mean to hurt you."可能误以为这是分类或场景说明。

**怎么改**
- CSS 改成左 border 引用条样式（左侧 3px 主色，背景用 `--color-bg-elevated`），并加上引号 `「...」` 或 `"..."`。
- 字段名 UI 上也建议改为"原句"或"出处"，更直观。

**预计工作量**：**0.1 人天**。

**影响面**
- 视觉层级更清晰，新用户秒懂。

---

## 3. P2 — 体验润色

### P2-1 单项 `SfDropdown` 包一项菜单是浪费

**问题描述**
- 第 65–73、134–142 行的 `SfDropdown` 里都只有一个 `dropdown-item`（取消收藏 / 删除）。
- 点击展开还要再点一下，徒增交互成本。
- 把展开动画、定位、ESC 关闭都白跑了。

**怎么改**
- 改成直接的 `SfButton ghost size="sm"` + `<Trash2 />` 图标按钮，长按/二次确认走 `showConfirm`。
- 或者保留 dropdown 但填充更多操作："复制原句"、"分享"、"编辑笔记"，为 P1-2 铺垫。

**预计工作量**：**0.1 人天**。

**影响面**
- 降低操作摩擦 1 次点击。

---

### P2-2 加载状态只有全屏 v-loading，没有骨架屏

**问题描述**
- 第 40 行 `v-loading="subtitleLoading"` 是 Element Plus 的全屏 loading，第一次进入时整个内容区空，体验突兀。
- 用户感知"页面没出来 → 是不是坏了？"。

**怎么改**
- 改用列表骨架：每条卡片渲染一个 `<div class="skeleton-card">`，3–5 条占位。
- 配合 P0-1 后端单次接口，首屏 200ms 内可见内容。

**预计工作量**：**0.2 人天**。

**影响面**
- 感知性能 + 品牌专业感。

---

### P2-3 字幕卡片没有视频封面缩略图

**问题描述**
- 卡片左侧只用了一个 3px 渐变条（CSS 第 545–556 行 `::before`）。
- 用户收藏 50 句来自 30 个不同视频时，肉眼分辨很慢。
- 后端 `/api/favorites` 已经返回了 `cover_path`（favorites.py 第 134 行），数据可用。

**怎么改**
- 卡片左侧放 48×48 圆角缩略图（懒加载 + `loading="lazy"`），点击缩略图直接跳视频详情（而不是跳到学习页，与"去练习"区分）。
- 如果觉得卡片会变高，可以把现有 meta 行折到缩略图右侧。

**预计工作量**：**0.3 人天**。

**影响面**
- 信息识别速度 ↑，符合"Fluenty"清新高效气质。

---

### P2-4 "练习 N 次"信息弱，缺少最后练习时间 / 复习入口

**问题描述**
- 第 59–61 行只是显示"练习 N 次"，没有最后练习时间。
- 收藏 2 个月没碰的字幕和昨天刚练的视觉上无差别，无法驱动用户回到"该复习的句子"。

**怎么改**
- 改成"3 天前练过 5 次"，hover tooltip 显示完整时间线。
- 旁边加"复习"快捷按钮（直接调 `subtitleBookmarkAPI.incrementPractice`）。
- 卡片底色根据 `last_practiced_at` 距离衰减（需要后端补字段）。

**预计工作量**：**0.3 人天**（如不补后端字段，纯展示 0.1 人天）。

**影响面**
- 让"练习次数"从数字变成可执行的复习钩子。

---

### P2-5 顶部"刷新"按钮位置与回退按钮冲突

**问题描述**
- 第 10–17 行：左侧"← 返回"圆形按钮 + 右侧"刷新"按钮，挤在 900px 容器内。
- 用户视线中心是标题，第 14 行的"刷新"按钮和标题视觉权重接近，可能被误读为次级 CTA。

**怎么改**
- 把"刷新"挪到 Tab 行的右侧（与 Tab 同高），图标按钮即可，省一个按钮文字。
- 或者干脆删掉——下拉刷新 / 自动 30s 拉新更现代。

**预计工作量**：**0.1 人天**。

---

### P2-6 移动端时长显示拥挤

**问题描述**
- 第 881–884 行（mobile）`.fav-card-meta` flex-wrap 已开，但练习次数 pill 是 10px 内边距 + 白底渐变，在 480px 屏幕下视觉重。
- 移动端卡片整体偏高（20px padding × 2 + 多行文本）。

**怎么改**
- 移动端隐藏"未练习"时长，只在练习过的时候显示。
- 移动端 padding 收到 14px。
- 卡片用 swipe-to-delete（vanilla touch + confirm）。

**预计工作量**：**0.2 人天**。

---

### P2-7 图标库与设计规则不一致

**问题描述**
- `AGENTS.md` 设计规则要求"使用 Iconify 图标库"，但 Favorites.vue 第 180–186 行 import 的是 `lucide-vue-next`。
- 与设计系统一致性问题。

**怎么改**
- 全局审计：是否其他文件也用 lucide-vue-next？如果是项目惯例，AGENTS.md 规则要更新；如果要严格执行，逐文件替换。
- 替换为 `@iconify/vue` + Iconify 名称（如 `@iconify-icons/lucide/arrow-left`）。

**预计工作量**：跨文件审计 0.5 人天；本文件替换 0.1 人天。

**影响面**
- 设计一致性、Bundle 体积（iconify 可 tree-shake）。

---

### P2-8 日期分组只有 4 个桶，长期用户不可用

**问题描述**
- 第 213–233 行 `groupedSubtitles` 只分"今天/昨天/近一周/更早"。
- 收藏 200 条时"更早"组会塞 150+ 条，列表退化。

**怎么改**
- 默认按真实日期（`MM-DD`）分组，sticky header。
- 用户可切到"按周"或"按月"视图，存 localStorage。
- 配合 P1-4 搜索，这是搜索替代不了的"浏览"路径。

**预计工作量**：**0.3 人天**。

---

### P2-9 `favoriteAPI.getList` 后端实现效率问题

**问题描述**
- `favorites.py` 第 110–112 行 `total = len(result.scalars().all())` 把所有行拉到 Python 端再 `len()`，应该用 `func.count(*)`：
  ```python
  total_query = select(func.count()).select_from(Favorite).where(...)
  ```
- 收藏 1 万条时这一句会爆内存。
- 同时 `favorites` 表没有 `(user_id, created_at)` 复合索引，`order_by created_at desc` 会慢。

**怎么改**
- 改用 `select(func.count(Favorite.id))`。
- 加索引 `Index('idx_fav_user_created', 'user_id', 'created_at')`。
- 这是性能优化，但当前用户量小不紧急——**P2**。

**预计工作量**：**0.2 人天**。

---

### P2-10 `subtitleDetailsMap` 缓存策略

**问题描述**
- 第 210、268–276 行的"缓存"是组件内 `ref`，没持久化、没失效策略。
- 视频的字幕极少变化，但完全没利用——每次进页面都重新拉。

**怎么改**
- 短期：在 `subtitleBookmarkAPI` 层加内存 LRU（key = material_id）。
- 长期：后端 `GET /api/materials/{id}/subtitles` 加 `ETag` / `Cache-Control: max-age=86400`。

**预计工作量**：**0.2 人天**。

---

## 4. 优先级与路线图

### Sprint 1（必修，3 人天）
| 编号 | 项 | 工时 |
|---|---|---|
| P0-1 | 后端新增 `/learning/bookmarks?page&page_size&keyword&material_id` 全量接口 | 1.0 |
| P0-1 | 前端去掉 N+1 循环 + 真分页 | 0.5 |
| P0-3 | "去练习"传 start_time + bookmark id，Learn.vue 适配 | 0.4 |
| P1-1 | 新增「视频」Tab | 0.5 |
| P2-2 | 骨架屏 | 0.2 |
| P2-1 | 简化单条 dropdown 为直接按钮 | 0.1 |
| P1-6 | 文案统一 | 0.1 |
| **合计** | | **2.8 人天** |

### Sprint 2（重要，4 人天）
| 编号 | 项 | 工时 |
|---|---|---|
| P1-2 | 笔记功能（前端 + 后端 PATCH） | 0.5 |
| P1-3 | 词汇"已掌握/待复习"开关与筛选 | 1.0 |
| P1-4 | 搜索 + 按视频过滤 | 0.5 |
| P1-5 | 批量删除 + 导出 JSON | 0.8 |
| P2-3 | 字幕卡片封面缩略图 | 0.3 |
| P2-4 | 复习次数 + 最后练习时间 | 0.3 |
| P2-7 | 图标库统一 | 0.1 |
| **合计** | | **3.5 人天** |

### Sprint 3（润色 / 性能，2 人天）
- P2-5 / P2-6 / P2-8 / P2-9 / P2-10 / P1-7

### Backlog（v2 候选）
- 收藏夹 / 用户自定义标签（书签维度）
- 与 SM-2 算法联动（推送到「今日待复习」流）
- 收藏数据可视化（哪类视频收藏最多、学习曲线）

---

## 5. 关键文件参考

- `/root/video_crawler/frontend/src/views/Favorites.vue` —— 本次分析对象
- `/root/video_crawler/backend/app/routers/favorites.py` —— material 级收藏 API（4 个 endpoint）
- `/root/video_crawler/backend/app/routers/learning.py:1225-1400` —— 字幕收藏 API（5 个 endpoint，缺全量列表）
- `/root/video_crawler/backend/app/models/models.py:123-158` —— Vocabulary 模型（含 SM-2 字段）
- `/root/video_crawler/backend/app/models/models.py:280-292` —— SubtitleBookmark 模型（含 note 字段）
- `/root/video_crawler/frontend/src/api/index.js:83-156` —— 前端 API 封装
- `/root/video_crawler/frontend/src/composables/useTTS.js` —— `speakWord` 实现
- `/root/video_crawler/frontend/src/views/Favorites.vue:252-305` —— N+1 循环位置（重点改造）

---

## 6. 不要改的事

- **不要建议改整体配色**：设计系统已锁定 #2563EB + #F59E0B，本报告所有建议都在该色板内。
- **不要重写 favorites.py 的 API 协议**：保持 `favoriteAPI.add/remove/check/getList` 4 个 endpoint 不变，只新增 `/learning/bookmarks` 全量接口。
- **不要把 SubtitleBookmark 和 Vocabulary 合并**：两张表语义不同（书签 vs 间隔重复词条），Schema 设计合理，保留独立。
