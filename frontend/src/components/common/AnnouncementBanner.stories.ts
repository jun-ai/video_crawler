import type { Meta, StoryObj } from '@storybook/vue3'
import AnnouncementBanner from './AnnouncementBanner.vue'
import { announcementAPI } from '@/api'

// 公告类型只有 4 种：info / warning / success / update
type AnnouncementType = 'info' | 'warning' | 'success' | 'update'

interface MockAnnouncement {
  id: number
  type: AnnouncementType
  title: string
  content: string
}

// 每个 story 在 setup 里覆盖 announcementAPI.getList，渲染时组件 onMounted 即可拿到 mock 数据
// 由于模块是单例，story 之间会按顺序覆盖，无需手动恢复
const mockAnnouncement = (data: MockAnnouncement) => {
  announcementAPI.getList = () => Promise.resolve([data])
}

// 真实项目里该组件会从 /api/announcements 拉取首条公告
// 这里在 story 中 mock，方便展示 4 种 type 视觉

const meta = {
  title: 'Common/AnnouncementBanner',
  component: AnnouncementBanner,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: '顶部公告横幅。组件挂载时调用 announcementAPI.getList({ limit: 1 }) 拉取首条公告，关闭后写入 localStorage。该组件支持的 type 仅有：info / warning / success / update。'
      }
    }
  }
} satisfies Meta<typeof AnnouncementBanner>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  name: 'Info',
  render: () => ({
    components: { AnnouncementBanner },
    setup() {
      mockAnnouncement({
        id: 1,
        type: 'info',
        title: '系统升级完成',
        content: '新版本已上线，搜索性能提升 40%，欢迎体验。'
      })
      return {}
    },
    template: '<AnnouncementBanner />'
  }),
  parameters: {
    docs: {
      description: {
        story: '默认 info 类型，蓝绿色调。'
      }
    }
  }
}

export const Warning: Story = {
  render: () => ({
    components: { AnnouncementBanner },
    setup() {
      mockAnnouncement({
        id: 2,
        type: 'warning',
        title: '服务维护通知',
        content: '本周日凌晨 02:00 - 04:00 进行服务维护，期间部分功能可能短暂不可用。'
      })
      return {}
    },
    template: '<AnnouncementBanner />'
  }),
  parameters: {
    docs: {
      description: {
        story: 'warning 类型，琥珀色调，用于风险/维护提醒。'
      }
    }
  }
}

export const Success: Story = {
  render: () => ({
    components: { AnnouncementBanner },
    setup() {
      mockAnnouncement({
        id: 3,
        type: 'success',
        title: '数据迁移成功',
        content: '所有资料已成功迁移到新账号，原始数据保留 30 天。'
      })
      return {}
    },
    template: '<AnnouncementBanner />'
  }),
  parameters: {
    docs: {
      description: {
        story: 'success 类型，绿色调，用于正向反馈。'
      }
    }
  }
}

export const Update: Story = {
  name: 'Update (Rocket)',
  render: () => ({
    components: { AnnouncementBanner },
    setup() {
      mockAnnouncement({
        id: 4,
        type: 'update',
        title: '新功能上线',
        content: 'v2.3.0 发布：新增 AI 字幕生成、跨设备同步、暗色模式。'
      })
      return {}
    },
    template: '<AnnouncementBanner />'
  }),
  parameters: {
    docs: {
      description: {
        story: 'update 类型（火箭图标），用于版本发布/新功能推送。注意：组件不支持 error 类型。'
      }
    }
  }
}

export const Dismissible: Story = {
  render: () => ({
    components: { AnnouncementBanner },
    setup() {
      mockAnnouncement({
        id: 5,
        type: 'info',
        title: '这是一条可关闭的公告',
        content: '点击右上角 × 关闭。关闭记录会写入 localStorage 的 closed_announcements（最多保留 20 条），刷新页面后同 ID 不再展示。'
      })
      return {}
    },
    template: `
      <div style="display: flex; flex-direction: column; gap: 12px; width: 100%; max-width: 720px;">
        <AnnouncementBanner />
        <p style="font-size: 12px; color: var(--color-text-muted); margin: 0;">
          点击「查看详情」展开完整内容，点击 × 关闭后该 ID 会被记忆。
        </p>
      </div>
    `
  }),
  parameters: {
    docs: {
      description: {
        story: '展示关闭交互：含「查看详情/收起」与 × 关闭按钮。'
      }
    }
  }
}

// 组件只支持 4 种 type（info / warning / success / update），不支持 error
