import type { Meta, StoryObj } from '@storybook/vue3'
import SfButton from './SfButton.vue'

const meta = {
  title: 'UI/SfButton',
  component: SfButton,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: { type: 'select' },
      options: ['default', 'primary', 'ghost', 'danger', 'subtle'],
      description: '视觉层级'
    },
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg'],
      description: '尺寸'
    },
    loading: { control: 'boolean' },
    disabled: { control: 'boolean' },
    block: { control: 'boolean' },
    round: { control: 'boolean' }
  }
} satisfies Meta<typeof SfButton>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    type: 'default',
    size: 'md',
    default: '默认按钮'
  },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}

export const Primary: Story = {
  args: { type: 'primary', default: '主要按钮' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}

export const Ghost: Story = {
  args: { type: 'ghost', default: '幽灵按钮' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}

export const Danger: Story = {
  args: { type: 'danger', default: '危险操作' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}

export const Subtle: Story = {
  args: { type: 'subtle', default: '次要按钮' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}

export const AllTypes: Story = {
  render: () => ({
    components: { SfButton },
    template: `
      <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
        <SfButton type="primary">主要</SfButton>
        <SfButton type="default">默认</SfButton>
        <SfButton type="ghost">幽灵</SfButton>
        <SfButton type="subtle">次要</SfButton>
        <SfButton type="danger">危险</SfButton>
      </div>
    `
  })
}

export const AllSizes: Story = {
  render: () => ({
    components: { SfButton },
    template: `
      <div style="display: flex; gap: 12px; align-items: center;">
        <SfButton type="primary" size="sm">小</SfButton>
        <SfButton type="primary" size="md">中</SfButton>
        <SfButton type="primary" size="lg">大</SfButton>
      </div>
    `
  })
}

export const Loading: Story = {
  args: { type: 'primary', loading: true, default: '加载中' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}

export const Disabled: Story = {
  args: { type: 'primary', disabled: true, default: '禁用' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}

export const Block: Story = {
  args: { type: 'primary', block: true, default: '块级按钮 (全宽)' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args" style="width: 240px;">{{ args.default }}</SfButton>'
  })
}

export const Round: Story = {
  args: { type: 'primary', round: true, default: '胶囊' },
  render: (args) => ({
    components: { SfButton },
    setup() { return { args } },
    template: '<SfButton v-bind="args">{{ args.default }}</SfButton>'
  })
}
