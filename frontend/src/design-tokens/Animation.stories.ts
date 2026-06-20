import type { Meta, StoryObj } from '@storybook/vue3'

const meta = {
  title: 'Design Tokens/Animation',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: '动画系统 — 时长 / 缓动 / 关键帧。@keyframes 已注册到全局。'
      }
    }
  }
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

/**
 * 用一个方块做 scale 循环动画,演示不同 duration
 */
const animBox = (label: string, durVar: string, easeVar: string) => `
  <div style="display: flex; flex-direction: column; align-items: center; gap: 12px; min-width: 140px;">
    <div
      style="
        width: 64px;
        height: 64px;
        background: var(--sf-brand-gradient, var(--color-brand));
        border-radius: var(--radius-md);
        animation: scale-pulse 2s var(${easeVar}) infinite;
        animation-duration: var(${durVar});
      "
    ></div>
    <code style="font-size: 11px; color: var(--color-text-primary); font-family: var(--font-mono); font-weight: 600;">${label}</code>
  </div>
`

/**
 * Storybook 内联 @keyframes,避免依赖全局注册
 */
const keyframes = `
<style>
@keyframes scale-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}
@keyframes fade-slide-up-demo {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.anim-demo-card {
  animation: fade-slide-up-demo 2s var(--sf-ease-standard) infinite alternate;
}
</style>
`

export const Durations: Story = {
  render: () => ({
    template: `
      ${keyframes}
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">动画时长 Durations</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">4 档 · fast (0.15s) / normal (0.2s) / slow (0.3s) / slower (0.5s)</p>
        <div style="display: flex; flex-wrap: wrap; gap: 32px; padding: 24px; background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
          ${animBox('--sf-duration-fast', '--sf-duration-fast', '--sf-ease-standard')}
          ${animBox('--sf-duration-normal', '--sf-duration-normal', '--sf-ease-standard')}
          ${animBox('--sf-duration-slow', '--sf-duration-slow', '--sf-ease-standard')}
          ${animBox('--sf-duration-slower', '--sf-duration-slower', '--sf-ease-standard')}
        </div>
        <p style="font-size: 12px; color: var(--color-text-muted); margin: 16px 0 0;">方块在 scale(1) ↔ scale(1.15) 之间循环,周期 2s,变化用对应 duration 缓动</p>
      </div>
    `
  })
}

export const Easings: Story = {
  render: () => ({
    template: `
      ${keyframes}
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">缓动曲线 Easings</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">standard · bounce · linear · 3 种 timing 对比</p>
        <div style="display: flex; flex-wrap: wrap; gap: 32px; padding: 24px; background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
          ${animBox('--sf-ease-standard', '--sf-duration-slow', '--sf-ease-standard')}
          ${animBox('--sf-ease-bounce', '--sf-duration-slow', '--sf-ease-bounce')}
        </div>
        <p style="font-size: 12px; color: var(--color-text-muted); margin: 16px 0 0;">bounce 弹性更明显,适合按钮按下/卡片出现等带反馈的微交互</p>
      </div>
    `
  })
}

export const PresetAnimations: Story = {
  render: () => ({
    template: `
      ${keyframes}
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">预设动画 Presets</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">全局注册的 animation 工具类</p>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
          <div class="anim-demo-card" style="padding: 24px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border); text-align: center;">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">fade-slide-up</code>
            <div style="font-size: 14px; color: var(--color-text-primary); margin-top: 6px;">入场淡入上移</div>
          </div>
          <div style="padding: 24px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border); text-align: center;">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">pulse-subtle</code>
            <div style="font-size: 14px; color: var(--color-text-primary); margin-top: 6px; animation: pulse-subtle 2s var(--ease-standard) infinite;">呼吸效果</div>
          </div>
          <div style="padding: 24px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border); text-align: center;">
            <code style="font-size: 11px; color: var(--color-text-muted); font-family: var(--font-mono);">spin</code>
            <div style="margin-top: 8px; display: inline-block; animation: spin 1.5s linear infinite; color: var(--color-brand); font-size: 20px;">⟳</div>
            <div style="font-size: 13px; color: var(--color-text-primary); margin-top: 4px;">Loading 旋转</div>
          </div>
        </div>
      </div>
    `
  })
}

export const StaggerDemo: Story = {
  render: () => ({
    template: `
      ${keyframes}
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">交错动画 Stagger</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">列表项依次进入 · 50ms 间隔</p>
        <div class="stagger-enter" style="display: flex; flex-direction: column; gap: 8px; max-width: 480px;">
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">1. 加载语料库</div>
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">2. 解析字幕</div>
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">3. 提取词伙</div>
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">4. 生成题目</div>
          <div style="padding: 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">5. 准备就绪</div>
        </div>
        <p style="font-size: 12px; color: var(--color-text-muted); margin: 16px 0 0;">刷新页面看依次出现效果</p>
      </div>
    `
  })
}
