# Fluenty Design System

> Fluenty/video_crawler 项目的设计系统索引。所有 UI 组件、Design Token、视觉规范的可视化文档。

## 在线访问

**Storybook** 是 design system 的主要展示方式：
- **本地启动**: `cd frontend && npm run storybook` → http://localhost:6006
- **构建静态**: `cd frontend && npm run build-storybook` → `frontend/storybook-static/`

## 目录结构

```
frontend/src/
├── components/
│   ├── ui/         # 22 个 Sf* 通用组件 (按钮/输入/对话框/...)
│   ├── common/     # 6 个 common 组件 (PageHeader/EmptyState/...)
│   └── learn/      # 业务组件 (LearnVideoPlayer/LearnSubtitleList/...)
├── design-tokens/  # 7 个 Design Token 故事 (色板/字体/间距/圆角/阴影/动效/暗色)
└── styles/
    ├── design-tokens.css  # --sf-* token 兼容层
    ├── design-system.md   # Token 详细说明
    ├── tailwind.css       # @theme 原始定义 (含 .dark 覆盖)
    └── global.css         # 全局样式
```

## UI 组件 (22 个)

| 组件 | 用途 | 必含 stories |
|------|------|-------------|
| `SfButton` | 按钮 (5 type × 3 size) | Default/Primary/Ghost/Subtle/Danger/Loading/Disabled/Round/Block |
| `SfInput` | 输入框 | Clearable/Password/Prefix/Error/Disabled/AllSizes |
| `SfDialog` | 模态对话框 | WithTitle/WithFooter/3 档宽度 |
| `SfTag` | 标签 (5 type) | Closable/AllTypes |
| `SfSwitch` | 开关 | WithLabel/Disabled/Sizes |
| `SfSelect` | 下拉选择 | Multiple/Clearable/Sizes |
| `SfDropdown` | 下拉菜单 | WithDivider/WithIcon/WithActions |
| `SfTabs` | 标签页 | ManyTabs/WithBadge |
| `SfEmpty` | 空状态 | WithIcon/WithCTA/AllVariants |
| `SfSpinner` | 加载动画 | 3 档尺寸 |
| `SfAvatar` | 头像 | 5 档尺寸/WithImage/WithInitials |
| `SfCombobox` | 可搜索下拉 | Searchable/WithClear/30+ items |
| `SfConfirmDialog` | 确认对话框 | Danger/Info |
| `SfProgress` | 进度条 (line/circle) | Success/Error |
| `SfPagination` | 分页器 | ManyPages/WithPageSize |
| `SfPopconfirm` | 气泡确认 | WithIcon/Danger |
| `SfTable` | 表格 | Striped/WithActions |
| `SfToast` | 提示消息 (4 type) | WithAction |
| `SfTooltip` | 文字提示 | 4 方向/ClickTrigger |
| `SfForm` + `SfFormItem` | 表单 | Validation/HorizontalLayout |
| `SfAvatar` / `SfSpinner` / ... | ... | ... |

(略 - 全部 22 个 Sf* 组件都有 stories)

## Common 组件 (6 个)

| 组件 | 用途 |
|------|------|
| `PageHeader` | 页面标题 + actions slot + 返回按钮 + 面包屑 |
| `EmptyState` | 空状态 (图标 + 描述 + CTA) |
| `FilterChip` | 筛选 chip (active/inactive + 图标 + 计数) |
| `ListSkeleton` | 列表骨架屏 (rows/avatar/actions) |
| `AnnouncementBanner` | 公告横幅 (info/warning/success/update) |
| `VideoCard` | 视频卡片 (cover + progress + duration + difficulty) |

## Design Tokens (7 个 stories)

通过 `Design Tokens/*` 路径访问，可视化展示所有设计变量。

| Token | 包含 |
|-------|------|
| `ColorPalette` | 品牌色/文字色/背景色/边框色/状态色 (5 stories) |
| `Typography` | 7 档字号 × 3 档字重 + 标题层级 (4 stories) |
| `Spacing` | 8 档 `--sf-space-*` 可视化条 (3 stories) |
| `Radius` | 5 档 `--sf-radius-*` 圆角 (3 stories) |
| `Shadow` | 4 档 `--sf-shadow-*` 阴影 (3 stories) |
| `Animation` | 3 档 `--sf-duration-*` + ease 动画 (4 stories) |
| `DarkMode` | 浅/暗主题切换对比 (3 stories) |

## 设计规范文档

- `frontend/STYLE_GUIDE.md` - 项目级样式指南
- `frontend/src/styles/design-system.md` - Token 详细说明
- `AGENTS.md` - 顶层设计规则 (反主流配色/无 emoji 图标/无 Tailwind 默认色)

## 主要 Token 速查

### 颜色 (--color-*)
```
--color-brand          # 品牌蓝
--color-brand-hover    # 品牌蓝 hover
--color-text-primary   # 主文字
--color-text-secondary # 次文字
--color-text-muted     # 弱化文字
--color-bg-base        # 页面背景
--color-bg-card        # 卡片背景
--color-bg-elevated    # 高亮层
--color-border         # 边框
--color-success / --color-warning / --color-danger / --color-info
```

### 圆角 (--sf-radius-*)
```
sm=8px  md=12px  lg=16px  xl=24px  full=9999px
```

### 间距 (--sf-space-*)
```
1=4px 2=8px 3=12px 4=16px 5=20px 6=24px 8=32px 10=40px
```

### 动画时长 (--sf-duration-*)
```
fast=150ms  normal=200ms  slow=300ms  slower=500ms
```

### 缓动 (--sf-ease-*)
```
standard  cubic-bezier(0.4, 0, 0.2, 1)
decelerate cubic-bezier(0, 0, 0.2, 1)
accelerate cubic-bezier(0.4, 0, 1, 1)
```

## 添加新组件

1. 在 `frontend/src/components/ui/` 创建 `SfXxx.vue` (继承 shadcn-vue/reka-ui 风格)
2. 同时创建 `SfXxx.stories.ts` (参考 SfButton.stories.ts 模板)
3. 至少 4 个 stories: Default + 主要 variants + AllVariants
4. 跑 `npm run storybook` 验证 (http://localhost:6006)
5. 提交: `feat(storybook): SfXxx stories`

## 添加新 Design Token

1. 在 `frontend/src/styles/tailwind.css` 加 `--color-xxx: #XXX` (亮 + 暗)
2. 在 `frontend/src/styles/design-tokens.css` 加兼容层 `--sf-xxx: var(--color-xxx)`
3. 更新 `frontend/src/design-tokens/ColorPalette.stories.ts` 加新色 swatch
4. 更新 `design-system.md` + 本文档
5. 跑 `npm run build-storybook` 验证

## 验证

```bash
# 启动 Storybook (开发)
cd frontend && npm run storybook

# 构建静态 (用于部署/GH Pages)
cd frontend && npm run build-storybook

# 验证生产构建未坏
cd frontend && npm run build

# 跑后端测试 (确保 storybook 改动没影响 API)
cd backend && source .venv/bin/activate && pytest -q
```

## 维护

- **版本**: 跟项目主版本 (v1.0.0)
- **更新频率**: 每个 UI 组件变更时同步更新 stories
- **owner**: @jun哥 (俊哥) - 主设计师 + 主开发
- **Storybook 版本**: 8.6+ (Vite 5 + Vue 3.4 兼容)
