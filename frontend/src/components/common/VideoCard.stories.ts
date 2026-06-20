import type { Meta, StoryObj } from '@storybook/vue3'
import VideoCard from './VideoCard.vue'

const meta = {
  title: 'Common/VideoCard',
  component: VideoCard,
  tags: ['autodocs'],
  argTypes: {
    id: { control: { type: 'text' } },
    title: { control: { type: 'text' } },
    description: { control: { type: 'text' } },
    cover: { control: { type: 'text' } },
    duration: { control: { type: 'number' } },
    progress: { control: { type: 'range', min: 0, max: 100, step: 1 } },
    difficulty: {
      control: { type: 'select' },
      options: [0, 1, 2, 3, 4, 5]
    },
    viewCount: { control: { type: 'number' } },
    layout: {
      control: { type: 'select' },
      options: ['grid', 'list']
    },
    showMeta: { control: 'boolean' },
    showPlayIcon: { control: 'boolean' },
    completed: { control: 'boolean' },
    favorited: { control: 'boolean' }
  }
} satisfies Meta<typeof VideoCard>

export default meta
type Story = StoryObj<typeof meta>

const SAMPLE_COVER = 'https://picsum.photos/seed/fluenty/640/360'
const SAMPLE_COVER_2 = 'https://picsum.photos/seed/learn/640/360'
const SAMPLE_COVER_3 = 'https://picsum.photos/seed/podcast/640/360'

const SAMPLE_TAGS = [
  { id: 1, name: '口语', color: '#2563EB' },
  { id: 2, name: '商务', color: '#F59E0B' },
  { id: 3, name: '日常', color: '#16A34A' }
]

export const Default: Story = {
  args: {
    id: 1,
    title: 'TED 演讲:如何用 30 秒讲清楚一个复杂观点',
    description: '前 BBC 主播的演讲技巧,3 个万能公式',
    cover: SAMPLE_COVER,
    duration: 596,
    progress: 35,
    difficulty: 3,
    viewCount: 12_800
  },
  render: (args) => ({
    components: { VideoCard },
    setup() { return { args } },
    template: '<VideoCard v-bind="args" style="width: 320px;" />'
  })
}

export const WithDuration: Story = {
  args: {
    id: 2,
    title: 'BBC 六分钟英语:远程办公的未来',
    description: '词伙 · hybrid working / burnout',
    cover: SAMPLE_COVER_2,
    duration: 372,
    difficulty: 2,
    viewCount: 8_460,
    tags: SAMPLE_TAGS
  },
  render: (args) => ({
    components: { VideoCard },
    setup() { return { args } },
    template: '<VideoCard v-bind="args" style="width: 320px;" />'
  })
}

export const WithProgress: Story = {
  args: {
    id: 3,
    title: '老友记 S01E01:重看还是笑出声',
    description: '高频场景句 · 90% 的人都用错过',
    cover: SAMPLE_COVER_3,
    duration: 1320,
    progress: 68,
    difficulty: 1,
    viewCount: 24_300,
    progressText: '已学 14 分钟 · 还剩 8 分钟'
  },
  render: (args) => ({
    components: { VideoCard },
    setup() { return { args } },
    template: '<VideoCard v-bind="args" style="width: 320px;" />'
  })
}

export const Completed: Story = {
  args: {
    id: 4,
    title: 'VOA 常速:全球芯片产业大转向',
    description: '行业词伙 · foundry / node',
    cover: SAMPLE_COVER,
    duration: 268,
    progress: 100,
    difficulty: 4,
    viewCount: 4_120,
    completed: true,
    favorited: true
  },
  render: (args) => ({
    components: { VideoCard },
    setup() { return { args } },
    template: '<VideoCard v-bind="args" style="width: 320px;" />'
  })
}

export const ListMode: Story = {
  args: {
    id: 5,
    title: '雅思口语 9 分示范:城市话题',
    cover: SAMPLE_COVER_2,
    duration: 482,
    progress: 12,
    difficulty: 5,
    viewCount: 1_240,
    layout: 'list'
  },
  render: (args) => ({
    components: { VideoCard },
    setup() { return { args } },
    template: '<VideoCard v-bind="args" />'
  })
}

export const AllVariants: Story = {
  render: () => ({
    components: { VideoCard },
    template: `
      <div style="display: grid; grid-template-columns: repeat(3, 320px); gap: 24px; padding: 16px; background: var(--color-bg-base);">
        <VideoCard
          :id="1"
          title="默认状态 · 学习中"
          cover="${SAMPLE_COVER}"
          :duration="596"
          :progress="35"
          :difficulty="3"
          :view-count="12800"
        />
        <VideoCard
          :id="2"
          title="已完成 + 收藏"
          cover="${SAMPLE_COVER_2}"
          :duration="372"
          :progress="100"
          :difficulty="2"
          :completed="true"
          :favorited="true"
          :view-count="8460"
        />
        <VideoCard
          :id="3"
          title="高级难度 · 高亮"
          cover="${SAMPLE_COVER_3}"
          :duration="1320"
          :progress="0"
          :difficulty="5"
          :tags="[
            { id: 1, name: '口语', color: '#2563EB' },
            { id: 2, name: '高级', color: '#DC2626' }
          ]"
          :view-count="24300"
        />
      </div>
    `
  })
}

export const AllDifficulties: Story = {
  render: () => ({
    components: { VideoCard },
    template: `
      <div style="display: grid; grid-template-columns: repeat(5, 200px); gap: 16px; padding: 16px; background: var(--color-bg-base);">
        <VideoCard :id="11" title="入门 L1" cover="${SAMPLE_COVER}" :duration="300" :difficulty="1" :view-count="100" />
        <VideoCard :id="12" title="基础 L2" cover="${SAMPLE_COVER_2}" :duration="420" :difficulty="2" :view-count="200" />
        <VideoCard :id="13" title="中级 L3" cover="${SAMPLE_COVER_3}" :duration="540" :difficulty="3" :view-count="300" />
        <VideoCard :id="14" title="进阶 L4" cover="${SAMPLE_COVER}" :duration="660" :difficulty="4" :view-count="400" />
        <VideoCard :id="15" title="高级 L5" cover="${SAMPLE_COVER_2}" :duration="780" :difficulty="5" :view-count="500" />
      </div>
    `
  })
}

export const ListLayoutGrid: Story = {
  render: () => ({
    components: { VideoCard },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px; padding: 16px; background: var(--color-bg-base); max-width: 640px;">
        <VideoCard :id="21" title="雅思口语 9 分示范:城市话题" cover="${SAMPLE_COVER}" :duration="482" :progress="12" :difficulty="5" layout="list" :view-count="1240" />
        <VideoCard :id="22" title="BBC:疫情后的混合办公模式" cover="${SAMPLE_COVER_2}" :duration="372" :progress="48" :difficulty="2" layout="list" :view-count="3460" />
        <VideoCard :id="23" title="老友记精选:感恩节特辑" cover="${SAMPLE_COVER_3}" :duration="1320" :progress="100" :difficulty="1" :completed="true" layout="list" :view-count="9820" />
      </div>
    `
  })
}