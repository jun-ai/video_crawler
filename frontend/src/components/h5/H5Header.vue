<!--
  H5Header — Phase 22: H5 顶部 header
  替换 App.vue 桌面 header 在移动端的显示

  设计原则:
  - 白底 + 极薄底部边框 (1px) 收口
  - 左侧 Logo+品牌文字, 中部可选 title 插槽, 右侧操作
  - 高度: 56px + env(safe-area-inset-top) (iOS 刘海)
  - sticky top-0 + z-[1000] + backdrop-blur (SpeakVlog 毛玻璃)
-->
<template>
  <header class="h5-header">
    <div class="h5-header-inner">
      <!-- 左: 返回箭头 (showBack 时) -->
      <button v-if="showBack" class="h5-header-btn" aria-label="返回" @click="onBack">
        <ArrowLeft :size="22" />
      </button>

      <!-- 左: 抽屉入口 (showMenu=true 时) -->
      <button v-else-if="showMenu" class="h5-header-btn" aria-label="菜单" @click="$emit('menu')">
        <Menu :size="22" />
      </button>

      <!-- 中: Logo + 品牌 (默认,被 flex:1 撑开;showBack/showMenu=false 时居左) -->
      <div v-if="!showBack && !title && $slots.default === undefined" class="h5-header-brand" @click="goHome">
        <div class="h5-header-logo">
          <GraduationCap :size="18" :stroke-width="2.4" />
        </div>
        <span class="h5-header-brand-text">Linyu</span>
      </div>

      <!-- 中: 标题 (有 title 或 default slot 时优先) -->
      <div v-if="title || $slots.default" class="h5-header-title">
        <slot>{{ title }}</slot>
      </div>

      <!-- 右: 右侧操作插槽 + 历史/筛选 icon -->
      <div class="h5-header-actions">
        <slot name="actions" />
        <!-- Phase 24 P0: 登录 + 会员 CTA (speakvlog 范式), 已登录态隐藏 -->
        <template v-if="!isLoggedIn">
          <button class="h5-header-cta h5-header-cta--ghost" aria-label="登录" @click="$router.push('/login')">登录</button>
          <button class="h5-header-cta h5-header-cta--primary" aria-label="会员" @click="$router.push('/pricing')">会员</button>
        </template>
        <button v-if="showFilter" class="h5-header-btn" aria-label="历史" @click="$emit('filter')">
          <Clock :size="20" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ArrowLeft, GraduationCap, Menu, Clock } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'

const router = useRouter()

const props = defineProps({
  title: { type: String, default: '' },
  showBack: { type: Boolean, default: false },
  showMenu: { type: Boolean, default: true },
  showFilter: { type: Boolean, default: true },
})

const emit = defineEmits(['back', 'menu', 'filter'])

// Phase 24 P0: 登录态判断 (简单从 localStorage 读 token, 不依赖 user store 避免循环)
const isLoggedIn = ref(false)
onMounted(() => {
  try { isLoggedIn.value = !!localStorage.getItem('token') } catch {}
})

function onBack() {
  emit('back')
  if (window.history.length > 1) router.back()
  else router.push('/')
}

function goHome() {
  router.push('/')
}
</script>

<style scoped>
.h5-header {
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(12px);
  -webkit-backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  padding-top: env(safe-area-inset-top, 0);
}

.h5-header-inner {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 56px;
  padding: 0 16px;
  max-width: 720px;
  margin: 0 auto;
}

.h5-header-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  border: none;
  background: transparent;
  color: var(--color-text-primary, #0F172A);
  cursor: pointer;
  transition: background 120ms ease;
}
.h5-header-btn:active { background: rgba(15, 23, 42, 0.06); }

.h5-header-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  flex: 1;          /* 撑开中间,让右侧 🕐 推到最右 */
  min-width: 0;
}

.h5-header-logo {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background: linear-gradient(135deg, #4DA06C 0%, var(--color-brand) 100%);
  box-shadow: 0 1px 2px rgba(47, 61, 53, 0.25);
}

.h5-header-brand-text {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--color-text-primary, #0F172A);
}

.h5-header-title {
  flex: 1;
  min-width: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary, #0F172A);
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.h5-header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* Phase 24 P0: 登录 + 会员 CTA pill */
.h5-header-cta {
  font-size: 13px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 9999px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 120ms ease;
  white-space: nowrap;
  line-height: 1.2;
}
.h5-header-cta:active { transform: scale(0.97); }
.h5-header-cta--ghost {
  background: transparent;
  color: var(--color-text-primary);
  border-color: rgba(15, 23, 42, 0.12);
}
.h5-header-cta--ghost:hover { border-color: var(--color-brand); color: var(--color-brand); }
.h5-header-cta--primary {
  background: var(--color-brand);
  color: #fff;
  border-color: var(--color-brand);
}
.h5-header-cta--primary:hover { background: var(--color-brand-hover); border-color: var(--color-brand-hover); }
</style>
