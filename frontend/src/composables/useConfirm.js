import { ref } from 'vue'

const confirmState = ref({
  visible: false,
  title: '',
  message: '',
  type: 'warning',
  confirmText: '确定',
  cancelText: '取消',
  onConfirm: null,
  onCancel: null,
})

export function showConfirm(options) {
  return new Promise((resolve) => {
    confirmState.value = {
      visible: true,
      title: options.title || '确认',
      message: options.message || '',
      type: options.type || 'warning',
      confirmText: options.confirmText || '确定',
      cancelText: options.cancelText || '取消',
      onConfirm: () => {
        confirmState.value.visible = false
        resolve(true)
      },
      onCancel: () => {
        confirmState.value.visible = false
        resolve(false)
      },
    }
  })
}

export { confirmState }
