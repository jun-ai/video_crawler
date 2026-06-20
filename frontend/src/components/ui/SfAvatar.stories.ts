import type { Meta, StoryObj } from '@storybook/vue3'
import SfAvatar from './SfAvatar.vue'

const meta = {
  title: 'UI/SfAvatar',
  component: SfAvatar,
  tags: ['autodocs'],
  argTypes: {
    src: { control: 'text', description: '图片地址 (为空则显示首字母)' },
    name: { control: 'text', description: '用户姓名, 取首字母作为 fallback' },
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg'],
      description: '尺寸: sm (32px) / md (40px) / lg (64px)'
    },
    alt: { control: 'text', description: '图片 alt' },
    bgColor: { control: 'color', description: '自定义背景色 (覆盖默认品牌色)' }
  }
} satisfies Meta<typeof SfAvatar>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    name: '小张',
    size: 'md'
  },
  render: (args) => ({
    components: { SfAvatar },
    setup() { return { args } },
    template: '<SfAvatar v-bind="args" />'
  })
}

export const Sizes: Story = {
  render: () => ({
    components: { SfAvatar },
    template: `
      <div style="display: flex; gap: 16px; align-items: center;">
        <div style="display: flex; flex-direction: column; align-items: center; gap: 6px;">
          <SfAvatar name="A" size="sm" />
          <span style="font-size: 11px; color: var(--color-text-tertiary, #9ca3af)">sm · 32px</span>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 6px;">
          <SfAvatar name="B" size="md" />
          <span style="font-size: 11px; color: var(--color-text-tertiary, #9ca3af)">md · 40px</span>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 6px;">
          <SfAvatar name="C" size="lg" />
          <span style="font-size: 11px; color: var(--color-text-tertiary, #9ca3af)">lg · 64px</span>
        </div>
      </div>
    `
  })
}

export const WithImage: Story = {
  args: {
    src: 'https://picsum.photos/seed/fluenty-avatar/120/120',
    name: '张三',
    size: 'lg',
    alt: '用户头像'
  },
  render: (args) => ({
    components: { SfAvatar },
    setup() { return { args } },
    template: '<SfAvatar v-bind="args" />'
  })
}

export const WithInitials: Story = {
  render: () => ({
    components: { SfAvatar },
    template: `
      <div style="display: flex; gap: 12px; align-items: center;">
        <SfAvatar name="张三" size="md" />
        <SfAvatar name="李四" size="md" />
        <SfAvatar name="Wang" size="md" />
        <SfAvatar name="alex" size="md" />
        <SfAvatar name="林夕" size="md" />
        <SfAvatar name="" size="md" />
      </div>
    `
  })
}

export const WithCustomBg: Story = {
  render: () => ({
    components: { SfAvatar },
    template: `
      <div style="display: flex; gap: 12px; align-items: center;">
        <SfAvatar name="紫" size="md" bg-color="#ede9fe" />
        <SfAvatar name="绿" size="md" bg-color="#dcfce7" />
        <SfAvatar name="红" size="md" bg-color="#fee2e2" />
        <SfAvatar name="黄" size="md" bg-color="#fef9c3" />
        <SfAvatar name="蓝" size="md" bg-color="#dbeafe" />
      </div>
    `
  })
}

export const AllSizes: Story = {
  render: () => ({
    components: { SfAvatar },
    template: `
      <div style="display: grid; grid-template-columns: repeat(3, max-content); gap: 24px 32px; align-items: center;">
        <SfAvatar src="https://picsum.photos/seed/av-sm/64/64" size="sm" alt="小" />
        <SfAvatar name="小" size="sm" />
        <SfAvatar name="小" size="sm" bg-color="#dcfce7" />

        <SfAvatar src="https://picsum.photos/seed/av-md/80/80" size="md" alt="中" />
        <SfAvatar name="中" size="md" />
        <SfAvatar name="中" size="md" bg-color="#fef9c3" />

        <SfAvatar src="https://picsum.photos/seed/av-lg/128/128" size="lg" alt="大" />
        <SfAvatar name="大" size="lg" />
        <SfAvatar name="大" size="lg" bg-color="#dbeafe" />
      </div>
    `
  })
}
