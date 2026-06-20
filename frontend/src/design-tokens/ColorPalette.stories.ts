import type { Meta, StoryObj } from '@storybook/vue3'

const meta = {
  title: 'Design Tokens/ColorPalette',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: '颜色调色板 — Phase 5 清新蓝系。所有颜色通过 CSS 变量驱动,亮/暗主题自动切换。'
      }
    }
  }
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

/**
 * 用一个 56×56 的实心方块渲染色值,下方写 token 名 + 用途说明。
 * 表格化展示,方便快速对比。
 */
const swatch = (name: string, varName: string, note: string, dark = false) => `
  <div style="display: flex; flex-direction: column; align-items: center; gap: 6px; min-width: 96px;">
    <div
      style="
        width: 56px;
        height: 56px;
        border-radius: var(--radius-md);
        background: var(${varName});
        ${dark ? 'border: 1px solid rgba(255,255,255,0.12);' : 'border: 1px solid var(--color-border);'}
      "
    ></div>
    <code style="font-size: 11px; color: var(--color-text-primary); font-family: var(--font-mono);">${name}</code>
    <span style="font-size: 11px; color: var(--color-text-muted); text-align: center;">${note}</span>
  </div>
`

export const BrandColors: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">品牌色 Brand</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">主操作 / 链接 / 高亮 — Phase 5 清新蓝</p>
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
          ${swatch('--color-brand', '--color-brand', '主品牌色 · CTA')}
          ${swatch('--color-brand-hover', '--color-brand-hover', 'hover 加深')}
          ${swatch('--color-brand-light', '--color-brand-light', '浅色文字/背景')}
          ${swatch('--color-brand-subtle', '--color-brand-subtle', '极浅高亮底')}
          ${swatch('--color-accent', '--color-accent', '强调 · 琥珀金')}
          ${swatch('--color-accent-hover', '--color-accent-hover', '琥珀 hover')}
        </div>
      </div>
    `
  })
}

export const TextColors: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">文字色 Text</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">从主到弱 4 级灰阶</p>
        <div style="display: flex; flex-direction: column; gap: 12px; max-width: 720px;">
          <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <span style="font-size: 20px; font-weight: 600; color: var(--color-text-primary);">主标题 · The quick brown fox</span>
            <code style="margin-left: auto; font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-text-primary</code>
          </div>
          <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <span style="font-size: 15px; color: var(--color-text-secondary);">次要文字 · 描述/标签</span>
            <code style="margin-left: auto; font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-text-secondary</code>
          </div>
          <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <span style="font-size: 13px; color: var(--color-text-muted);">弱化文字 · 元信息/时间戳</span>
            <code style="margin-left: auto; font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-text-muted</code>
          </div>
          <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <input
              placeholder="占位文字 · placeholder"
              style="background: transparent; border: none; outline: none; color: var(--color-text-primary); font-size: 14px; flex: 1;"
            />
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-text-placeholder</code>
          </div>
        </div>
      </div>
    `
  })
}

export const BackgroundColors: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">背景色 Background</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">5 层叠加 — base / card / elevated / hover / mask</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px;">
          <div style="padding: 24px; background: var(--color-bg-base); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-bg-base</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 8px;">页面底色</div>
          </div>
          <div style="padding: 24px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-bg-card</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 8px;">卡片底</div>
          </div>
          <div style="padding: 24px; background: var(--color-bg-elevated); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-bg-elevated</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 8px;">悬浮层</div>
          </div>
          <div style="padding: 24px; background: var(--color-bg-hover); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-bg-hover</code>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 8px;">hover 状态</div>
          </div>
        </div>
      </div>
    `
  })
}

export const BorderColors: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">边框色 Border</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">普通 / 加强 / 品牌高亮</p>
        <div style="display: flex; flex-direction: column; gap: 16px; max-width: 720px;">
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; color: var(--color-text-primary);">常规边框</span>
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-border</code>
          </div>
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1.5px solid var(--color-border-strong); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; color: var(--color-text-primary);">加粗边框</span>
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-border-strong</code>
          </div>
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1.5px solid var(--color-border-brand); display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 14px; color: var(--color-text-primary);">品牌高亮 (focus)</span>
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--color-border-brand</code>
          </div>
        </div>
      </div>
    `
  })
}

export const StatusColors: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">状态色 Status</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">success / warning / danger / info + 浅色背景</p>
        <div style="display: flex; flex-wrap: wrap; gap: 16px;">
          ${swatch('--color-success', '--color-success', '成功 · 完成')}
          ${swatch('--color-success-light', '--color-success-light', '成功背景')}
          ${swatch('--color-warning', '--color-warning', '警告 · 提醒')}
          ${swatch('--color-warning-light', '--color-warning-light', '警告背景')}
          ${swatch('--color-danger', '--color-danger', '错误 · 删除')}
          ${swatch('--color-danger-light', '--color-danger-light', '错误背景')}
          ${swatch('--color-info', '--color-info', '信息 · 提示')}
          ${swatch('--color-info-light', '--color-info-light', '信息背景')}
        </div>
      </div>
    `
  })
}

export const AnnotationColors: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">标注色 Annotation</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">字幕标注 3 色: 词汇 / 词伙 / 重点</p>
        <div style="display: flex; flex-direction: column; gap: 12px; max-width: 720px;">
          <div style="padding: 14px 18px; background: var(--color-bg-card); border-radius: var(--radius-md); border-left: 4px solid var(--color-annotation-vocabulary);">
            <code style="font-size: 11px; color: var(--color-annotation-vocabulary); font-family: var(--font-mono); font-weight: 600;">--color-annotation-vocabulary</code>
            <div style="font-size: 15px; color: var(--color-text-primary); margin-top: 4px;">vocabulary — 单词标注</div>
          </div>
          <div style="padding: 14px 18px; background: var(--color-bg-card); border-radius: var(--radius-md); border-left: 4px solid var(--color-annotation-phrase);">
            <code style="font-size: 11px; color: var(--color-annotation-phrase); font-family: var(--font-mono); font-weight: 600;">--color-annotation-phrase</code>
            <div style="font-size: 15px; color: var(--color-text-primary); margin-top: 4px;">phrase — 词伙标注</div>
          </div>
          <div style="padding: 14px 18px; background: var(--color-bg-card); border-radius: var(--radius-md); border-left: 4px solid var(--color-annotation-important);">
            <code style="font-size: 11px; color: var(--color-annotation-important); font-family: var(--font-mono); font-weight: 600;">--color-annotation-important</code>
            <div style="font-size: 15px; color: var(--color-text-primary); margin-top: 4px;">important — 重点强调</div>
          </div>
        </div>
      </div>
    `
  })
}
