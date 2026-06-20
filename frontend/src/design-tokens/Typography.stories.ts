import type { Meta, StoryObj } from '@storybook/vue3'

const meta = {
  title: 'Design Tokens/Typography',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: '字体系统 — 字号 / 字重 / 标题层级 / 行高。Inter + Noto Sans SC。'
      }
    }
  }
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

export const FontSizes: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">字号 Font Size</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">7 级 scale — xs (12) → 5xl (48)</p>
        <div style="display: flex; flex-direction: column; gap: 8px; max-width: 720px;">
          <div style="display: flex; align-items: baseline; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 100px;">--text-xs</code>
            <span style="font-size: var(--text-xs); color: var(--color-text-primary);">辅助说明文字 12px</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 100px;">--text-sm</code>
            <span style="font-size: var(--text-sm); color: var(--color-text-primary);">正文/标签 14px</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 100px;">--text-base</code>
            <span style="font-size: var(--text-base); color: var(--color-text-primary);">段落正文 16px</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 100px;">--text-lg</code>
            <span style="font-size: var(--text-lg); color: var(--color-text-primary);">小标题 18px</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 100px;">--text-xl</code>
            <span style="font-size: var(--text-xl); color: var(--color-text-primary);">大标题 20px</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 100px;">--text-2xl</code>
            <span style="font-size: var(--text-2xl); color: var(--color-text-primary);">页面标题 24px</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono); min-width: 100px;">--text-3xl</code>
            <span style="font-size: var(--text-3xl); color: var(--color-text-primary);">Hero / 30px</span>
          </div>
        </div>
      </div>
    `
  })
}

export const FontWeights: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">字重 Font Weight</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">4 级 weight + 3 种 scale 交叉演示</p>
        <div style="display: grid; grid-template-columns: 110px 1fr 1fr 1fr; gap: 1px; background: var(--color-border); border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--color-border);">
          <div style="padding: 12px 16px; background: var(--color-bg-elevated); font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);"></div>
          <div style="padding: 12px 16px; background: var(--color-bg-elevated); font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--text-sm (14)</div>
          <div style="padding: 12px 16px; background: var(--color-bg-elevated); font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--text-base (16)</div>
          <div style="padding: 12px 16px; background: var(--color-bg-elevated); font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--text-lg (18)</div>

          <div style="padding: 16px; background: var(--color-bg-card); font-size: 12px; color: var(--color-text-secondary);">normal · 400</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 400; font-size: var(--text-sm); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 400; font-size: var(--text-base); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 400; font-size: var(--text-lg); color: var(--color-text-primary);">The quick brown fox</div>

          <div style="padding: 16px; background: var(--color-bg-card); font-size: 12px; color: var(--color-text-secondary);">medium · 500</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 500; font-size: var(--text-sm); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 500; font-size: var(--text-base); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 500; font-size: var(--text-lg); color: var(--color-text-primary);">The quick brown fox</div>

          <div style="padding: 16px; background: var(--color-bg-card); font-size: 12px; color: var(--color-text-secondary);">semibold · 600</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 600; font-size: var(--text-sm); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 600; font-size: var(--text-base); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 600; font-size: var(--text-lg); color: var(--color-text-primary);">The quick brown fox</div>

          <div style="padding: 16px; background: var(--color-bg-card); font-size: 12px; color: var(--color-text-secondary);">bold · 700</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 700; font-size: var(--text-sm); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 700; font-size: var(--text-base); color: var(--color-text-primary);">The quick brown fox</div>
          <div style="padding: 16px; background: var(--color-bg-card); font-weight: 700; font-size: var(--text-lg); color: var(--color-text-primary);">The quick brown fox</div>
        </div>
      </div>
    `
  })
}

export const HeadingLevels: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">标题层级 Heading Levels</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">h1-h4 实际渲染 · 卡片背景对比</p>
        <div style="max-width: 720px; padding: 32px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
          <h1 style="font-size: var(--text-3xl); font-weight: 700; color: var(--color-text-primary); margin: 0 0 16px; line-height: var(--leading-tight);">H1 · 主标题 30/700</h1>
          <h2 style="font-size: var(--text-2xl); font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px; line-height: var(--leading-tight);">H2 · 区块标题 24/600</h2>
          <h3 style="font-size: var(--text-xl); font-weight: 600; color: var(--color-text-primary); margin: 0 0 8px; line-height: var(--leading-tight);">H3 · 子标题 20/600</h3>
          <h4 style="font-size: var(--text-lg); font-weight: 500; color: var(--color-text-primary); margin: 0 0 16px; line-height: var(--leading-tight);">H4 · 卡片标题 18/500</h4>
          <p style="font-size: var(--text-base); font-weight: 400; color: var(--color-text-secondary); margin: 0 0 12px; line-height: var(--leading-base);">正文段落 16/400 — 行高 1.5,适合长阅读,呼吸感舒服。</p>
          <p style="font-size: var(--text-sm); font-weight: 400; color: var(--color-text-muted); margin: 0; line-height: var(--leading-base);">辅助说明 14/400 — 元信息、时间戳、次要描述。</p>
        </div>
      </div>
    `
  })
}

export const LineHeights: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">行高 Line Height</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">4 个 leading token · 标题用 tight,正文用 base</p>
        <div style="display: flex; flex-direction: column; gap: 12px; max-width: 720px;">
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--leading-xs · 1.33</code>
            <p style="font-size: var(--text-base); line-height: var(--leading-xs); color: var(--color-text-primary); margin: 8px 0 0;">紧凑行高 — 标题、列表、卡片信息密度高。<br/>适合短文本,长段落会显得挤。</p>
          </div>
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--leading-sm · 1.43</code>
            <p style="font-size: var(--text-base); line-height: var(--leading-sm); color: var(--color-text-primary); margin: 8px 0 0;">小行高 — 副标题、表格内文。<br/>在 UI 密集区使用,平衡密度与可读性。</p>
          </div>
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--leading-base · 1.5</code>
            <p style="font-size: var(--text-base); line-height: var(--leading-base); color: var(--color-text-primary); margin: 8px 0 0;">基础行高 — 默认正文。<br/>单行间距舒适,长段落不疲劳,行业标准值。</p>
          </div>
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">--leading-lg · 1.6</code>
            <p style="font-size: var(--text-base); line-height: var(--leading-lg); color: var(--color-text-primary); margin: 8px 0 0;">宽松行高 — 文章、长博客、说明文档。<br/>呼吸感强,适合沉浸式阅读,但会占更多垂直空间。</p>
          </div>
        </div>
      </div>
    `
  })
}
