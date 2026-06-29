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
    // P0 安全 (6-29 体检发现): 不要 console.log 登录响应
    // res 含 access_token 完整 JWT, devtools 任何人都能看 + 复制 = 账号被盗
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
