import type { Meta, StoryObj } from '@storybook/vue3'
import SfEmpty from './SfEmpty.vue'
import SfButton from './SfButton.vue'
import { Search, Inbox, Heart, Film, Compass } from 'lucide-vue-next'

const meta = {
  title: 'UI/SfEmpty',
  component: SfEmpty,
  tags: ['autodocs'],
  argTypes: {
    description: {
      control: { type: 'text' },
      description: '描述文字'
    }
  }
} satisfies Meta<typeof SfEmpty>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    description: '暂无数据'
  },
  render: (args) => ({
    components: { SfEmpty },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--border); border-radius: 8px;">
        <SfEmpty :description="args.description" />
      </div>
    `
  })
}

export const WithIcon: Story = {
  args: {
    description: '没找到匹配的搜索结果'
  },
  render: (args) => ({
    components: { SfEmpty, Search },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--border); border-radius: 8px;">
        <SfEmpty :description="args.description">
          <template #icon>
            <Search :size="64" :stroke-width="1.5" />
          </template>
        </SfEmpty>
      </div>
    `
  })
}

export const WithCTA: Story = {
  args: {
    description: '还没有订阅任何频道'
  },
  render: (args) => ({
    components: { SfEmpty, SfButton, Heart },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--border); border-radius: 8px;">
        <SfEmpty :description="args.description">
          <template #icon>
            <Heart :size="64" :stroke-width="1.5" />
          </template>
          <SfButton type="primary">去看看热门频道</SfButton>
        </SfEmpty>
      </div>
    `
  })
}

export const AllVariants: Story = {
  render: () => ({
    components: { SfEmpty, SfButton, Search, Inbox, Heart, Film, Compass },
    template: `
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; width: 720px;">
        <div style="border: 1px dashed var(--border); border-radius: 8px;">
          <SfEmpty description="暂无数据" />
        </div>
        <div style="border: 1px dashed var(--border); border-radius: 8px;">
          <SfEmpty description="没找到匹配结果">
            <template #icon>
              <Search :size="64" :stroke-width="1.5" />
            </template>
          </SfEmpty>
        </div>
        <div style="border: 1px dashed var(--border); border-radius: 8px;">
          <SfEmpty description="收件箱是空的">
            <template #icon>
              <Inbox :size="64" :stroke-width="1.5" />
            </template>
          </SfEmpty>
        </div>
        <div style="border: 1px dashed var(--border); border-radius: 8px;">
          <SfEmpty description="没有收藏的视频">
            <template #icon>
              <Film :size="64" :stroke-width="1.5" />
            </template>
            <SfButton type="primary">去发现</SfButton>
          </SfEmpty>
        </div>
      </div>
    `
  })
}

export const CustomDescription: Story = {
  args: {
    description: '这个频道还没有发布过视频, 先收藏一下等更新吧'
  },
  render: (args) => ({
    components: { SfEmpty, Compass },
    setup() { return { args } },
    template: `
      <div style="width: 480px; border: 1px dashed var(--border); border-radius: 8px;">
        <SfEmpty :description="args.description">
          <template #icon>
            <Compass :size="64" :stroke-width="1.5" />
          </template>
        </SfEmpty>
      </div>
    `
  })
}
