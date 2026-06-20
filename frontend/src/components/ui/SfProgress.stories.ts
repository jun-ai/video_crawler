import type { Meta, StoryObj } from '@storybook/vue3'
import SfProgress from './SfProgress.vue'

const meta = {
  title: 'UI/SfProgress',
  component: SfProgress,
  tags: ['autodocs'],
  argTypes: {
    percentage: {
      control: { type: 'range', min: 0, max: 100, step: 1 },
      description: '进度百分比 0-100'
    },
    type: {
      control: { type: 'select' },
      options: ['brand', 'success', 'danger'],
      description: '颜色: brand (渐变) / success (绿) / danger (红)'
    },
    strokeWidth: {
      control: { type: 'number', min: 2, max: 24, step: 1 },
      description: '进度条高度 (px)'
    },
    showText: {
      control: 'boolean',
      description: '右侧是否显示百分比文字'
    }
  }
} satisfies Meta<typeof SfProgress>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    percentage: 30,
    type: 'brand',
    strokeWidth: 6,
    showText: false
  },
  render: (args) => ({
    components: { SfProgress },
    setup() { return { args } },
    template: '<div style="width: 360px;"><SfProgress v-bind="args" /></div>'
  })
}

export const Linear50: Story = {
  args: {
    percentage: 50,
    type: 'brand',
    strokeWidth: 8,
    showText: true
  },
  render: (args) => ({
    components: { SfProgress },
    setup() { return { args } },
    template: '<div style="width: 360px;"><SfProgress v-bind="args" /></div>'
  })
}

export const Success: Story = {
  args: {
    percentage: 100,
    type: 'success',
    strokeWidth: 8,
    showText: true
  },
  render: (args) => ({
    components: { SfProgress },
    setup() { return { args } },
    template: `
      <div style="width: 360px;">
        <SfProgress v-bind="args" />
        <div style="margin-top: 8px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af)">
          任务完成
        </div>
      </div>
    `
  })
}

export const Danger: Story = {
  args: {
    percentage: 88,
    type: 'danger',
    strokeWidth: 8,
    showText: true
  },
  render: (args) => ({
    components: { SfProgress },
    setup() { return { args } },
    template: `
      <div style="width: 360px;">
        <SfProgress v-bind="args" />
        <div style="margin-top: 8px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af)">
          失败率过高, 红色提示
        </div>
      </div>
    `
  })
}

export const ThinBar: Story = {
  args: {
    percentage: 64,
    type: 'brand',
    strokeWidth: 3,
    showText: false
  },
  render: (args) => ({
    components: { SfProgress },
    setup() { return { args } },
    template: '<div style="width: 360px;"><SfProgress v-bind="args" /></div>'
  })
}

export const ThickBar: Story = {
  args: {
    percentage: 42,
    type: 'brand',
    strokeWidth: 18,
    showText: true
  },
  render: (args) => ({
    components: { SfProgress },
    setup() { return { args } },
    template: '<div style="width: 360px;"><SfProgress v-bind="args" /></div>'
  })
}

export const EdgeCases: Story = {
  render: () => ({
    components: { SfProgress },
    template: `
      <div style="display: flex; flex-direction: column; gap: 14px; width: 360px;">
        <div>
          <div style="font-size: 12px; color: var(--color-text-tertiary, #9ca3af); margin-bottom: 4px;">0%</div>
          <SfProgress :percentage="0" :show-text="true" />
        </div>
        <div>
          <div style="font-size: 12px; color: var(--color-text-tertiary, #9ca3af); margin-bottom: 4px;">100%</div>
          <SfProgress :percentage="100" :show-text="true" />
        </div>
        <div>
          <div style="font-size: 12px; color: var(--color-text-tertiary, #9ca3af); margin-bottom: 4px;">超 100 (clamped to 100)</div>
          <SfProgress :percentage="142" :show-text="true" />
        </div>
        <div>
          <div style="font-size: 12px; color: var(--color-text-tertiary, #9ca3af); margin-bottom: 4px;">负数 (clamped to 0)</div>
          <SfProgress :percentage="-30" :show-text="true" />
        </div>
      </div>
    `
  })
}

export const AllProgress: Story = {
  render: () => ({
    components: { SfProgress },
    template: `
      <div style="display: flex; flex-direction: column; gap: 18px; width: 360px;">
        <div>
          <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; font-weight: 500">下载进度</div>
          <SfProgress :percentage="68" type="brand" :show-text="true" />
        </div>
        <div>
          <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; font-weight: 500">转码完成</div>
          <SfProgress :percentage="100" type="success" :show-text="true" />
        </div>
        <div>
          <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; font-weight: 500">解析失败</div>
          <SfProgress :percentage="88" type="danger" :show-text="true" />
        </div>
        <div>
          <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 6px; font-weight: 500">加载字幕</div>
          <SfProgress :percentage="34" :stroke-width="3" />
        </div>
      </div>
    `
  })
}
