import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 从 localStorage 读取主题设置，默认跟随系统
  const getStoredTheme = () => {
    const stored = localStorage.getItem('theme')
    if (stored) return stored

    // 跟随系统设置
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
    return 'light'
  }

  const theme = ref(getStoredTheme())

  // 是否为深色模式
  const isDark = () => theme.value === 'dark'

  // 切换主题
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  // 设置主题
  const setTheme = (newTheme) => {
    theme.value = newTheme
  }

  // 监听主题变化，更新 DOM 和 localStorage
  watch(theme, (newTheme) => {
    // 保存到 localStorage
    localStorage.setItem('theme', newTheme)

    // 更新 html 标签的 class
    const html = document.documentElement
    if (newTheme === 'dark') {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }, { immediate: true })

  return {
    theme,
    isDark,
    toggleTheme,
    setTheme
  }
})
