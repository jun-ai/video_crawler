import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

function addToast(options) {
  const id = ++toastId
  const t = {
    id,
    type: options.type || 'info',
    message: options.message || '',
    duration: options.duration ?? 3000,
    showClose: options.showClose ?? false,
  }
  toasts.value.push(t)

  if (t.duration > 0) {
    setTimeout(() => removeToast(id), t.duration)
  }
  return id
}

function removeToast(id) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

export function useToast() {
  return { toast: _toast, toasts, removeToast }
}

// 单例 toast 对象
const _toast = {
  success: (message, options = {}) => addToast({ ...options, type: 'success', message }),
  error: (message, options = {}) => addToast({ ...options, type: 'error', message, duration: options.duration ?? 4000 }),
  warning: (message, options = {}) => addToast({ ...options, type: 'warning', message }),
  info: (message, options = {}) => addToast({ ...options, type: 'info', message }),
  // 4-P1-6: 支持 action 按钮 (撤销等), options.action = { label, onClick }
  withAction: (message, action, options = {}) => addToast({
    ...options, type: options.type ?? 'info', message, action,
    duration: options.duration ?? 5000
  }),
  close: removeToast,
}

export { toasts, removeToast }
export const toast = _toast
