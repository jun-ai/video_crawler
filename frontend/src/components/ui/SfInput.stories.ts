import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import { Search, Mail, User } from 'lucide-vue-next'
import SfInput from './SfInput.vue'

const meta = {
  title: 'UI/SfInput',
  component: SfInput,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'text' },
    placeholder: { control: 'text' },
    type: {
      control: { type: 'select' },
      options: ['text', 'password', 'email', 'number', 'tel', 'url', 'search'],
      description: '原生 input type'
    },
    disabled: { control: 'boolean' },
    readonly: { control: 'boolean' },
    clearable: { control: 'boolean', description: '显示清空按钮 (有内容时)' },
    maxlength: { control: 'number' },
    textarea: { control: 'boolean', description: '渲染为多行文本域' },
    rows: { control: 'number', description: 'textarea 行数' }
  }
} satisfies Meta<typeof SfInput>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    modelValue: '',
    placeholder: '随便写点什么...',
    type: 'text'
  },
  render: (args) => ({
    components: { SfInput },
    setup() { return { args } },
    template: '<SfInput v-bind="args" style="width: 320px" />'
  })
}

export const WithClearable: Story = {
  args: {
    modelValue: '点右边圆圈可以清空',
    placeholder: '搜索...',
    clearable: true
  },
  render: (args) => ({
    components: { SfInput },
    setup() { return { args } },
    template: '<SfInput v-bind="args" style="width: 320px" />'
  })
}

export const WithPassword: Story = {
  args: {
    modelValue: 'mypassword123',
    placeholder: '输入密码',
    type: 'password'
  },
  render: (args) => ({
    components: { SfInput },
    setup() { return { args } },
    template: '<SfInput v-bind="args" style="width: 320px" />'
  })
}

export const WithPrefix: Story = {
  args: {
    modelValue: '',
    placeholder: '搜索视频...',
    clearable: true
  },
  render: (args) => ({
    components: { SfInput, Search, Mail, User },
    setup() { return { args } },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px; width: 320px">
        <SfInput v-bind="args">
          <template #prefix><Search :size="16" /></template>
        </SfInput>
        <SfInput placeholder="输入邮箱" v-model="args.modelValue">
          <template #prefix><Mail :size="16" /></template>
        </SfInput>
        <SfInput placeholder="用户名" v-model="args.modelValue">
          <template #prefix><User :size="16" /></template>
        </SfInput>
      </div>
    `
  })
}

export const WithError: Story = {
  args: {
    modelValue: '不是合法邮箱',
    placeholder: ''
  },
  render: (args) => ({
    components: { SfInput },
    setup() { return { args } },
    template: `
      <div style="width: 320px">
        <SfInput v-bind="args" />
        <div style="margin-top: 6px; font-size: 12px; color: var(--destructive)">
          ⚠ 邮箱格式不对
        </div>
      </div>
    `
  })
}

export const Disabled: Story = {
  args: {
    modelValue: '锁定状态',
    placeholder: '',
    disabled: true
  },
  render: (args) => ({
    components: { SfInput },
    setup() { return { args } },
    template: '<SfInput v-bind="args" style="width: 320px" />'
  })
}

export const Textarea: Story = {
  args: {
    modelValue: '这是一个多行文本域\n可以拉右下角改变高度',
    placeholder: '写点什么...',
    textarea: true,
    rows: 4,
    maxlength: 200
  },
  render: (args) => ({
    components: { SfInput },
    setup() { return { args } },
    template: '<SfInput v-bind="args" style="width: 320px" />'
  })
}

export const AllSizes: Story = {
  render: () => ({
    components: { SfInput },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px; width: 320px">
        <SfInput placeholder="默认尺寸" />
        <SfInput placeholder="紧凑 (custom style)" style="height: 36px" />
        <SfInput placeholder="加大 (custom style)" style="height: 48px; font-size: 16px" />
        <SfInput placeholder="textarea 模式" textarea :rows="3" />
      </div>
    `
  })
}

export const Interactive: Story = {
  render: () => ({
    components: { SfInput },
    setup() {
      const v = ref('')
      return { v }
    },
    template: `
      <div style="width: 320px">
        <SfInput v-model="v" placeholder="试试输入..." clearable />
        <div style="margin-top: 8px; font-size: 12px; color: var(--color-text-muted)">
          当前值: <code style="color: var(--color-text-secondary)">{{ v || '(空)' }}</code>
        </div>
      </div>
    `
  })
}
