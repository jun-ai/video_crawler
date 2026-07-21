<template>
  <div class="forgot-page">
    <!-- 装饰背景: H5 下用 CSS 隐藏 -->
    <div class="forgot-decor">
      <div class="forgot-glow forgot-glow-1" />
      <div class="forgot-glow forgot-glow-2" />
      <div class="forgot-grid" />
    </div>

    <div class="forgot-card">
      <div class="forgot-header">
        <div class="forgot-logo">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="white">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
        </div>
        <h1 class="forgot-title">重置密码</h1>
        <p class="forgot-subtitle">填写注册时使用的手机号和激活码验证身份</p>
      </div>

      <form @submit.prevent="handleReset" class="forgot-form">
        <div class="forgot-field">
          <SfInput v-model="form.phone" placeholder="注册时使用的手机号" maxlength="11">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.phone" class="forgot-error">{{ errors.phone }}</p>
        </div>

        <div class="forgot-field">
          <SfInput v-model="form.invite_code" placeholder="注册时使用的激活码">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2"/><path d="M13 17v2"/><path d="M13 11v2"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.invite_code" class="forgot-error">{{ errors.invite_code }}</p>
        </div>

        <div class="forgot-field">
          <SfInput v-model="form.new_password" type="password" placeholder="新密码（至少 6 位）">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.new_password" class="forgot-error">{{ errors.new_password }}</p>
        </div>

        <div class="forgot-field">
          <SfInput v-model="form.confirmPassword" type="password" placeholder="确认新密码">
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </template>
          </SfInput>
          <p v-if="errors.confirmPassword" class="forgot-error">{{ errors.confirmPassword }}</p>
        </div>

        <div class="forgot-tip">
          忘记激活码？请联系客服
        </div>

        <SfButton
          type="primary"
          size="lg"
          block
          :loading="loading"
          html-type="submit"
          class="forgot-submit"
        >
          重置密码
        </SfButton>
      </form>

      <div class="forgot-footer">
        <router-link to="/login" class="forgot-link">返回登录</router-link>
        <span class="forgot-divider">|</span>
        <router-link to="/register" class="forgot-link">去注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  phone: '',
  invite_code: '',
  new_password: '',
  confirmPassword: ''
})

const errors = reactive({
  phone: '',
  invite_code: '',
  new_password: '',
  confirmPassword: ''
})

function validate() {
  Object.keys(errors).forEach(k => errors[k] = '')

  if (!form.phone) {
    errors.phone = '请输入手机号'
  } else if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    errors.phone = '请输入正确的手机号'
  }

  if (!form.invite_code) {
    errors.invite_code = '请输入激活码'
  }

  if (!form.new_password) {
    errors.new_password = '请输入新密码'
  } else if (form.new_password.length < 6) {
    errors.new_password = '新密码至少 6 个字符'
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认新密码'
  } else if (form.confirmPassword !== form.new_password) {
    errors.confirmPassword = '两次输入的密码不一致'
  }

  return !Object.values(errors).some(e => e)
}

const handleReset = async () => {
  if (!validate()) return
  loading.value = true
  try {
    await authAPI.forgotPassword(form.phone, form.invite_code, form.new_password)
    // toast 提示由 axios 拦截器统一处理
    router.push('/login')
  } catch (e) {
    // axios 拦截器已 toast 错误
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-page {
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

.forgot-decor {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.forgot-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
}

.forgot-glow-1 {
  top: -10%;
  left: -8%;
  width: 480px;
  height: 480px;
  opacity: 0.16;
  background: radial-gradient(circle, var(--color-brand) 0%, transparent 70%);
  animation: forgot-float 12s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.forgot-glow-2 {
  bottom: -10%;
  right: -8%;
  width: 420px;
  height: 420px;
  opacity: 0.14;
  background: radial-gradient(circle, var(--color-accent) 0%, transparent 70%);
  animation: forgot-float 14s cubic-bezier(0.4, 0, 0.2, 1) infinite reverse;
}

.forgot-grid {
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

@keyframes forgot-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(12px, -8px) scale(1.02); }
}

.forgot-card {
  position: relative;
  width: 100%;
  max-width: 480px;
  padding: 44px 40px 32px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  animation: forgot-enter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes forgot-enter {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.forgot-header {
  text-align: center;
  margin-bottom: 32px;
}

.forgot-logo {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  background: var(--color-brand);
  box-shadow: 0 6px 20px rgba(77, 160, 108, 0.22);
}

.forgot-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
  margin: 0 0 6px 0;
}

.forgot-subtitle {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}

.forgot-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.forgot-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.forgot-error {
  font-size: 12px;
  color: var(--color-danger);
  margin: 0;
}

.forgot-tip {
  font-size: 12px;
  color: var(--color-text-secondary);
  background: var(--color-bg-base);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  text-align: center;
  margin-top: -4px;
}

.forgot-submit {
  margin-top: 6px;
  height: 48px !important;
  font-size: 16px;
  font-weight: 600;
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%)) !important;
  border: none;
  border-radius: var(--radius-full, 9999px);
  width: 100%;
  box-shadow: 0 6px 20px rgba(77, 160, 108, 0.28);
  transition: transform var(--sf-duration-normal) cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.25s ease;
}

.forgot-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(77, 160, 108, 0.38);
}

.forgot-submit:active {
  transform: translateY(0) scale(0.98);
}

.forgot-footer {
  text-align: center;
  margin-top: 22px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.forgot-link {
  font-weight: 600;
  color: var(--color-brand);
  text-decoration: none;
  transition: color var(--sf-duration-normal);
}

.forgot-link:hover {
  color: var(--color-accent);
}

.forgot-divider {
  margin: 0 12px;
  color: var(--color-border);
}

/* ── H5 原生 App 形态 (≤768px) ── */
@media (max-width: 768px) {
  .forgot-page {
    display: block;
    align-items: initial;
    min-height: 100vh;
    margin: 0;
    padding: 0;
    background: radial-gradient(
      ellipse at top,
      rgba(77, 160, 108, 0.06) 0%,
      var(--color-bg-base) 55%
    );
    overflow-y: auto;                   /* 字段多, 允许滚动 */
  }

  /* H5 隐藏 PC 装饰背景 */
  .forgot-decor {
    display: none;
  }

  .forgot-card {
    max-width: none;
    padding: 48px 20px 32px;
    background: transparent;
    border: none;
    border-radius: 0;
    box-shadow: none;
    animation: none;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;            /* 整体垂直居中, 内容多时自动滚动 */
  }

  .forgot-header {
    text-align: center;                 /* logo + 标题 + 副标题居中 */
    margin-bottom: 28px;
  }
  .forgot-logo {
    width: 52px;
    height: 52px;
    margin: 0 auto 16px;
    border-radius: var(--radius-lg);
  }
  .forgot-title {
    font-size: 22px;
    margin: 0 0 6px 0;
  }
  .forgot-subtitle {
    font-size: 13px;
  }

  .forgot-form {
    gap: 16px;
  }

  .forgot-tip {
    font-size: 12px;
    padding: 10px 12px;
  }

  .forgot-footer {
    text-align: center;                 /* "返回登录 | 去注册" 居中 */
    margin-top: 28px;
    font-size: 13px;
  }

  .forgot-submit {
    height: 48px !important;            /* 满足 --touch-target-min: 44px */
  }
}

/* ── 超小屏微调 (<481px) ── */
@media (max-width: 480px) {
  .forgot-card {
    padding: 32px 16px 24px;
    justify-content: flex-start;        /* 字段多, 改为顶对齐避免遮挡 */
  }
  .forgot-title {
    font-size: 20px;
  }
}
</style>
