import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import SfCombobox from './SfCombobox.vue'

const meta = {
  title: 'UI/SfCombobox',
  component: SfCombobox,
  tags: ['autodocs'],
  argTypes: {
    modelValue: {
      control: { type: 'select' },
      options: ['react', 'vue', 'svelte', 'solid'],
      description: '当前选中值 (v-model)'
    },
    options: {
      control: 'object',
      description: '选项数组 [{ value, label, sublabel? }]'
    },
    placeholder: { control: 'text', description: '占位文本' },
    searchable: { control: 'boolean', description: '是否可输入搜索' },
    displayValue: { control: 'text', description: '强制显示的文字 (覆盖自动匹配)' }
  }
} satisfies Meta<typeof SfCombobox>

export default meta
type Story = StoryObj<typeof meta>

const frameworkOptions = [
  { value: 'react', label: 'React', sublabel: 'Meta 出品, 生态最大' },
  { value: 'vue', label: 'Vue', sublabel: '渐进式, 上手快' },
  { value: 'svelte', label: 'Svelte', sublabel: '编译时框架, 体积小' },
  { value: 'solid', label: 'Solid', sublabel: '细粒度响应式' },
  { value: 'qwik', label: 'Qwik', sublabel: '可恢复性, 瞬时加载' }
]

export const Default: Story = {
  args: {
    modelValue: null,
    placeholder: '选个框架',
    searchable: true,
    options: frameworkOptions
  },
  render: (args) => ({
    components: { SfCombobox },
    setup() { return { args } },
    template: '<div style="width: 280px;"><SfCombobox v-bind="args" /></div>'
  })
}

export const WithSelectedValue: Story = {
  args: {
    modelValue: 'vue',
    placeholder: '选个框架',
    searchable: true,
    options: frameworkOptions
  },
  render: (args) => ({
    components: { SfCombobox },
    setup() { return { args } },
    template: '<div style="width: 280px;"><SfCombobox v-bind="args" /></div>'
  })
}

export const Searchable: Story = {
  render: () => ({
    components: { SfCombobox },
    setup() {
      const value = ref(null)
      return { value, options: frameworkOptions }
    },
    template: `
      <div style="width: 280px;">
        <SfCombobox
          v-model="value"
          :options="options"
          placeholder="试试输入 're' / 'v' / 's'"
          searchable
        />
        <div style="margin-top: 12px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af);">
          当前值: <code>{{ value }}</code>
        </div>
      </div>
    `
  })
}

export const NotSearchable: Story = {
  render: () => ({
    components: { SfCombobox },
    setup() {
      const value = ref('vue')
      return { value, options: frameworkOptions }
    },
    template: `
      <div style="width: 280px;">
        <SfCombobox
          v-model="value"
          :options="options"
          placeholder="不可搜索, 只能点开选"
          :searchable="false"
        />
        <div style="margin-top: 12px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af);">
          只读模式下, 输入框会被 readonly 锁住
        </div>
      </div>
    `
  })
}

export const WithClear: Story = {
  render: () => ({
    components: { SfCombobox },
    setup() {
      const value = ref('react')
      return { value, options: frameworkOptions }
    },
    template: `
      <div style="width: 280px;">
        <SfCombobox
          v-model="value"
          :options="options"
          placeholder="可清除"
        />
        <div style="margin-top: 12px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af);">
          鼠标悬停到输入框上, 选中项右侧会出现 X 清除按钮
        </div>
      </div>
    `
  })
}

export const WithManyOptions: Story = {
  render: () => ({
    components: { SfCombobox },
    setup() {
      const value = ref(null)
      const options = Array.from({ length: 30 }, (_, i) => ({
        value: `city-${i}`,
        label: `城市 ${i + 1}`,
        sublabel: `第 ${i + 1} 个候选`
      }))
      return { value, options }
    },
    template: `
      <div style="width: 320px;">
        <SfCombobox
          v-model="value"
          :options="options"
          placeholder="30 个城市可选, 试试输入数字"
        />
        <div style="margin-top: 12px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af);">
          选中的城市: <code>{{ value ?? '(无)' }}</code>
        </div>
      </div>
    `
  })
}

export const WithSublabels: Story = {
  render: () => ({
    components: { SfCombobox },
    setup() {
      const value = ref('chrome')
      const browsers = [
        { value: 'chrome', label: 'Chrome', sublabel: '份额 65% · Blink' },
        { value: 'safari', label: 'Safari', sublabel: '份额 19% · WebKit' },
        { value: 'edge', label: 'Edge', sublabel: '份额 5% · Blink' },
        { value: 'firefox', label: 'Firefox', sublabel: '份额 3% · Gecko' },
        { value: 'opera', label: 'Opera', sublabel: '份额 < 1% · Blink' }
      ]
      return { value, browsers }
    },
    template: `
      <div style="width: 320px;">
        <SfCombobox
          v-model="value"
          :options="browsers"
          placeholder="选个浏览器"
        />
        <div style="margin-top: 12px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af);">
          sublabel 副标题会在下拉项里以浅色小字显示
        </div>
      </div>
    `
  })
}
