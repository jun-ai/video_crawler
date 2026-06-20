import type { Meta, StoryObj } from '@storybook/vue3'
import SfSpinner from './SfSpinner.vue'

const meta = {
  title: 'UI/SfSpinner',
  component: SfSpinner,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg'],
      description: '尺寸: sm (16px) / md (24px) / lg (40px)'
    }
  }
} satisfies Meta<typeof SfSpinner>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    size: 'md'
  },
  render: (args) => ({
    components: { SfSpinner },
    setup() { return { args } },
    template: `
      <div style="padding: 32px; display: flex; align-items: center; justify-content: center;">
        <SfSpinner :size="args.size" />
      </div>
    `
  })
}

export const AllSizes: Story = {
  render: () => ({
    components: { SfSpinner },
    template: `
      <div style="padding: 32px; display: flex; gap: 32px; align-items: center;">
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
          <SfSpinner size="sm" />
          <span style="font-size: 12px; color: var(--muted-foreground);">sm · 16px</span>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
          <SfSpinner size="md" />
          <span style="font-size: 12px; color: var(--muted-foreground);">md · 24px</span>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
          <SfSpinner size="lg" />
          <span style="font-size: 12px; color: var(--muted-foreground);">lg · 40px</span>
        </div>
      </div>
    `
  })
}

export const WithText: Story = {
  args: {
    size: 'md'
  },
  render: (args) => ({
    components: { SfSpinner },
    setup() { return { args } },
    template: `
      <div style="padding: 32px; display: flex; flex-direction: column; gap: 24px; align-items: flex-start;">
        <div style="display: flex; align-items: center; gap: 8px; color: var(--muted-foreground); font-size: 14px;">
          <SfSpinner :size="args.size" />
          <span>加载中...</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; color: var(--muted-foreground); font-size: 14px;">
          <SfSpinner size="sm" />
          <span>正在解析视频...</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px; color: var(--muted-foreground); font-size: 14px;">
          <SfSpinner size="lg" />
          <span>正在准备下载, 请稍候</span>
        </div>
      </div>
    `
  })
}

export const Centered: Story = {
  args: {
    size: 'lg'
  },
  render: (args) => ({
    components: { SfSpinner },
    setup() { return { args } },
    template: `
      <div style="width: 100%; height: 240px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; border: 1px dashed var(--border); border-radius: 8px;">
        <SfSpinner :size="args.size" />
        <span style="font-size: 14px; color: var(--muted-foreground);">正在加载数据...</span>
      </div>
    `
  })
}
