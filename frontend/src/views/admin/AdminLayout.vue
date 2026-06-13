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
.admin-layout {
  min-height: 100vh;
  background: var(--sf-admin-bg);
}

.admin-container {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: 240px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
}

.sidebar-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
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
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  color: #f1f5f9;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  flex: 1;
  padding-top: 8px;
  display: flex;
  flex-direction: column;
}

.sidebar-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 2px 8px;
  border-radius: 8px;
  height: 40px;
  line-height: 40px;
  padding: 0 16px;
  color: rgba(255, 255, 255, 0.55);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.sidebar-menu-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.85);
}

.sidebar-menu-item.active {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #fff;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
}

.sidebar-divider {
  margin: 8px 16px;
  border-color: rgba(255, 255, 255, 0.08);
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.back-btn {
  color: rgba(255, 255, 255, 0.45);
  width: 100%;
  justify-content: flex-start;
  height: 36px;
  border-radius: 8px;
  transition: all 0.2s;
}

.back-btn:hover {
  color: rgba(255, 255, 255, 0.8) !important;
  background: rgba(255, 255, 255, 0.06) !important;
}

.admin-main {
  flex: 1;
  padding: 28px;
  background: var(--sf-admin-bg);
  min-height: 100vh;
}

/* ====== 移动端隐藏桌面元素 ====== */
.mobile-header,
.mobile-nav {
  display: none;
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .admin-sidebar {
    display: none;
  }

  .admin-container {
    flex-direction: column;
  }

  .mobile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: linear-gradient(135deg, #0f172a, #1e293b);
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
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: #fff;
    font-weight: 700;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-title {
    color: #f1f5f9;
    font-size: 16px;
    font-weight: 600;
  }

  .mobile-back-btn {
    color: rgba(255, 255, 255, 0.6);
    font-size: 13px;
  }

  .mobile-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--sf-admin-border);
    z-index: 100;
    padding: 4px 0;
    padding-bottom: env(safe-area-inset-bottom, 4px);
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.06);
  }

  .mobile-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 6px 2px;
    color: var(--sf-admin-text-muted, #9ca3af);
    cursor: pointer;
    font-size: 10px;
    font-weight: 500;
    transition: color 0.2s;
    min-width: 0;
  }

  .mobile-nav-item.active {
    color: #2563eb;
  }

  .admin-main {
    padding: 16px;
    padding-bottom: 80px;
    padding-top: 8px;
    min-height: auto;
  }
}
</style>
