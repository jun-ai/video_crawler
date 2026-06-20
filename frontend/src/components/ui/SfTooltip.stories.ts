import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import SfTooltip from './SfTooltip.vue'
import SfButton from './SfButton.vue'
import { Info, HelpCircle, AlertCircle } from 'lucide-vue-next'

const meta = {
  title: 'UI/SfTooltip',
  component: SfTooltip,
  tags: ['autodocs'],
  argTypes: {
    content: {
      control: 'text',
      description: '提示文本（字符串）'
    },
    placement: {
      control: { type: 'select' },
      options: ['top', 'right', 'bottom', 'left'],
      description: '弹出位置'
    }
  }
} satisfies Meta<typeof SfTooltip>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    content: '悬浮看提示',
    placement: 'top'
  },
  render: (args) => ({
    components: { SfTooltip, SfButton },
    setup() { return { args } },
    template: `
      <SfTooltip v-bind="args">
        <SfButton type="default">悬浮在我上面</SfButton>
      </SfTooltip>
    `
  })
}

export const OnIcon: Story = {
  args: {
    content: '这是图标的说明',
    placement: 'top'
  },
  render: (args) => ({
    components: { SfTooltip, Info },
    setup() { return { args } },
    template: `
      <SfTooltip v-bind="args">
        <Info :size="20" style="cursor: help; color: var(--color-text-secondary)" />
      </SfTooltip>
    `
  })
}

export const ClickTrigger: Story = {
  name: 'Click Trigger',
  render: () => ({
    components: { SfTooltip, SfButton },
    setup() {
      const tooltipEl = ref<any>(null)
      let shown = false
      function toggle() {
        const el = tooltipEl.value?.$el
        if (!el) return
        const evt = shown ? 'mouseleave' : 'mouseenter'
        el.dispatchEvent(new MouseEvent(evt, { bubbles: false }))
        shown = !shown
      }
      return { tooltipEl, toggle }
    },
    template: `
      <SfTooltip ref="tooltipEl" content="由点击触发的提示">
        <SfButton type="primary" @click="toggle">点我看提示</SfButton>
      </SfTooltip>
    `
  })
}

export const Positions: Story = {
  name: '四个方向',
  render: () => ({
    components: { SfTooltip, SfButton },
    template: `
      <div style="display: flex; gap: 80px; padding: 80px 40px; align-items: center; justify-content: center;">
        <SfTooltip content="顶部提示" placement="top">
          <SfButton type="default">Top</SfButton>
        </SfTooltip>
        <SfTooltip content="右侧提示" placement="right">
          <SfButton type="default">Right</SfButton>
        </SfTooltip>
      </div>
      <div style="display: flex; gap: 80px; padding: 40px; align-items: center; justify-content: center;">
        <SfTooltip content="底部提示" placement="bottom">
          <SfButton type="default">Bottom</SfButton>
        </SfTooltip>
        <SfTooltip content="左侧提示" placement="left">
          <SfButton type="default">Left</SfButton>
        </SfTooltip>
      </div>
    `
  })
}

export const WithRichContent: Story = {
  name: '富文本提示',
  render: () => ({
    components: { SfTooltip, SfButton, AlertCircle },
    template: `
      <div style="display: flex; gap: 24px; align-items: center;">
        <SfTooltip content="账号将被永久删除 · 不可恢复">
          <SfButton type="danger">删除账号</SfButton>
        </SfTooltip>
        <SfTooltip content="新功能上线 · 立即体验">
          <AlertCircle :size="20" style="cursor: help; color: var(--color-brand)" />
        </SfTooltip>
        <SfTooltip content="提示：按 Cmd + S 可以快速保存">
          <SfButton type="subtle">保存</SfButton>
        </SfTooltip>
      </div>
    `
  })
}

export const WithHelpIcon: Story = {
  name: '帮助图标',
  render: () => ({
    components: { SfTooltip, HelpCircle },
    template: `
      <div style="display: flex; align-items: center; gap: 8px;">
        <span>用户名</span>
        <SfTooltip content="用户名是登录凭证，3-20 字符">
          <HelpCircle :size="14" style="cursor: help; color: var(--color-text-muted)" />
        </SfTooltip>
      </div>
    `
  })
}