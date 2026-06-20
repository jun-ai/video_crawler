import type { Meta, StoryObj } from '@storybook/vue3'
import SfFormItem from './SfFormItem.vue'
import SfInput from './SfInput.vue'

const meta = {
  title: 'UI/SfFormItem',
  component: SfFormItem,
  tags: ['autodocs'],
  argTypes: {
    label: {
      control: 'text',
      description: '标签文字'
    },
    required: {
      control: 'boolean',
      description: '是否必填（红色星号）'
    },
    error: {
      control: 'text',
      description: '错误提示文字（红字显示在下方）'
    }
  }
} satisfies Meta<typeof SfFormItem>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: '基础',
  args: {
    label: '用户名',
    required: false,
    error: ''
  },
  render: (args) => ({
    components: { SfFormItem, SfInput },
    setup() { return { args } },
    template: `
      <div style="width: 320px;">
        <SfFormItem v-bind="args">
          <SfInput model-value="" placeholder="随便写点什么..." />
        </SfFormItem>
      </div>
    `
  })
}

export const Required: Story = {
  name: '必填',
  args: {
    label: '邮箱',
    required: true,
    error: ''
  },
  render: (args) => ({
    components: { SfFormItem, SfInput },
    setup() { return { args } },
    template: `
      <div style="width: 320px;">
        <SfFormItem v-bind="args">
          <SfInput model-value="" type="email" placeholder="you@example.com" />
        </SfFormItem>
      </div>
    `
  })
}

export const WithError: Story = {
  name: '错误提示',
  args: {
    label: '密码',
    required: true,
    error: '密码至少 8 位，且必须包含数字'
  },
  render: (args) => ({
    components: { SfFormItem, SfInput },
    setup() { return { args } },
    template: `
      <div style="width: 320px;">
        <SfFormItem v-bind="args">
          <SfInput model-value="abc" type="password" />
        </SfFormItem>
      </div>
    `
  })
}

export const WithHelp: Story = {
  name: '带帮助文字',
  render: () => ({
    components: { SfFormItem, SfInput },
    template: `
      <div style="width: 360px;">
        <SfFormItem label="用户名" required>
          <SfInput model-value="" placeholder="3-20 字符" />
          <p style="margin: 6px 0 0; font-size: 12px; color: var(--color-text-muted); line-height: 1.5;">
            提示：用户名是登录凭证，设置后不能修改
          </p>
        </SfFormItem>
      </div>
    `
  })
}

export const NoLabel: Story = {
  name: '无标签',
  render: () => ({
    components: { SfFormItem, SfInput },
    template: `
      <div style="width: 320px;">
        <SfFormItem>
          <SfInput model-value="" placeholder="只有输入框" />
        </SfFormItem>
      </div>
    `
  })
}

export const MultipleErrors: Story = {
  name: '多种状态',
  render: () => ({
    components: { SfFormItem, SfInput },
    template: `
      <div style="display: flex; flex-direction: column; gap: 20px; width: 360px;">
        <SfFormItem label="昵称">
          <SfInput model-value="夜猫子" />
        </SfFormItem>
        <SfFormItem label="邮箱" required>
          <SfInput model-value="me@fluenty.app" />
        </SfFormItem>
        <SfFormItem label="个人简介">
          <SfInput model-value="" :textarea="true" :rows="3" placeholder="一句话介绍自己..." />
        </SfFormItem>
        <SfFormItem label="手机号" required error="手机号已被注册">
          <SfInput model-value="13800000000" />
        </SfFormItem>
      </div>
    `
  })
}