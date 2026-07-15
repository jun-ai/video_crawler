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
      <!-- 左: 返回箭头 (可选) -->
      <button v-if="showBack" class="h5-header-btn" aria-label="返回" @click="onBack">
        <ArrowLeft :size="22" />
      </button>

      <!-- 左: Logo + 品牌 (无标题时显示) -->
      <div v-else class="h5-header-brand" @click="goHome">
        <div class="h5-header-logo">
          <GraduationCap :size="18" :stroke-width="2.4" />
        </div>
        <span class="h5-header-brand-text">fluenty</span>
      </div>

      <!-- 中: 标题 (可覆盖) -->
      <div v-if="title || $slots.default" class="h5-header-title">
        <slot>{{ title }}</slot>
      </div>

      <!-- 右: 右侧操作插槽 -->
      <div class="h5-header-actions">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<script setup>
import { ArrowLeft, GraduationCap } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, default: '' },
  showBack: { type: Boolean, default: false },
})

const emit = defineEmits(['back'])
const router = useRouter()

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
}

.h5-header-logo {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background: linear-gradient(135deg, #4DA06C 0%, #0F4C3A 100%);
  box-shadow: 0 1px 2px rgba(15, 76, 58, 0.25);
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
  gap: 4px;
  flex-shrink: 0;
}
</style>
