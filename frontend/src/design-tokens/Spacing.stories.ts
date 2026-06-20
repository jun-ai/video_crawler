import type { Meta, StoryObj } from '@storybook/vue3'

const meta = {
  title: 'Design Tokens/Spacing',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: '间距系统 — 8 个常用间距 + 视觉化条形 + 实际使用对比。'
      }
    }
  }
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

/**
 * 用一个 50% 宽的实心 bar 演示间距值,bar 宽度 = token × 2(让 4px 也看得见)
 */
const bar = (name: string, value: string, scale: number) => {
  const widthPx = scale * 2 // 视觉放大: 1=2px, 16=32px 让 4px 也可见
  return `
    <div style="display: flex; align-items: center; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
      <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 130px;">${name}</code>
      <div style="width: 50%; height: 24px; background: var(--color-bg-elevated); border-radius: var(--radius-sm); position: relative; overflow: hidden;">
        <div style="position: absolute; left: 0; top: 0; height: 100%; width: ${widthPx}px; background: linear-gradient(90deg, var(--color-brand) 0%, var(--color-accent) 100%); border-radius: var(--radius-sm);"></div>
      </div>
      <code style="font-size: 11px; color: var(--color-text-primary); font-family: var(--font-mono); min-width: 50px;">${value}</code>
    </div>
  `
}

export const VisualScale: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">间距比例 Spacing Scale</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">8 档 4 的倍数 · bar 宽度视觉放大 2 倍</p>
        <div style="display: flex; flex-direction: column; gap: 8px; max-width: 720px;">
          ${bar('--sf-space-0', '0', 0)}
          ${bar('--sf-space-1', '4px', 1)}
          ${bar('--sf-space-2', '8px', 2)}
          ${bar('--sf-space-3', '12px', 3)}
          ${bar('--sf-space-4', '16px', 4)}
          ${bar('--sf-space-6', '24px', 6)}
          ${bar('--sf-space-8', '32px', 8)}
          ${bar('--sf-space-12', '48px', 12)}
        </div>
      </div>
    `
  })
}

export const UsageComparison: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">使用场景对比</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">按钮内边距 / 卡片间距 / 段落间距 · 真实组件片段</p>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
          <!-- 按钮内边距 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <h3 style="font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px;">按钮内边距 (8/12)</h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <button style="padding: var(--sf-space-2) var(--sf-space-3); background: var(--sf-cta-gradient, var(--color-brand)); color: #fff; border: none; border-radius: var(--radius-md); font-size: 13px; cursor: pointer;">
                紧凑 · 8×12
              </button>
              <button style="padding: var(--sf-space-3) var(--sf-space-6); background: var(--sf-cta-gradient, var(--color-brand)); color: #fff; border: none; border-radius: var(--radius-md); font-size: 14px; cursor: pointer;">
                标准 · 12×24
              </button>
              <button style="padding: var(--sf-space-4) var(--sf-space-8); background: var(--sf-cta-gradient, var(--color-brand)); color: #fff; border: none; border-radius: var(--radius-md); font-size: 16px; cursor: pointer;">
                宽松 · 16×32
              </button>
            </div>
            <code style="display: block; font-size: 10px; color: var(--color-text-muted); font-family: var(--font-mono); margin-top: 12px;">--sf-space-2 / 3 / 4 / 6 / 8</code>
          </div>

          <!-- 卡片间距 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <h3 style="font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px;">卡片间距 (12/16)</h3>
            <div style="display: flex; flex-direction: column; gap: var(--sf-space-3);">
              <div style="padding: var(--sf-space-3); background: var(--color-brand-subtle); border-radius: var(--radius-sm); font-size: 12px; color: var(--color-text-primary);">紧凑 12px</div>
              <div style="padding: var(--sf-space-3); background: var(--color-brand-subtle); border-radius: var(--radius-sm); font-size: 12px; color: var(--color-text-primary);">列表间距</div>
            </div>
            <div style="height: var(--sf-space-4);"></div>
            <div style="display: flex; flex-direction: column; gap: var(--sf-space-4);">
              <div style="padding: var(--sf-space-4); background: var(--color-accent-subtle); border-radius: var(--radius-sm); font-size: 12px; color: var(--color-text-primary);">标准 16px</div>
              <div style="padding: var(--sf-space-4); background: var(--color-accent-subtle); border-radius: var(--radius-sm); font-size: 12px; color: var(--color-text-primary);">卡片间距</div>
            </div>
            <code style="display: block; font-size: 10px; color: var(--color-text-muted); font-family: var(--font-mono); margin-top: 12px;">--sf-space-3 / 4</code>
          </div>

          <!-- 段落间距 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <h3 style="font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px;">段落间距 (16/24)</h3>
            <div style="font-size: 13px; color: var(--color-text-primary); line-height: var(--leading-base);">
              <p style="margin: 0 0 var(--sf-space-4);">段落之间 16px 间距 — 紧凑阅读,信息密度高。</p>
              <p style="margin: 0 0 var(--sf-space-6);">段落之间 24px 间距 — 呼吸感强,适合长文。</p>
              <p style="margin: 0;">段落之间 24px 间距 — 阅读舒适。</p>
            </div>
            <code style="display: block; font-size: 10px; color: var(--color-text-muted); font-family: var(--font-mono); margin-top: 12px;">--sf-space-4 / 6</code>
          </div>
        </div>
      </div>
    `
  })
}

export const FullScale: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">完整 Spacing Scale</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">12 档 — 从 0 到 64px</p>
        <div style="display: flex; flex-direction: column; gap: 6px; max-width: 720px;">
          ${bar('--sf-space-0', '0', 0)}
          ${bar('--sf-space-1', '4px', 1)}
          ${bar('--sf-space-2', '8px', 2)}
          ${bar('--sf-space-3', '12px', 3)}
          ${bar('--sf-space-4', '16px', 4)}
          ${bar('--sf-space-5', '20px', 5)}
          ${bar('--sf-space-6', '24px', 6)}
          ${bar('--sf-space-8', '32px', 8)}
          ${bar('--sf-space-10', '40px', 10)}
          ${bar('--sf-space-12', '48px', 12)}
          ${bar('--sf-space-16', '64px', 16)}
        </div>
      </div>
    `
  })
}
