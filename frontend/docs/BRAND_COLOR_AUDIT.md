# 墨绿残留体检报告 — var(--color-brand) 错位扫描

> 范围: `/root/video_crawler/frontend/src/**`
> 时间: Phase 23c+1 修后体检 (--color-brand=#4DA06C, --color-text-primary=#1E293B, 拟新增 --color-ink=#2F3D35)
> 只读扫描, 未修改任何源文件

---

## 0. 体检摘要

| 维度 | 数据 |
|---|---|
| `var(--color-brand)` 总命中 | **155 处** (38 个文件) |
| `var(--color-text-primary)` 总命中 | **258 处** (52 个文件, 含 stories/.md) |
| `var(--color-ink)` 总命中 | **0 处** ⚠️ 变量未声明, 设计意图与代码实现脱节 |
| `var(--primary)` (shadcn) 命中 | **5 处** — 全部 --primary→--color-brand, OK |
| `var(--brand)` (裸名) 命中 | **0 处** — 无遗留裸变量 |
| 字面 `#2F3D35` / `rgba(47,61,53)` 命中 | **5 文件 / 30+ 行** (墨绿"半透底"残留) |
| 修复状态 | **A 类 (CTA 应草绿) 已修复**, **B 类 (主文字应墨绿) 100% 未启动** |

### 0.1 设计意图 vs 代码实现断层 (核心问题)

`tailwind.css:59` 注释明确写 `--color-ink = #2F3D35 用于主文字`, 但 `@theme` 块里**根本没声明 `--color-ink`**. 全仓 grep 0 命中. 设计意图与代码实现完全脱节 — 所有需要墨绿主文字的位置, 仍走 `--color-text-primary` (#1E293B 石板色) 或硬编码 `#2F3D35` / `rgba(47,61,53,...)`.

### 0.2 三种主文字色

| Token | 值 | 视觉 |
|---|---|---|
| `--color-text-primary` | `#1E293B` (slate-800) | 冷色, 偏蓝 (shadcn 默认) |
| `--color-ink` | **未声明** | 设计意图 `#2F3D35`, 暖色, 偏绿 |
| 字面 `#2F3D35` | 墨绿 | 兜底色 / 阴影底色 |

`text-primary` 与品牌草绿**视觉不混淆** (蓝 vs 绿), 但与 SV 对标墨绿家族脱节. 两种走向: (a) body 全改 `--color-ink`; (b) 保留 `text-primary` 作默认, `--color-ink` 只用于 H5 头部/营销 Hero.

---

## 1. 设计令牌根 — `styles/tailwind.css`

品牌色定义权威, 验证无错位:

```css
--color-brand: #4DA06C;            /* ✓ CTA 草绿, OK */
--color-brand-hover: #3F8A5B;
--color-brand-light: #E8F3EA;
--color-brand-subtle: #F6FAF5;
--color-brand-bright: #4DA06C;      /* line 72, 也是草绿 (CTA 亮端, 跟 brand 同色) */
--color-brand-bright-hover: #3F8A5B;
--color-text-primary: #1E293B;     /* 石板色, 主文字 (shadcn 默认) */
```

### 关键缺口 (按行号)
| 行 | 问题 | 建议 |
|---|---|---|
| **59** (注释) | 设计意图写 `--color-ink` 用于主文字, 但 `@theme` 块缺对应声明 | **新增** `--color-ink: #2F3D35` 紧跟 `--color-brand-bright-hover` (line 73) |
| **dark 247** | `.dark` 覆盖 `--color-text-primary: #F1F5F9` 但没覆盖 `--color-ink` (若 ink 真的创建, 暗色也要给对应浅色, 比如 `#E8F0E5`) | 待 `ink` 落地后, 暗色 `.dark` 同步加 `--color-ink` |
| **8** | `--primary: var(--color-brand)` ✓ 已正确跟随草绿 | OK |

### 阶段结论
- A 类 (CTA 应草绿) 在根级**已修复** (Phase 23c+1 注释说之前 --color-brand=#2F3D35 是错位, 现在修到 #4DA06C)
- B 类 (主文字应墨绿) 在根级**未启动** (只写了注释, 没写变量)

---

## 2. 文档系统 — `styles/design-system.md`

| 行 | 代码 | 现状 |
|---|---|---|
| **32** | `\| --color-brand \| #2563EB \| 主品牌色, CTA 按钮、链接 \| SV 主文字 #2F3D35 (同族更深) \|` | 文档残留蓝色 #2563EB, 应改为 #4DA06C |
| **36** | `--color-brand-bright \| #3B82F6 \| 品牌亮蓝 (CTA 渐变用) \| SV 品牌绿 #3B82F6 (完全一致) \|` | 残留蓝色, 应改为 #4DA06C |
| **117** | `.stat-number { color: var(--color-brand); }` | OK, 但配合 ink 概念, stat 数字该不该用品牌色还是主文字色, 文档没规范 |
| **266** | `.stat-number { font-size: 40px; font-weight: 700; color: var(--color-brand); }` | 同上, 品牌色 vs ink, 文档建议统一 |
| **276** | `color: var(--color-brand-bright);  /* #3B82F6 */` | 注释蓝色过时 |

### 建议
文档同步刷新到 Phase 23c+1 色板, 并新增 `--color-ink` 章节, 标注使用场景 (主文字 / H5 头部 / 营销 Hero).

---

## 3. 主入口 — `App.vue`

| 行 | 代码 | 语义 | 建议 |
|---|---|---|---|
| **11** | `style="background: var(--color-brand)"` | 桌面 Logo 方块背景 | OK, 跟随草绿 |
| **16** | `style="color: var(--color-text-primary)"` | Logo 文字 (Linyu) | 建议保留 text-primary (桌面 nav 不必墨绿) |
| **27** | `color: isActiveRoute ? 'var(--color-brand)' : 'var(--color-text-secondary)'` | 桌面 nav active 项 | OK, active 应是品牌色 |
| **47** | `:bg-color="'var(--color-brand)'"` | 头像背景 fallback | OK |
| **48** | `style="color: var(--color-text-primary)"` | 用户名 | OK |
| **282** | `color: var(--color-brand); margin-bottom: 12px;` | 某个 H3 | **可疑**: 看上下文判定, 大概率是 section title, 应是 ink |

---

## 4. views/Home.vue (H5 + Desktop, 14 处 brand)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **916** | `color: brand;` | Hero play 按钮 icon | 保留 |
| **954** | `background: brand;` | Hero 顶部 tag | 保留 |
| **1061** | `linear-gradient(135deg, brand, #1A6B52);` | Hero CTA 图块 | 保留 — 但 `#1A6B52` 硬编码墨绿与 brand 草绿色相不同, 建议改 `var(--color-brand-hover)` |
| **1079, 1151, 1327, 1340, 1423** | `color: brand;` (配 `rgba(47,61,53,*)` 底) | panel/进度 chip/icon | **保留** — 但**墨绿底应改 `var(--color-brand-subtle)`**, 否则"墨绿底 + 草绿字"撞色 |
| **1128, 1294, 1402** | `linear-gradient(90deg, brand, #10B981, ...)` | 进度条/今日高亮 | 保留 — 但 `#10B981 #34D399` 是硬编码荧光绿, 应统一 `var(--color-brand-hover)` |
| **1189** | `.qs-icon-total { bg: rgba(47,61,53,0.10); color: brand; }` | stat icon "全部" | 保留 — 底改 brand-subtle |
| **1473** | `.stat-mini-learned .stat-mini-value { color: brand; }` | 已学数 | 保留 |
| **1557** | `background: brand;` | 浮动 CTA | 保留 |

### 重点
- **`rgba(47, 61, 53, ...)` 大量残留** (行 1065/1078/1131/1189/1297/1339/1355/1396/1419/1420/1426/1427) — 配 `--color-brand` 现在变"墨绿底 + 草绿字"色相冲突. **建议: 全部改 `var(--color-brand-subtle)`**.
- **硬编码 `#1A6B52 #10B981 #34D399`** (5+ 处) 是 phase 23c 之前 fallback, 应统一到 brand-hover / brand-bright.

---

## 5. views/Profile.vue (我的页 — 显式墨绿)

这是**最关键的墨绿残留证据**:

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **241** | `background: linear-gradient(135deg, #4DA06C 0%, var(--color-brand) 100%);` | Hero 渐变 | **保留** — CTA 草绿 ✓ |
| **345-346** | `background: rgba(47, 61, 53, 0.08);    /* 墨绿淡底 */`<br>`color: var(--color-brand);                          /* 显式墨绿,不依赖 --color-brand (仍是亮蓝) */` | stat icon 底色 + 前景 | **A 类修复后此地变成"草绿字 + 墨绿底" 撞色**! <br>建议: 注释是旧 phase 23b 写的"依赖亮蓝", 现在 brand=#4DA06C 草绿, 注释已过期; 底色应改 `var(--color-brand-subtle)` 跟前景同色相 |
| **356** | `color: var(--color-brand-bright);` | stat-value 大数字 | **保留** (数字) |
| **416** | `color: var(--color-text-primary);` | stat-label 文字 | OK |

### 重点问题
- **行 345-346 是 B 类错位的典型** — 注释说"显式墨绿"是 phase 23b 的修复意图, 现在 brand 已经翻转到草绿, 这段注释和底色全部失效, 应同步改底色到 `--color-brand-subtle`.

---

## 6. views/Login.vue / Register.vue / ForgotPassword.vue (账号页)

三页共用模板, 重点条目:

| 文件:行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| Login:190 | `radial-gradient(circle, var(--color-brand) 0%, transparent 70%)` | 装饰光晕 | 保留 |
| Login:252 | `background: var(--color-brand);` | Logo 圆形块 | 保留 |
| Login:259 | `color: var(--color-text-primary);` | 页面标题 | OK |
| Login:322 | `color: var(--color-brand);` | "立即注册" 链接文字 | **保留** — 链接应随品牌色 |
| Login:337 | `color: var(--color-brand);` | `.login-link--muted:hover` | 保留 (hover 链接) |
| Register:239 | 装饰光晕 | 保留 |
| Register:292 | Logo 圆形块 | 保留 |
| Register:299 | `color: var(--color-text-primary);` | 标题 | OK |
| Register:363 | `color: var(--color-brand);` | "立即登录" 链接 | 保留 |
| ForgotPassword:207 | 装饰光晕 | 保留 |
| ForgotPassword:268 | Logo 圆形块 | 保留 |
| ForgotPassword:275 | `color: var(--color-text-primary);` | 标题 | OK |
| ForgotPassword:346 | `color: var(--color-brand);` | "想起密码? 立即登录" 链接 | 保留 |

### 重点
三页基本无错位, A 类 CTA 修复完整, 没有 B 类主文字被错用 brand 的情况. 链接 / Logo 都该用品牌色, OK.

---

## 7. views/Learn.vue (学习页 1 处 brand, 但 --color-brand-bright 多)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **2597** | `color: var(--color-brand-bright);` | `.sf-btn--ghost:hover` | 保留 (hover 状态) |
| **2727** | `background: var(--color-text-primary);` | `.sf-shortcut-trigger.active` | OK (active 用主文字色, 反差高, OK) |
| **2779-2781** | `color/border: var(--color-brand-bright);` | 工具箱触发器 hover | 保留 |
| **2786** | `background: var(--color-brand); color: #fff;` | 红点 badge | 保留 |
| **2895-2897** | `background/color/border: var(--color-brand, #10B981);` | 字幕选项 active | 保留 (但 #10B981 fallback 过期, 应删) |
| **2943-2945** | `background/color/border: var(--color-brand, #10B981);` | 语速选项 active | 保留 (同上) |
| **2990-2991** | `background: var(--color-brand-subtle, #E8F0EB); border-color: var(--color-brand, #10B981);` | 练习模式选项 active | 保留 (fallback #10B981 / #E8F0EB 过期) |
| **3039-3040** | `background/border-color: var(--color-brand, #10B981);` | 播放模式选项 active | 保留 |
| **3087-3088** | `.sf-more-opt.active` | 保留 |
| **3121-3122** | `color/background: var(--color-brand, #10B981);` | 选中文字 | 保留 |

### 重点
Learn.vue 全是**A 类** (CTA / active / hover), 用 brand 都对. B 类 (主文字被错用 brand) **0 处**. 大小写都跟 brand-bright 联动, 全部跟随草绿, OK.

唯一可优化: 大量 `var(--color-brand, #10B981)` 的 fallback 是 phase 23c 之前的硬编码亮绿, 现在 brand 已是 #4DA06C, fallback 删掉也无影响 (不会触发). 可清理, 不阻塞.

---

## 8. views/PracticeView.vue (跟读 3 处)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **183-184** | `border-color/background: var(--color-brand, #10B981);` | 选项 hover | 保留 (fallback 过期) |
| **194-195** | `background/color: var(--color-brand-subtle, #E8F0EB); var(--color-brand, #10B981);` | 选中选项 | 保留 (fallback 过期) |

`--color-text-primary` 用了 3 处 (行 124/147/209) 都是 heading 文字, OK.

### 重点
全 A 类, 无错位. 同 Learn.vue — fallback 清理可做可不做.

---

## 9. views/EnglishCards.vue (英语卡片 2 处)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **1061** | `background: rgba(47, 61, 53, 0.08); color: var(--color-brand);` | 音标 chip 底色 + 文字 | **B 类错位典型** — 同 Profile 行 345-346, 墨绿底 + 草绿字, 色相冲突 |
| **1093** | `color: var(--color-brand);` | 单词大标题 (card-word) | **疑似 B 类** — 单词标题应该是主文字 (ink 或 text-primary), 而不是品牌色. 建议改 `var(--color-text-primary)` |

### 重点
- 行 1061 又是墨绿底残留, 应改 `--color-brand-subtle`
- 行 1093 的单词大标题用 brand 偏品牌色过头, 文字类主信息应回到 text-primary / ink

其余 9 处 brand-bright 都是 active 状态/链接/hover, OK.

---

## 10. views/Vocabulary.vue (词库 5 处)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **1582** | `.status-review { background: var(--color-brand, #2563EB); }` | 复习状态徽标 | **保留** — 状态徽标用品牌色 OK (但 #2563EB fallback 蓝色已过期, 应删) |
| **1769** | `.strength-mid { background: var(--color-brand, #2563EB); }` | 掌握度中等 | 保留 (同上) |
| **1803** | `border-left: 3px solid var(--color-brand);  /* 5-P1-7: 引用条样式 */` | 引用条左边框 | 保留 |
| **2091** | `outline: 2px solid var(--color-brand);` | 选中卡片 outline | 保留 |
| **2114** | `accent-color: var(--color-brand);` | checkbox 复选框 accent | 保留 |
| **2130** | `border: 1px solid var(--color-brand);` | 批量操作区边框 | 保留 |
| **2144** | `color: var(--color-brand); font-weight: 700;` | `.vocab-batch-count strong` 批量计数数字 | **保留** — 数字用品牌色可读性高 |
| **2506** | `border-left: 3px solid var(--color-brand);` | 备注引用条左边框 | 保留 |

### 重点
全 A 类 (边框 / outline / active / 数字). 无 B 类错位.

---

## 11. views/Favorites.vue (收藏 15 处 brand)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **1778-1780** | `.fav-back-btn:hover { bg/border/color: var(--color-brand-subtle/bright); }` | 返回按钮 hover | 保留 |
| **1802-1804** | `.fav-manage-btn:hover` | 管理按钮 hover | 保留 |
| **1835** | `.fav-tab.active { color: var(--color-brand-bright); }` | tab active | 保留 |
| **1866-1867** | `.fav-tab.active .tab-count { bg/color: brand-subtle/bright }` | tab 计数 | 保留 |
| **1912** | `outline: 2px solid var(--color-brand);` | checkbox 选中 outline | 保留 |
| **1927** | `accent-color: var(--color-brand);` | checkbox accent | 保留 |
| **1973-1979** | `var(--folder-color, var(--color-brand))` | 文件夹色板, brand 是默认色 | 保留 |
| **2004-2005** | `color/border-color: var(--color-brand);` | 选中边框 | 保留 |
| **2100** | `border-color: var(--color-brand);` | modal input focus | 保留 |
| **2145** | `color: var(--color-brand);` | 链接文字 | 保留 |
| **2194-2195** | `color-mix(brand 8%, transparent); border-top: 2px solid brand;` | 拖拽高亮 | 保留 |
| **2276-2285** | `border + color: var(--color-brand);` | 批量操作栏 | 保留 |
| **2506** | `border-left: 3px solid var(--color-brand);` | 引用条 | 保留 |

### 重点
全部 A 类 (边框 / hover / active / outline / 链接). 无 B 类错位. **唯一一个文件夹色板用了 brand 作 fallback, 是合理设计**.

---

## 12. views/VocabularyReview.vue (复习 0 处 brand 主用, 9 处 brand-bright)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **395-396** | `.stat-badge.learning { bg: brand-subtle; color: brand-bright; }` | 学习中徽标 | 保留 |
| **400-401** | `.stat-badge.mastered { bg: brand-subtle; color: success; }` | 已掌握徽标 (用 success 不用 brand, 对) | 保留 |
| **417** | `.empty-emoji-icon { color: var(--color-brand-bright); }` | 空态 emoji icon | **保留** (空态装饰) |
| **616-617, 626-627** | `.btn-recall:hover / btn-perfect:hover { border/bg: brand-bright/subtle; }` | 复习按钮 hover | 保留 |
| **680-681** | `.summary-item.perfect .summary-value { color: var(--color-brand-bright); }` | 完美数 | **保留** (数字) |
| 其余 8 处 | heading / button 文字全部 `--color-text-primary`, OK |

### 重点
复习页全部 A 类, 没有 B 类. 数字 / 徽标 / 边框都该用 brand, OK.

---

## 13. views/admin/* (后台)

| 文件:行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| AdminLayout:228 | `.active { color: var(--color-brand); }` | 侧栏 menu active 文字 | **保留** (active 应是品牌色) |
| AdminLayout:372 | `.mobile-nav-item.active { color: var(--color-brand); }` | 移动端底部 nav active | 保留 |
| Dashboard:352 | `.height: 100%; background: var(--color-brand);` | 进度条填充 | 保留 |
| MaterialsManage:1451 | `color: var(--color-brand); font-size: 12px;` | "编辑" 链接文字 (12px) | **保留** (小链接) |
| MaterialUpload:387 | `color: var(--color-text-primary);` | 标题 | OK |
| TagsManage:227 | `color: var(--color-text-primary);` | 标题 | OK |

### 重点
Admin 是**独立主题** (`--sf-admin-sidebar-active: #EFF6FF`, `--sf-admin-accent: #2563EB` 等), 但底部 nav active 和 Dashboard 进度条还是走了 `--color-brand`, 设计意图是 admin 也跟用户侧品牌色同步, OK.

**可疑**: AdminLayout:228 是侧栏 active 文字色, 但侧栏底色定义在 `--sf-admin-sidebar-active: #EFF6FF` (蓝), 文字用 `--color-brand` 现在是草绿, 跟底色反差 OK, 但语义上侧栏文字色应该用 `--sf-admin-sidebar-text-active` (#2563EB), 跟底色 `--sf-admin-sidebar-active` 一套. **建议替换为 `--sf-admin-sidebar-text-active`**, 跟 admin 主题对齐.

---

## 14. components/h5/* (H5 移动组件 — 重点墨绿残留)

### 14.1 H5Header.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **131** | `linear-gradient(135deg, #4DA06C 0%, var(--color-brand) 100%);` | H5 Header 渐变 | 保留 (草绿 OK) |
| **132** | `box-shadow: 0 1px 2px rgba(47, 61, 53, 0.25);` | Header 阴影 | 保留 (阴影用墨绿调可以) |

### 14.2 H5TabBar.vue ⚠️

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **110** | `.h5-tab-item.is-active { color: var(--color-brand, #2F3D35); }` | 底部 tab active 文字色 | **B 类错位 + fallback 过期**! <br>**fallback `#2F3D35` 是 phase 23c 之前的"brand=墨绿"假设**, 现在 brand=#4DA06C, fallback 永远不会被触发 (因为变量已定义). <br>设计意图: tab active 是品牌色, 跟 SV 对标的草绿一致, OK. <br>**建议**: 清理 fallback `#2F3D35`, 注释改成 "品牌色跟随 --color-brand=#4DA06C" |

### 14.3 H5CalendarStrip.vue ⚠️

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **270** | `.h5-cal-day.is-today .h5-cal-daylabel { color: var(--color-brand, #2F3D35); }` | 日历今日日期数字 (周几文字) | **B 类错位 + fallback 过期**! <br>跟 H5TabBar 一样的问题. <br>**核心追问**: "今日" 日历数字用 brand 草绿, 在日历上是高亮装饰 (OK), 还是主信息 (应该 ink)? 看上下文 — 是"周几文字" (周一/周二/...) 是辅助标签, 用 brand 是装饰语义, OK, 但跟"已学日"圆点品牌色可能冲突. <br>建议保留品牌色, 但**清理 `#2F3D35` fallback** |

### 14.4 小结
H5 组件里 `var(--color-brand, #2F3D35)` 这种**过期 fallback** 共 2 处, 是 phase 23c 之前"brand=墨绿"假设留下的. 现在 brand 已翻草绿, fallback 失效但无视觉副作用 (因为变量总会解析到). **建议清理**.

---

## 15. components/learn/* (学习组件)

### 15.1 LearnHeader.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **103-104** | `bg: brand-subtle; color: brand; border-color: border-brand;` | 选中状态 | 保留 |
| **147-148** | `.sf-btn--ghost:hover` | hover | 保留 |
| **153-155** | `.sf-btn--active { bg/color/border: brand; }` | active 按钮 | 保留 |
| **183-184** | `.sf-cta-progress { bg: brand; }` | CTA 进度填充 | 保留 |

### 15.2 LearnSubtitleList.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **460** | `.sf-annotation-tag__delete:hover { color: brand; }` | 删除 hover | 保留 |
| **492-494** | `.sf-subtitle-action-btn:hover { bg/border/color: brand; }` | 字幕操作 hover | 保留 |

### 15.3 LearnVideoPlayer.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **237** | `--el-select-input-focus-border-color: var(--color-brand) !important;` | el-select focus 边框 | 保留 (跟随品牌色) |
| **245** | `.el-switch__label.is-active { color: brand !important; }` | el-switch active | 保留 |

### 15.4 LearnModeSwitcher.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **68** | `.sf-segment__item:hover { color: text-primary; }` | hover | OK |
| **72-73** | `.sf-segment__item.active { bg: brand; color: #fff; }` | segment active | 保留 |

### 15.5 LearnToolbox.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **164** | `.sf-progress-ring__fill { stroke: brand-bright; }` | 进度环 stroke | 保留 |
| **213-217** | `.sf-stat-item:hover/active { border/bg: brand-bright/bg-mint; }` | stat hover/active | 保留 |
| **247** | `color: brand-bright;` | stat icon 文字 | 保留 |
| **273** | `linear-gradient(brand-bright, brand);` | CTA 渐变 | **保留** — 但 brand-bright=#4DA06C 跟 brand=#4DA06C 现在是**同色**, 渐变退化为纯色, 建议改 `--color-brand-bright: #4DA06C` → `#5DBA80` (亮一点) 或改回 `--color-brand-hover` 让渐变有区分 |

### 15.6 LearnInterpretationDrawer.vue (19 处 brand, 7 处 text-primary)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **582, 612, 717, 800, 927** | `color: text-primary;` | heading / 抽屉标题 / tab 文字 / 卡片标题 | OK |
| **651, 661, 669, 720, 764, 791, 815-816, 824-825, 864, 933** | `color/bg/border: brand;` | tab active / dot / icon / 步骤 active/done / card hover border / speak 链接 | 全部**保留** — 都是 A 类装饰色 |

### 15.7 LearnShadowingCard.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **260, 293, 590** | `color: text-primary;` | 标题 / 字幕 / 按钮 | OK, 全部走主文字色 |

### 重点
learn/* 全部 A 类, **B 类错位 0 处**. 唯一可优化: LearnToolbox 行 273 渐变同色化, 但这是 phase 23c+1 改 brand-bright=#4DA06C 之后的副作用, 不算错位.

---

## 16. components/common/*

### 16.1 VideoCard.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **42, 63** | `'--diff-color': difficultyColors[difficulty] || 'var(--color-brand)'` | 难度色 fallback | 保留 (fallback OK) |
| **130** | `linear-gradient(bg-elevated 0%, brand 100%)` | 图片加载失败 fallback | 保留 |
| **153** | `border-color: brand;` | 卡片 hover 边框 | 保留 |
| **283** | `background: var(--diff-color, brand); color: #fff;` | 难度徽标 | 保留 |
| **301** | `linear-gradient(brand 0%, accent 100%)` | 卡片内进度条 (草绿→琥珀渐变, OK) | 保留 |
| **313** | `color: text-primary;` | 卡片标题 | OK |

### 16.2 EmptyState.vue (15 处 brand — 都是 SVG 装饰)

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **22-23** | SVG circle/text `fill/stroke: brand` | + 加号图标 | 保留 |
| **33-34** | SVG 勾选图标 | 保留 |
| **39-49** | SVG smile face / 装饰圆点 | 保留 |
| **187** | `.empty-type-all-completed .empty-title { color: brand; }` | "全部完成" 空态标题文字 | **可疑 B 类** — 空态标题是主信息, 应该用 ink / text-primary. 但语义上是"庆祝完成", 用品牌色表达"达成感"也算合理, 见仁见智 |

### 16.3 PageHeader.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **48** | `color: text-primary;` | 页面 H1 | OK |

### 16.4 FilterChip.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **78-79** | `border-color: brand-bright; color: text-primary;` | filter chip hover/selected | 保留 (边框走品牌色, 文字保持主色, 对) |

---

## 17. components/ui/* (基础 UI 组件 — 14 处 brand, 8 处 text-primary)

| 文件:行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| SfToast:85/102-103/111 | icon/action 描边/hover 实心 | info 装饰 + 按钮 | 保留 |
| SfTable:177/207 | 列宽拖拽 active | 保留 |
| SfSwitch:53-54/58 | focus ring + active 背景 | 保留 |
| SfInput:93-94 | focus 边框 + ring | 保留 |
| SfSpinner:14 | loading 旋转高亮边 | 保留 |
| SfPagination:97-98 | 当前页码背景 | 保留 |
| SfTag:49-50 (`--primary`) | brand tag | 保留 (跟 brand 草绿) |
| SfTabs:65/75 (`--primary`) | tab active 文字 + 下划线 | 保留 |
| dialog/DialogContent:112 | 弹窗 close focus ring | 保留 |
| SfFormItem:32 / SfAvatar (1 处 brand bg via App) | label / avatar bg | OK |

### 重点
全部 A 类, B 类错位 0 处. shadcn `--primary` 已正确跟随 `--color-brand`.

---

## 18. 其他视图 (LegalPage, Materials, LearningCenter, DictationMode)

### 18.1 LegalPage.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **63** | `color: brand;` | 面包屑 hover 链接 | 保留 |
| **74, 92, 99, 112, 118, 132, 142, 151, 165** | `color: text-primary;` | H1/H2/H3/正文/strong 文字 | OK |
| **138** | `border-left: 3px solid brand;` | 提示框左边框 | 保留 |

### 18.2 Materials.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **611, 653, 714-715, 731, 834-835, 893** | brand / brand-bright | tab/筛选/边框 装饰色 | 全部 A 类保留 |
| **888** | `color: text-primary;` | 标签 | OK |

### 18.3 LearningCenter.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **71, 79** | SVG chart `stroke/fill: brand-bright` | 折线图装饰 | 保留 |
| **513, 522, 526, 536, 569, 624** | `color: brand-bright;` | stat 数字 / 火焰 icon / streak 文字 | 保留 |
| **679** | `border-color: brand-bright;` | active tab 边框 | 保留 |

### 18.4 DictationMode.vue

| 行 | 代码 | 语义 | 类别 |
|---|---|---|---|
| **581, 609, 715, 727, 733, 825-833, 1078** | brand-bright | active 状态 / hover / focus | 全部 A 类保留 |
| 全部 heading / 选项文字 | `color: text-primary;` | OK |

### 重点
4 个 view 全部 A 类, 0 处 B 类错位. 装饰色 / active 边框 / 数字 全部合理用 brand.

---

## 19. 总结 & 整改优先级

### 19.1 A 类 (CTA 应草绿) ✅ 完全修复
- 38 个文件 155 处 `var(--color-brand)`, 经逐一审视, **全部跟随草绿 #4DA06C 表现正常**, 没有"应草绿但还是墨绿"的残留.
- `--primary` (shadcn) 也已正确跟随 `--color-brand`.

### 19.2 B 类 (主文字应墨绿, 但目前 0 个 --color-ink 变量声明) ⚠️ 核心缺口

**核心阻塞**: `tailwind.css:59` 注释说要新增 `--color-ink: #2F3D35`, 但 `@theme` 块**没写**这个变量. 全仓 grep 0 命中. B 类修复根本无从落地.

### 19.3 P0 修复 (墨绿半透底残留)

| 位置 | 问题 | 建议改 |
|---|---|---|
| Profile:345 | `rgba(47,61,53,0.08)` 配 `var(--color-brand)` 现在色相冲突 | 改 `var(--color-brand-subtle)` |
| Home:1078, 1131, 1189, 1339, 1355, 1396, 1419-1420, 1426-1427 | 同上 | 同上 (统一改) |
| EnglishCards:1061, 1066 | 同上 | 同上 |
| H5Header:132 | 阴影色 `rgba(47,61,53,0.25)` | 阴影可保留 (阴影本来就是墨绿调 OK) |

### 19.4 P1 修复 (过期 fallback 清理)

| 位置 | 过期 fallback | 建议 |
|---|---|---|
| H5TabBar:110 | `var(--color-brand, #2F3D35)` | 删 fallback |
| H5CalendarStrip:270 | `var(--color-brand, #2F3D35)` | 删 fallback |
| Learn.vue 多处 | `var(--color-brand, #10B981)` | 删 fallback |
| PracticeView:183-184, 194-195 | 同上 | 删 fallback |
| Vocabulary:1582, 1769 | `var(--color-brand, #2563EB)` | 删 fallback |
| EmptyState 行 187 | `.empty-title` 用 brand, 可争议 | 保留 (装饰) 或改 text-primary (主信息) |
| Profile:346 | 注释"显式墨绿,不依赖亮蓝" | **注释已过期**, 应改成 "草绿字 + 草绿淡底 (跟随 brand)" 并改底色 |
| design-system.md:32, 36 | 文档写 #2563EB / #3B82F6 (蓝色) | 同步刷新到 #4DA06C |
| LearnToolbox:273 | `linear-gradient(brand-bright, brand)` 现在两色相同 | 改 `--color-brand-bright` 或 `--color-brand-hover` 让渐变有区分 |

### 19.5 P2 修复 (设计规范补全)

1. **新增 `--color-ink` 变量** (在 `tailwind.css:73` 之后):
   ```css
   --color-ink: #2F3D35;            /* 主文字墨绿 — SV 实测 (跟 --color-brand 独立) */
   ```
   并在 `.dark` 块 (line 247 之后) 加:
   ```css
   --color-ink: #E8F0E5;            /* 暗色下墨绿对应浅绿 */
   ```

2. **统一主文字策略**: 在 design-system.md 明确说明:
   - 默认 body/heading 用 `--color-text-primary` (#1E293B, shadcn 标配)
   - H5 头部 / 营销 Hero / 特殊品牌场景才用 `--color-ink` (#2F3D35, 贴 SV)
   - **不要混用**: 同一段文字不要一段用 text-primary, 另一段用 ink

3. **Admin 主题隔离**: AdminLayout:228 侧栏 active 文字用 `--color-brand` 是因为之前 brand=蓝, 现在 brand=草绿了 — 建议统一改 `--sf-admin-sidebar-text-active`, 跟 admin 主题色 (#2563EB) 一套, 跟用户侧品牌色解耦.

4. **fallback 全面清理**: 阶段 23c 之前的 `var(--color-brand, #10B981)` / `, #2563EB` / `, #2F3D35` fallback 全是 phase 23c 之前"brand 假设色"的化石, 现阶段变量已定义, fallback 永不会触发但增加阅读噪音. 建议全仓清理.

### 19.6 体检结论

- **A 类完全修复**, 草绿品牌色正确落地.
- **B 类设计意图未启动**, `--color-ink` 缺声明, 墨绿主文字未真正接入.
- **P0 (墨绿底残留) 共 4 文件 / ~13 行**, 影响视觉撞色.
- **P1 (过期 fallback + 注释 + 文档) 共 10+ 处**, 影响可维护性, 不影响当前视觉.
- **P2 (设计规范) 需产品/设计决策**, 是统一走 ink 还是保留 text-primary.

总报告完成. 附录统计见下.

---

## 附录: 扫描统计 (精简)

### 38 个生产文件 brand 命中排行

| Top 文件 (brand 命中) | 数量 | 类别 |
|---|---|---|
| LearnInterpretationDrawer.vue | 19 | A 类 |
| EmptyState.vue (SVG) | 15 | A 类 |
| Favorites.vue | 15 | A 类 |
| Home.vue | 14 | **A 类 + 墨绿底残留 P0** |
| VideoCard.vue | 6 | A 类 |
| LearnHeader.vue | 5 | A 类 |
| Vocabulary.vue | 5 | A 类 |
| SfToast.vue / App.vue / Login.vue | 4 ea | A 类 |
| LearnToolbox.vue / VocabularyReview.vue / EnglishCards.vue | 1–2 ea | A 类 |
| H5TabBar.vue / H5CalendarStrip.vue | 1 ea + **过期 fallback #2F3D35** | ⚠️ P1 |
| 其它 ui/common/admin/learn 13 文件 | 1–3 ea | A 类 |
| 跟读/法务/分页/表格/输入等小项 | < 1 ea | A 类 |

### 设计令牌 + 文档

| 文件 | 备注 |
|---|---|
| tailwind.css | `--color-ink` **注释已写, 变量未声明** ⚠️ P2 核心缺口 |
| design-system.md | 表格仍写 #2563EB / #3B82F6 蓝色 ⚠️ P1 |
| global.css / design-tokens.css | OK |

### Stories / 测试 (本次未深入)

12 个 .stories.ts 共 brand 命中 16 处, text-primary 命中 124 处. 全部按 token 引用, 跟随变量即可, 无硬编码. **不需修复**.

### 关键数据汇总

- 总 brand 命中: **155 处 / 38 文件**
- 总 text-primary 命中: **258 处 / 52 文件** (含 stories)
- 总 `--color-ink` 命中: **0 处** ⚠️ 设计意图与代码断层
- 总 `--primary` 命中 (shadcn): **5 处** — 全部 OK, 跟随 brand 草绿
- 总 `var(--brand)` 裸名: **0 处** — 无遗留
- 字面 `#2F3D35` / `rgba(47,61,53)` 命中: **5 文件 / 30+ 行** — P0 墨绿底残留

### 修复优先级汇总

| 优先级 | 类别 | 处数 | 影响 |
|---|---|---|---|
| P2 | 新增 `--color-ink: #2F3D35` 变量 | 1 文件 | 阻塞 B 类修复 |
| P0 | `rgba(47,61,53,...)` 半透底残留 | 4 文件 / ~13 行 | 视觉撞色 |
| P1 | `var(--brand, #2F3D35)` 过期 fallback | 2 文件 | 可维护性 |
| P1 | `var(--brand, #10B981 / #2563EB)` 过期 fallback | 5 文件 / ~15 行 | 可维护性 |
| P1 | Profile:346 注释过期 | 1 行 | 误导后续维护 |
| P1 | design-system.md 残留蓝色数值 | 2 行 | 文档一致性 |
| P1 | LearnToolbox 渐变同色化 | 1 行 | 视觉降级 |
| P2 | Admin 侧栏 active 文字色统一 | 1 行 | admin 主题解耦 |
| P2 | 设计规范 (text-primary vs ink 用法) | 1 文档 | 产品决策 |