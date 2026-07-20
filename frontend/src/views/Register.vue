<template>
  <div class="register-page">
    <!-- Phase 6 (H5): 极简 header + 返回按钮 -->
    <header v-if="isMobileView" class="sf-h5-header">
      <button class="sf-h5-back" type="button" @click="goBack" aria-label="返回">
        <ArrowLeft :size="22" />
      </button>
      <h1 class="sf-h5-title">注册</h1>
    </header>
    <!-- 装饰背景 -->
    <div class="register-decor">
      <div class="register-glow register-glow-1" />
      <div class="register-glow register-glow-2" />
      <div class="register-grid" />
    </div>

    <div class="register-card">
      <!-- Header -->
      <div class="register-header">
        <div class="register-logo">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="white">
            <path d="M12 3L1 9l11 6 9-4.91V17h2V9M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
          </svg>
        </div>
        <h1 class="register-title">创建账号</h1>
        <p class="register-subtitle">加入 Linyu，开始你的英语学习之旅</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="register-field">
          <SfInput v-model="form.username" placeholder="用户名">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.username" class="register-error">{{ errors.username }}</p>
        </div>

        <div class="register-field">
          <SfInput v-model="form.phone" placeholder="手机号" maxlength="11">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.phone" class="register-error">{{ errors.phone }}</p>
        </div>

        <div class="register-field">
          <SfInput v-model="form.invite_code" placeholder="激活码（必填）" :maxlength="64">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2"/><path d="M13 17v2"/><path d="M13 11v2"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.invite_code" class="register-error">{{ errors.invite_code }}</p>
        </div>

        <div class="register-field">
          <SfInput v-model="form.password" type="password" placeholder="密码">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.password" class="register-error">{{ errors.password }}</p>
        </div>

        <div class="register-field">
          <SfInput v-model="form.confirmPassword" type="password" placeholder="确认密码">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.confirmPassword" class="register-error">{{ errors.confirmPassword }}</p>
        </div>

        <SfButton
          type="primary"
          size="lg"
          block
          :loading="loading"
          html-type="submit"
          class="register-submit"
        >
          注 册
        </SfButton>
      </form>

      <!-- Footer -->
      <div class="register-footer">
        已有账号？
        <router-link to="/login" class="register-link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import { toast } from '@/composables/useToast'
import { authAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'

const router = useRouter()

// Phase 6 (H5): 移动端检测
const isMobileView = ref(typeof window !== 'undefined' && window.matchMedia('(max-width: 768px)').matches)
const updateIsMobile = () => {
  isMobileView.value = window.matchMedia('(max-width: 768px)').matches
}
onMounted(() => window.addEventListener('resize', updateIsMobile))
onUnmounted(() => window.removeEventListener('resize', updateIsMobile))

// Phase 6 (H5): 返回按钮
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/login')
  }
}
const loading = ref(false)

const form = reactive({
  username: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  username: '',
  phone: '',
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
      invite_code: form.invite_code || undefined
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

<style scoped>
.register-page {
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
.register-decor {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.register-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
}

.register-glow-1 {
  top: -12%;
  left: -8%;
  width: 520px;
  height: 520px;
  opacity: 0.16;
  background: radial-gradient(circle, var(--color-accent) 0%, transparent 70%);
  animation: register-float 11s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.register-glow-2 {
  bottom: -10%;
  right: -6%;
  width: 440px;
  height: 440px;
  opacity: 0.14;
  background: radial-gradient(circle, var(--color-brand) 0%, transparent 70%);
  animation: register-float 13s cubic-bezier(0.4, 0, 0.2, 1) infinite reverse;
}

.register-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--color-border) 1px, transparent 1px),
    linear-gradient(90deg, var(--color-border) 1px, transparent 1px);
  background-size: 64px 64px;
  opacity: 0.15;
  mask-image: radial-gradient(ellipse at center, black 10%, transparent 60%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 10%, transparent 60%);
}

@keyframes register-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(14px, -10px) scale(1.02); }
}

/* ── 卡片 ── */
.register-card {
  position: relative;
  width: 100%;
  max-width: 520px;
  padding: 44px 40px 36px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  animation: register-enter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes register-enter {
  from { opacity: 0; transform: translateY(14px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Header ── */
.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-logo {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  background: var(--color-brand);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.22);
}

.register-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  margin: 0 0 6px 0;
}

.register-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* ── Form ── */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.register-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.register-error {
  font-size: 12px;
  color: var(--color-danger);
  margin: 0;
}

/* ── 提交按钮 ── */
.register-submit {
  margin-top: 6px;
  height: 48px !important;
  font-size: 16px;
  font-weight: 600;
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%)) !important;
  border: none;
  border-radius: var(--radius-full, 9999px);
  width: 100%;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
  transition: transform var(--sf-duration-normal) cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.25s ease;
}

.register-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(37, 99, 235, 0.4);
}

.register-submit:active {
  transform: translateY(0) scale(0.98);
}

/* ── Footer ── */
.register-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.register-link {
  font-weight: 600;
  color: var(--color-brand);
  text-decoration: none;
  transition: color var(--sf-duration-normal);
}

.register-link:hover {
  color: var(--color-accent);
}

/* ── Mobile ── */
@media (max-width: 480px) {
  .register-page {
    padding: 24px 16px;
    align-items: flex-start;
    padding-top: 40px;
  }

  .register-card {
    padding: 28px 20px 24px;
    border-radius: var(--radius-md);
    max-width: 100%;
  }

  .register-title {
    font-size: 22px;
  }

  .register-submit {
    width: 100%;
  }
}
</style>
