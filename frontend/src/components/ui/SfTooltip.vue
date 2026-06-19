<template>
  <div class="sf-tooltip" @mouseenter="show" @mouseleave="hide">
    <slot />
    <Transition name="sf-tooltip">
      <div v-if="visible" class="sf-tooltip-popup" :class="`sf-tooltip--${placement}`">
        {{ content }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  content: { type: String, default: '' },
  placement: { type: String, default: 'top' },
})

const visible = ref(false)
let timer = null

function show() {
  clearTimeout(timer)
  timer = setTimeout(() => { visible.value = true }, 100)
}

function hide() {
  clearTimeout(timer)
  timer = setTimeout(() => { visible.value = false }, 100)
}
</script>

<style scoped>
.sf-tooltip {
  position: relative;
  display: inline-flex;
}

.sf-tooltip-popup {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 10px;
  font-size: 12px;
  line-height: 1.4;
  color: #fff;
  background: #1f2937;
  border-radius: 6px;
  white-space: nowrap;
  z-index: var(--z-tooltip);
  pointer-events: none;
}

.sf-tooltip--top {
  bottom: calc(100% + 6px);
}

.sf-tooltip--bottom {
  top: calc(100% + 6px);
}

.sf-tooltip-enter-active,
.sf-tooltip-leave-active {
  transition: opacity var(--sf-duration-fast);
}
.sf-tooltip-enter-from,
.sf-tooltip-leave-to {
  opacity: 0;
}
</style>
