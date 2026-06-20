import type { Meta, StoryObj } from '@storybook/vue3'
import SfTabs from './SfTabs.vue'
import { ref } from 'vue'

const meta = {
  title: 'UI/SfTabs',
  component: SfTabs,
  tags: ['autodocs'],
  argTypes: {
    modelValue: {
      control: { type: 'text' },
      description: '当前激活 tab 的 key'
    },
    tabs: {
      control: { type: 'object' },
      description: 'tab 列表 [{ key, label }]'
    }
  }
} satisfies Meta<typeof SfTabs>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    modelValue: 'overview',
    tabs: [
      { key: 'overview', label: '概览' },
      { key: 'detail', label: '详情' },
      { key: 'reviews', label: '评价' }
    ]
  },
  render: (args) => ({
    components: { SfTabs },
    setup() {
      const active = ref(args.modelValue)
      return { args, active }
    },
    template: `
      <div style="width: 480px;">
        <SfTabs v-model="active" :tabs="args.tabs">
          <div v-if="active === 'overview'" style="padding: 24px 0; color: var(--foreground);">
            <h3 style="margin: 0 0 8px;">概览内容</h3>
            <p style="margin: 0; color: var(--muted-foreground); font-size: 14px;">这里展示概览相关的统计和信息。</p>
          </div>
          <div v-else-if="active === 'detail'" style="padding: 24px 0; color: var(--foreground);">
            <h3 style="margin: 0 0 8px;">详情内容</h3>
            <p style="margin: 0; color: var(--muted-foreground); font-size: 14px;">这里展示详细参数和规格。</p>
          </div>
          <div v-else-if="active === 'reviews'" style="padding: 24px 0; color: var(--foreground);">
            <h3 style="margin: 0 0 8px;">评价内容</h3>
            <p style="margin: 0; color: var(--muted-foreground); font-size: 14px;">这里展示用户评价列表。</p>
          </div>
        </SfTabs>
      </div>
    `
  })
}

export const ManyTabs: Story = {
  args: {
    modelValue: 'tab1',
    tabs: [
      { key: 'tab1', label: '首页' },
      { key: 'tab2', label: '热门' },
      { key: 'tab3', label: '订阅' },
      { key: 'tab4', label: '收藏' },
      { key: 'tab5', label: '历史' }
    ]
  },
  render: (args) => ({
    components: { SfTabs },
    setup() {
      const active = ref(args.modelValue)
      return { args, active }
    },
    template: `
      <div style="width: 480px;">
        <SfTabs v-model="active" :tabs="args.tabs">
          <div style="padding: 24px 0; color: var(--muted-foreground); font-size: 14px;">
            当前: {{ active }}
          </div>
        </SfTabs>
      </div>
    `
  })
}

export const WithBadge: Story = {
  args: {
    modelValue: 'all',
    tabs: [
      { key: 'all', label: '全部' },
      { key: 'unread', label: '未读 (3)' },
      { key: 'mentions', label: '@我的' },
      { key: 'archived', label: '已归档' }
    ]
  },
  render: (args) => ({
    components: { SfTabs },
    setup() {
      const active = ref(args.modelValue)
      return { args, active }
    },
    template: `
      <div style="width: 480px;">
        <SfTabs v-model="active" :tabs="args.tabs">
          <div v-if="active === 'all'" style="padding: 24px 0;">全部消息列表</div>
          <div v-else-if="active === 'unread'" style="padding: 24px 0;">3 条未读</div>
          <div v-else-if="active === 'mentions'" style="padding: 24px 0;">@ 我的消息</div>
          <div v-else style="padding: 24px 0;">归档列表</div>
        </SfTabs>
      </div>
    `
  })
}

export const TwoTabs: Story = {
  args: {
    modelValue: 'login',
    tabs: [
      { key: 'login', label: '登录' },
      { key: 'register', label: '注册' }
    ]
  },
  render: (args) => ({
    components: { SfTabs },
    setup() {
      const active = ref(args.modelValue)
      return { args, active }
    },
    template: `
      <div style="width: 320px;">
        <SfTabs v-model="active" :tabs="args.tabs">
          <div v-if="active === 'login'" style="padding: 24px 0; color: var(--foreground);">
            <p style="margin: 0; font-size: 14px;">使用账号密码登录</p>
          </div>
          <div v-else style="padding: 24px 0; color: var(--foreground);">
            <p style="margin: 0; font-size: 14px;">创建新账号</p>
          </div>
        </SfTabs>
      </div>
    `
  })
}
