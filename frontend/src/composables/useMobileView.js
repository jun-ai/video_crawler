// useMobileView — Phase 22: 复用 H5 / 桌面判断
// 在 (max-width: 768px) 视口下返回 true
// SSR 安全 (typeof window)

import { ref, onMounted, onBeforeUnmount } from 'vue'

const QUERY = '(max-width: 768px)'

export function useMobileView() {
  const isMobile = ref(false)
  let mql = null
  const onChange = () => { isMobile.value = !!mql?.matches }

  onMounted(() => {
    if (typeof window === 'undefined') return
    mql = window.matchMedia(QUERY)
    isMobile.value = mql.matches
    mql.addEventListener?.('change', onChange)
  })

  onBeforeUnmount(() => {
    mql?.removeEventListener?.('change', onChange)
  })

  return { isMobile }
}
