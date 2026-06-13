import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  // 只依赖 token 判断登录状态
  const isLoggedIn = computed(() => !!token.value)

  // 判断是否为管理员
  const isAdmin = computed(() => user.value?.role === 1)

  const login = async (phone, password) => {
    const res = await authAPI.login(phone, password)
    console.log('Login response:', res) // 调试
    if (!res.access_token) {
      throw new Error('登录失败：未返回 token')
    }
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    // 获取用户信息
    await fetchProfile()
  }

  const fetchProfile = async () => {
    if (!token.value) return
    try {
      user.value = await authAPI.getProfile()
    } catch (e) {
      console.error('获取用户信息失败', e)
      // 如果是 401 错误，清除无效 token
      if (e.response?.status === 401) {
        logout()
      }
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  // 初始化时获取用户信息
  if (token.value) {
    fetchProfile()
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchProfile
  }
})
