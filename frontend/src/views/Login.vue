<template>
  <div class="login-page">
    <!-- 装饰背景 -->
    <div class="login-decor">
      <div class="login-glow login-glow-1" />
      <div class="login-glow login-glow-2" />
      <div class="login-grid" />
    </div>

    <div class="login-card">
      <!-- Header -->
      <div class="login-header">
        <div class="login-logo">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
            <path d="M12 3L1 9l11 6 9-4.91V17h2V9M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
          </svg>
        </div>
        <h1 class="login-title">登录 Fluenty</h1>
        <p class="login-subtitle">看视频学英语</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="login-field">
          <SfInput
            v-model="form.phone"
            placeholder="请输入手机号"
            maxlength="11"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.phone" class="login-error">{{ errors.phone }}</p>
        </div>

        <div class="login-field">
          <SfInput
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.password" class="login-error">{{ errors.password }}</p>
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
        <router-link to="/register" class="login-link">去注册</router-link>
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
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 64px);
  margin: -24px;
  padding: 24px;
  position: relative;
  background: var(--color-bg-base);
  font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── 装饰背景 ── */
.login-decor {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.login-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.18;
}

.login-glow-1 {
  top: -8%;
  right: -6%;
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, var(--color-brand) 0%, transparent 70%);
  animation: login-float 10s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.login-glow-2 {
  bottom: -8%;
  left: -6%;
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, var(--color-accent) 0%, transparent 70%);
  animation: login-float 12s cubic-bezier(0.4, 0, 0.2, 1) infinite reverse;
}

.login-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--color-border) 1px, transparent 1px),
    linear-gradient(90deg, var(--color-border) 1px, transparent 1px);
  background-size: 64px 64px;
  opacity: 0.2;
  mask-image: radial-gradient(ellipse at center, black 15%, transparent 65%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 15%, transparent 65%);
}

@keyframes login-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(16px, -12px) scale(1.03); }
}

/* ── 卡片 ── */
.login-card {
  position: relative;
  width: 100%;
  max-width: 480px;
  padding: 48px 40px 40px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  animation: login-enter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes login-enter {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Header ── */
.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-logo {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  background: var(--color-brand);
  box-shadow: 0 6px 20px rgba(15, 76, 58, 0.25);
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  margin: 0 0 6px 0;
}

.login-subtitle {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* ── Form ── */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.login-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.login-error {
  font-size: 12px;
  color: var(--color-danger);
  margin: 0;
}

/* ── 提交按钮 ── */
.login-submit {
  margin-top: 8px;
  height: 48px !important;
  font-size: 16px;
  font-weight: 600;
  background: var(--color-brand) !important;
  border: none;
  border-radius: var(--radius-md);
  transition: background 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-submit:hover {
  background: var(--color-brand-hover) !important;
  box-shadow: 0 4px 16px rgba(15, 76, 58, 0.2);
}

.login-submit:active {
  transform: scale(0.98);
}

/* ── Footer ── */
.login-footer {
  text-align: center;
  margin-top: 28px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.login-link {
  font-weight: 600;
  color: var(--color-brand);
  text-decoration: none;
  transition: color 0.2s;
}

.login-link:hover {
  color: var(--color-accent);
}

/* ── Mobile ── */
@media (max-width: 480px) {
  .login-page {
    padding: 24px 16px;
  }

  .login-card {
    padding: 32px 20px 28px;
    border-radius: var(--radius-md);
  }

  .login-title {
    font-size: 24px;
  }
}
</style>
