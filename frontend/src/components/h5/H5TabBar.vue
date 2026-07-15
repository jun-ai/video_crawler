<!--
  H5TabBar — Phase 22: H5 底部 4-tab 导航
  替换 App.vue mobile-tab-bar (原 3-tab), 升级为 4-tab (首页/学习/卡片/我的)

  设计原则:
  - 4 个入口, 等分宽度, 居中图标 + 文字
  - 激活态: 文字加粗 + 蓝色 + 顶部小蓝点 (SpeakVlog 视觉签名)
  - 默认隐藏 (桌面), 通过父容器 CSS @media 控制
  - 高度: 56px + iOS safe-area bottom padding
-->
<template>
  <nav class="h5-tab-bar" aria-label="主导航">
    <div
      v-for="item in items"
      :key="item.path"
      :class="['h5-tab-item', { 'is-active': isActive(item.path) }]"
      @click="onClick(item)"
    >
      <span class="h5-tab-indicator" v-if="isActive(item.path)" />
      <component
        :is="item.icon"
        :size="22"
        :stroke-width="isActive(item.path) ? 2.4 : 1.8"
      />
      <span class="h5-tab-label">{{ item.label }}</span>
    </div>
  </nav>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { Home, GraduationCap, Layers, UserCircle, UserCheck } from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const items = computed(() => [
  { path: '/', label: '首页', icon: Home },
  // 学习: 优先跳最近学习, 否则学习中心
  { path: userStore.lastLearningPath || '/learning-center', label: '学习', icon: GraduationCap },
  { path: '/english-cards', label: '卡片', icon: Layers },
  { path: '/profile', label: '我的', icon: userStore.isLoggedIn ? UserCheck : UserCircle },
])

function isActive(path) {
  if (path === '/') return route.path === '/'
  // 学习 tab 可能在 /learn/<id> 时也保持激活
  if (path.startsWith('/learn') && route.path.startsWith('/learn') && path.startsWith('/learn')) return true
  return route.path === path || route.path.startsWith(path + '/')
}

function onClick(item) {
  router.push(item.path)
}
</script>

<style scoped>
.h5-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: none; /* 默认隐藏, 桌面端隐藏; H5 时由 App.vue / 父级 @media 控制 */
  height: calc(56px + env(safe-area-inset-bottom, 0px));
  padding-bottom: env(safe-area-inset-bottom, 0px);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: saturate(180%) blur(16px);
  -webkit-backdrop-filter: saturate(180%) blur(16px);
  border-top: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.02);
  /* 显示条件在 App.vue 由父级 .app-main 加 padding-bottom 避免遮挡 */
}

@media (max-width: 1023px) {
  .h5-tab-bar {
    display: flex;
  }
}

.h5-tab-item {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  user-select: none;
  color: var(--color-text-muted, #94A3B8);
  transition: color 150ms ease;
}

.h5-tab-item:active {
  opacity: 0.7;
}

.h5-tab-indicator {
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 18px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, #4DA06C 0%, #3F8A5B 100%);
}

.h5-tab-item.is-active {
  color: var(--color-brand, #0F4C3A);
}

.h5-tab-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0;
}

.h5-tab-item.is-active .h5-tab-label {
  font-weight: 700;
}
</style>
