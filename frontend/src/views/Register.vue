<template>
  <div class="flex min-h-[calc(100vh-64px)] items-center justify-center -m-6 p-6"
       style="background: var(--color-bg-base)">
    <!-- 装饰背景 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-1/4 -left-1/4 w-[600px] h-[600px] rounded-full opacity-20"
           style="background: radial-gradient(circle, var(--color-accent) 0%, transparent 70%)" />
      <div class="absolute -bottom-1/4 -right-1/4 w-[500px] h-[500px] rounded-full opacity-15"
           style="background: radial-gradient(circle, var(--color-brand) 0%, transparent 70%)" />
    </div>

    <div class="relative w-full max-w-[420px] rounded-2xl p-10 border"
         style="background: var(--color-bg-card); border-color: var(--color-border); box-shadow: var(--shadow-lg)">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-4"
             style="background: var(--color-brand)">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="white">
            <path d="M12 3L1 9l11 6 9-4.91V17h2V9M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
          </svg>
        </div>
        <h1 class="text-3xl font-bold tracking-tight" style="color: var(--color-text-primary)">创建账号</h1>
        <p class="text-base mt-2" style="color: var(--color-text-secondary)">加入我们，开始你的英语学习之旅</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleRegister" class="flex flex-col gap-5">
        <div class="flex flex-col gap-1.5">
          <SfInput v-model="form.username" placeholder="用户名">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.username" class="text-xs mt-0.5" style="color: var(--color-danger)">{{ errors.username }}</p>
        </div>

        <div class="flex flex-col gap-1.5">
          <SfInput v-model="form.phone" placeholder="手机号" maxlength="11">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.phone" class="text-xs mt-0.5" style="color: var(--color-danger)">{{ errors.phone }}</p>
        </div>

        <div class="flex flex-col gap-1.5">
          <SfInput v-model="form.invite_code" placeholder="激活码（必填）">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21 2-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.invite_code" class="text-xs mt-0.5" style="color: var(--color-danger)">{{ errors.invite_code }}</p>
        </div>

        <div class="flex flex-col gap-1.5">
          <SfInput v-model="form.password" type="password" placeholder="密码">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.password" class="text-xs mt-0.5" style="color: var(--color-danger)">{{ errors.password }}</p>
        </div>

        <div class="flex flex-col gap-1.5">
          <SfInput v-model="form.confirmPassword" type="password" placeholder="确认密码">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.confirmPassword" class="text-xs mt-0.5" style="color: var(--color-danger)">{{ errors.confirmPassword }}</p>
        </div>

        <SfButton
          type="primary"
          size="lg"
          block
          :loading="loading"
          html-type="submit"
        >
          注 册
        </SfButton>
      </form>

      <!-- Footer -->
      <div class="text-center mt-6 text-sm" style="color: var(--color-text-secondary)">
        已有账号？
        <router-link to="/login" class="font-semibold" style="color: var(--color-brand)">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { authAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  phone: '',
  invite_code: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  username: '',
  phone: '',
  invite_code: '',
  password: '',
  confirmPassword: ''
})

function validate() {
  Object.keys(errors).forEach(k => errors[k] = '')

  if (!form.username) {
    errors.username = '请输入用户名'
  } else if (form.username.length < 3 || form.username.length > 20) {
    errors.username = '用户名长度 3-20 个字符'
  }

  if (!form.phone) {
    errors.phone = '请输入手机号'
  } else if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    errors.phone = '请输入正确的手机号'
  }

  if (!form.invite_code) {
    errors.invite_code = '请输入激活码'
  }

  if (!form.password) {
    errors.password = '请输入密码'
  } else if (form.password.length < 6) {
    errors.password = '密码至少 6 个字符'
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认密码'
  } else if (form.confirmPassword !== form.password) {
    errors.confirmPassword = '两次输入的密码不一致'
  }

  return !Object.values(errors).some(e => e)
}

const handleRegister = async () => {
  if (!validate()) return
  loading.value = true
  try {
    await authAPI.register({
      username: form.username,
      phone: form.phone,
      password: form.password,
      invite_code: form.invite_code
    })
    toast.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    console.error('注册失败', e)
  } finally {
    loading.value = false
  }
}
</script>
