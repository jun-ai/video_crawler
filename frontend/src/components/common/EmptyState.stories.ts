import type { Meta, StoryObj } from '@storybook/vue3'
import EmptyState from './EmptyState.vue'
import SfButton from '../ui/SfButton.vue'
import { Search, BookOpen, Heart, CheckCircle2, Sparkles, SearchX, Plus, RefreshCw, Compass } from 'lucide-vue-next'

const meta = {
  title: 'Common/EmptyState',
  component: EmptyState,
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: { type: 'text' },
      description: '自定义标题（留空则用预设）'
    },
    description: {
      control: { type: 'text' },
      description: '描述文案'
    },
    type: {
      control: { type: 'select' },
      options: ['default', 'no-materials', 'no-vocabulary', 'no-favorites', 'all-completed', 'welcome', 'no-results'],
      description: '预设场景（控制内置插画）'
    }
  }
} satisfies Meta<typeof EmptyState>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    description: '暂时没有数据，下拉刷新试试'
  },
  render: (args) => ({
    components: { EmptyState },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--color-border); border-radius: 12px;">
        <EmptyState :description="args.description" />
      </div>
    `
  })
}

export const WithIcon: Story = {
  args: {
    type: 'no-results',
    description: '换个关键词或者筛选条件试试'
  },
  render: (args) => ({
    components: { EmptyState },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--color-border); border-radius: 12px;">
        <EmptyState :type="args.type" :description="args.description" />
      </div>
    `
  })
}

export const WithCTA: Story = {
  args: {
    type: 'welcome',
    description: '浏览语料库，选择感兴趣的视频开始学习吧'
  },
  render: (args) => ({
    components: { EmptyState, SfButton, Compass, Search },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--color-border); border-radius: 12px;">
        <EmptyState :type="args.type" :description="args.description">
          <template #actions>
            <SfButton type="default">
              <Search :size="14" style="margin-right: 4px;" />
              浏览全部
            </SfButton>
            <SfButton type="primary">
              <Compass :size="14" style="margin-right: 4px;" />
              探索推荐
            </SfButton>
          </template>
        </EmptyState>
      </div>
    `
  })
}

export const NoVocabulary: Story = {
  args: {
    type: 'no-vocabulary'
  },
  render: (args) => ({
    components: { EmptyState, SfButton, BookOpen },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--color-border); border-radius: 12px;">
        <EmptyState :type="args.type">
          <template #actions>
            <SfButton type="primary">
              <BookOpen :size="14" style="margin-right: 4px;" />
              去学习
            </SfButton>
          </template>
        </EmptyState>
      </div>
    `
  })
}

export const NoFavorites: Story = {
  args: {
    type: 'no-favorites'
  },
  render: (args) => ({
    components: { EmptyState, SfButton, Heart },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--color-border); border-radius: 12px;">
        <EmptyState :type="args.type">
          <template #actions>
            <SfButton type="primary">
              <Heart :size="14" style="margin-right: 4px;" />
              去发现
            </SfButton>
          </template>
        </EmptyState>
      </div>
    `
  })
}

export const AllCompleted: Story = {
  args: {
    type: 'all-completed'
  },
  render: (args) => ({
    components: { EmptyState, SfButton, CheckCircle2, RefreshCw },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--color-border); border-radius: 12px;">
        <EmptyState :type="args.type">
          <template #actions>
            <SfButton type="primary">
              <RefreshCw :size="14" style="margin-right: 4px;" />
              再来一轮
            </SfButton>
          </template>
        </EmptyState>
      </div>
    `
  })
}

export const AllVariants: Story = {
  render: () => ({
    components: { EmptyState, SfButton, Search, BookOpen, Heart, CheckCircle2, Sparkles, SearchX, Plus, RefreshCw, Compass },
    template: `
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; width: 760px;">
        <div style="border: 1px dashed var(--color-border); border-radius: 12px;">
          <EmptyState type="default" description="暂无数据" />
        </div>
        <div style="border: 1px dashed var(--color-border); border-radius: 12px;">
          <EmptyState type="no-results" description="换个关键词试试">
            <template #actions>
              <SfButton type="default" size="sm">
                <RefreshCw :size="13" style="margin-right: 4px;" />
                重试
              </SfButton>
            </template>
          </EmptyState>
        </div>
        <div style="border: 1px dashed var(--color-border); border-radius: 12px;">
          <EmptyState type="no-vocabulary">
            <template #actions>
              <SfButton type="primary" size="sm">
                <BookOpen :size="13" style="margin-right: 4px;" />
                去添加
              </SfButton>
            </template>
          </EmptyState>
        </div>
        <div style="border: 1px dashed var(--color-border); border-radius: 12px;">
          <EmptyState type="no-favorites">
            <template #actions>
              <SfButton type="primary" size="sm">
                <Heart :size="13" style="margin-right: 4px;" />
                去发现
              </SfButton>
            </template>
          </EmptyState>
        </div>
        <div style="border: 1px dashed var(--color-border); border-radius: 12px;">
          <EmptyState type="welcome" description="挑一个你喜欢的频道开始吧">
            <template #actions>
              <SfButton type="primary" size="sm">
                <Compass :size="13" style="margin-right: 4px;" />
                探索
              </SfButton>
            </template>
          </EmptyState>
        </div>
        <div style="border: 1px dashed var(--color-border); border-radius: 12px;">
          <EmptyState type="all-completed">
            <template #actions>
              <SfButton type="primary" size="sm">
                <Plus :size="13" style="margin-right: 4px;" />
                选新内容
              </SfButton>
            </template>
          </EmptyState>
        </div>
      </div>
    `
  })
}
