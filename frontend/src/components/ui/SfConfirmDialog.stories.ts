import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import SfConfirmDialog from './SfConfirmDialog.vue'
import SfButton from './SfButton.vue'
import { showConfirm } from '@/composables/useConfirm'

const meta = {
  title: 'UI/SfConfirmDialog',
  component: SfConfirmDialog,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: '基于 Promise 的确认弹窗。在业务代码里调用 `showConfirm({...})` 即可, 全局只需挂载一次本组件。'
      }
    }
  }
} satisfies Meta<typeof SfConfirmDialog>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => ({
    components: { SfConfirmDialog, SfButton },
    setup() {
      const result = ref(null)
      const onClick = async () => {
        result.value = await showConfirm({
          title: '确认操作',
          message: '你确定要继续吗?',
          type: 'warning'
        })
        if (result.value === null) result.value = '已关闭'
      }
      return { onClick, result }
    },
    template: `
      <div>
        <SfButton type="primary" @click="onClick">触发默认确认</SfButton>
        <div style="margin-top: 16px; font-size: 13px; color: var(--color-text-secondary);">
          按钮返回值: <code>{{ result ?? '(还没点过)' }}</code>
        </div>
        <SfConfirmDialog />
      </div>
    `
  })
}

export const Danger: Story = {
  render: () => ({
    components: { SfConfirmDialog, SfButton },
    setup() {
      const log = ref([])
      const onDelete = async () => {
        const ok = await showConfirm({
          title: '删除这条视频?',
          message: '操作不可撤销, 视频记录、字幕、下载历史都会被一起清理。',
          type: 'danger',
          confirmText: '永久删除',
          cancelText: '再想想'
        })
        log.value.unshift({ at: new Date().toLocaleTimeString(), ok })
      }
      return { onDelete, log }
    },
    template: `
      <div>
        <SfButton type="danger" @click="onDelete">删除视频</SfButton>
        <div style="margin-top: 16px; font-size: 12px; color: var(--color-text-tertiary, #9ca3af);">
          <div style="margin-bottom: 4px;">点击记录:</div>
          <div v-if="log.length === 0">(无)</div>
          <div v-for="row in log" :key="row.at" style="font-family: monospace;">
            [{{ row.at }}] ok = {{ row.ok }}
          </div>
        </div>
        <SfConfirmDialog />
      </div>
    `
  })
}

export const Info: Story = {
  render: () => ({
    components: { SfConfirmDialog, SfButton },
    setup() {
      const onInfo = async () => {
        await showConfirm({
          title: '提示',
          message: '本周末 (周六 02:00-04:00) 会有一波数据库维护, 期间服务会短暂不可用。',
          type: 'warning',
          confirmText: '知道了',
          cancelText: '不再提醒'
        })
      }
      return { onInfo }
    },
    template: `
      <div>
        <SfButton @click="onInfo">显示信息提示</SfButton>
        <SfConfirmDialog />
      </div>
    `
  })
}

export const WithCustomText: Story = {
  render: () => ({
    components: { SfConfirmDialog, SfButton },
    setup() {
      const result = ref(null)
      const onPublish = async () => {
        const ok = await showConfirm({
          title: '发布 v1.2.0?',
          message: '构建产物已就绪, 共 47 个文件, 总大小 2.3 MB, 部署到生产预计耗时 30 秒。',
          type: 'warning',
          confirmText: '立即发布',
          cancelText: '暂不发布'
        })
        result.value = ok ? '已发布' : '已取消'
      }
      return { onPublish, result }
    },
    template: `
      <div>
        <SfButton type="primary" @click="onPublish">发布版本</SfButton>
        <div style="margin-top: 16px; font-size: 13px; color: var(--color-text-secondary);">
          状态: <code>{{ result ?? '(等待操作)' }}</code>
        </div>
        <SfConfirmDialog />
      </div>
    `
  })
}

export const AllTypes: Story = {
  render: () => ({
    components: { SfConfirmDialog, SfButton },
    setup() {
      const fire = (type) => {
        const map = {
          warning: { title: '警告', message: '这是一个警告型确认, 默认黄色。', type: 'warning' },
          danger: { title: '危险', message: '不可逆操作, 红色按钮提示风险。', type: 'danger', confirmText: '我清楚风险' }
        }
        showConfirm({ ...map[type], confirmText: map[type].confirmText || '确定', cancelText: '取消' })
      }
      return { fire }
    },
    template: `
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        <SfButton type="primary" @click="fire('warning')">Warning (默认)</SfButton>
        <SfButton type="danger" @click="fire('danger')">Danger (删除)</SfButton>
        <SfConfirmDialog />
      </div>
    `
  })
}
