import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import SfPagination from './SfPagination.vue'

const meta = {
  title: 'UI/SfPagination',
  component: SfPagination,
  tags: ['autodocs'],
  argTypes: {
    currentPage: { control: { type: 'number', min: 1 }, description: '当前页 (v-model)' },
    pageSize: { control: { type: 'number', min: 1 }, description: '每页条数' },
    total: { control: { type: 'number', min: 0 }, description: '总条数' }
  }
} satisfies Meta<typeof SfPagination>

export default meta
type Story = StoryObj<typeof meta>

// 3 页 (27 条 / 10) — 简单分页
export const Default: Story = {
  args: {
    currentPage: 1,
    pageSize: 10,
    total: 27
  },
  render: (args) => ({
    components: { SfPagination },
    setup() {
      const page = ref(args.currentPage)
      return { args, page }
    },
    template: `
      <div style="padding: 24px; width: 480px;">
        <SfPagination
          :current-page="page"
          :page-size="args.pageSize"
          :total="args.total"
          @update:current-page="page = $event"
        />
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          当前页: {{ page }}
        </p>
      </div>
    `
  })
}

// 12 页 — 触发省略号
export const ManyPages: Story = {
  args: {
    currentPage: 6,
    pageSize: 10,
    total: 120
  },
  render: (args) => ({
    components: { SfPagination },
    setup() {
      const page = ref(args.currentPage)
      return { args, page }
    },
    template: `
      <div style="padding: 24px; width: 560px;">
        <SfPagination
          :current-page="page"
          :page-size="args.pageSize"
          :total="args.total"
          @update:current-page="page = $event"
        />
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          共 {{ args.total }} 条, 每页 {{ args.pageSize }} 条, 当前第 {{ page }} 页
        </p>
      </div>
    `
  })
}

// 不同 pageSize 对比
export const WithPageSize: Story = {
  args: {
    currentPage: 1,
    pageSize: 5,
    total: 50
  },
  render: (args) => ({
    components: { SfPagination },
    setup() {
      const page = ref(args.currentPage)
      const sizes = [5, 10, 20, 50]
      return { args, page, sizes }
    },
    template: `
      <div style="padding: 24px; width: 560px;">
        <div style="display: flex; gap: 8px; margin-bottom: 20px; align-items: center;">
          <span style="font-size: 13px; color: var(--color-text-secondary);">每页</span>
          <button
            v-for="s in sizes"
            :key="s"
            style="padding: 4px 10px; border-radius: 6px; border: 1px solid var(--color-border); background: var(--color-bg-card); color: var(--color-text-primary); cursor: pointer; font-size: 13px;"
            :style="{ background: args.pageSize === s ? 'var(--color-brand)' : 'var(--color-bg-card)', color: args.pageSize === s ? '#fff' : 'var(--color-text-primary)', borderColor: args.pageSize === s ? 'var(--color-brand)' : 'var(--color-border)' }"
            @click="args.pageSize = s"
          >
            {{ s }}
          </button>
        </div>
        <SfPagination
          :current-page="page"
          :page-size="args.pageSize"
          :total="args.total"
          @update:current-page="page = $event"
        />
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          pageSize={{ args.pageSize }} → 总 {{ Math.ceil(args.total / args.pageSize) }} 页
        </p>
      </div>
    `
  })
}

// 第一页 / 最后一页 边界态
export const BoundaryStates: Story = {
  render: () => ({
    components: { SfPagination },
    data() {
      return { page1: 1, page2: 10 }
    },
    template: `
      <div style="padding: 24px; display: flex; flex-direction: column; gap: 28px;">
        <div>
          <p style="font-size: 13px; color: var(--color-text-muted); margin-bottom: 8px;">第一页 (上一页禁用)</p>
          <SfPagination :current-page="page1" :page-size="10" :total="100" @update:current-page="page1 = $event" />
        </div>
        <div>
          <p style="font-size: 13px; color: var(--color-text-muted); margin-bottom: 8px;">最后一页 (下一页禁用)</p>
          <SfPagination :current-page="page2" :page-size="10" :total="100" @update:current-page="page2 = $event" />
        </div>
      </div>
    `
  })
}

// 单页 — 不显示分页栏
export const SinglePage: Story = {
  args: {
    currentPage: 1,
    pageSize: 10,
    total: 5
  },
  render: (args) => ({
    components: { SfPagination },
    setup() {
      const page = ref(args.currentPage)
      return { args, page }
    },
    template: `
      <div style="padding: 24px; width: 480px;">
        <SfPagination
          :current-page="page"
          :page-size="args.pageSize"
          :total="args.total"
          @update:current-page="page = $event"
        />
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          总数 ≤ pageSize 时只显示 1 页
        </p>
      </div>
    `
  })
}