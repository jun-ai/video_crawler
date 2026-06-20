import type { Meta, StoryObj } from '@storybook/vue3'
import { toast } from '@/composables/useToast'
import SfToast from './SfToast.vue'
import SfButton from './SfButton.vue'

const meta = {
  title: 'UI/SfToast',
  component: SfToast,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          '全局 toast 单例组件, 需要 SfToast 实例挂载到 DOM 才能渲染。' +
          '本 stories 每个示例都会自动包含 SfToast, 按钮通过 useToast 单例触发。'
      }
    }
  }
} satisfies Meta<typeof SfToast>

export default meta
type Story = StoryObj<typeof meta>

// 注意: SfToast 通过 Teleport 渲染到 body, 必须在每个 story 里手动挂载一次
const withToastMount = (slot: string) => ({
  components: { SfToast, SfButton },
  template: `
    <div>
      ${slot}
      <SfToast />
    </div>
  `
})

// 4 种类型 — 4 个按钮触发
export const AllTypes: Story = {
  render: () => ({
    ...withToastMount(`
      <div style="padding: 24px; display: flex; flex-wrap: wrap; gap: 12px;">
        <SfButton type="primary" @click="toast.success('视频已下载到本地')">success</SfButton>
        <SfButton type="danger" @click="toast.error('下载失败, 网络断开')">error</SfButton>
        <SfButton type="default" @click="toast.warning('存储空间不足 1GB')">warning</SfButton>
        <SfButton @click="toast.info('正在解析视频元数据…')">info</SfButton>
      </div>
    `),
    setup() {
      return { toast }
    }
  })
}

// 成功 toast — 带持续时长 + 自动消失
export const Success: Story = {
  render: () => ({
    ...withToastMount(`
      <div style="padding: 24px;">
        <SfButton type="primary" @click="toast.success('已保存到「我的收藏」', { duration: 2500 })">
          触发成功提示
        </SfButton>
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          2.5 秒后自动消失, 右上角弹出
        </p>
      </div>
    `),
    setup() {
      return { toast }
    }
  })
}

// 错误 toast — 默认 4 秒
export const Error: Story = {
  render: () => ({
    ...withToastMount(`
      <div style="padding: 24px;">
        <SfButton type="danger" @click="toast.error('上传失败: 文件超过 500MB 限制')">
          触发错误提示
        </SfButton>
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          error 默认 duration=4s, 比其他类型停留更久
        </p>
      </div>
    `),
    setup() {
      return { toast }
    }
  })
}

// 警告 toast — 不自动消失 + 显示关闭按钮
export const Warning: Story = {
  render: () => ({
    ...withToastMount(`
      <div style="padding: 24px;">
        <SfButton type="default" @click="toast.warning('检测到重复视频, 是否跳过?', { duration: 0, showClose: true })">
          触发警告 (常驻 + 关闭按钮)
        </SfButton>
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          duration=0 表示不自动消失, showClose=true 显示右上角 X
        </p>
      </div>
    `),
    setup() {
      return { toast }
    }
  })
}

// 普通 info
export const Info: Story = {
  render: () => ({
    ...withToastMount(`
      <div style="padding: 24px;">
        <SfButton @click="toast.info('正在解析 3 个视频的元数据…')">
          触发 info 提示
        </SfButton>
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          用于普通通知, 3 秒后自动消失
        </p>
      </div>
    `),
    setup() {
      return { toast }
    }
  })
}

// 带 action 按钮 — 撤销场景
export const WithAction: Story = {
  render: () => ({
    ...withToastMount(`
      <div style="padding: 24px;">
        <SfButton
          type="danger"
          @click="toast.withAction('视频已删除', { label: '撤销', onClick: () => toast.success('已恢复删除的视频') }, { type: 'info' })"
        >
          删除视频 (5 秒内可撤销)
        </SfButton>
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          toast.withAction(message, { label, onClick }) — 点撤销触发回调并自动关闭
        </p>
      </div>
    `),
    setup() {
      return { toast }
    }
  })
}

// 同时堆叠多个
export const Stacked: Story = {
  render: () => ({
    ...withToastMount(`
      <div style="padding: 24px;">
        <SfButton
          type="primary"
          @click="() => {
            toast.info('开始批量下载 (3/10)')
            setTimeout(() => toast.success('第 1 个完成'), 400)
            setTimeout(() => toast.success('第 2 个完成'), 800)
            setTimeout(() => toast.warning('第 3 个失败, 已跳过'), 1200)
            setTimeout(() => toast.info('批量下载完成'), 1600)
          }"
        >
          触发批量操作 (看堆叠动画)
        </SfButton>
        <p style="margin-top: 16px; color: var(--color-text-muted); font-size: 13px;">
          多个 toast 堆叠, 每条带 enter/leave 动画
        </p>
      </div>
    `),
    setup() {
      return { toast }
    }
  })
}