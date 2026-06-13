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
        class="sf-dropdown-menu"
        :style="{ [placement]: 'calc(100% + 4px)' }"
        role="menu"
      >
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

defineProps({
  placement: { type: String, default: 'top' },
})

const opened = ref(false)
const dropdownRef = ref(null)

function toggle() {
  opened.value = !opened.value
}

function close() {
  opened.value = false
}

function onClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    opened.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))

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
  transition: all 0.15s;
}
.sf-dropdown-enter-from,
.sf-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
