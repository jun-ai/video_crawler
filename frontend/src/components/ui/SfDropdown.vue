<template>
  <div class="sf-dropdown" ref="dropdownRef">
    <div
      class="sf-dropdown-trigger"
      :aria-expanded="opened"
      :aria-haspopup="true"
      role="button"
      tabindex="0"
      @click="toggle"
      @keydown.enter.prevent="toggle"
      @keydown.space.prevent="toggle"
      @keydown.escape="close"
    >
      <slot name="trigger" />
    </div>
    <Transition name="sf-dropdown">
      <div
        v-if="opened"
        ref="menuRef"
        class="sf-dropdown-menu"
        :style="[resolvedPlacementStyle, menuStyle]"
        role="menu"
      >
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  placement: { type: String, default: 'bottom' },
  menuStyle: { type: Object, default: () => ({}) }
})

const opened = ref(false)
const dropdownRef = ref(null)
const menuRef = ref(null)

// placement 解析 — 'top'/'bottom' 控制上下,'-end' 控制右对齐
// 注意: placement 表示菜单相对触发器的方向。CSS 定位用相反边:
//   placement='top'    → 菜单在上方 → 用 bottom:100% 把菜单底边贴到触发器顶部
//   placement='bottom' → 菜单在下方 → 用 top:100% 把菜单顶边贴到触发器底部
const basePlacementStyle = computed(() => {
  const isEnd = props.placement.endsWith('-end')
  const side = props.placement.replace(/-end$/, '')
  const offsetSide = side === 'top' ? 'bottom' : 'top'
  const style = { [offsetSide]: 'calc(100% + 4px)' }
  if (isEnd) { style.left = 'auto'; style.right = '0' }
  return style
})

// viewport auto-flip: 如果按 base placement 打开会超出视口底部, 翻到 top
// 'open' = null (初始, 用 base placement) | 'up' | 'down'
const flipState = ref(null)
const resolvedPlacementStyle = computed(() => {
  const style = { ...basePlacementStyle.value }
  if (flipState.value === 'up') {
    style.top = 'auto'
    style.bottom = 'calc(100% + 4px)'
  } else if (flipState.value === 'down') {
    // 强制 down (overrides base placement='top')
    if (style.bottom) { style.bottom = 'auto' }
    style.top = 'calc(100% + 4px)'
  }
  return style
})

// 预判: 如果按 base placement 打开, 菜单会不会超出视口?
// 用 trigger rect + 预估 menu 高度 (默认 200, 实测后纠正)
function decideSide() {
  if (!dropdownRef.value) return null
  const triggerRect = dropdownRef.value.getBoundingClientRect()
  const menuH = menuRef.value?.offsetHeight || 200
  const margin = 8
  const baseSide = props.placement.replace(/-end$/, '')
  if (baseSide === 'bottom') {
    if (triggerRect.bottom + menuH + margin > window.innerHeight
        && triggerRect.top - menuH - margin > 0) {
      return 'up'
    }
  } else {  // 'top'
    if (triggerRect.top - menuH - margin < 0
        && triggerRect.bottom + menuH + margin < window.innerHeight) {
      return 'down'
    }
  }
  return null  // 用 base placement
}

function toggle() {
  opened.value = !opened.value
  if (opened.value) {
    flipState.value = decideSide()  // 打开前就决定
  }
}

function close() {
  opened.value = false
}

function onClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    opened.value = false
  }
}

function onResize() {
  if (opened.value) {
    flipState.value = decideSide()
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  window.addEventListener('resize', onResize)
  window.addEventListener('scroll', onResize, true)  // 滚动也重测
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('scroll', onResize, true)
})

defineExpose({ close })
</script>

<style scoped>
.sf-dropdown {
  position: relative;
  display: inline-flex;
}

.sf-dropdown-trigger:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
  border-radius: 4px;
}

.sf-dropdown-menu {
  position: absolute;
  left: 0;
  right: auto;
  min-width: 160px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: var(--shadow-lg);
  z-index: var(--z-dropdown);
  padding: 4px;
}

.sf-dropdown-enter-active,
.sf-dropdown-leave-active {
  transition: all var(--sf-duration-fast);
}
.sf-dropdown-enter-from,
.sf-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
