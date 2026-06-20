import type { Meta, StoryObj } from '@storybook/vue3'
import SfButton from '../components/ui/SfButton.vue'
import SfInput from '../components/ui/SfInput.vue'
import SfTag from '../components/ui/SfTag.vue'

const meta = {
  title: 'Design Tokens/DarkMode',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    backgrounds: { disable: true },
    docs: {
      description: {
        component: '暗色主题 — 所有 token 自动响应 .dark class。顶部有工具栏可切换主题。'
      }
    }
  }
} satisfies Meta

export default meta
type Story = StoryObj<typeof meta>

/**
 * 用普通 token 演示,值会随当前主题自动变化
 */
const tokenRow = (label: string, varName: string, note: string) => `
  <div style="display: flex; align-items: center; gap: 16px; padding: 12px 16px; background: var(--color-bg-card); border-radius: var(--radius-md); border: 1px solid var(--color-border);">
    <div style="width: 36px; height: 36px; border-radius: var(--radius-sm); background: var(${varName}); border: 1px solid var(--color-border); flex-shrink: 0;"></div>
    <div style="flex: 1; min-width: 0;">
      <code style="font-size: 11px; color: var(--color-text-primary); font-family: var(--font-mono); font-weight: 600;">${varName}</code>
      <div style="font-size: 11px; color: var(--color-text-muted); margin-top: 2px;">${note}</div>
    </div>
    <span style="font-size: 12px; color: var(--color-text-secondary);">${label}</span>
  </div>
`

export const ColorComparison: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <div style="padding: 16px 20px; background: var(--color-accent-subtle); border: 1px solid var(--color-accent); border-radius: var(--radius-md); margin-bottom: 24px; color: var(--color-text-primary);">
          <strong>💡 切换到 dark 主题</strong>
          <p style="margin: 4px 0 0; font-size: 13px; color: var(--color-text-secondary);">工具栏(顶部)找到画笔图标选择 Dark 主题,所有 token 值会自动变化</p>
        </div>

        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">Token 主题对比</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">所有 token 自动响应主题 · 切换查看差异</p>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 960px;">
          ${tokenRow('品牌主色', '--color-brand', '亮色: #2563EB / 暗色: #60A5FA')}
          ${tokenRow('品牌 hover', '--color-brand-hover', '加深一档')}
          ${tokenRow('品牌浅色', '--color-brand-light', 'rgba 半透明 · 暗色更亮')}
          ${tokenRow('强调色', '--color-accent', '琥珀金')}
          ${tokenRow('主文字', '--color-text-primary', '亮: 深石板 / 暗: 浅灰')}
          ${tokenRow('次文字', '--color-text-secondary', '辅助描述')}
          ${tokenRow('弱化文字', '--color-text-muted', '时间戳/元信息')}
          ${tokenRow('页面底色', '--color-bg-base', '整页背景')}
          ${tokenRow('卡片底色', '--color-bg-card', '所有卡片/弹窗')}
          ${tokenRow('悬浮层', '--color-bg-elevated', '下拉/Tag/二级面板')}
          ${tokenRow('常规边框', '--color-border', '亮: 实色 / 暗: 半透明白')}
          ${tokenRow('加强边框', '--color-border-strong', 'focus 状态')}
        </div>
      </div>
    `
  })
}

export const ComponentShowcase: Story = {
  render: () => ({
    components: { SfButton, SfInput, SfTag },
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <div style="padding: 16px 20px; background: var(--color-accent-subtle); border: 1px solid var(--color-accent); border-radius: var(--radius-md); margin-bottom: 24px; color: var(--color-text-primary);">
          <strong>💡 切换到 dark 主题</strong>
          <p style="margin: 4px 0 0; font-size: 13px; color: var(--color-text-secondary);">所有 SfButton / SfInput / SfTag 会自动适配暗色背景</p>
        </div>

        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">组件暗色表现</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">SfButton × SfInput × SfTag 组合演示</p>

        <div style="max-width: 720px; padding: 32px; background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid var(--color-border); box-shadow: var(--shadow-md);">
          <!-- 标题 -->
          <h3 style="font-size: 18px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">新建学习任务</h3>
          <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 20px;">为这个视频添加学习目标</p>

          <!-- 表单 -->
          <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px;">
            <div>
              <label style="display: block; font-size: 13px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 6px;">视频名称</label>
              <SfInput placeholder="TED: 30 秒讲清楚一个观点" />
            </div>
            <div>
              <label style="display: block; font-size: 13px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 6px;">学习目标</label>
              <SfInput placeholder="掌握演讲开场 3 公式" />
            </div>
          </div>

          <!-- Tag 选择 -->
          <div style="margin-bottom: 20px;">
            <label style="display: block; font-size: 13px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 8px;">标签</label>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <SfTag type="brand">口语</SfTag>
              <SfTag type="success">商务</SfTag>
              <SfTag type="warning">雅思 7.0</SfTag>
              <SfTag type="danger">高级</SfTag>
              <SfTag>日常</SfTag>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div style="display: flex; gap: 8px; justify-content: flex-end; padding-top: 16px; border-top: 1px solid var(--color-border);">
            <SfButton type="default">取消</SfButton>
            <SfButton type="primary">保存任务</SfButton>
          </div>
        </div>

        <!-- 颜色方块 -->
        <div style="margin-top: 32px; display: flex; flex-wrap: wrap; gap: 12px;">
          <div style="padding: 12px 16px; background: var(--color-brand-subtle); color: var(--color-brand); border-radius: var(--radius-md); font-size: 13px; font-weight: 500;">品牌底色 + 品牌文字</div>
          <div style="padding: 12px 16px; background: var(--color-success-light); color: var(--color-success); border-radius: var(--radius-md); font-size: 13px; font-weight: 500;">成功底 + 成功字</div>
          <div style="padding: 12px 16px; background: var(--color-warning-light); color: var(--color-warning); border-radius: var(--radius-md); font-size: 13px; font-weight: 500;">警告底 + 警告字</div>
          <div style="padding: 12px 16px; background: var(--color-danger-light); color: var(--color-danger); border-radius: var(--radius-md); font-size: 13px; font-weight: 500;">错误底 + 错误字</div>
        </div>
      </div>
    `
  })
}

export const SemanticMigration: Story = {
  render: () => ({
    template: `
      <div style="padding: 32px; background: var(--color-bg-base); min-height: 100vh;">
        <div style="padding: 16px 20px; background: var(--color-accent-subtle); border: 1px solid var(--color-accent); border-radius: var(--radius-md); margin-bottom: 24px; color: var(--color-text-primary);">
          <strong>💡 切换到 dark 主题</strong>
          <p style="margin: 4px 0 0; font-size: 13px; color: var(--color-text-secondary);">标注/难度/状态色 全部响应主题 · 不写死 hex</p>
        </div>

        <h2 style="font-size: 24px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 4px;">语义色迁移</h2>
        <p style="font-size: 13px; color: var(--color-text-secondary); margin: 0 0 24px;">标注 / 难度 / 状态 token · 暗色下全部自动反相</p>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 960px;">
          <!-- 标注色 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
            <h3 style="font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px;">字幕标注 Annotation</h3>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <div style="padding: 10px 12px; background: var(--color-bg-elevated); border-left: 3px solid var(--color-annotation-vocabulary); border-radius: var(--radius-sm); font-size: 13px; color: var(--color-annotation-vocabulary);">vocabulary · 词汇</div>
              <div style="padding: 10px 12px; background: var(--color-bg-elevated); border-left: 3px solid var(--color-annotation-phrase); border-radius: var(--radius-sm); font-size: 13px; color: var(--color-annotation-phrase);">phrase · 词伙</div>
              <div style="padding: 10px 12px; background: var(--color-bg-elevated); border-left: 3px solid var(--color-annotation-important); border-radius: var(--radius-sm); font-size: 13px; color: var(--color-annotation-important);">important · 重点</div>
            </div>
          </div>

          <!-- 难度色 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
            <h3 style="font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px;">难度 Difficulty</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <span style="padding: 4px 12px; background: var(--color-diff-easy-bg); color: var(--color-diff-easy-text); border-radius: var(--sf-radius-full); font-size: 12px; font-weight: 500;">入门 L1</span>
              <span style="padding: 4px 12px; background: var(--color-diff-medium-bg); color: var(--color-diff-medium-text); border-radius: var(--sf-radius-full); font-size: 12px; font-weight: 500;">中级 L3</span>
              <span style="padding: 4px 12px; background: var(--color-diff-hard-bg); color: var(--color-diff-hard-text); border-radius: var(--sf-radius-full); font-size: 12px; font-weight: 500;">高级 L5</span>
            </div>
          </div>

          <!-- 状态色 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
            <h3 style="font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px;">状态 Status</h3>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--color-success-light); color: var(--color-success); border-radius: var(--radius-sm); font-size: 13px;">✓ 已保存到我的语料库</div>
              <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--color-warning-light); color: var(--color-warning); border-radius: var(--radius-sm); font-size: 13px;">⚠ 还有 3 个单词没复习</div>
              <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--color-danger-light); color: var(--color-danger); border-radius: var(--radius-sm); font-size: 13px;">✗ 网络连接失败</div>
              <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--color-info-light); color: var(--color-info); border-radius: var(--radius-sm); font-size: 13px;">ⓘ 新版本已发布</div>
            </div>
          </div>

          <!-- 渐变 -->
          <div style="padding: 20px; background: var(--color-bg-card); border-radius: var(--radius-lg); border: 1px solid var(--color-border);">
            <h3 style="font-size: 14px; font-weight: 600; color: var(--color-text-primary); margin: 0 0 12px;">渐变 Gradient</h3>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <div style="height: 40px; background: var(--sf-brand-gradient, linear-gradient(135deg, #2563EB 0%, #3B82F6 50%, #F59E0B 100%)); border-radius: var(--radius-md); display: flex; align-items: center; padding: 0 12px; color: #fff; font-size: 12px; font-weight: 600;">--sf-brand-gradient</div>
              <div style="height: 40px; background: var(--sf-cta-gradient, linear-gradient(#3B82F6 0%, #2563EB 100%)); border-radius: var(--radius-md); display: flex; align-items: center; padding: 0 12px; color: #fff; font-size: 12px; font-weight: 600;">--sf-cta-gradient</div>
              <div style="height: 40px; background: var(--sf-bg-gradient, linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 25%, #F8FAFC 100%)); border-radius: var(--radius-md); border: 1px solid var(--color-border); display: flex; align-items: center; padding: 0 12px; color: var(--color-text-secondary); font-size: 12px; font-weight: 600;">--sf-bg-gradient</div>
            </div>
          </div>
        </div>
      </div>
    `
  })
}
