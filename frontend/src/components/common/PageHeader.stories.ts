import type { Meta, StoryObj } from '@storybook/vue3'
import PageHeader from './PageHeader.vue'
import SfButton from '../ui/SfButton.vue'
import { ChevronLeft, ChevronRight, Plus, Settings } from 'lucide-vue-next'

const meta = {
  title: 'Common/PageHeader',
  component: PageHeader,
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: { type: 'text' },
      description: '页面主标题'
    },
    subtitle: {
      control: { type: 'text' },
      description: '副标题 / 描述'
    }
  }
} satisfies Meta<typeof PageHeader>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    title: '语料库',
    subtitle: ''
  }
}

export const WithSubtitle: Story = {
  args: {
    title: '生词本',
    subtitle: '已收录 124 个单词，最近一次学习是昨天'
  }
}

export const WithActions: Story = {
  args: {
    title: '设置',
    subtitle: '个性化你的学习体验'
  },
  render: (args) => ({
    components: { PageHeader, SfButton, Settings },
    setup() { return { args } },
    template: `
      <PageHeader v-bind="args">
        <template #actions>
          <SfButton type="default" size="sm">
            <Settings :size="14" style="margin-right: 4px;" />
            偏好设置
          </SfButton>
          <SfButton type="primary" size="sm">
            <Plus :size="14" style="margin-right: 4px;" />
            新建
          </SfButton>
        </template>
      </PageHeader>
    `
  })
}

export const WithBack: Story = {
  args: {
    title: '频道详情',
    subtitle: 'TED-Ed · 142 个视频'
  },
  render: (args) => ({
    components: { PageHeader, SfButton, ChevronLeft },
    setup() { return { args } },
    template: `
      <PageHeader v-bind="args">
        <template #actions>
          <SfButton type="ghost" size="sm">
            <ChevronLeft :size="16" style="margin-right: 2px;" />
            返回
          </SfButton>
          <SfButton type="primary" size="sm">订阅</SfButton>
        </template>
      </PageHeader>
    `
  })
}

export const WithBreadcrumb: Story = {
  args: {
    title: '日语 N2 高频词汇',
    subtitle: '更新于 2 小时前'
  },
  render: (args) => ({
    components: { PageHeader, SfButton, ChevronRight },
    setup() { return { args, ChevronRight } },
    template: `
      <PageHeader v-bind="args">
        <template #actions>
          <nav style="display: flex; align-items: center; gap: 4px; font-size: 13px; color: var(--color-text-secondary);">
            <a style="color: var(--color-text-secondary); text-decoration: none; cursor: pointer;">语料库</a>
            <ChevronRight :size="12" />
            <a style="color: var(--color-text-secondary); text-decoration: none; cursor: pointer;">日语</a>
            <ChevronRight :size="12" />
            <span style="color: var(--color-text-primary); font-weight: 500;">N2 词汇</span>
          </nav>
        </template>
      </PageHeader>
    `
  })
}

export const WithExtra: Story = {
  args: {
    title: '我的学习',
    subtitle: '今天是个好日子'
  },
  render: (args) => ({
    components: { PageHeader },
    setup() { return { args } },
    template: `
      <PageHeader v-bind="args">
        <template #actions>
          <SfButton type="default" size="sm">切换视图</SfButton>
        </template>
        <template #extra>
          <div style="
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 999px;
            background: var(--sf-cta-gradient, linear-gradient(135deg, #667eea, #764ba2));
            color: #fff;
            font-size: 12px;
            font-weight: 600;
          ">
            🔥 连续学习 7 天
          </div>
        </template>
      </PageHeader>
    `
  })
}

export const AllVariants: Story = {
  render: () => ({
    components: { PageHeader, SfButton, Settings, ChevronLeft, Plus },
    template: `
      <div style="display: flex; flex-direction: column; gap: 24px; width: 720px;">
        <div style="border-bottom: 1px dashed var(--color-border); padding-bottom: 8px;">
          <PageHeader title="默认" subtitle="只有标题" />
        </div>
        <div style="border-bottom: 1px dashed var(--color-border); padding-bottom: 8px;">
          <PageHeader title="带副标题" subtitle="补充说明文字会出现在标题下方" />
        </div>
        <div style="border-bottom: 1px dashed var(--color-border); padding-bottom: 8px;">
          <PageHeader title="带操作按钮" subtitle="右侧槽位放主要动作">
            <template #actions>
              <SfButton type="default" size="sm">取消</SfButton>
              <SfButton type="primary" size="sm">
                <Plus :size="14" style="margin-right: 4px;" />
                新建
              </SfButton>
            </template>
          </PageHeader>
        </div>
        <div style="border-bottom: 1px dashed var(--color-border); padding-bottom: 8px;">
          <PageHeader title="返回上一页" subtitle="用 ghost 按钮承载返回动作">
            <template #actions>
              <SfButton type="ghost" size="sm">
                <ChevronLeft :size="16" style="margin-right: 2px;" />
                返回
              </SfButton>
            </template>
          </PageHeader>
        </div>
        <div>
          <PageHeader title="带面包屑" subtitle="面包屑放在 actions 槽位">
            <template #actions>
              <span style="font-size: 13px; color: var(--color-text-secondary);">首页 / 学习 / 当前页</span>
              <SfButton type="default" size="sm">
                <Settings :size="14" />
              </SfButton>
            </template>
          </PageHeader>
        </div>
      </div>
    `
  })
}
