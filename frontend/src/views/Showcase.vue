<template>
  <div class="showcase">
    <PageHeader
      title="Sf* 组件展示"
      description="Fluenty 前端设计系统 · 所有 UI 组件的可视化参考(P3 阶段)"
    />

    <!-- 主题切换 -->
    <div class="theme-toggle">
      <SfButton :type="isDark ? 'primary' : 'default'" size="sm" @click="toggleTheme">
        <Sun v-if="isDark" :size="14" />
        <Moon v-else :size="14" />
        {{ isDark ? '切换浅色' : '切换暗色' }}
      </SfButton>
    </div>

    <!-- ========== Buttons ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Buttons · 按钮层级</h2>
      <p class="section-desc">5 种类型 × 3 种尺寸。规则:一个页面最多 1 个 primary。</p>

      <div class="demo-row">
        <SfButton type="primary">主操作 Primary</SfButton>
        <SfButton type="default">次操作 Default</SfButton>
        <SfButton type="ghost">弱化 Ghost</SfButton>
        <SfButton type="subtle">更弱 Subtle</SfButton>
        <SfButton type="danger">危险 Danger</SfButton>
      </div>

      <div class="demo-row">
        <SfButton type="primary" :loading="true">加载中</SfButton>
        <SfButton type="primary" disabled>禁用</SfButton>
        <SfButton type="primary" round>圆角</SfButton>
        <SfButton type="primary" block>Block 按钮</SfButton>
      </div>

      <div class="demo-row">
        <SfButton type="primary" size="sm">小</SfButton>
        <SfButton type="primary" size="md">中</SfButton>
        <SfButton type="primary" size="lg">大</SfButton>
      </div>

      <div class="demo-row">
        <SfButton type="primary">
          <Plus :size="14" />新建
        </SfButton>
        <SfButton type="default">
          <Download :size="14" />导出
        </SfButton>
        <SfButton type="danger">
          <Trash2 :size="14" />删除
        </SfButton>
      </div>
    </section>

    <!-- ========== Form ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Form · 表单</h2>

      <div class="demo-form">
        <SfForm @submit="onSubmit">
          <SfFormItem label="用户名" required>
            <SfInput v-model="form.username" placeholder="请输入用户名" />
          </SfFormItem>
          <SfFormItem label="邮箱" required :error="form.emailError">
            <SfInput v-model="form.email" type="email" placeholder="user@example.com" />
          </SfFormItem>
          <SfFormItem label="简介">
            <SfInput v-model="form.bio" textarea :rows="3" placeholder="一句话介绍自己" />
          </SfFormItem>
          <SfFormItem label="难度" required>
            <SfSelect
              v-model="form.level"
              :options="[
                { value: 'easy', label: '简单' },
                { value: 'medium', label: '中等' },
                { value: 'hard', label: '困难' }
              ]"
              placeholder="选择难度"
            />
          </SfFormItem>
          <SfFormItem label="记住我">
            <SfSwitch v-model="form.remember" />
          </SfFormItem>
          <SfFormItem>
            <SfButton type="primary" html-type="submit">提交</SfButton>
            <SfButton type="ghost" @click="resetForm">重置</SfButton>
          </SfFormItem>
        </SfForm>
      </div>
    </section>

    <!-- ========== Tags / Badges ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Tags · 标签</h2>
      <div class="demo-row">
        <SfTag>默认</SfTag>
        <SfTag type="primary">主</SfTag>
        <SfTag type="success">成功</SfTag>
        <SfTag type="warning">警告</SfTag>
        <SfTag type="danger">危险</SfTag>
        <SfTag type="info">信息</SfTag>
      </div>
    </section>

    <!-- ========== Loading / Feedback ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Loading & Feedback · 加载与反馈</h2>
      <div class="demo-row">
        <SfSpinner :size="16" />
        <SfSpinner :size="24" />
        <SfSpinner :size="32" />
        <SfButton type="primary" @click="showToast('success')">成功 Toast</SfButton>
        <SfButton type="default" @click="showToast('error')">错误 Toast</SfButton>
        <SfButton type="default" @click="showToast('info')">信息 Toast</SfButton>
      </div>
    </section>

    <!-- ========== Empty State ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Empty State · 空状态</h2>
      <div class="demo-empty">
        <SfEmpty title="暂无数据" description="还没有任何内容,先新建一个吧" />
      </div>
    </section>

    <!-- ========== Progress ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Progress · 进度条</h2>
      <div class="demo-stack">
        <SfProgress :value="20" />
        <SfProgress :value="50" status="primary" />
        <SfProgress :value="80" status="success" />
        <SfProgress :value="100" status="success" />
      </div>
    </section>

    <!-- ========== Colors · 调色板 ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Color Palette · 调色板</h2>
      <p class="section-desc">所有 --sf-* 颜色变量可视化</p>

      <div class="palette-group">
        <h3>Brand</h3>
        <div class="palette-row">
          <div class="swatch" style="background: var(--sf-brand);">brand</div>
          <div class="swatch" style="background: var(--sf-brand-hover);">hover</div>
          <div class="swatch" style="background: var(--sf-brand-light);">light</div>
          <div class="swatch" style="background: var(--sf-brand-subtle);">subtle</div>
        </div>
      </div>

      <div class="palette-group">
        <h3>Status</h3>
        <div class="palette-row">
          <div class="swatch" style="background: var(--sf-success);">success</div>
          <div class="swatch" style="background: var(--sf-warning);">warning</div>
          <div class="swatch" style="background: var(--sf-danger);">danger</div>
          <div class="swatch" style="background: var(--sf-info);">info</div>
          <div class="swatch" style="background: var(--sf-accent);">accent</div>
        </div>
      </div>

      <div class="palette-group">
        <h3>Text</h3>
        <div class="palette-row">
          <div class="swatch outline" style="color: var(--sf-text-primary); background: var(--sf-bg-card);">primary</div>
          <div class="swatch outline" style="color: var(--sf-text-secondary); background: var(--sf-bg-card);">secondary</div>
          <div class="swatch outline" style="color: var(--sf-text-muted); background: var(--sf-bg-card);">muted</div>
        </div>
      </div>

      <div class="palette-group">
        <h3>Admin (独立主题)</h3>
        <div class="palette-row">
          <div class="swatch" style="background: var(--sf-admin-bg); color: var(--sf-admin-text-secondary);">admin-bg</div>
          <div class="swatch" style="background: var(--sf-admin-bg-card); color: var(--sf-admin-text-secondary);">admin-card</div>
          <div class="swatch" style="background: var(--sf-admin-bg-hover);">admin-hover</div>
          <div class="swatch" style="background: var(--sf-admin-bg-active);">admin-active</div>
          <div class="swatch" style="background: var(--sf-admin-accent);">admin-accent</div>
        </div>
      </div>
    </section>

    <!-- ========== Spacing & Radius ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Spacing & Radius · 间距和圆角</h2>
      <p class="section-desc">4px 网格化间距 + 6/10/14/20 圆角</p>

      <div class="demo-stack">
        <div class="spacing-demo" v-for="n in [1, 2, 3, 4, 5, 6, 8, 10]" :key="`sp${n}`">
          <span class="spacing-label">--sf-space-{{ n }} ({{ n * 4 }}px)</span>
          <div class="spacing-bar" :style="{ width: `${n * 4}px`, height: '16px', background: 'var(--sf-brand)' }"></div>
        </div>
      </div>

      <div class="demo-row" style="margin-top: 24px;">
        <div class="radius-box" style="border-radius: var(--sf-radius-sm);">sm 6px</div>
        <div class="radius-box" style="border-radius: var(--sf-radius-md);">md 10px</div>
        <div class="radius-box" style="border-radius: var(--sf-radius-lg);">lg 14px</div>
        <div class="radius-box" style="border-radius: var(--sf-radius-xl);">xl 20px</div>
        <div class="radius-box" style="border-radius: var(--sf-radius-full);">full 9999px</div>
      </div>
    </section>

    <!-- ========== Animation ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Animation · 动画时长</h2>
      <p class="section-desc">fast 150ms · normal 200ms · slow 300ms</p>
      <div class="demo-row">
        <SfButton type="primary" class="anim-fast">fast 150ms</SfButton>
        <SfButton type="primary" class="anim-normal">normal 200ms</SfButton>
        <SfButton type="primary" class="anim-slow">slow 300ms</SfButton>
      </div>
    </section>

    <!-- ========== Icon Set ========== -->
    <section class="showcase-section">
      <h2 class="section-title">Icon Set · 图标库</h2>
      <p class="section-desc">lucide-vue-next · 常用图标一览</p>
      <div class="icon-grid">
        <div class="icon-cell" v-for="icon in demoIcons" :key="icon.name">
          <component :is="icon.comp" :size="20" />
          <span class="icon-name">{{ icon.name }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  Sun, Moon, Plus, Download, Trash2,
  BookOpen, Target, Lightbulb, Bookmark, Star, Heart,
  Play, Pause, Video, Headphones, Mic, Camera,
  BarChart3, TrendingUp, Trophy, Crown, Flame,
  Sparkles, Wand2, GraduationCap, Library,
  Check, X, AlertCircle, Info,
  ChevronLeft, ChevronRight, ArrowLeft, ArrowRight,
  Edit, Settings, Search, Filter, MoreHorizontal
} from 'lucide-vue-next'
import PageHeader from '@/components/common/PageHeader.vue'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfSpinner from '@/components/ui/SfSpinner.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'
import SfProgress from '@/components/ui/SfProgress.vue'
import SfSwitch from '@/components/ui/SfSwitch.vue'
import { toast } from '@/composables/useToast'

const isDark = ref(false)

const form = reactive({
  username: '',
  email: '',
  emailError: '',
  bio: '',
  level: '',
  remember: false
})

function onSubmit() {
  if (!form.username) {
    form.emailError = ''
    toast.error('请输入用户名')
    return
  }
  if (!form.email.includes('@')) {
    form.emailError = '邮箱格式不正确'
    return
  }
  form.emailError = ''
  toast.success('提交成功')
}

function resetForm() {
  form.username = ''
  form.email = ''
  form.bio = ''
  form.level = ''
  form.remember = false
  form.emailError = ''
}

function showToast(type) {
  if (type === 'success') toast.success('操作成功')
  else if (type === 'error') toast.error('操作失败')
  else toast.info('这是一条提示信息')
}

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

onMounted(() => {
  isDark.value = document.documentElement.classList.contains('dark')
})

const demoIcons = [
  { name: 'BookOpen', comp: BookOpen },
  { name: 'Target', comp: Target },
  { name: 'Lightbulb', comp: Lightbulb },
  { name: 'Bookmark', comp: Bookmark },
  { name: 'Star', comp: Star },
  { name: 'Heart', comp: Heart },
  { name: 'Play', comp: Play },
  { name: 'Pause', comp: Pause },
  { name: 'Video', comp: Video },
  { name: 'Headphones', comp: Headphones },
  { name: 'Mic', comp: Mic },
  { name: 'Camera', comp: Camera },
  { name: 'BarChart3', comp: BarChart3 },
  { name: 'TrendingUp', comp: TrendingUp },
  { name: 'Trophy', comp: Trophy },
  { name: 'Crown', comp: Crown },
  { name: 'Flame', comp: Flame },
  { name: 'Sparkles', comp: Sparkles },
  { name: 'Wand2', comp: Wand2 },
  { name: 'GraduationCap', comp: GraduationCap },
  { name: 'Library', comp: Library },
  { name: 'Check', comp: Check },
  { name: 'X', comp: X },
  { name: 'AlertCircle', comp: AlertCircle },
  { name: 'Info', comp: Info },
  { name: 'ChevronLeft', comp: ChevronLeft },
  { name: 'ChevronRight', comp: ChevronRight },
  { name: 'ArrowLeft', comp: ArrowLeft },
  { name: 'ArrowRight', comp: ArrowRight },
  { name: 'Edit', comp: Edit },
  { name: 'Settings', comp: Settings },
  { name: 'Search', comp: Search },
  { name: 'Filter', comp: Filter },
  { name: 'MoreHorizontal', comp: MoreHorizontal }
]
</script>

<style scoped>
.showcase {
  max-width: 1100px;
  margin: 0 auto;
  padding: var(--sf-space-6) var(--sf-space-4) calc(var(--sf-space-16) + 80px);
}

.theme-toggle {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 100;
}

.showcase-section {
  background: var(--sf-bg-card);
  border: 1px solid var(--sf-border);
  border-radius: var(--sf-radius-lg);
  padding: var(--sf-space-6);
  margin-bottom: var(--sf-space-6);
}

.section-title {
  margin: 0 0 var(--sf-space-2);
  font-size: 20px;
  font-weight: 700;
  color: var(--sf-text-primary);
  letter-spacing: -0.3px;
}

.section-desc {
  margin: 0 0 var(--sf-space-5);
  font-size: 13px;
  color: var(--sf-text-muted);
}

.demo-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--sf-space-3);
  margin-bottom: var(--sf-space-3);
}

.demo-form {
  max-width: 480px;
}

.demo-empty {
  max-width: 360px;
  margin: 0 auto;
}

.demo-stack {
  display: flex;
  flex-direction: column;
  gap: var(--sf-space-3);
}

/* ========== 调色板 ========== */
.palette-group {
  margin-bottom: var(--sf-space-4);
}

.palette-group h3 {
  margin: 0 0 var(--sf-space-2);
  font-size: 13px;
  font-weight: 600;
  color: var(--sf-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.palette-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sf-space-2);
}

.swatch {
  height: 64px;
  min-width: 96px;
  padding: var(--sf-space-2) var(--sf-space-3);
  display: flex;
  align-items: flex-end;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  border-radius: var(--sf-radius-md);
  text-transform: lowercase;
  font-family: var(--font-mono, monospace);
}

.swatch.outline {
  border: 1px solid var(--sf-border);
}

/* ========== 间距 / 圆角演示 ========== */
.spacing-demo {
  display: flex;
  align-items: center;
  gap: var(--sf-space-3);
}

.spacing-label {
  font-size: 12px;
  color: var(--sf-text-secondary);
  font-family: var(--font-mono, monospace);
  min-width: 160px;
}

.radius-box {
  height: 80px;
  min-width: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--sf-brand-subtle);
  color: var(--sf-brand);
  font-size: 12px;
  font-weight: 600;
  border: 1px solid var(--sf-brand);
}

/* ========== 动画演示 ========== */
.anim-fast { transition: all var(--sf-duration-fast) var(--sf-ease-standard); }
.anim-normal { transition: all var(--sf-duration-normal) var(--sf-ease-standard); }
.anim-slow { transition: all var(--sf-duration-slow) var(--sf-ease-bounce); }

.anim-fast:hover { transform: translateY(-2px); }
.anim-normal:hover { transform: translateY(-4px); }
.anim-slow:hover { transform: translateY(-6px) scale(1.05); }

/* ========== 图标网格 ========== */
.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: var(--sf-space-2);
}

.icon-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sf-space-1);
  padding: var(--sf-space-3) var(--sf-space-2);
  border: 1px solid var(--sf-border);
  border-radius: var(--sf-radius-md);
  background: var(--sf-bg);
  color: var(--sf-text-secondary);
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
}

.icon-cell:hover {
  border-color: var(--sf-brand);
  color: var(--sf-brand);
  background: var(--sf-brand-subtle);
}

.icon-name {
  font-size: 11px;
  font-family: var(--font-mono, monospace);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
</style>
