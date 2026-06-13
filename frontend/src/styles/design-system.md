# Fluenty Design System

> Phase 0 设计规范（2026-06-13）。后续所有组件 / 页面改动必须遵守。

## 配色 (Colors)

### 主品牌色 (Brand) — 墨绿系

| Token | Hex | 用途 |
|-------|-----|------|
| `--color-brand` | `#0F4C3A` | 主品牌色，CTA 按钮、链接 |
| `--color-brand-hover` | `#0A3A2D` | hover 态 |
| `--color-brand-light` | `#B8D4C5` | 文字背景 |
| `--color-brand-subtle` | `#E8F0EB` | 高亮背景 / 选中态 |

### 强调色 (Accent) — 暖橙系

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

| Token | Hex | 用途 |
|-------|-----|------|
| `--color-text-primary` | `#1A2B22` | 主文字 |
| `--color-text-secondary` | `#5A6B62` | 次要文字 |
| `--color-text-muted` | `#8B9A91` | 弱化文字 |
| `--color-bg-base` | `#FAFAF7` | 页面底色（米白） |
| `--color-bg-card` | `#FFFFFF` | 卡片背景 |
| `--color-bg-elevated` | `#F0F0EB` | 浮起背景 |
| `--color-border` | `#E5E5DE` | 边框 |

### 暗色模式

| Token | Hex |
|-------|-----|
| `--color-brand` | `#6FA386` |
| `--color-accent` | `#F08A72` |
| `--color-bg-base` | `#0F1A14` |
| `--color-bg-card` | `#1A2820` |

## 字体 (Typography)

- **主字体 (Sans)**：`Inter` + `Noto Sans SC`
  - CSS：`'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif`
- **等宽 (Mono)**：`JetBrains Mono`
  - CSS：`'JetBrains Mono', 'Fira Code', monospace`

字号 scale：

| Token | Size |
|-------|------|
| `--text-xs` | 12px |
| `--text-sm` | 14px |
| `--text-base` | 16px |
| `--text-lg` | 18px |
| `--text-xl` | 20px |
| `--text-2xl` | 24px |
| `--text-3xl` | 30px |
| `--text-4xl` | 36px |
| `--text-5xl` | 48px |

字重：`300 / 400 / 500 / 600 / 700`

## 圆角 (Radius)

| Token | Value |
|-------|-------|
| `--radius-sm` | 8px |
| `--radius-md` | 12px |
| `--radius-lg` | 16px |
| `--radius-xl` | 24px |
| `--radius-2xl` | 32px |
| `--radius-full` | 9999px |

## 阴影 (Shadow)

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)` |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04)` |
| `--shadow-lg` | `0 12px 32px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06)` |

## 间距 (Spacing)

`4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64`

## 动画

| Token | Value |
|-------|-------|
| `--ease-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `--ease-bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` |
| `--duration-fast` | 0.15s |
| `--duration-normal` | 0.2s |
| `--duration-slow` | 0.3s |

## 组件样式约定

### 按钮 (SfButton)

| Variant | Tailwind |
|---------|----------|
| primary | `bg-brand text-white hover:bg-brand-hover` |
| secondary | `bg-bg-elevated text-text-primary hover:bg-bg-hover` |
| ghost | `bg-transparent text-text-secondary hover:bg-bg-elevated` |
| danger | `bg-danger text-white hover:opacity-90` |
| accent | `bg-accent text-white hover:bg-accent-hover` |

### 卡片

```css
background: var(--color-bg-card);
border: 1px solid var(--color-border);
border-radius: var(--radius-lg);
box-shadow: var(--shadow-sm);
```

可选 hover：`hover:shadow-md hover:border-brand`

### 链接

```css
color: var(--color-text-primary);
&:hover { color: var(--color-brand); }
```

### Tag / Chip

```css
background: var(--color-brand-subtle);
color: var(--color-brand);
border-radius: var(--radius-full);
```

## 禁用项（来自 `AGENTS.md`）

❌ **绝对禁止**：

- 紫色 / 靛蓝色 / 蓝紫渐变（已从代码库彻底清除：grep 验证）
- 纯平背景色（必须有纹理或渐变）
- Tailwind 默认色板（indigo-500 等）
- Hero + 三卡片布局
- 完美居中对齐
- Shadcn 默认组件（必须深度定制）
- Emoji 作为功能图标
- 线性动画（用 spring / ease-out）

## 响应式断点

| Name | Range | 设备 |
|------|-------|------|
| xs | < 480px | 小屏手机 |
| sm | 480-768px | 普通手机 |
| md | 768-1024px | 平板 |
| lg | 1024-1280px | 小屏笔记本 |
| xl | > 1280px | 桌面 |

## 触摸目标

移动端 button / link / clickable 最小 `44px × 44px`（使用 `--touch-target-min`）

## 安全区域

刘海屏 / Home Indicator 用 `env(safe-area-inset-*)`，已支持 `.safe-area-top` / `.safe-area-bottom`

## 渐变（推荐用法）

| 渐变 | 用途 |
|------|------|
| `--yt-brand-gradient` | Hero / 大标题背景 |
| `--yt-bg-gradient` | 页面背景（米白渐变） |

## Phase 历史

- **Phase 0 (2026-06-13)**：墨绿 + 暖橙 + Noto Sans SC，紫色彻底清除