import type { Meta, StoryObj } from '@storybook/vue3'
import SfSelect from './SfSelect.vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './select'

const meta = {
  title: 'UI/SfSelect',
  component: SfSelect,
  tags: ['autodocs'],
  argTypes: {
    modelValue: {
      control: 'text',
      description: '当前选中值（v-model，String | Number）'
    },
    options: {
      control: 'object',
      description: '选项数组 [{ label, value }]'
    },
    placeholder: {
      control: 'text',
      description: '占位文本'
    },
    disabled: {
      control: 'boolean',
      description: '是否禁用'
    },
    clearable: {
      control: 'boolean',
      description: '是否可清除（SfSelect 当前仅占位 prop，需配合业务层实现）'
    }
  }
} satisfies Meta<typeof SfSelect>

export default meta
type Story = StoryObj<typeof meta>

const fruitOptions = [
  { label: '🍎 苹果', value: 'apple' },
  { label: '🍌 香蕉', value: 'banana' },
  { label: '🍇 葡萄', value: 'grape' },
  { label: '🍊 橘子', value: 'orange' },
  { label: '🥝 猕猴桃', value: 'kiwi' }
]

const langOptions = [
  { label: '英语', value: 'en' },
  { label: '日语', value: 'ja' },
  { label: '韩语', value: 'ko' },
  { label: '法语', value: 'fr' },
  { label: '德语', value: 'de' }
]

export const Default: Story = {
  args: {
    modelValue: '',
    placeholder: '选个水果',
    disabled: false,
    options: fruitOptions
  },
  render: (args) => ({
    components: { SfSelect },
    setup() { return { args } },
    template: '<SfSelect v-bind="args" style="width: 240px;" />'
  })
}

export const WithEmpty: Story = {
  render: () => ({
    components: { SfSelect },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px; width: 240px;">
        <SfSelect :options="[]" placeholder="空选项 - 啥也没有" />
        <SfSelect
          :options="[{ label: '只有一项', value: 'only' }]"
          placeholder="单选项"
        />
      </div>
    `
  })
}

export const Disabled: Story = {
  render: () => ({
    components: { SfSelect },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px; width: 240px;">
        <SfSelect
          :options="langOptions"
          :disabled="true"
          placeholder="禁用状态（未选）"
        />
        <SfSelect
          :options="langOptions"
          :model-value="'en'"
          :disabled="true"
          placeholder="禁用状态（已选）"
        />
      </div>
    `
  })
}

export const Clearable: Story = {
  render: () => ({
    components: { SfSelect },
    data() {
      return { value: 'apple' }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 12px; width: 320px;">
        <SfSelect
          v-model="value"
          :options="fruitOptions"
          placeholder="可清除选择"
          style="flex: 1;"
        />
        <button
          v-if="value"
          @click="value = ''"
          style="
            padding: 6px 12px;
            font-size: 13px;
            border: 1px solid var(--color-border);
            border-radius: 6px;
            background: var(--color-bg-card);
            cursor: pointer;
          "
        >
          清空 ✕
        </button>
      </div>
    `
  })
}

export const Multiple: Story = {
  render: () => ({
    components: { Select, SelectContent, SelectItem, SelectTrigger, SelectValue },
    data() {
      return {
        selected: ['apple'],
        options: fruitOptions
      }
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 8px; width: 280px;">
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0;">
          SfSelect 当前为单选封装，多选用底层 reka-ui Select (multiple)
        </p>
        <Select v-model="selected" multiple>
          <SelectTrigger class="sf-select-trigger">
            <SelectValue placeholder="多选水果" />
          </SelectTrigger>
          <SelectContent class="sf-select-content">
            <SelectItem v-for="opt in options" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </SelectItem>
          </SelectContent>
        </Select>
        <div style="font-size: 12px; color: var(--color-text-secondary);">
          当前选中: {{ selected.join(', ') || '(空)' }}
        </div>
      </div>
    `
  })
}

export const SizesAndWidth: Story = {
  render: () => ({
    components: { SfSelect },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <SfSelect :options="langOptions" placeholder="窄 160px" style="width: 160px;" />
        <SfSelect :options="langOptions" placeholder="中 240px" style="width: 240px;" />
        <SfSelect :options="langOptions" placeholder="宽 100%" style="width: 100%;" />
      </div>
    `
  })
}

export const WithLabel: Story = {
  render: () => ({
    components: { SfSelect },
    template: `
      <div style="width: 280px;">
        <SfSelect :options="langOptions" placeholder="选学哪种语言">
          <template #label>推荐语言</template>
        </SfSelect>
      </div>
    `
  })
}

export const Interactive: Story = {
  render: () => ({
    components: { SfSelect },
    data() {
      return {
        picked: '',
        options: langOptions
      }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 16px;">
        <SfSelect
          v-model="picked"
          :options="options"
          placeholder="点击选择"
          style="width: 200px;"
        />
        <span style="color: var(--color-text-secondary); font-size: 14px;">
          输出: <b>{{ picked || '(空)' }}</b>
        </span>
      </div>
    `
  })
}