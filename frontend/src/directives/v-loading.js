const vLoading = {
  mounted(el, binding) {
    const isLoading = binding.value
    if (isLoading) createSpinner(el)
  },
  updated(el, binding) {
    if (binding.value) {
      if (!el.__loadingOverlay) createSpinner(el)
    } else {
      removeSpinner(el)
    }
  },
  unmounted(el) {
    removeSpinner(el)
  }
}

function createSpinner(el) {
  if (el.__loadingOverlay) return

  el.style.position = el.style.position || 'relative'

  const overlay = document.createElement('div')
  overlay.className = 'sf-loading-overlay'
  overlay.innerHTML = '<div class="sf-loading-spinner"></div>'
  el.appendChild(overlay)
  el.__loadingOverlay = overlay
}

function removeSpinner(el) {
  if (el.__loadingOverlay) {
    el.__loadingOverlay.remove()
    el.__loadingOverlay = null
  }
}

export default vLoading
