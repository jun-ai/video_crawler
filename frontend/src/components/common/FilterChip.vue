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
    <component v-if="icon" :is="icon" :size="14" class="chip-icon" />
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
  icon: {
    type: Object,
    default: null
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
  gap: 5px;
  padding: 8px 18px;
  background: var(--color-bg-card);
  border: 1.5px solid var(--color-border);
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  user-select: none;
  white-space: nowrap;
  font-family: inherit;
  line-height: 1.4;
}

.chip-icon {
  flex-shrink: 0;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.sf-filter-chip:hover {
  border-color: var(--color-brand);
  color: var(--color-text-primary);
  transform: translateY(-1px);
}

.sf-filter-chip:hover .chip-icon {
  opacity: 1;
}

.sf-filter-chip:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
}

.sf-filter-chip.active {
  background: var(--color-brand);
  color: #fff;
  border-color: var(--color-brand);
  box-shadow: 0 2px 8px rgba(15, 76, 58, 0.25);
}

.sf-filter-chip.active .chip-icon {
  opacity: 1;
}

.chip-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  padding: 0 5px;
  margin-left: 2px;
  font-size: 10px;
  font-weight: 600;
  border-radius: 9px;
  background: rgba(0, 0, 0, 0.06);
  color: var(--color-text-muted);
}

.sf-filter-chip.active .chip-count {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
}
</style>
