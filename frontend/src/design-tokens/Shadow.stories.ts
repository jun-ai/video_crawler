import type { Meta, StoryObj } from '@storybook/vue3'

const meta = {
  title: 'Design Tokens/Shadow',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: '阴影系统 — 4 级 elevation · 卡片悬浮 / 弹窗 / 抽屉。'
      }
    }
  }
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

/**
 * 用一个白卡 + 阴影,演示不同 elevation
 */
const shadowBox = (name: string, varName: string, label: string) => `
  <div style="display: flex; flex-direction: column; align-items: center; gap: 12px;">
    <div
      style="
        width: 140px;
        height: 90px;
        background: var(--color-bg-card);
        border-radius: var(--radius-lg);
        box-shadow: var(${varName});
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        color: var(--color-text-primary);
        font-weight: 500;
      "
    >${label}</div>
    <code style="font-size: 12px; color: var(--color-text-primary); font-family: var(--font-mono); font-weight: 600;">${name}</code>
  </div>
`

export const AllShadows: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">阴影等级 Shadow</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">4 级 elevation — 从微妙到强烈</p>
        <div style="display: flex; flex-wrap: wrap; gap: 40px; align-items: flex-end; padding: 32px; background: var(--color-bg-elevated); border-radius: var(--radius-lg);">
          ${shadowBox('--sf-shadow-xs', '--sf-shadow-xs', 'xs · 边缘')}
          ${shadowBox('--sf-shadow-sm', '--sf-shadow-sm', 'sm · 卡片')}
          ${shadowBox('--sf-shadow-md', '--sf-shadow-md', 'md · 悬浮')}
          ${shadowBox('--sf-shadow-lg', '--sf-shadow-lg', 'lg · 弹窗')}
        </div>
      </div>
    `
  })
}

export const Elevation: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">Elevation 层次</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">不同 z-height 卡片对比 · 暗色背景更明显</p>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; padding: 48px 24px; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: var(--radius-lg);">
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); box-shadow: var(--sf-shadow-xs); text-align: center;">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">xs</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 6px;">列表项</div>
          </div>
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); box-shadow: var(--sf-shadow-sm); text-align: center;">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">sm</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 6px;">基础卡片</div>
          </div>
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); box-shadow: var(--sf-shadow-md); text-align: center;">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">md</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 6px;">悬浮卡片</div>
          </div>
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); box-shadow: var(--sf-shadow-lg); text-align: center;">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">lg</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 6px;">Modal 弹窗</div>
          </div>
        </div>
      </div>
    `
  })
}

export const InteractiveHover: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">交互式悬浮</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">hover 卡片看阴影变化 · transition 已内置</p>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 720px;">
          <div class="card-hover" style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border); cursor: pointer;">
            <h3 style="font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 6px;">基础卡片</h3>
            <p style="font-size: 12px; color: var(--color-text-secondary); margin: 0;">hover 看 transform + shadow 联动</p>
          </div>
          <div class="card-hover" style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border); cursor: pointer;">
            <h3 style="font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 6px;">品牌高亮</h3>
            <p style="font-size: 12px; color: var(--color-text-secondary); margin: 0;">border 也变蓝 + 上浮 4px</p>
          </div>
          <div class="card-hover" style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border); cursor: pointer;">
            <h3 style="font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 6px;">完整反馈</h3>
            <p style="font-size: 12px; color: var(--color-text-secondary); margin: 0;">视觉层次清晰</p>
          </div>
        </div>
      </div>
    `
  })
}
