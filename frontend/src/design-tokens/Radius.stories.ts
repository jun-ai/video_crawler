import type { Meta, StoryObj } from '@storybook/vue3'

const meta = {
  title: 'Design Tokens/Radius',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: '圆角系统 — 5 个圆角档位 + 实际组件应用。'
      }
    }
  }
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

/**
 * 渲染一个 96×96 的圆角方块,带 token 标签
 */
const radiusBox = (name: string, varName: string, label: string) => `
  <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
    <div
      style="
        width: 96px;
        height: 96px;
        background: var(--sf-brand-gradient, var(--color-brand));
        border-radius: var(${varName});
        box-shadow: var(--shadow-md);
      "
    ></div>
    <code style="font-size: 12px; color: var(--color-text-primary); font-family: var(--font-mono); font-weight: 600;">${name}</code>
    <span style="font-size: 11px; color: var(--color-text-muted);">${label}</span>
  </div>
`

export const AllRadius: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">圆角档位 Radius</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">5 档 — sm 8px / md 12px / lg 16px / xl 24px / full 9999px</p>
        <div style="display: flex; flex-wrap: wrap; gap: 32px; align-items: flex-end;">
          ${radiusBox('--sf-radius-sm', '--sf-radius-sm', '8px · 小标签/输入框')}
          ${radiusBox('--sf-radius-md', '--sf-radius-md', '12px · 按钮/小卡片')}
          ${radiusBox('--sf-radius-lg', '--sf-radius-lg', '16px · 主卡片')}
          ${radiusBox('--sf-radius-xl', '--sf-radius-xl', '24px · 大区块')}
          ${radiusBox('--sf-radius-full', '--sf-radius-full', '9999 · 胶囊/头像')}
        </div>
      </div>
    `
  })
}

export const Usage: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">使用场景对比</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">按钮 / 卡片 / Tag · 同一组件不同圆角</p>

        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; max-width: 960px;">
          <!-- 按钮圆角 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <h3 style="font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 16px;">按钮</h3>
            <div style="display: flex; flex-direction: column; gap: 12px; align-items: flex-start;">
              <button style="padding: 8px 16px; background: var(--color-brand); color: #fff; border: none; border-radius: var(--sf-radius-sm); font-size: 13px; cursor: pointer;">直角 · sm</button>
              <button style="padding: 8px 16px; background: var(--color-brand); color: #fff; border: none; border-radius: var(--sf-radius-md); font-size: 13px; cursor: pointer;">柔和 · md</button>
              <button style="padding: 8px 16px; background: var(--color-brand); color: #fff; border: none; border-radius: var(--sf-radius-full); font-size: 13px; cursor: pointer;">胶囊 · full</button>
            </div>
          </div>

          <!-- 卡片圆角 -->
          <div style="padding: 20px; background: transparent; border-radius: 0; border: none;">
            <h3 style="font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 16px;">卡片</h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              <div style="padding: 16px; background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--sf-radius-md); font-size: 12px; color: var(--color-text-primary);">
                小卡 · md
              </div>
              <div style="padding: 16px; background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--sf-radius-lg); font-size: 12px; color: var(--color-text-primary);">
                主卡 · lg
              </div>
              <div style="padding: 16px; background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--sf-radius-xl); font-size: 12px; color: var(--color-text-primary);">
                大卡 · xl
              </div>
            </div>
          </div>

          <!-- Tag 圆角 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <h3 style="font-size: 13px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 16px;">Tag 标签</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <span style="padding: 3px 8px; background: var(--color-brand-subtle); color: var(--color-brand); border-radius: var(--sf-radius-sm); font-size: 11px; font-weight: 500;">口语 · sm</span>
              <span style="padding: 3px 8px; background: var(--color-brand-subtle); color: var(--color-brand); border-radius: var(--sf-radius-md); font-size: 11px; font-weight: 500;">商务 · md</span>
              <span style="padding: 3px 10px; background: var(--color-accent-subtle); color: var(--color-accent-hover); border-radius: var(--sf-radius-full); font-size: 11px; font-weight: 500;">高阶 · full</span>
            </div>
            <div style="margin-top: 16px; display: flex; flex-wrap: wrap; gap: 8px;">
              <span style="padding: 3px 8px; background: var(--color-success-light); color: var(--color-success); border-radius: var(--sf-radius-sm); font-size: 11px; font-weight: 500;">CET-4</span>
              <span style="padding: 3px 8px; background: var(--color-warning-light); color: var(--color-warning); border-radius: var(--sf-radius-sm); font-size: 11px; font-weight: 500;">雅思 7.0</span>
            </div>
          </div>
        </div>
      </div>
    `
  })
}

export const FullCollection: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">全档对比</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">6 档 — 包含 --radius-2xl</p>
        <div style="display: flex; flex-wrap: wrap; gap: 24px; align-items: flex-end;">
          ${radiusBox('--sf-radius-sm', '--sf-radius-sm', '8px')}
          ${radiusBox('--sf-radius-md', '--sf-radius-md', '12px')}
          ${radiusBox('--sf-radius-lg', '--sf-radius-lg', '16px')}
          ${radiusBox('--sf-radius-xl', '--sf-radius-xl', '24px')}
          <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
            <div style="width: 96px; height: 96px; background: var(--sf-brand-gradient, var(--color-brand)); border-radius: var(--radius-2xl); box-shadow: var(--shadow-md);"></div>
            <code style="font-size: 12px; color: var(--color-text-primary); font-family: var(--font-mono); font-weight: 600;">--radius-2xl</code>
            <span style="font-size: 11px; color: var(--color-text-muted);">32px · 弹窗</span>
          </div>
          ${radiusBox('--sf-radius-full', '--sf-radius-full', '9999px')}
        </div>
      </div>
    `
  })
}
