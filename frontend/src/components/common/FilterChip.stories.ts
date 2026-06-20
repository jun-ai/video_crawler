import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import FilterChip from './FilterChip.vue'
import { Globe, Clock, Star, Film, Tv, Headphones, BookOpen, Flame } from 'lucide-vue-next'

const meta = {
  title: 'Common/FilterChip',
  component: FilterChip,
  tags: ['autodocs'],
  argTypes: {
    modelValue: {
      control: { type: 'text' },
      description: '当前选中值（v-model）'
    },
    value: {
      control: { type: 'text' },
      description: '本 chip 的值（必填）'
    },
    label: {
      control: { type: 'text' },
      description: 'chip 显示文字（也可用默认 slot 替代）'
    },
    count: {
      control: { type: 'number' },
      description: '尾部数字徽标'
    }
  }
} satisfies Meta<typeof FilterChip>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    value: 'all',
    label: '全部'
  },
  render: (args) => ({
    components: { FilterChip },
    setup() {
      const selected = ref<string | null>('all')
      return { args, selected }
    },
    template: `
      <FilterChip
        v-model="selected"
        :value="args.value"
        :label="args.label"
      />
    `
  })
}

export const Active: Story = {
  args: {
    value: 'japanese',
    label: '日语'
  },
  render: (args) => ({
    components: { FilterChip },
    setup() {
      const selected = ref<string | null>('japanese')
      return { args, selected }
    },
    template: `
      <FilterChip
        v-model="selected"
        :value="args.value"
        :label="args.label"
      />
    `
  })
}

export const WithIcon: Story = {
  args: {
    value: 'recent',
    label: '最近更新'
  },
  render: (args) => ({
    components: { FilterChip, Clock },
    setup() {
      const selected = ref<string | null>(null)
      return { args, selected, Clock }
    },
    template: `
      <FilterChip
        v-model="selected"
        :value="args.value"
        :label="args.label"
        :icon="Clock"
      />
    `
  })
}

export const WithCount: Story = {
  args: {
    value: 'favorites',
    label: '我的收藏',
    count: 23
  },
  render: (args) => ({
    components: { FilterChip },
    setup() {
      const selected = ref<string | null>('favorites')
      return { args, selected }
    },
    template: `
      <FilterChip
        v-model="selected"
        :value="args.value"
        :label="args.label"
        :count="args.count"
      />
    `
  })
}

export const FullFeatured: Story = {
  args: {
    value: 'trending',
    label: '热门',
    count: 128
  },
  render: (args) => ({
    components: { FilterChip, Flame },
    setup() {
      const selected = ref<string | null>('trending')
      return { args, selected, Flame }
    },
    template: `
      <FilterChip
        v-model="selected"
        :value="args.value"
        :label="args.label"
        :icon="Flame"
        :count="args.count"
      />
    `
  })
}

export const AllStates: Story = {
  render: () => ({
    components: { FilterChip, Globe, Clock, Star, Film, Tv, Headphones, BookOpen },
    setup() {
      const lang = ref<string | null>('jp')
      const sort = ref<string | null>('recent')
      const category = ref<string | null>('film')
      return { lang, sort, category, Globe, Clock, Star, Film, Tv, Headphones, BookOpen }
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 20px; width: 560px;">
        <div>
          <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 8px;">单选 chip · 默认状态</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <FilterChip v-model="lang" value="all">全部</FilterChip>
            <FilterChip v-model="lang" value="jp" :icon="Globe">日语</FilterChip>
            <FilterChip v-model="lang" value="en" :icon="Globe">英语</FilterChip>
            <FilterChip v-model="lang" value="es" :icon="Globe">西班牙语</FilterChip>
          </div>
        </div>

        <div>
          <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 8px;">带计数 · 含激活态</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <FilterChip v-model="category" value="film" :icon="Film" :count="42">电影</FilterChip>
            <FilterChip v-model="category" value="tv" :icon="Tv" :count="18">剧集</FilterChip>
            <FilterChip v-model="category" value="podcast" :icon="Headphones" :count="7">播客</FilterChip>
            <FilterChip v-model="category" value="book" :icon="BookOpen" :count="23">书籍</FilterChip>
          </div>
        </div>

        <div>
          <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 8px;">排序 chip · 时钟图标</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <FilterChip v-model="sort" value="recent" :icon="Clock">最新</FilterChip>
            <FilterChip v-model="sort" value="hot" :icon="Star">最热</FilterChip>
            <FilterChip v-model="sort" value="recommended">推荐</FilterChip>
          </div>
        </div>
      </div>
    `
  })
}
