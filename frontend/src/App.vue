<template>
  <SfProvider>
    <div :class="themeStore.theme === 'dark' ? 'dark' : ''" style="min-height: 100vh; background: var(--color-bg-base)">
      <!-- 顶部导航栏 — SpeakVlog 毛玻璃 -->
      <header class="fixed top-0 left-0 right-0 h-16 flex items-center justify-between px-6 z-[1000]"
              style="background: var(--color-bg-frosted); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(0,0,0,0.04)">
        <div class="flex items-center gap-8">
          <!-- Logo -->
          <div class="flex items-center gap-2 cursor-pointer flex-shrink-0" @click="$router.push('/')">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white"
                 style="background: var(--color-brand)">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12 3L1 9l11 6 9-4.91V17h2V9M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
              </svg>
            </div>
            <span class="text-lg font-bold tracking-tight hidden md:block" style="color: var(--color-text-primary)">SpeakFlow</span>
          </div>

          <!-- 水平导航 -->
          <nav class="hidden lg:flex items-center gap-1">
            <div
              v-for="item in navItems"
              :key="item.path"
              :class="['px-3.5 py-1.5 rounded-lg text-sm font-medium cursor-pointer transition-all duration-150 whitespace-nowrap',
                        isActiveRoute(item.path) ? 'font-semibold' : '']"
              :style="{
                color: isActiveRoute(item.path) ? 'var(--color-brand)' : 'var(--color-text-secondary)',
                background: isActiveRoute(item.path) ? 'var(--color-brand-subtle)' : 'transparent'
              }"
              @click="navigateTo(item.path)"
            >
              {{ item.label }}
            </div>
          </nav>
        </div>

        <!-- 右侧操作 -->
        <div class="flex items-center gap-3 flex-shrink-0">
          <template v-if="userStore.isLoggedIn">
            <SfDropdown>
              <template #trigger>
                <div class="flex items-center gap-2 cursor-pointer px-2 py-1 rounded-lg transition-colors duration-150"
                     style="color: var(--color-text-secondary)"
                     @mouseenter="$event.currentTarget.style.background = 'var(--color-bg-elevated)'"
                     @mouseleave="$event.currentTarget.style.background = 'transparent'">
                  <SfAvatar :name="userStore.user?.username || ''" size="sm"
                            :bg-color="'var(--color-brand)'" />
                  <span class="hidden md:block text-sm font-medium" style="color: var(--color-text-primary)">
                    {{ userStore.user?.username }}
                  </span>
                </div>
              </template>
              <div class="px-2 py-1.5 rounded-lg cursor-pointer flex items-center gap-2.5 text-sm transition-colors duration-150"
                   style="color: var(--color-text-secondary)"
                   @click="$router.push('/profile')"
                   @mouseenter="$event.currentTarget.style.background = 'var(--color-bg-elevated)'"
                   @mouseleave="$event.currentTarget.style.background = 'transparent'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                个人中心
              </div>
              <div class="px-2 py-1.5 rounded-lg cursor-pointer flex items-center gap-2.5 text-sm transition-colors duration-150"
                   style="color: var(--color-text-secondary)"
                   @click="themeStore.toggleTheme()"
                   @mouseenter="$event.currentTarget.style.background = 'var(--color-bg-elevated)'"
                   @mouseleave="$event.currentTarget.style.background = 'transparent'">
                <svg v-if="themeStore.theme === 'dark'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                {{ themeStore.theme === 'dark' ? '浅色模式' : '深色模式' }}
              </div>
              <div class="my-1 border-t" style="border-color: var(--color-border)" />
              <div class="px-2 py-1.5 rounded-lg cursor-pointer flex items-center gap-2.5 text-sm transition-colors duration-150"
                   style="color: var(--color-danger)"
                   @click="logout"
                   @mouseenter="$event.currentTarget.style.background = 'var(--color-bg-elevated)'"
                   @mouseleave="$event.currentTarget.style.background = 'transparent'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                退出登录
              </div>
            </SfDropdown>
          </template>
          <template v-else>
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium cursor-pointer px-3 py-1.5 rounded-lg transition-colors duration-150"
                    style="color: var(--color-text-secondary)"
                    @click="$router.push('/login')"
                    @mouseenter="$event.target.style.background = 'var(--color-bg-elevated)'"
                    @mouseleave="$event.target.style.background = 'transparent'">
                登录
              </span>
              <button class="px-4 py-2 rounded-xl text-sm font-semibold text-white transition-all duration-200"
                      style="background: linear-gradient(#60A5FA 0%, #3B82F6 100%)"
                      @mouseenter="$event.target.style.opacity = '0.9'"
                      @mouseleave="$event.target.style.opacity = '1'"
                      @click="$router.push('/login')">
                开始学习
              </button>
            </div>
          </template>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="mt-16 px-6 min-[calc(100vh-64px)] max-w-[1440px] mx-auto" style="padding-bottom: env(safe-area-inset-bottom, 0px)">
        <router-view v-slot="{ Component }">
          <transition name="page-slide" mode="in-out">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- 全局 Footer — SpeakVlog 浅绿底（Phase 0+） -->
      <footer class="app-footer">
        <div class="app-footer-inner">
          <div class="app-footer-brand">
            <div class="app-footer-logo">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12 3L1 9l11 6 9-4.91V17h2V9M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
              </svg>
              <span>SpeakFlow</span>
            </div>
            <p class="app-footer-tagline">看视频学英语，每天 10 分钟。</p>
          </div>
          <div class="app-footer-cols">
            <div class="app-footer-col">
              <h4>产品</h4>
              <a href="/materials">视频库</a>
              <a href="/english-cards">英语卡片</a>
              <a href="/vocabulary">生词本</a>
            </div>
            <div class="app-footer-col">
              <h4>学习</h4>
              <a href="/learning-center">学习记录</a>
              <a href="/favorites">我的收藏</a>
              <a href="/vocabulary-review">复习中心</a>
            </div>
            <div class="app-footer-col">
              <h4>关于</h4>
              <a href="#">使用指南</a>
              <a href="#">意见反馈</a>
              <a href="#">联系我们</a>
            </div>
          </div>
        </div>
        <div class="app-footer-bottom">
          <span>© 2026 Fluenty · 看视频学英语</span>
          <span class="app-footer-icp">浙ICP备 2025xxxxxx 号</span>
        </div>
      </footer>

      <!-- 移动端底部导航 -->
      <nav class="fixed bottom-0 left-0 right-0 h-14 flex lg:hidden border-t z-[1000]"
           style="background: var(--color-bg-card); border-color: var(--color-border); padding-bottom: env(safe-area-inset-bottom, 0px)">
        <div
          v-for="item in mobileNavItems"
          :key="item.path"
          :class="['flex-1 flex flex-col items-center justify-center gap-0.5 cursor-pointer transition-colors duration-150',
                    isActiveRoute(item.path) ? '' : '']"
          :style="{ color: isActiveRoute(item.path) ? 'var(--color-brand)' : 'var(--color-text-muted)' }"
          @click="navigateTo(item.path)"
        >
          <component :is="item.icon" :size="20" />
          <span class="text-[10px] font-medium">{{ item.label }}</span>
        </div>
      </nav>
    </div>
  </SfProvider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { Home, Video, BarChart3, Star, BookOpen, Layers } from 'lucide-vue-next'
import SfProvider from '@/components/ui/SfProvider.vue'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import SfAvatar from '@/components/ui/SfAvatar.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const navItems = computed(() => {
  const items = [
    { path: '/', label: '首页' },
    { path: '/materials', label: '视频库' },
    { path: '/learning-center', label: '学习记录' },
    { path: '/english-cards', label: '英语卡片' }
  ]
  if (userStore.isLoggedIn) {
    items.push({ path: '/favorites', label: '收藏' })
    items.push({ path: '/vocabulary', label: '生词本' })
  }
  if (userStore.isAdmin) {
    items.push({ path: '/admin', label: '管理' })
  }
  return items
})

const mobileNavItems = [
  { path: '/', label: '首页', icon: Home },
  { path: '/materials', label: '视频库', icon: Video },
  { path: '/learning-center', label: '学习', icon: BarChart3 },
  { path: '/vocabulary', label: '生词本', icon: BookOpen },
  { path: '/english-cards', label: '卡片', icon: Layers }
]

const isActiveRoute = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const navigateTo = (path) => {
  router.push(path)
}

const logout = () => {
  userStore.logout()
  router.push('/')
}
</script>

<style scoped>
.page-slide-enter-active,
.page-slide-leave-active {
  transition: opacity 0.15s ease;
}
.page-slide-enter-from,
.page-slide-leave-to {
  opacity: 0;
}

/* ====== 全局 Footer — SpeakVlog 浅绿底（Phase 0+） ====== */
.app-footer {
  background: var(--color-footer, #F1F6EE);
  margin-top: 64px;
  padding: 56px 24px 24px;
  border-top: 1px solid var(--color-border);
}

.app-footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.4fr 2fr;
  gap: 56px;
  padding-bottom: 32px;
  border-bottom: 1px solid rgba(37, 99, 235, 0.1);
}

.app-footer-logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-brand);
  margin-bottom: 12px;
}

.app-footer-tagline {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
  max-width: 280px;
}

.app-footer-cols {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.app-footer-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.app-footer-col h4 {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px;
  letter-spacing: 0.5px;
}

.app-footer-col a {
  font-size: 13px;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.app-footer-col a:hover {
  color: var(--color-brand-bright);
}

.app-footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--color-text-muted);
}

.app-footer-icp {
  font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 1024px) {
  main {
    padding: 20px !important;
  }

  .app-footer-inner {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

@media (max-width: 768px) {
  main {
    padding: 16px !important;
    padding-bottom: 72px !important;
  }

  .app-footer {
    padding: 40px 16px 20px;
    margin-top: 48px;
  }

  .app-footer-cols {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .app-footer-bottom {
    flex-direction: column;
    gap: 6px;
    align-items: flex-start;
  }
}
</style>
