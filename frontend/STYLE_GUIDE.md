# Linyu 前端设计规范 (P3 设计令牌文档)

> 阶段: P0-P3 全部完成 (2026-06-19)
> 维护者: 前端团队
> 配套文件: `src/styles/design-tokens.css` · `src/styles/tailwind.css`

---

## 一、设计原则

| 原则 | 说明 |
|------|------|
| **克制配色** | 颜色变量只有一套 `--sf-*` 前缀,禁止内联十六进制 |
| **图标优先** | 全部用 `lucide-vue-next`,**禁止 emoji / HTML entity** |
| **组件统一** | UI 一律走 `Sf*` 组件,禁止 `el-*` (Element Plus) |
| **变量优先** | CSS 颜色 / 间距 / 圆角 / 动画时长必须用变量,不允许魔法数字 |
| **响应式** | 覆盖 1280 / 1024 / 768 / 480 断点 |
| **暗色模式** | 所有新加 CSS 必须用 `--sf-*` 变量 (自动支持) |

---

## 二、命名体系 (设计令牌)

### 2.1 颜色 — `--sf-*` 前缀 (P0 统一)

| Token | 浅色 | 暗色 (P2 优化后) | 用途 |
|-------|------|-----------------|------|
| `--sf-brand` | `#2563EB` | `#60A5FA` | 主品牌色,CTA、链接 |
| `--sf-brand-hover` | `#0A3A2D` | `#93C5FD` | hover 态 |
| `--sf-brand-light` | `#93C5FD` | rgba(96,165,250,0.25) | 文字背景 |
| `--sf-brand-subtle` | `#E8F0EB` | rgba(96,165,250,0.12) | 高亮背景 / 选中态 |
| `--sf-accent` | `#F59E0B` | `#FBBF24` | 琥珀金强调(热度/警示) |
| `--sf-success` | `#10B981` | `#86EFAC` | 成功 |
| `--sf-warning` | `#F59E0B` | `#FBBF24` | 警告 |
| `--sf-danger` | `#EF4444` | `#F87171` | 危险 |
| `--sf-info` | `#6366F1` | `#60A5FA` | 信息 |
| `--sf-text-primary` | `#111827` | `#F1F5F9` | 主文字 |
| `--sf-text-secondary` | `#6B7280` | `#94A3B8` | 次文字 |
| `--sf-text-muted` | `#9CA3AF` | `#64748B` | 弱化文字 |
| `--sf-bg` | `#F9FAFB` | `#1a1a2e` | 主背景 |
| `--sf-bg-card` | `#FFFFFF` | `#252540` | 卡片背景 |
| `--sf-bg-elevated` | `#F3F4F6` | `#2d2d4a` | 高亮层 |
| `--sf-border` | `#E5E7EB` | rgba(255,255,255,0.08) | 边框 |

### 2.2 Admin 独立令牌 (P0 新增)

| Token | 浅色 | 暗色 | 用途 |
|-------|------|------|------|
| `--sf-admin-bg` | `#F5F7F5` | `#1a1a2e` | 后台底色 (暖灰白 / 深石板) |
| `--sf-admin-bg-card` | `#FFFFFF` | `#252540` | 卡片 |
| `--sf-admin-bg-hover` | `#F0F4F1` | rgba(96,165,250,0.08) | hover |
| `--sf-admin-bg-active` | `#E8F5EE` | rgba(96,165,250,0.15) | 菜单激活 |
| `--sf-admin-border` | `#E5E9E5` | rgba(255,255,255,0.08) | 边框 |
| `--sf-admin-border-hover` | `#DDE2DD` | rgba(255,255,255,0.16) | 边框 hover |
| `--sf-admin-text-primary` | `#1A2820` | `#F1F5F9` | 主文字 |
| `--sf-admin-text-secondary` | `#5A6B62` | `#94A3B8` | 次文字 |
| `--sf-admin-text-muted` | `#8A9A90` | `#64748B` | 弱化 |
| `--sf-admin-accent` | `#F59E0B` | `#60A5FA` | 琥珀强调 |
| `--sf-admin-overlay` | rgba(255,255,255,0.04) | rgba(255,255,255,0.04) | 内部叠加层 |

### 2.3 圆角 — `--sf-radius-*` (P1 4px 网格化)

| Token | 值 | 用途 |
|-------|-----|------|
| `--sf-radius-sm` | 6px | 标签、小徽章 |
| `--sf-radius-md` | 10px | 输入框、下拉框 |
| `--sf-radius-lg` | 14px | 卡片 |
| `--sf-radius-xl` | 20px | 大卡片、弹窗 |
| `--sf-radius-full` | 9999px | 药丸按钮、筛选标签 |

### 2.4 间距 — `--sf-space-*` (P1 4px 网格化)

| Token | 值 | 用途 |
|-------|-----|------|
| `--sf-space-0` | 0 | 复位 |
| `--sf-space-1` | 4px | 最小间距 |
| `--sf-space-2` | 8px | 紧凑间距 |
| `--sf-space-3` | 12px | 组件内 padding |
| `--sf-space-4` | 16px | 常规间距 |
| `--sf-space-5` | 20px | 卡片内 padding |
| `--sf-space-6` | 24px | section 间距 |
| `--sf-space-8` | 32px | 大间距 |
| `--sf-space-10` | 40px | 段落间距 |
| `--sf-space-12` | 48px | 区块间距 |
| `--sf-space-16` | 64px | 页面级间距 |

### 2.5 动画 — `--sf-duration-*` / `--sf-ease-*` (P2 标准化)

| Token | 值 | 用途 |
|-------|-----|------|
| `--sf-duration-fast` | 150ms | hover、focus、tap |
| `--sf-duration-normal` | 200ms | 弹窗、tooltip |
| `--sf-duration-slow` | 300ms | 大动画、页面切换 |
| `--sf-ease-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` | 默认 |
| `--sf-ease-bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | 弹跳反馈 |

### 2.6 阴影 — `--sf-shadow-*`

| Token | 值 | 用途 |
|-------|-----|------|
| `--sf-shadow-xs` | `0 1px 2px rgba(0,0,0,0.05)` | 文字辅助 |
| `--sf-shadow-sm` | `0 1px 3px rgba(0,0,0,0.1)` | 卡片 |
| `--sf-shadow-md` | `0 4px 12px rgba(0,0,0,0.1)` | hover 卡片 |
| `--sf-shadow-lg` | `0 12px 32px rgba(0,0,0,0.15)` | 弹窗 |

---

## 三、组件体系

### 3.1 UI 组件 (`src/components/ui/`)

| 组件 | 用途 | 替代 |
|------|------|------|
| `SfButton` | 按钮(5 类型 × 3 尺寸) | `<button>`, `el-button` |
| `SfInput` | 输入框 | `<input>`, `el-input` |
| `SfSelect` | 下拉 | `<select>`, `el-select` |
| `SfForm` / `SfFormItem` | 表单 | `el-form` / `el-form-item` |
| `SfDialog` | 弹窗 | `el-dialog` |
| `SfPagination` | 分页 | `el-pagination` |
| `SfToast` | Toast 提示 | `ElMessage` |
| `SfTag` | 标签 | `el-tag` |
| `SfAvatar` | 头像 | — |
| `SfEmpty` | 空状态 | — |
| `SfSpinner` | Loading | — |
| `SfSwitch` | 开关 | `el-switch` |
| `SfDropdown` | 下拉菜单 | `el-dropdown` |
| `SfPopconfirm` | 气泡确认 | `el-popconfirm` |
| `SfConfirmDialog` | 确认弹窗 | `el-message-box` |
| `SfProgress` | 进度条 | `el-progress` |
| `SfTooltip` | 提示 | `el-tooltip` |
| `SfTabs` | Tab | `el-tabs` |
| `SfTable` | 表格 | `el-table` |

### 3.2 公共组件 (`src/components/common/`)

| 组件 | 用途 |
|------|------|
| `PageHeader` | 页面头部(标题 + 描述 + 操作) |
| `VideoCard` | 视频卡片(支持 completed / showPlayIcon / progressText props) |
| `FilterChip` | 筛选标签(支持 count 徽章) |
| `EmptyState` | 空状态(支持图片 + CTA) |
| `ListSkeleton` | 列表骨架屏 |
| `AnnouncementBanner` | 公告横幅(顶部 / 弹窗两态) |

### 3.3 按钮层级 (P1 标准化)

| type | 用途 | 样式 |
|------|------|------|
| `primary` | 主操作(只允许 1 个/页) | 实心品牌色 |
| `default` | 次要操作 | 边框 + 透明 |
| `ghost` | 取消/弱化 | 文字 + 无边框 |
| `subtle` | 二级弱化(导出/复制) | 浅灰背景 |
| `danger` | 删除/不可逆 | 红色实心 |

**规则**:
- 一个页面最多 1 个 `primary` 按钮
- `danger` 必须配 `popconfirm` 二次确认
- `loading` 状态自动显示 spinner,禁用点击

### 3.4 Loading 状态 (P1 统一)

| 场景 | 组件 |
|------|------|
| 按钮内 | `SfButton :loading="true"` |
| 区块加载 | `<SfSpinner />` 或 `v-loading` |
| 页面级 | `ListSkeleton` |
| 异步操作反馈 | `toast.success()` / `toast.error()` |

### 3.5 Hover 规范 (P1)

| 元素 | hover 效果 |
|------|----------|
| 按钮 | `background-color` 切换,150ms |
| 卡片 | `transform: translateY(-2px)` + 阴影加深 |
| 链接 | 下划线出现或颜色加深 |
| 菜单项 | 背景 `var(--sf-bg-hover)` |

---

## 四、图标系统 (P0 替换)

**必须用 `lucide-vue-next`,禁止 emoji / HTML entity**

```vue
<!-- ✅ 推荐 -->
<template>
  <BookOpen :size="16" class="trust-icon" />
  <Target :size="14" />
  <Lightbulb :size="14" />
</template>

<script setup>
import { BookOpen, Target, Lightbulb } from 'lucide-vue-next'
</script>

<!-- ❌ 禁止 -->
<span>📚 1000+ 精选视频</span>
<span class="icon">&#128214;</span>
```

**常用图标速查**:
- 学习:`BookOpen`, `GraduationCap`, `Library`
- 视频:`Play`, `Pause`, `Video`, `Headphones`
- 智能解读:`Sparkles`, `Lightbulb`, `Wand2`
- 跟读:`Mic`, `Crosshair`(发音问题)
- 收藏:`Bookmark`, `Star`, `Heart`
- 状态:`Check`, `X`, `AlertCircle`, `Info`
- 导航:`ChevronLeft`, `ChevronRight`, `ArrowLeft`, `ArrowRight`
- 统计:`BarChart3`, `TrendingUp`, `Flame`(连续), `Trophy`, `Crown`
- 操作:`Plus`, `Minus`, `Edit`, `Trash2`, `Settings`, `Search`, `Filter`, `MoreHorizontal`

---

## 五、暗色模式 (P2 优化)

### 5.1 优化前后对比

| Token | 优化前 | 优化后 | 改动原因 |
|-------|--------|--------|----------|
| `--color-bg-base` | `#0F172A` 深石板 | `#1a1a2e` 紫调 | 没这么黑,更现代 |
| `--color-bg-card` | `#1E293B` 蓝灰 | `#252540` 蓝紫 | 跟底色协调 |
| `--color-bg-elevated` | `#334155` | `#2d2d4a` | 卡片→高亮过渡更自然 |
| `--glass-bg` | `rgba(30,41,59,0.9)` | `rgba(37,37,64,0.9)` | 跟新卡片色一致 |

### 5.2 主题切换

主题存储在 `useUserStore.theme`,支持 `light` / `dark` / `auto`。通过 `<html data-theme="dark">` 切换。

### 5.3 开发规则

- ✅ 所有颜色用 `--sf-*` / `--color-*` 变量
- ❌ 禁止在 `<style scoped>` 中写 `#0F172A` / `#1E293B` 等硬编码
- ❌ 禁止用 `:deep()` 改第三方组件颜色(改用 Sf* 包装)

---

## 六、响应式断点 (P1 标准化)

```css
/* 移动优先 */
@media (min-width: 480px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

| 断点 | 宽度 | 设备 |
|------|------|------|
| `xs` | 480px | 大手机 |
| `sm` | 576px | 手机横屏 |
| `md` | 768px | 平板竖屏 |
| `lg` | 1024px | 平板横屏 / 小桌面 |
| `xl` | 1280px | 桌面 |
| `2xl` | 1536px | 大屏 |

---

## 七、组件展示

所有 `Sf*` 组件的可视化效果见 `/_showcase` 路由(开发环境),包括:
- 按钮 5 类型 × 3 尺寸
- 表单 (Input / Select / FormItem)
- 弹窗 / 确认 / 提示
- 反馈 (Toast / Spinner / Skeleton)
- 数据 (Table / Pagination / Tabs / Tag)

---

## 八、新组件开发流程

1. 在 `src/components/ui/` 创建 `SfXxx.vue`
2. 用 `--sf-*` 变量(不要硬编码)
3. 支持 `loading` / `disabled` / `size` 标准 props
4. 暗色模式自动适配
5. 响应式覆盖标准断点
6. 接入 `/_showcase` 展示页
7. 写 markdown 用法说明在本文件

---

## 九、禁止项清单

- ❌ 颜色硬编码(`#FF0000`, `rgba(0,0,0,0.5)` 等)
- ❌ Emoji / HTML entity 作为图标
- ❌ `el-*` Element Plus 组件
- ❌ 间距 / 圆角 / 时长魔法数字
- ❌ `transition: all`(改用具体属性)
- ❌ 线性动画 `ease-in-out`(改用 `var(--sf-ease-standard)`)
- ❌ Tailwind 默认色板(用 `--color-brand` 等)
- ❌ 完美居中三卡片布局
- ❌ 紫色 / 靛蓝渐变

---

## 十、参考资源

- 设计系统文档: `src/styles/design-system.md`
- 设计令牌: `src/styles/design-tokens.css`
- Tailwind 配置: `src/styles/tailwind.css`
- AGENTS.md 规则: `/AGENTS.md`
- 组件展示: `/_showcase` 路由
- 参考站: blue.com (清新绿系) / speakvlog.com
