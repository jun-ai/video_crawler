<template>
  <div
    class="sf-filter-chip"
    :class="{ active: modelValue === value }"
    role="button"
    :aria-pressed="modelValue === value"
    tabindex="0"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <slot>{{ label }}</slot>
    <span v-if="count != null" class="chip-count">{{ count }}</span>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean, null],
    default: null
  },
  value: {
    type: [String, Number, Boolean, null],
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  count: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'click'])

const handleClick = () => {
  emit('update:modelValue', props.value)
  emit('click', props.value)
}
</script>

<style scoped>
.sf-filter-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 12px;
  background: var(--color-bg-elevated);
  border: 1px solid transparent;
  border-radius: var(--sf-radius-full);
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-bounce);
  user-select: none;
  white-space: nowrap;
  font-family: inherit;
  line-height: 1.4;
}

.sf-filter-chip:hover {
  border-color: var(--color-border);
  color: var(--color-text-primary);
}

.sf-filter-chip:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
}

.sf-filter-chip.active {
  background: var(--color-brand);
  color: #fff;
  box-shadow: var(--sf-shadow-sm);
}

.chip-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  padding: 0 4px;
  margin-left: 4px;
  font-size: 10px;
  font-weight: 600;
  border-radius: var(--sf-radius-full);
  background: rgba(0, 0, 0, 0.08);
  color: var(--color-text-muted);
}

.sf-filter-chip.active .chip-count {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
}
</style>
