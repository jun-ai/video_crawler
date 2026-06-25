<template>
  <div class="admin-layout">
    <div class="admin-container">
      <!-- 移动端顶部栏 -->
      <div class="mobile-header">
        <div class="mobile-logo">
          <div class="logo-icon-sm">A</div>
          <span class="mobile-title">管理后台</span>
        </div>
        <SfButton type="ghost" size="sm" @click="goHome" class="mobile-back-btn">
          <ArrowLeft :size="16" />
          前台
        </SfButton>
      </div>

      <!-- 移动端底部导航 -->
      <nav class="mobile-nav">
        <div
          v-for="item in mobileMenuItems"
          :key="item.path"
          :class="['mobile-nav-item', { active: isMenuActive(item.path) }]"
          @click="router.push(item.path)"
        >
          <component :is="item.icon" :size="20" />
          <span>{{ item.label }}</span>
        </div>
      </nav>

      <!-- 侧边栏（桌面端） -->
      <div class="admin-sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo">
            <div class="logo-icon">A</div>
            <div class="logo-text">管理后台</div>
          </div>
        </div>
        <nav class="sidebar-menu">
          <div
            v-for="item in sidebarMenuItems"
            :key="item.path"
            :class="['sidebar-menu-item', { active: isMenuActive(item.path) }]"
            @click="router.push(item.path)"
          >
            <component :is="item.icon" :size="18" />
            <span>{{ item.label }}</span>
          </div>

          <hr class="sidebar-divider" />

          <div
            v-for="item in sidebarMenuItems2"
            :key="item.path"
            :class="['sidebar-menu-item', { active: isMenuActive(item.path) }]"
            @click="router.push(item.path)"
          >
            <component :is="item.icon" :size="18" />
            <span>{{ item.label }}</span>
          </div>
        </nav>
        <div class="sidebar-footer">
          <SfButton type="ghost" size="sm" @click="goHome" class="back-btn">
            <ArrowLeft :size="16" />
            <span>返回前台</span>
          </SfButton>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="admin-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BarChart3, Video, Upload, Tag, ArrowLeft, Key, Bell } from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

function isMenuActive(itemPath) {
  if (route.path === itemPath) return true
  // 父路径匹配：/admin/upload 高亮 /admin/upload/transcribe
  return route.path.startsWith(itemPath + '/')
}

const sidebarMenuItems = [
  { path: '/admin', label: '数据统计', icon: BarChart3 },
  { path: '/admin/materials', label: '语料管理', icon: Video },
  { path: '/admin/upload', label: '上传语料', icon: Upload },
  { path: '/admin/tags', label: '标签管理', icon: Tag }
]

const sidebarMenuItems2 = [
  { path: '/admin/activation-codes', label: '激活码管理', icon: Key },
  { path: '/admin/announcements', label: '公告管理', icon: Bell }
]

const mobileMenuItems = [
  { path: '/admin', label: '统计', icon: BarChart3 },
  { path: '/admin/materials', label: '语料', icon: Video },
  { path: '/admin/upload', label: '上传', icon: Upload },
  { path: '/admin/tags', label: '标签', icon: Tag },
  { path: '/admin/activation-codes', label: '激活码', icon: Key },
  { path: '/admin/announcements', label: '公告', icon: Bell }
]

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
/* ========================================
   AdminLayout — Phase 0+ 浅色主题
   ======================================== */

.admin-layout {
  min-height: 100vh;
  background: var(--sf-admin-bg);
}

.admin-container {
  display: flex;
  min-height: 100vh;
}

/* ── Desktop Sidebar ── */
.admin-sidebar {
  width: 200px;
  min-width: 200px;
  background: var(--sf-admin-bg-card);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--sf-admin-border);
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  overflow-y: auto;
}

.sidebar-header {
  padding: 24px 20px 20px;
  border-bottom: 1px solid var(--sf-admin-border);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--sf-cta-gradient);
  color: #fff;
  font-weight: 700;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.logo-text {
  color: var(--sf-admin-text-primary);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.sidebar-menu {
  flex: 1;
  padding: 12px 0;
  display: flex;
  flex-direction: column;
}

/* ── Menu Items ── */
.sidebar-menu-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 1px 8px;
  border-radius: 8px;
  height: 40px;
  padding: 0 16px;
  color: var(--sf-admin-text-secondary);
  cursor: pointer;
  transition: background var(--sf-duration-fast) var(--sf-ease-standard),
              color var(--sf-duration-fast) var(--sf-ease-standard);
  font-size: 14px;
  font-weight: 400;
  user-select: none;
}

.sidebar-menu-item::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: var(--sf-admin-accent);
  border-radius: 0 2px 2px 0;
  transition: height var(--sf-duration-normal) var(--sf-ease-bounce);
}

.sidebar-menu-item:hover {
  background: var(--sf-admin-bg-hover);
  color: var(--sf-admin-text-primary);
}

.sidebar-menu-item.active {
  background: var(--sf-admin-bg-active);
  color: var(--color-brand);
  font-weight: 600;
}

.sidebar-menu-item.active::before {
  height: 20px;
  background: var(--sf-admin-accent);
}

.sidebar-divider {
  margin: 8px 16px;
  border: none;
  border-top: 1px solid var(--sf-admin-border);
}

/* ── Sidebar Footer ── */
.sidebar-footer {
  padding: 12px 16px 16px;
  border-top: 1px solid var(--sf-admin-border);
}

.back-btn {
  color: var(--sf-admin-text-muted);
  width: 100%;
  justify-content: flex-start;
  height: 36px;
  border-radius: 8px;
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
}

.back-btn:hover {
  color: var(--sf-admin-text-primary) !important;
  background: var(--sf-admin-bg-hover) !important;
}

/* ── Main Content ── */
.admin-main {
  flex: 1;
  margin-left: 240px;
  padding: 28px 32px;
  background: var(--sf-admin-bg);
  min-height: 100vh;
}

/* ── Mobile: hidden by default ── */
.mobile-header,
.mobile-nav {
  display: none;
}

/* ========================================
   Responsive — tablet & mobile (< 1024px)
   ======================================== */
@media (max-width: 1023px) {
  .admin-sidebar {
    display: none;
  }

  .admin-main {
    margin-left: 0;
    padding: 16px;
    padding-bottom: 88px;
    padding-top: 8px;
    min-height: auto;
  }

  .admin-container {
    flex-direction: column;
  }

  /* ── Mobile Header ── */
  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: var(--sf-admin-bg-card);
    border-bottom: 1px solid var(--sf-admin-border);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .mobile-logo {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .logo-icon-sm {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: var(--sf-cta-gradient);
    color: #fff;
    font-weight: 700;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-title {
    color: var(--sf-admin-text-primary);
    font-size: 15px;
    font-weight: 600;
  }

  .mobile-back-btn {
    color: var(--sf-admin-text-secondary);
    font-size: 13px;
  }

  /* ── Mobile Bottom Nav ── */
  .mobile-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--sf-admin-bg-card);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--sf-admin-border);
    z-index: 100;
    padding: 4px 0;
    padding-bottom: env(safe-area-inset-bottom, 4px);
  }

  .mobile-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 8px 2px;
    color: var(--sf-admin-text-muted);
    cursor: pointer;
    font-size: 10px;
    font-weight: 500;
    transition: color var(--sf-duration-fast);
    min-width: 0;
  }

  .mobile-nav-item.active {
    color: var(--color-brand);
  }
}

@media (max-width: 480px) {
  .admin-main {
    padding: 12px;
    padding-bottom: 80px;
  }
}
</style>
