import type { Meta, StoryObj } from '@storybook/vue3'
import SfPopconfirm from './SfPopconfirm.vue'
import SfButton from './SfButton.vue'
import { Trash2, LogOut, Star, Download } from 'lucide-vue-next'

const meta = {
  title: 'UI/SfPopconfirm',
  component: SfPopconfirm,
  tags: ['autodocs'],
  argTypes: {
    title: { control: 'text', description: '气泡提示文案' }
  }
} satisfies Meta<typeof SfPopconfirm>

export default meta
type Story = StoryObj<typeof meta>

// 基础 — 点击按钮弹出确认气泡
export const Default: Story = {
  args: {
    title: '确定要执行此操作吗？'
  },
  render: (args) => ({
    components: { SfPopconfirm, SfButton },
    setup() {
      const onConfirm = () => window.alert('已确认 ✓')
      const onCancel = () => window.alert('已取消 ✗')
      return { args, onConfirm, onCancel }
    },
    template: `
      <div style="padding: 80px 24px 24px; display: flex; gap: 16px;">
        <SfPopconfirm :title="args.title" @confirm="onConfirm" @cancel="onCancel">
          <SfButton type="primary">点击弹出气泡</SfButton>
        </SfPopconfirm>
      </div>
    `
  })
}

// 自定义文案 + 图标 trigger
export const WithIcon: Story = {
  args: {
    title: '收藏这个视频到「我的最爱」?'
  },
  render: (args) => ({
    components: { SfPopconfirm, SfButton, Star },
    setup() {
      const onConfirm = () => window.alert('已收藏 ★')
      return { args, onConfirm, Star }
    },
    template: `
      <div style="padding: 80px 24px 24px; display: flex; gap: 16px; align-items: center;">
        <SfPopconfirm :title="args.title" @confirm="onConfirm">
          <button style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 8px; border: 1px solid var(--color-border); background: var(--color-bg-card); color: var(--color-text-primary); cursor: pointer; font-size: 14px;">
            <Star :size="16" />
            收藏
          </button>
        </SfPopconfirm>
        <SfPopconfirm title="下载这 3 个视频到本地?" @confirm="onConfirm">
          <button style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 8px; border: 1px solid var(--color-border); background: var(--color-bg-card); color: var(--color-text-primary); cursor: pointer; font-size: 14px;">
            <Download :size="16" />
            批量下载
          </button>
        </SfPopconfirm>
      </div>
    `
  })
}

// 删除场景 — 危险样式 (虽然组件本身没 danger, 用红色 trigger 强化语义)
export const Danger: Story = {
  args: {
    title: '这条视频会被永久删除,无法找回。确定吗?'
  },
  render: (args) => ({
    components: { SfPopconfirm, SfButton, Trash2 },
    setup() {
      const onConfirm = () => window.alert('已删除 (模拟)')
      return { args, onConfirm, Trash2 }
    },
    template: `
      <div style="padding: 80px 24px 24px;">
        <SfPopconfirm :title="args.title" @confirm="onConfirm">
          <SfButton type="danger">
            <template #default>
              <span style="display: inline-flex; align-items: center; gap: 6px;">
                <Trash2 :size="16" />
                删除视频
              </span>
            </template>
          </SfButton>
        </SfPopconfirm>
        <p style="margin-top: 24px; color: var(--color-text-muted); font-size: 13px;">
          点击删除按钮, 弹出确认气泡 → 点确定触发 confirm 事件
        </p>
      </div>
    `
  })
}

// 退出登录
export const Logout: Story = {
  args: {
    title: '退出后需要重新登录, 确定吗?'
  },
  render: (args) => ({
    components: { SfPopconfirm, SfButton, LogOut },
    setup() {
      const onConfirm = () => window.alert('已退出登录 (模拟)')
      return { args, onConfirm, LogOut }
    },
    template: `
      <div style="padding: 80px 24px 24px; display: flex; justify-content: flex-end;">
        <SfPopconfirm :title="args.title" @confirm="onConfirm">
          <SfButton type="subtle">
            <template #default>
              <span style="display: inline-flex; align-items: center; gap: 6px;">
                <LogOut :size="16" />
                退出登录
              </span>
            </template>
          </SfButton>
        </SfPopconfirm>
      </div>
    `
  })
}

// 不同文案对比
export const TitleVariants: Story = {
  render: () => ({
    components: { SfPopconfirm, SfButton },
    template: `
      <div style="padding: 80px 24px 24px; display: flex; gap: 12px; flex-wrap: wrap;">
        <SfPopconfirm title="保存草稿?">
          <SfButton>保存草稿</SfButton>
        </SfPopconfirm>
        <SfPopconfirm title="清空所有筛选条件?">
          <SfButton>清空筛选</SfButton>
        </SfPopconfirm>
        <SfPopconfirm title="取消订阅这个频道?">
          <SfButton>取消订阅</SfButton>
        </SfPopconfirm>
        <SfPopconfirm title="合并到「工作」收藏夹?">
          <SfButton>合并收藏夹</SfButton>
        </SfPopconfirm>
      </div>
    `
  })
}