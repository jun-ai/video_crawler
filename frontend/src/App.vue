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
                      style="background: linear-gradient(#4DA06C 0%, #3F8A5B 100%)"
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

@media (max-width: 1024px) {
  main {
    padding: 20px !important;
  }
}

@media (max-width: 768px) {
  main {
    padding: 16px !important;
    padding-bottom: 72px !important;
  }
}
</style>
