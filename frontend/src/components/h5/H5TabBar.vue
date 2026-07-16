<!--
  H5TabBar — Phase 24 P0: 恢复 3-tab (首页 / 学习 / 我的) + 中间 FAB 跳视频库
  设计: FAB 默认跳 /materials (视频库 — 不会空白, H5 用户最自然的下一步入口),
        进入任意视频后由 /materials 跳转 /learn/:id
-->
<template>
  <nav class="h5-tab-bar" aria-label="主导航">
    <div
      v-for="item in items"
      :key="item.path"
      :class="['h5-tab-item', { 'is-active': isActive(item.path), 'is-fab': item.fab }]"
      @click="onClick(item)"
    >
      <span class="h5-tab-indicator" v-if="isActive(item.path) && !item.fab" />
      <component
        :is="item.icon"
        :size="item.fab ? 26 : 22"
        :stroke-width="isActive(item.path) ? 2.4 : 1.8"
      />
      <span v-if="!item.fab" class="h5-tab-label">{{ item.label }}</span>
    </div>
  </nav>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { Home, PlayCircle, UserCheck } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// Phase 26+1: 中间 FAB 跳 /materials (视频库, 不会空白; 用户选视频后进 Learn)
//         而非 /learn/:id 需 ID 参数, 没参数时空白
const items = computed(() => [
  { path: '/', label: '首页', icon: Home },
  { path: '/materials', label: '', icon: PlayCircle, fab: true },  // FAB → 视频库 (无空白, 一视频可进 Learn)
  { path: '/profile', label: '我的', icon: UserCheck },
])

function isActive(path) {
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
  color: var(--color-brand);  /* Phase 24: 删 #2F3D35 fallback (phase 23c 之前 brand=墨绿假设) */
}

.h5-tab-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0;
}

.h5-tab-item.is-active .h5-tab-label {
  font-weight: 700;
}

/* Phase 24 P0: 中间 FAB 视觉样式 — 圆形草绿凸起按钮 */
.h5-tab-item.is-fab {
  position: relative;
  flex: 0 0 64px;
  margin-top: -22px;
  align-items: center;
  justify-content: center;
}
.h5-tab-item.is-fab::before {
  content: '';
  position: absolute;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-brand) 0%, var(--color-brand-hover) 100%);
  box-shadow: 0 6px 16px rgba(77, 160, 108, 0.35);
  z-index: -1;
}
.h5-tab-item.is-fab :deep(svg) {
  color: #fff;
}
.h5-tab-item.is-fab:active::before { transform: scale(0.96); }
.h5-tab-item.is-fab:active {
  opacity: 1;
}
</style>
