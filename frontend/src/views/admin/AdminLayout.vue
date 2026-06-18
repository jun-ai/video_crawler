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
          :class="['mobile-nav-item', { active: activeMenu === item.path }]"
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
            :class="['sidebar-menu-item', { active: activeMenu === item.path }]"
            @click="router.push(item.path)"
          >
            <component :is="item.icon" :size="18" />
            <span>{{ item.label }}</span>
          </div>

          <hr class="sidebar-divider" />

          <div
            v-for="item in sidebarMenuItems2"
            :key="item.path"
            :class="['sidebar-menu-item', { active: activeMenu === item.path }]"
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
  background: #F5F7F5;
}

.admin-container {
  display: flex;
  min-height: 100vh;
}

/* ── Desktop Sidebar ── */
.admin-sidebar {
  width: 240px;
  min-width: 240px;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #E5E9E5;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  overflow-y: auto;
}

.sidebar-header {
  padding: 24px 20px 20px;
  border-bottom: 1px solid #E5E9E5;
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
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
  color: #fff;
  font-weight: 700;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.logo-text {
  color: #1A2820;
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
  color: #5A6B62;
  cursor: pointer;
  transition: background 0.18s cubic-bezier(0.4, 0, 0.2, 1),
              color 0.18s cubic-bezier(0.4, 0, 0.2, 1);
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
  background: #F59E0B;
  border-radius: 0 2px 2px 0;
  transition: height 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.sidebar-menu-item:hover {
  background: #F0F4F1;
  color: #1A2820;
}

.sidebar-menu-item.active {
  background: #E8F5EE;
  color: #2563EB;
  font-weight: 600;
}

.sidebar-menu-item.active::before {
  height: 20px;
  background: #F59E0B;
}

.sidebar-divider {
  margin: 8px 16px;
  border: none;
  border-top: 1px solid #E5E9E5;
}

/* ── Sidebar Footer ── */
.sidebar-footer {
  padding: 12px 16px 16px;
  border-top: 1px solid #E5E9E5;
}

.back-btn {
  color: #8A9A90;
  width: 100%;
  justify-content: flex-start;
  height: 36px;
  border-radius: 8px;
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-btn:hover {
  color: #1A2820 !important;
  background: #F0F4F1 !important;
}

/* ── Main Content ── */
.admin-main {
  flex: 1;
  margin-left: 240px;
  padding: 32px;
  background: #F5F7F5;
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
    background: #FFFFFF;
    border-bottom: 1px solid #E5E9E5;
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
    background: linear-gradient(135deg, #2563EB, #3B82F6);
    color: #fff;
    font-weight: 700;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-title {
    color: #1A2820;
    font-size: 15px;
    font-weight: 600;
  }

  .mobile-back-btn {
    color: #5A6B62;
    font-size: 13px;
  }

  /* ── Mobile Bottom Nav ── */
  .mobile-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #FFFFFF;
    backdrop-filter: blur(12px);
    border-top: 1px solid #E5E9E5;
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
    color: #8A9A90;
    cursor: pointer;
    font-size: 10px;
    font-weight: 500;
    transition: color 0.18s;
    min-width: 0;
  }

  .mobile-nav-item.active {
    color: #2563EB;
  }
}

@media (max-width: 480px) {
  .admin-main {
    padding: 12px;
    padding-bottom: 80px;
  }
}
</style>
