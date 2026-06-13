# Fluenty Design System

> Phase 0+ 设计规范（2026-06-13 起草，2026-06-14 SpeakVlog 借鉴升级）。
> 后续所有组件 / 页面改动必须遵守。

---

## 设计灵感 (Design Reference)

**参考站：speakvlog.com** — 清新绿系教育产品站，核心特征：

1. **克制的配色**：白 + 绿两色系，零多余颜色
2. **大字排版**：H1 80px+ / H2 44px，层次极度分明
3. **宽裕间距**：section padding 72-88px
4. **药丸标签**：border-radius 999px pill tag
5. **绿色渐变 CTA**：按钮用 `linear-gradient(#4DA06C → #3F8A5B)`
6. **半透明导航**：毛玻璃效果 `rgba(246,250,245,0.85) + backdrop-filter`
7. **5 步时间线**：编号式步骤列表
8. **统计数字展示**：大数字 + 小标签（200+ / 10+ / 12+）
9. **FAQ 手风琴**：简洁折叠

Fluenty 在此基础上加入 **暖橙强调色** 和 **不对称布局**（AGENTS.md 要求）。

---

## 配色 (Colors)

### 主品牌色 (Brand) — 墨绿系（SpeakVlog 绿同族更深）

| Token | Hex | 用途 | SpeakVlog 参考 |
|-------|-----|------|---------------|
| `--color-brand` | `#0F4C3A` | 主品牌色，CTA 按钮、链接 | SV 主文字 #2F3D35（同族更深） |
| `--color-brand-hover` | `#0A3A2D` | hover 态 | — |
| `--color-brand-light` | `#B8D4C5` | 文字背景 | — |
| `--color-brand-subtle` | `#E8F0EB` | 高亮背景 / 选中态 | SV 浅绿 #E8F3EA（几乎一样） |
| `--color-brand-bright` | `#3F8A5B` | 品牌亮绿（CTA 渐变用） | SV 品牌绿 #3F8A5B（完全一致） |
| `--color-brand-bright-hover` | `#4DA06C` | 亮绿 hover | SV 渐变亮端 #4DA06C |
| `--color-bg-frosted` | `rgba(246,250,245,0.85)` | 导航毛玻璃底 | SV 导航（直接借用） |
| `--color-bg-pale` | `#F6FAF5` | 极浅绿背景 | SV section 背景 |
| `--color-bg-mint` | `#E8F3EA` | 薄荷绿背景 | SV 卡片背景 |
| `--color-footer` | `#F1F6EE` | footer 底色 | SV footer（直接借用） |

### 强调色 (Accent) — 暖橙系（Fluenty 独有，SV 没有这层）

| Token | Hex | 用途 |
|-------|-----|------|
| `--color-accent` | `#E2725B` | 强调（重要 CTA、警示、热度） |
| `--color-accent-hover` | `#C95E47` | hover 态 |
| `--color-accent-light` | `#F5C8B5` | 文字背景 |
| `--color-accent-subtle` | `#FBEDE6` | 高亮背景 |

### 语义色

| Token | Hex | 用途 |
|-------|-----|------|
| `--color-success` | `#2D8659` | 成功状态 |
| `--color-warning` | `#E2725B` | 警告（同 accent） |
| `--color-danger` | `#C73E3A` | 错误 / 删除 |
| `--color-info` | `#0F4C3A` | 信息（同 brand） |

### 文字 / 背景 / 边框（亮色）

| Token | Hex | 用途 | SpeakVlog 参考 |
|-------|-----|------|---------------|
| `--color-text-primary` | `#1A2B22` | 主文字 | SV 主文字 #2F3D35（同族） |
| `--color-text-secondary` | `#5A6B62` | 次要文字 | SV 次要 #4A5A50 |
| `--color-text-muted` | `#8B9A91` | 弱化文字 | — |
| `--color-bg-base` | `#FAFAF7` | 页面底色（米白） | SV 纯白 #FFFFFF |
| `--color-bg-card` | `#FFFFFF` | 卡片背景 | — |
| `--color-bg-elevated` | `#F0F0EB` | 浮起背景 | — |
| `--color-border` | `#E5E5DE` | 边框 | — |

### 暗色模式

| Token | Hex |
|-------|-----|
| `--color-brand` | `#6FA386` |
| `--color-accent` | `#F08A72` |
| `--color-bg-base` | `#0F1A14` |
| `--color-bg-card` | `#1A2820` |

---

## 字体 (Typography)

**核心借鉴 SpeakVlog 的大字排版层级**

- **主字体 (Sans)**：`Inter` + `Noto Sans SC`
  - CSS：`'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif`
- **等宽 (Mono)**：`JetBrains Mono`
  - CSS：`'JetBrains Mono', 'Fira Code', monospace`

字号 scale（SpeakVlog 风格大字头）：

| Token | Size | 用途 | SpeakVlog 参考 |
|-------|------|------|---------------|
| `--text-xs` | 12px | 辅助信息 | — |
| `--text-sm` | 14px | 次要文字 | — |
| `--text-base` | 16px | 正文 | SV body 16px |
| `--text-lg` | 18px | 大正文 | — |
| `--text-xl` | 20px | 小标题 | — |
| `--text-2xl` | 24px | 标题 | — |
| `--text-3xl` | 30px | 大标题 | — |
| `--text-4xl` | 36px | 区块标题 | — |
| `--text-5xl` | 48px | 大区块标题 | — |
| `--text-hero` | 72-84px | 首页 Hero 标题 | SV H1 84px |
| `--text-section` | 44px | 区块 H2 | SV H2 44px |

字重：`300 / 400 / 500 / 600 / 700`

**Hero 排版规则（借鉴 SpeakVlog）**：
- H1: 72-84px / font-weight: 700 / color: var(--color-text-primary) 或 #fff（渐变背景上）
- H1 关键词可以用 `--color-accent` 或 `--color-brand-bright` 高亮
- H1 下方加小标签行（如 `— speak · every day —`），14px / 大写 / letter-spacing 2px / muted 色

**统计数字排版（借鉴 SpeakVlog）**：
- 数字：40px / font-weight: 700 / color: var(--color-brand)
- 标签：14px / font-weight: 400 / color: var(--color-text-secondary)

---

## 布局 (Layout)

### Section 间距（借鉴 SpeakVlog 的宽裕感）

```
section padding: 72px 0 (桌面) / 48px 0 (平板) / 36px 0 (手机)
max-width: 1200px (内容区)
```

### 导航栏（借鉴 SpeakVlog 毛玻璃）

```
position: fixed / sticky
background: var(--color-bg-frosted)      /* rgba(246,250,245,0.85) */
backdrop-filter: blur(12px)
border-bottom: 1px solid rgba(0,0,0,0.04)
padding: 12px 24px
z-index: 50
```

### 页面区块顺序（首页，借鉴 SpeakVlog 结构）

1. **Hero** — 大标题 + 副标题 + 统计数字 + CTA
2. **功能展示** — 12 项功能网格（✓ 清单 + icon）
3. **内容库** — 主题标签云 + 视频卡片网格
4. **学习法** — N 步时间线（01/02/03...）
5. **全设备** — 设备截图展示
6. **FAQ** — 手风琴折叠
7. **CTA 底部** — 双按钮 + 微信二维码

---

## 圆角 (Radius)

| Token | Value | 用途 |
|-------|-------|------|
| `--radius-sm` | 8px | 小组件 |
| `--radius-md` | 12px | 按钮（SpeakVlog 也用 12px） |
| `--radius-lg` | 16px | 卡片 |
| `--radius-xl` | 24px | 大卡片 / 模态框 |
| `--radius-2xl` | 32px | Hero 区 |
| `--radius-full` | 9999px | 药丸标签（SpeakVlog pill tag） |

---

## 阴影 (Shadow)

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)` |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)` |
| `--shadow-lg` | `0 12px 32px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06)` |

---

## 间距 (Spacing)

`4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64 / 72 / 88`

（新增 72 和 88，对应 SpeakVlog 的 section padding）

---

## 动画

| Token | Value |
|-------|-------|
| `--ease-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `--ease-bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` |
| `--duration-fast` | 0.15s |
| `--duration-normal` | 0.2s |
| `--duration-slow` | 0.3s |

---

## 组件样式约定

### CTA 按钮（核心按钮，借鉴 SpeakVlog 绿色渐变）

**主要 CTA**（等同于 SpeakVlog "立即激活"）：
```css
background: linear-gradient(#4DA06C 0%, #3F8A5B 100%);  /* SpeakVlog 渐变 */
color: #FFFFFF;
border-radius: 12-14px;
font-weight: 600;
font-size: 14-16px;
padding: 10px 22px;
hover: opacity 0.9 或加深渐变
```

**次要 CTA**（等同于 SpeakVlog "先去免费试看"）：
```css
background: #FFFFFF;
color: #3F8A5B;
border: 1px solid #E5E5DE;
border-radius: 12-14px;
font-weight: 600;
hover: border-color #3F8A5B
```

### 按钮 (SfButton)

| Variant | 样式 |
|---------|------|
| primary | 绿色渐变 `bg-gradient(#4DA06C→#3F8A5B)` text-white |
| secondary | `bg-bg-elevated` text-text-primary hover:bg-bg-hover |
| ghost | `bg-transparent` text-text-secondary hover:bg-bg-elevated |
| danger | `bg-danger` text-white hover:opacity-90 |
| accent | `bg-accent` text-white hover:bg-accent-hover（暖橙，Fluenty 独有） |

### 卡片

```css
background: var(--color-bg-card);
border: 1px solid var(--color-border);
border-radius: var(--radius-lg);   /* 16px */
box-shadow: var(--shadow-sm);
```

可选 hover：`hover:shadow-md hover:border-brand`

### Tag / Chip（药丸标签，借鉴 SpeakVlog）

```css
background: #FFFFFF;               /* SpeakVlog 白底 */
color: var(--color-text-primary);  /* #2F3D35 */
border-radius: 999px;              /* 完全圆角 */
padding: 8px 18px;
font-size: 16px;
border: 1px solid var(--color-border);
active: background var(--color-brand-bright); color #fff
```

### 统计数字区块（借鉴 SpeakVlog Hero 统计）

```html
<div class="stat-group">
  <div class="stat-item">
    <span class="stat-number">200+</span>
    <span class="stat-label">期学习素材</span>
  </div>
</div>
```
```css
.stat-number { font-size: 40px; font-weight: 700; color: var(--color-brand); }
.stat-label { font-size: 14px; color: var(--color-text-secondary); }
```

### 步骤时间线（借鉴 SpeakVlog 5步跟读法）

```css
.step-number {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-brand-bright);  /* #3F8A5B */
}
.step-title { font-weight: 600; font-size: 18px; }
.step-desc { color: var(--color-text-secondary); font-size: 14px; }
```

### FAQ 手风琴（借鉴 SpeakVlog）

```css
.faq-item { border-bottom: 1px solid var(--color-border); }
.faq-question { font-weight: 600; font-size: 16px; padding: 20px 0; cursor: pointer; }
.faq-answer { color: var(--color-text-secondary); font-size: 15px; padding-bottom: 20px; }
```

### 链接

```css
color: var(--color-text-primary);
&:hover { color: var(--color-brand); }
```

---

## 渐变（推荐用法）

| 渐变 | 值 | 用途 |
|------|-----|------|
| `--yt-brand-gradient` | `linear-gradient(135deg, #0F4C3A 0%, #1A6B4F 50%, #E2725B 100%)` | Hero 背景渐变 |
| `--yt-cta-gradient` | `linear-gradient(#4DA06C 0%, #3F8A5B 100%)` | CTA 按钮渐变（新增，SpeakVlog 同款） |
| `--yt-bg-gradient` | `linear-gradient(180deg, #FAFAF7 0%, #F5F5F0 25%, #FAFAF7 100%)` | 页面背景 |

---

## 禁用项（来自 `AGENTS.md`）

❌ **绝对禁止**：

- 紫色 / 靛蓝色 / 蓝紫渐变（#6366F1、#8B5CF6）
- 纯平背景色（必须有纹理或渐变）
- Tailwind 默认色板（indigo-500 等）
- Hero + 三卡片布局
- 完美居中对齐
- Shadcn/Material UI 默认组件（必须深度定制）
- Emoji 作为功能图标
- 线性动画（ease-in-out）

---

## 响应式断点

| Name | Range | 设备 |
|------|-------|------|
| xs | < 480px | 小屏手机 |
| sm | 480-768px | 普通手机 |
| md | 768-1024px | 平板 |
| lg | 1024-1280px | 小屏笔记本 |
| xl | > 1280px | 桌面 |

## 触摸目标

移动端 button / link / clickable 最小 `44px × 44px`

## 安全区域

刘海屏 / Home Indicator 用 `env(safe-area-inset-*)`

---

## Phase 历史

- **Phase 0 (2026-06-13)**：墨绿 + 暖橙 + Noto Sans SC，紫色彻底清除
- **Phase 0+ (2026-06-14)**：SpeakVlog 借鉴升级 — 新增亮绿 token / 大字排版 / 药丸标签 / 渐变 CTA / 毛玻璃导航 / 步骤时间线 / FAQ 手风琴 / 统计数字组件
