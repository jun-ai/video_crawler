import type { Meta, StoryObj } from '@storybook/vue3'
import SfTag from './SfTag.vue'

const meta = {
  title: 'UI/SfTag',
  component: SfTag,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: { type: 'select' },
      options: ['default', 'brand', 'success', 'warning', 'danger'],
      description: '颜色语义'
    },
    closable: { control: 'boolean', description: '显示关闭按钮' }
  }
} satisfies Meta<typeof SfTag>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    type: 'default',
    default: '标签'
  },
  render: (args) => ({
    components: { SfTag },
    setup() { return { args } },
    template: '<SfTag v-bind="args">{{ args.default }}</SfTag>'
  })
}

export const Brand: Story = {
  args: {
    type: 'brand',
    default: '推荐'
  },
  render: (args) => ({
    components: { SfTag },
    setup() { return { args } },
    template: '<SfTag v-bind="args">{{ args.default }}</SfTag>'
  })
}

export const Success: Story = {
  args: {
    type: 'success',
    default: '已完成'
  },
  render: (args) => ({
    components: { SfTag },
    setup() { return { args } },
    template: '<SfTag v-bind="args">{{ args.default }}</SfTag>'
  })
}

export const Warning: Story = {
  args: {
    type: 'warning',
    default: '处理中'
  },
  render: (args) => ({
    components: { SfTag },
    setup() { return { args } },
    template: '<SfTag v-bind="args">{{ args.default }}</SfTag>'
  })
}

export const Danger: Story = {
  args: {
    type: 'danger',
    default: '失败'
  },
  render: (args) => ({
    components: { SfTag },
    setup() { return { args } },
    template: '<SfTag v-bind="args">{{ args.default }}</SfTag>'
  })
}

export const Closable: Story = {
  args: {
    type: 'brand',
    closable: true,
    default: '可关闭'
  },
  render: (args) => ({
    components: { SfTag },
    setup() { return { args } },
    template: '<SfTag v-bind="args" @close="() => {}">{{ args.default }}</SfTag>'
  })
}

export const AllTypes: Story = {
  render: () => ({
    components: { SfTag },
    template: `
      <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center">
        <SfTag>默认</SfTag>
        <SfTag type="brand">品牌</SfTag>
        <SfTag type="success">成功</SfTag>
        <SfTag type="warning">警告</SfTag>
        <SfTag type="danger">危险</SfTag>
      </div>
      <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 16px">
        <SfTag closable>可关</SfTag>
        <SfTag type="brand" closable>品牌</SfTag>
        <SfTag type="success" closable>成功</SfTag>
        <SfTag type="warning" closable>警告</SfTag>
        <SfTag type="danger" closable>危险</SfTag>
      </div>
    `
  })
}

export const UseCases: Story = {
  render: () => ({
    components: { SfTag },
    template: `
      <div style="display: flex; flex-direction: column; gap: 16px">
        <div>
          <div style="font-size: 12px; color: var(--color-text-muted); margin-bottom: 6px">视频标签</div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap">
            <SfTag type="brand">热门</SfTag>
            <SfTag type="success">4K</SfTag>
            <SfTag>教程</SfTag>
            <SfTag closable>前端</SfTag>
            <SfTag closable>Vue</SfTag>
          </div>
        </div>
        <div>
          <div style="font-size: 12px; color: var(--color-text-muted); margin-bottom: 6px">任务状态</div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap">
            <SfTag type="success">已完成</SfTag>
            <SfTag type="warning">下载中</SfTag>
            <SfTag type="danger">已失败</SfTag>
            <SfTag>排队中</SfTag>
          </div>
        </div>
      </div>
    `
  })
}
