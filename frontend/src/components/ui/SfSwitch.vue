<template>
  <button
    class="sf-switch"
    :class="{ 'sf-switch--active': modelValue, 'sf-switch--disabled': disabled }"
    :aria-checked="modelValue"
    :aria-label="label || '开关'"
    role="switch"
    tabindex="0"
    @click="toggle"
    @keydown.space.prevent="toggle"
    @keydown.enter.prevent="toggle"
  >
    <span class="sf-switch-dot" />
    <span v-if="label" class="sf-switch-label">{{ label }}</span>
  </button>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  label: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'change'])

function toggle() {
  if (!props.disabled) {
    emit('update:modelValue', !props.modelValue)
    emit('change', !props.modelValue)
  }
}
</script>

<style scoped>
.sf-switch {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--color-border-strong);
  border-radius: 9999px;
  transition: background 0.2s, box-shadow 0.2s;
}

.sf-switch:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
}

.sf-switch--active {
  background: var(--color-brand);
}

.sf-switch--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sf-switch-dot {
  position: absolute;
  left: 2px;
  top: 2px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.sf-switch--active .sf-switch-dot {
  transform: translateX(20px);
}

.sf-switch-label {
  position: absolute;
  left: calc(100% + 8px);
  white-space: nowrap;
  font-size: 14px;
  color: var(--color-text-secondary);
  width: max-content;
}
</style>
