import type { Meta, StoryObj } from '@storybook/vue3'
import ListSkeleton from './ListSkeleton.vue'

const meta = {
  title: 'Common/ListSkeleton',
  component: ListSkeleton,
  tags: ['autodocs'],
  argTypes: {
    count: {
      control: { type: 'number', min: 1, max: 24, step: 1 },
      description: '骨架屏行数'
    },
    listMode: {
      control: 'boolean',
      description: '列表模式（紧凑横向布局）'
    }
  }
} satisfies Meta<typeof ListSkeleton>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    count: 3,
    listMode: false
  },
  render: (args) => ({
    components: { ListSkeleton },
    setup() { return { args } },
    template: '<ListSkeleton v-bind="args" />'
  })
}

export const WithAvatar: Story = {
  args: {
    count: 4,
    listMode: true
  },
  render: (args) => ({
    components: { ListSkeleton },
    setup() { return { args } },
    template: '<ListSkeleton v-bind="args" />'
  })
}

export const WithActions: Story = {
  args: {
    count: 5,
    listMode: false
  },
  render: (args) => ({
    components: { ListSkeleton },
    setup() { return { args } },
    template: '<ListSkeleton v-bind="args" />'
  })
}

export const ManyRows: Story = {
  args: {
    count: 10,
    listMode: false
  },
  render: (args) => ({
    components: { ListSkeleton },
    setup() { return { args } },
    template: '<ListSkeleton v-bind="args" />'
  })
}

export const SingleRow: Story = {
  args: {
    count: 1,
    listMode: false
  },
  render: (args) => ({
    components: { ListSkeleton },
    setup() { return { args } },
    template: '<ListSkeleton v-bind="args" />'
  })
}

export const AllVariants: Story = {
  render: () => ({
    components: { ListSkeleton },
    template: `
      <div style="display: flex; flex-direction: column; gap: 32px; width: 720px;">
        <section>
          <h3 style="margin: 0 0 12px; font-size: 13px; font-weight: 600; color: var(--color-text-secondary);">网格模式 · 3 行</h3>
          <ListSkeleton :count="3" />
        </section>
        <section>
          <h3 style="margin: 0 0 12px; font-size: 13px; font-weight: 600; color: var(--color-text-secondary);">列表模式 · 4 行</h3>
          <ListSkeleton :count="4" :list-mode="true" />
        </section>
        <section>
          <h3 style="margin: 0 0 12px; font-size: 13px; font-weight: 600; color: var(--color-text-secondary);">大量骨架 · 10 行</h3>
          <ListSkeleton :count="10" />
        </section>
      </div>
    `
  })
}
