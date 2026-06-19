<template>
  <transition name="banner-slide">
    <div
      v-if="visible && currentAnnouncement"
      :class="['announcement-banner', `banner-${currentAnnouncement.type}`]"
    >
      <div class="banner-inner">
        <div class="banner-icon">
          <component :is="iconMap[currentAnnouncement.type] || Info" :size="18" class="banner-icon-svg" />
        </div>
        <div class="banner-content">
          <span class="banner-title">{{ currentAnnouncement.title }}</span>
          <span class="banner-text" v-if="expanded">{{ currentAnnouncement.content }}</span>
        </div>
        <div class="banner-actions">
          <button class="banner-expand" @click="expanded = !expanded" v-if="currentAnnouncement.content">
            {{ expanded ? '收起' : '查看详情' }}
          </button>
          <button class="banner-close" @click="closeBanner">
            &times;
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { announcementAPI } from '@/api'
import { AlertTriangle, CheckCircle, Rocket, Info } from 'lucide-vue-next'

const iconMap = {
  warning: AlertTriangle,
  success: CheckCircle,
  update: Rocket,
  info: Info
}

const visible = ref(false)
const expanded = ref(false)
const currentAnnouncement = ref(null)

const STORAGE_KEY = 'closed_announcements'

const loadAnnouncements = async () => {
  try {
    const list = await announcementAPI.getList({ limit: 1 })
    if (list && list.length > 0) {
      const announcement = list[0]
      // Check if already closed
      const closed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
      if (!closed.includes(announcement.id)) {
        currentAnnouncement.value = announcement
        visible.value = true
      }
    }
  } catch (e) {
    // Silent fail - announcements are not critical
    console.warn('Failed to load announcements:', e)
  }
}

const closeBanner = () => {
  visible.value = false
  if (currentAnnouncement.value) {
    const closed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    closed.push(currentAnnouncement.value.id)
    // Keep only last 20 closed IDs
    if (closed.length > 20) closed.splice(0, closed.length - 20)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(closed))
  }
}

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
.announcement-banner {
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.banner-info {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(22, 163, 74, 0.06));
  border: 1px solid rgba(37, 99, 235, 0.15);
  color: #2563EB;
}

.banner-warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(251, 191, 36, 0.06));
  border: 1px solid rgba(245, 158, 11, 0.15);
  color: #b45309;
}

.banner-success {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(52, 211, 153, 0.06));
  border: 1px solid rgba(16, 185, 129, 0.15);
  color: #047857;
}

.banner-update {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(96, 165, 250, 0.06));
  border: 1px solid rgba(37, 99, 235, 0.15);
  color: #2563EB;
}

.banner-inner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
}

.banner-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.banner-icon-svg {
  flex-shrink: 0;
}

.banner-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.banner-title {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

.banner-text {
  font-size: 13px;
  opacity: 0.85;
  line-height: 1.5;
}

.banner-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.banner-expand {
  background: none;
  border: none;
  font-size: 12px;
  font-weight: 600;
  color: inherit;
  opacity: 0.7;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all var(--sf-duration-normal);
  white-space: nowrap;
}

.banner-expand:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.05);
}

.banner-close {
  background: none;
  border: none;
  font-size: 20px;
  color: inherit;
  opacity: 0.4;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all var(--sf-duration-normal);
  line-height: 1;
}

.banner-close:hover {
  opacity: 0.8;
  background: rgba(0, 0, 0, 0.05);
}

.banner-slide-enter-active,
.banner-slide-leave-active {
  transition: all var(--sf-duration-slow) ease;
}

.banner-slide-enter-from,
.banner-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* ========== 暗色模式 ========== */
.dark .banner-info {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(96, 165, 250, 0.1));
  border-color: rgba(37, 99, 235, 0.3);
  color: #60A5FA;
}

.dark .banner-warning {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(252, 211, 77, 0.1));
  border-color: rgba(251, 191, 36, 0.3);
  color: #fcd34d;
}

.dark .banner-success {
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.15), rgba(16, 185, 129, 0.1));
  border-color: rgba(52, 211, 153, 0.3);
  color: #6ee7b7;
}

.dark .banner-update {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.15), rgba(96, 165, 250, 0.1));
  border-color: rgba(37, 99, 235, 0.3);
  color: #60A5FA;
}

.dark .banner-expand:hover {
  background: rgba(255, 255, 255, 0.08);
}

.dark .banner-close:hover {
  background: rgba(255, 255, 255, 0.08);
}
</style>
