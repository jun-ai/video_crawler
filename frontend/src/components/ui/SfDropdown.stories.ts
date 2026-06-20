import type { Meta, StoryObj } from '@storybook/vue3'
import SfDropdown from './SfDropdown.vue'
import SfButton from './SfButton.vue'
import { ChevronDown, User, Settings, LogOut, Trash2, Edit3, Copy, Download } from 'lucide-vue-next'

const meta = {
  title: 'UI/SfDropdown',
  component: SfDropdown,
  tags: ['autodocs'],
  argTypes: {
    placement: {
      control: { type: 'select' },
      options: ['top', 'bottom', 'left', 'right'],
      description: '菜单位置（CSS 方向）'
    }
  }
} satisfies Meta<typeof SfDropdown>

export default meta
type Story = StoryObj<typeof meta>

// 通用菜单项样式（包在 scoped 不到的样式里，所以用全局 class）
const menuItemStyle = `
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-primary);
  transition: background var(--sf-duration-fast);
  user-select: none;
`
const menuItemHover = `
  onmouseover="this.style.background='var(--color-bg-hover, rgba(0,0,0,0.05))'"
  onmouseout="this.style.background='transparent'"
`

export const Default: Story = {
  args: {
    placement: 'bottom'
  },
  render: (args) => ({
    components: { SfDropdown, SfButton, ChevronDown },
    setup() { return { args } },
    template: `
      <SfDropdown v-bind="args">
        <template #trigger>
          <SfButton type="default">
            点击打开
            <ChevronDown :size="14" style="margin-left: 4px;" />
          </SfButton>
        </template>
        <div style="min-width: 160px;">
          <div style="${menuItemStyle}" ${menuItemHover}>选项一</div>
          <div style="${menuItemStyle}" ${menuItemHover}>选项二</div>
          <div style="${menuItemStyle}" ${menuItemHover}>选项三</div>
        </div>
      </SfDropdown>
    `
  })
}

export const WithDivider: Story = {
  render: () => ({
    components: { SfDropdown, SfButton, ChevronDown },
    template: `
      <SfDropdown>
        <template #trigger>
          <SfButton type="default">
            含分隔线
            <ChevronDown :size="14" style="margin-left: 4px;" />
          </SfButton>
        </template>
        <div style="min-width: 180px;">
          <div style="${menuItemStyle}" ${menuItemHover}>个人主页</div>
          <div style="${menuItemStyle}" ${menuItemHover}>收藏夹</div>
          <div style="height: 1px; background: var(--color-border); margin: 4px 8px;"></div>
          <div style="${menuItemStyle}" ${menuItemHover}>设置</div>
          <div style="${menuItemStyle}" ${menuItemHover}>帮助中心</div>
          <div style="height: 1px; background: var(--color-border); margin: 4px 8px;"></div>
          <div style="${menuItemStyle}; color: var(--color-danger, #ef4444);" ${menuItemHover}>退出登录</div>
        </div>
      </SfDropdown>
    `
  })
}

export const WithIcon: Story = {
  render: () => ({
    components: { SfDropdown, SfButton, ChevronDown, User, Settings, LogOut },
    template: `
      <SfDropdown>
        <template #trigger>
          <SfButton type="primary">
            <User :size="16" style="margin-right: 6px;" />
            我的账户
            <ChevronDown :size="14" style="margin-left: 4px;" />
          </SfButton>
        </template>
        <div style="min-width: 180px;">
          <div style="${menuItemStyle}" ${menuItemHover}>
            <User :size="16" /> 个人资料
          </div>
          <div style="${menuItemStyle}" ${menuItemHover}>
            <Settings :size="16" /> 账户设置
          </div>
          <div style="height: 1px; background: var(--color-border); margin: 4px 8px;"></div>
          <div style="${menuItemStyle}; color: var(--color-danger, #ef4444);" ${menuItemHover}>
            <LogOut :size="16" /> 退出登录
          </div>
        </div>
      </SfDropdown>
    `
  })
}

export const WithActions: Story = {
  render: () => ({
    components: { SfDropdown, SfButton, ChevronDown, Edit3, Trash2, Copy, Download },
    template: `
      <SfDropdown>
        <template #trigger>
          <SfButton type="default" size="sm">
            操作
            <ChevronDown :size="14" style="margin-left: 4px;" />
          </SfButton>
        </template>
        <div style="min-width: 160px;">
          <div style="${menuItemStyle}" ${menuItemHover}>
            <Edit3 :size="14" /> 编辑
          </div>
          <div style="${menuItemStyle}" ${menuItemHover}>
            <Copy :size="14" /> 复制
          </div>
          <div style="${menuItemStyle}" ${menuItemHover}>
            <Download :size="14" /> 导出
          </div>
          <div style="height: 1px; background: var(--color-border); margin: 4px 8px;"></div>
          <div style="${menuItemStyle}; color: var(--color-danger, #ef4444);" ${menuItemHover}>
            <Trash2 :size="14" /> 删除
          </div>
        </div>
      </SfDropdown>
    `
  })
}

export const Placements: Story = {
  render: () => ({
    components: { SfDropdown, SfButton, ChevronDown },
    template: `
      <div style="display: flex; gap: 16px; flex-wrap: wrap;">
        <SfDropdown placement="bottom">
          <template #trigger>
            <SfButton type="default" size="sm">↓ 向下</SfButton>
          </template>
          <div style="${menuItemStyle}" ${menuItemHover}>向下选项</div>
          <div style="${menuItemStyle}" ${menuItemHover}>向下选项二</div>
        </SfDropdown>
        <SfDropdown placement="top">
          <template #trigger>
            <SfButton type="default" size="sm">↑ 向上</SfButton>
          </template>
          <div style="${menuItemStyle}" ${menuItemHover}>向上选项</div>
          <div style="${menuItemStyle}" ${menuItemHover}>向上选项二</div>
        </SfDropdown>
        <SfDropdown placement="left">
          <template #trigger>
            <SfButton type="default" size="sm">← 向左</SfButton>
          </template>
          <div style="${menuItemStyle}" ${menuItemHover}>向左选项</div>
          <div style="${menuItemStyle}" ${menuItemHover}>向左选项二</div>
        </SfDropdown>
        <SfDropdown placement="right">
          <template #trigger>
            <SfButton type="default" size="sm">→ 向右</SfButton>
          </template>
          <div style="${menuItemStyle}" ${menuItemHover}>向右选项</div>
          <div style="${menuItemStyle}" ${menuItemHover}>向右选项二</div>
        </SfDropdown>
      </div>
    `
  })
}

export const CustomTrigger: Story = {
  render: () => ({
    components: { SfDropdown },
    template: `
      <SfDropdown>
        <template #trigger>
          <div
            style="
              display: inline-flex;
              align-items: center;
              gap: 6px;
              padding: 8px 14px;
              border-radius: 9999px;
              background: var(--sf-cta-gradient, linear-gradient(135deg, #667eea, #764ba2));
              color: #fff;
              font-size: 14px;
              font-weight: 500;
              cursor: pointer;
              user-select: none;
            "
          >
            <span style="
              width: 8px;
              height: 8px;
              border-radius: 50%;
              background: #22c55e;
              box-shadow: 0 0 0 2px rgba(34,197,94,0.3);
            "></span>
            在线 · 点我
          </div>
        </template>
        <div style="min-width: 180px;">
          <div style="${menuItemStyle}" ${menuItemHover}>设为在线</div>
          <div style="${menuItemStyle}" ${menuItemHover}>设为离开</div>
          <div style="${menuItemStyle}" ${menuItemHover}>请勿打扰</div>
          <div style="height: 1px; background: var(--color-border); margin: 4px 8px;"></div>
          <div style="${menuItemStyle}" ${menuItemHover}>隐身</div>
        </div>
      </SfDropdown>
    `
  })
}