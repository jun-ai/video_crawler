<template>
  <div class="upload-layout">
    <!-- 子导航 -->
    <div class="sub-nav">
      <div
        v-for="tab in tabs"
        :key="tab.path"
        :class="['sub-nav-item', { active: isActive(tab.path) }]"
        @click="goTo(tab.path)"
      >
        <component :is="tab.icon" :size="16" />
        <span>{{ tab.label }}</span>
      </div>
    </div>

    <!-- 子页面 -->
    <router-view />
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { Upload, Mic, Link2 } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const tabs = [
  { path: '/admin/upload', label: '直接上传', icon: Upload },
  { path: '/admin/upload/fetch-url', label: '通过 URL 抓取', icon: Link2 },
  { path: '/admin/upload/transcribe', label: '视频转字幕', icon: Mic }
]

function isActive(path) {
  return route.path === path
}

function goTo(path) {
  router.push(path)
}
</script>

<style scoped>
.upload-layout {
  height: 100%;
}

.sub-nav {
  display: flex;
  gap: 4px;
  padding: 0 24px;
  border-bottom: 1px solid var(--sf-admin-border);
  background: var(--sf-admin-bg-card);
  margin-bottom: 0;
}

.sub-nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 16px;
  font-size: 14px;
  color: var(--sf-admin-text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s ease;
  user-select: none;
}

.sub-nav-item:hover {
  color: var(--sf-admin-text);
  background: var(--sf-admin-bg-hover, rgba(64, 158, 255, 0.04));
}

.sub-nav-item.active {
  color: var(--sf-primary, #409eff);
  border-bottom-color: var(--sf-primary, #409eff);
  font-weight: 500;
}

@media (max-width: 640px) {
  .sub-nav {
    padding: 0 12px;
  }
  .sub-nav-item {
    padding: 12px 12px;
    font-size: 13px;
  }
  .sub-nav-item span {
    display: none;
  }
}
</style>
