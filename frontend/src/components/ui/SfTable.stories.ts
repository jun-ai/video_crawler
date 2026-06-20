import type { Meta, StoryObj } from '@storybook/vue3'
import SfTable from './SfTable.vue'
import SfButton from './SfButton.vue'
import SfTag from './SfTag.vue'
import { Eye, Pencil, Trash2 } from 'lucide-vue-next'

const meta = {
  title: 'UI/SfTable',
  component: SfTable,
  tags: ['autodocs'],
  argTypes: {
    columns: {
      control: 'object',
      description: '列定义: [{ key, label, width }]'
    },
    data: {
      control: 'object',
      description: '数据行 (对象数组, key 与 columns 对应)'
    }
  }
} satisfies Meta<typeof SfTable>

export default meta
type Story = StoryObj<typeof meta>

const baseColumns = [
  { key: 'title', label: '标题', width: '40%' },
  { key: 'channel', label: '频道', width: '20%' },
  { key: 'views', label: '播放量', width: '15%' },
  { key: 'duration', label: '时长', width: '12%' },
  { key: 'uploadedAt', label: '上传时间', width: '13%' }
]

const baseData = [
  { title: '用 10 分钟讲清楚 WebAssembly', channel: '码农高师傅', views: '12.4 万', duration: '09:58', uploadedAt: '2 天前' },
  { title: '为什么 Rust 是我最喜欢的系统语言', channel: '铁锈教父', views: '8.7 万', duration: '21:33', uploadedAt: '5 天前' },
  { title: 'iPhone 16 真实使用一周感受', channel: '数码老炮儿', views: '32.1 万', duration: '14:02', uploadedAt: '1 周前' }
]

// 5 列 × 3 行基础表格
export const Default: Story = {
  args: {
    columns: baseColumns,
    data: baseData
  },
  render: (args) => ({
    components: { SfTable },
    setup() { return { args } },
    template: `
      <div style="padding: 24px; width: 880px;">
        <SfTable :columns="args.columns" :data="args.data" />
      </div>
    `
  })
}

// Striped 风格 — 通过 slot 自定义行背景 (table 原生不支持 striped, 用 nth-child 模拟)
export const Striped: Story = {
  args: {
    columns: baseColumns,
    data: baseData
  },
  render: (args) => ({
    components: { SfTable },
    setup() { return { args } },
    template: `
      <div style="padding: 24px; width: 880px;">
        <style>
          .sf-table-striped tbody tr:nth-child(even) td {
            background: var(--color-bg-elevated) !important;
          }
        </style>
        <SfTable :columns="args.columns" :data="args.data" class="sf-table-striped" />
        <p style="margin-top: 12px; color: var(--color-text-muted); font-size: 13px;">
          偶数行用浅色背景,提高长表格可读性
        </p>
      </div>
    `
  })
}

// 带操作列 — 用 slot 注入按钮
export const WithActions: Story = {
  args: {
    columns: [
      ...baseColumns.slice(0, 4),
      { key: 'status', label: '状态', width: '12%' },
      { key: 'actions', label: '操作', width: '140px' }
    ],
    data: [
      { title: '用 10 分钟讲清楚 WebAssembly', channel: '码农高师傅', views: '12.4 万', duration: '09:58', status: '已发布' },
      { title: '为什么 Rust 是我最喜欢的系统语言', channel: '铁锈教父', views: '8.7 万', duration: '21:33', status: '审核中' },
      { title: 'iPhone 16 真实使用一周感受', channel: '数码老炮儿', views: '32.1 万', duration: '14:02', status: '草稿' }
    ]
  },
  render: (args) => ({
    components: { SfTable, SfButton, SfTag, Eye, Pencil, Trash2 },
    setup() { return { args, Eye, Pencil, Trash2 } },
    template: `
      <div style="padding: 24px; width: 960px;">
        <SfTable :columns="args.columns" :data="args.data">
          <template #status="{ row }">
            <SfTag :type="row.status === '已发布' ? 'success' : row.status === '审核中' ? 'warning' : 'default'">
              {{ row.status }}
            </SfTag>
          </template>
          <template #actions="{ row }">
            <div style="display: flex; gap: 6px;">
              <SfButton size="sm" type="ghost" title="查看">
                <template #default><Eye :size="14" /></template>
              </SfButton>
              <SfButton size="sm" type="default" title="编辑">
                <template #default><Pencil :size="14" /></template>
              </SfButton>
              <SfButton size="sm" type="danger" title="删除">
                <template #default><Trash2 :size="14" /></template>
              </SfButton>
            </div>
          </template>
        </SfTable>
      </div>
    `
  })
}

// 空数据 — 组件内置「暂无数据」兜底
export const Empty: Story = {
  args: {
    columns: baseColumns,
    data: []
  },
  render: (args) => ({
    components: { SfTable },
    setup() { return { args } },
    template: `
      <div style="padding: 24px; width: 880px;">
        <SfTable :columns="args.columns" :data="args.data" />
      </div>
    `
  })
}

// 长数据 — 验证横向滚动
export const ManyColumns: Story = {
  args: {
    columns: [
      { key: 'id', label: 'ID', width: '60px' },
      { key: 'title', label: '标题', width: '220px' },
      { key: 'channel', label: '频道', width: '140px' },
      { key: 'category', label: '分类', width: '100px' },
      { key: 'views', label: '播放量', width: '100px' },
      { key: 'likes', label: '点赞', width: '90px' },
      { key: 'comments', label: '评论', width: '90px' },
      { key: 'duration', label: '时长', width: '80px' },
      { key: 'uploadedAt', label: '上传时间', width: '120px' },
      { key: 'quality', label: '画质', width: '80px' }
    ],
    data: [
      { id: 'v001', title: 'Vue 3.5 新特性深度解读', channel: '前端早茶', category: '前端', views: '5.2 万', likes: '3.1 千', comments: '287', duration: '18:42', uploadedAt: '2026-06-15', quality: '1080p' },
      { id: 'v002', title: '我用 30 天学完了 CS50', channel: '转码日记', category: '编程', views: '12.8 万', likes: '8.4 千', comments: '1.2 千', duration: '24:11', uploadedAt: '2026-06-10', quality: '4K' },
      { id: 'v003', title: '东京 vlog | 一个人吃拉面', channel: '走走停停', category: '旅行', views: '28.6 万', likes: '1.9 万', comments: '3.4 千', duration: '12:08', uploadedAt: '2026-06-08', quality: '1440p' }
    ]
  },
  render: (args) => ({
    components: { SfTable },
    setup() { return { args } },
    template: `
      <div style="padding: 24px; width: 720px;">
        <SfTable :columns="args.columns" :data="args.data" />
        <p style="margin-top: 12px; color: var(--color-text-muted); font-size: 13px;">
          列数超出容器宽度时自动横向滚动
        </p>
      </div>
    `
  })
}

// 自定义单元格 — 头像 + 名称
export const CustomCells: Story = {
  args: {
    columns: [
      { key: 'user', label: '用户', width: '40%' },
      { key: 'role', label: '角色', width: '20%' },
      { key: 'posts', label: '发帖数', width: '15%' },
      { key: 'joinedAt', label: '加入时间', width: '25%' }
    ],
    data: [
      { name: '高师傅', avatar: 'https://picsum.photos/seed/u1/40/40', role: '管理员', posts: 1284, joinedAt: '2024-03-12' },
      { name: 'Lin', avatar: 'https://picsum.photos/seed/u2/40/40', role: '编辑', posts: 562, joinedAt: '2024-08-21' },
      { name: '老炮儿', avatar: 'https://picsum.photos/seed/u3/40/40', role: '会员', posts: 89, joinedAt: '2025-11-04' }
    ]
  },
  render: (args) => ({
    components: { SfTable, SfTag },
    setup() { return { args } },
    template: `
      <div style="padding: 24px; width: 720px;">
        <SfTable :columns="args.columns" :data="args.data">
          <template #user="{ row }">
            <div style="display: flex; align-items: center; gap: 10px;">
              <img :src="row.avatar" :alt="row.name" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />
              <span style="font-weight: 500;">{{ row.name }}</span>
            </div>
          </template>
          <template #role="{ row }">
            <SfTag :type="row.role === '管理员' ? 'danger' : row.role === '编辑' ? 'warning' : 'default'">
              {{ row.role }}
            </SfTag>
          </template>
        </SfTable>
      </div>
    `
  })
}