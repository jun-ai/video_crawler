import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import SfDialog from './SfDialog.vue'
import SfButton from './SfButton.vue'

const meta = {
  title: 'UI/SfDialog',
  component: SfDialog,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'boolean', description: 'v-model 控制显隐' },
    title: { control: 'text' },
    width: { control: 'text', description: '对话框宽度' },
    maxWidth: { control: 'text', description: '对话框最大宽度' },
    showClose: { control: 'boolean', description: '右上角关闭按钮' },
    closeOnClickOverlay: { control: 'boolean', description: '点击遮罩是否关闭' },
    closeOnEsc: { control: 'boolean', description: '按 ESC 是否关闭' }
  }
} satisfies Meta<typeof SfDialog>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    modelValue: false,
    title: '默认弹窗',
    width: '480px'
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton type="primary" @click="args.modelValue = true">打开弹窗</SfButton>
        <SfDialog v-bind="args">
          <p>这是一个最基础的弹窗。点外面、ESC、右上角 X 都能关掉。</p>
        </SfDialog>
      </div>
    `
  })
}

export const WithTitle: Story = {
  args: {
    modelValue: false,
    title: '🎬 视频详情',
    width: '520px'
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton type="primary" @click="args.modelValue = true">查看视频</SfButton>
        <SfDialog v-bind="args">
          <p style="line-height: 1.6; color: var(--color-text-secondary)">
            标题通过 prop 传入。也可以用 <code>#header</code> slot 自定义头部内容。
          </p>
          <p style="margin-top: 12px; color: var(--color-text-secondary)">
            视频 ID: 12345
          </p>
        </SfDialog>
      </div>
    `
  })
}

export const WithFooter: Story = {
  args: {
    modelValue: false,
    title: '确认操作',
    width: '420px'
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton type="danger" @click="args.modelValue = true">删除视频</SfButton>
        <SfDialog v-bind="args">
          <p style="color: var(--color-text-secondary)">
            这条视频会被永久删除,无法找回。确定继续吗?
          </p>
          <template #footer>
            <div style="display: flex; gap: 8px; justify-content: flex-end">
              <SfButton type="default" @click="args.modelValue = false">取消</SfButton>
              <SfButton type="danger" @click="args.modelValue = false">确定删除</SfButton>
            </div>
          </template>
        </SfDialog>
      </div>
    `
  })
}

export const SmallWidth: Story = {
  args: {
    modelValue: false,
    title: '小弹窗',
    width: '320px'
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton @click="args.modelValue = true">打开 (320px)</SfButton>
        <SfDialog v-bind="args">
          <p>紧凑的小弹窗,适合提示类场景。</p>
        </SfDialog>
      </div>
    `
  })
}

export const MediumWidth: Story = {
  args: {
    modelValue: false,
    title: '中等弹窗',
    width: '640px'
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton @click="args.modelValue = true">打开 (640px)</SfButton>
        <SfDialog v-bind="args">
          <p>适合表单、列表、设置项。</p>
        </SfDialog>
      </div>
    `
  })
}

export const LargeWidth: Story = {
  args: {
    modelValue: false,
    title: '大弹窗',
    width: '880px'
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton @click="args.modelValue = true">打开 (880px)</SfButton>
        <SfDialog v-bind="args">
          <p>适合详情页、对比视图、多栏布局。</p>
        </SfDialog>
      </div>
    `
  })
}

export const NoCloseOnOverlay: Story = {
  args: {
    modelValue: false,
    title: '强制操作',
    width: '420px',
    closeOnClickOverlay: false,
    showClose: true
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton type="primary" @click="args.modelValue = true">打开</SfButton>
        <SfDialog v-bind="args">
          <p style="color: var(--color-text-secondary)">
            点击遮罩不会关闭,必须通过底部按钮或右上角 X 操作。
            适合重要操作、不可中断的流程。
          </p>
          <template #footer>
            <div style="display: flex; gap: 8px; justify-content: flex-end">
              <SfButton type="primary" @click="args.modelValue = false">我知道了</SfButton>
            </div>
          </template>
        </SfDialog>
      </div>
    `
  })
}

export const CustomHeader: Story = {
  args: {
    modelValue: false,
    width: '480px',
    showClose: false
  },
  render: (args) => ({
    components: { SfDialog, SfButton },
    setup() { return { args } },
    template: `
      <div>
        <SfButton type="primary" @click="args.modelValue = true">自定义头部</SfButton>
        <SfDialog v-bind="args">
          <template #header>
            <div style="padding: 8px 0">
              <div style="font-size: 18px; font-weight: 600">自定义标题</div>
              <div style="font-size: 12px; color: var(--color-text-muted); margin-top: 4px">
                副标题 / 描述
              </div>
            </div>
          </template>
          <p>用 <code>#header</code> slot 可以完全自定义头部,比如加图标、徽章、操作按钮。</p>
          <template #footer>
            <div style="display: flex; gap: 8px; justify-content: flex-end">
              <SfButton type="default" @click="args.modelValue = false">关闭</SfButton>
            </div>
          </template>
        </SfDialog>
      </div>
    `
  })
}
