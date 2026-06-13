<template>
  <div class="login-page flex min-h-[calc(100vh-64px)] items-center justify-center -m-6 p-6">
    <!-- 装饰背景 -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <!-- 渐变光晕 -->
      <div class="login-glow login-glow-1" />
      <div class="login-glow login-glow-2" />
      <!-- 装饰线条 -->
      <div class="login-grid" />
    </div>

    <div class="login-card">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="login-logo">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
            <path d="M12 3L1 9l11 6 9-4.91V17h2V9M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
          </svg>
        </div>
        <h1 class="login-title">SpeakFlow</h1>
        <p class="login-subtitle">专为口语练习设计的英语学习平台</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="flex flex-col gap-5">
        <div class="flex flex-col gap-1.5">
          <SfInput
            v-model="form.phone"
            placeholder="请输入手机号"
            maxlength="11"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.phone" class="text-xs mt-0.5 text-destructive">{{ errors.phone }}</p>
        </div>

        <div class="flex flex-col gap-1.5">
          <SfInput
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.password" class="text-xs mt-0.5 text-destructive">{{ errors.password }}</p>
        </div>

        <SfButton
          type="primary"
          size="lg"
          block
          :loading="loading"
          html-type="submit"
          class="login-submit"
        >
          登 录
        </SfButton>
      </form>

      <!-- Footer -->
      <div class="login-footer">
        还没有账号？
        <router-link to="/register" class="login-link">使用激活码注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { useUserStore } from '@/stores/user'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  phone: '',
  password: ''
})

const errors = reactive({
  phone: '',
  password: ''
})

function validate() {
  errors.phone = ''
  errors.password = ''

  if (!form.phone) {
    errors.phone = '请输入手机号'
  } else if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    errors.phone = '请输入正确的手机号'
  }

  if (!form.password) {
    errors.password = '请输入密码'
  }

  return !errors.phone && !errors.password
}

const handleLogin = async () => {
  if (!validate()) return
  loading.value = true
  try {
    await userStore.login(form.phone, form.password)
    toast.success('登录成功')
    router.push('/')
  } catch (e) {
    console.error('登录失败', e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  background: var(--background);
}

.login-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.login-glow-1 {
  top: -10%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, var(--color-brand) 0%, transparent 70%);
  animation: float 8s ease-in-out infinite;
}

.login-glow-2 {
  bottom: -10%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--color-accent) 0%, transparent 70%);
  animation: float 10s ease-in-out infinite reverse;
}

.login-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.3;
  mask-image: radial-gradient(ellipse at center, black 20%, transparent 70%);
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: var(--card);
  border-radius: 20px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-lg);
  animation: scale-in 0.3s var(--ease-bounce);
}

.login-logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, var(--color-brand) 0%, var(--color-accent) 100%);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--foreground);
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 15px;
  color: var(--muted-foreground);
}

.login-submit {
  margin-top: 8px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--color-brand) 0%, var(--color-accent) 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
  transition: all 0.2s;
}

.login-submit:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

.login-submit:active {
  transform: translateY(0);
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--muted-foreground);
}

.login-link {
  font-weight: 600;
  color: var(--color-brand);
  transition: color 0.2s;
}

.login-link:hover {
  color: var(--color-accent);
}

.text-destructive {
  color: var(--destructive);
}
</style>
