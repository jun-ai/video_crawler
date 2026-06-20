import type { Meta, StoryObj } from '@storybook/vue3'
import SfSwitch from './SfSwitch.vue'

const meta = {
  title: 'UI/SfSwitch',
  component: SfSwitch,
  tags: ['autodocs'],
  argTypes: {
    modelValue: {
      control: 'boolean',
      description: '是否开启（v-model）'
    },
    disabled: {
      control: 'boolean',
      description: '是否禁用'
    },
    label: {
      control: 'text',
      description: '右侧文本（不传则不显示）'
    }
  }
} satisfies Meta<typeof SfSwitch>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    modelValue: false,
    disabled: false,
    label: ''
  },
  render: (args) => ({
    components: { SfSwitch },
    setup() { return { args } },
    template: '<SfSwitch v-bind="args" />'
  })
}

export const Checked: Story = {
  args: {
    modelValue: true,
    disabled: false,
    label: ''
  },
  render: (args) => ({
    components: { SfSwitch },
    setup() { return { args } },
    template: '<SfSwitch v-bind="args" />'
  })
}

export const WithLabel: Story = {
  render: () => ({
    components: { SfSwitch },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <SfSwitch :model-value="true" label="开启通知" />
        <SfSwitch :model-value="false" label="深色模式" />
        <SfSwitch :model-value="true" label="自动保存" />
        <SfSwitch :model-value="false" label="音效" />
      </div>
    `
  })
}

export const Disabled: Story = {
  render: () => ({
    components: { SfSwitch },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <SfSwitch :model-value="false" :disabled="true" label="禁用 - 关" />
        <SfSwitch :model-value="true" :disabled="true" label="禁用 - 开" />
        <SfSwitch :model-value="false" :disabled="true" />
        <SfSwitch :model-value="true" :disabled="true" />
      </div>
    `
  })
}

export const Sizes: Story = {
  render: () => ({
    components: { SfSwitch },
    template: `
      <div style="display: flex; flex-direction: column; gap: 16px;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <SfSwitch :model-value="true" label="小号 (sm)" class="sf-switch--sm" />
          <SfSwitch :model-value="true" label="中号 (md)" />
          <SfSwitch :model-value="true" label="大号 (lg)" class="sf-switch--lg" />
        </div>
      </div>
      <style>
        .sf-switch--sm { transform: scale(0.8); transform-origin: left center; }
        .sf-switch--lg { transform: scale(1.2); transform-origin: left center; }
      </style>
    `
  })
}

export const Interactive: Story = {
  render: () => ({
    components: { SfSwitch },
    data() {
      return { on: false, count: 0 }
    },
    template: `
      <div style="display: flex; align-items: center; gap: 16px;">
        <SfSwitch v-model="on" label="点我切换" />
        <span style="color: var(--color-text-secondary); font-size: 14px;">
          状态: <b>{{ on ? 'ON' : 'OFF' }}</b>
        </span>
      </div>
    `
  })
}