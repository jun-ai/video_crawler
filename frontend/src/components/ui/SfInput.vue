<template>
  <div class="sf-input-wrap" :class="{ 'sf-input--focused': focused, 'sf-input--disabled': disabled }">
    <div v-if="$slots.prefix" class="sf-input-prefix">
      <slot name="prefix" />
    </div>
    <input
      v-if="!textarea"
      ref="inputRef"
      :type="showPassword ? 'text' : type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :maxlength="maxlength"
      class="sf-input"
      @input="$emit('update:modelValue', $event.target.value)"
      @focus="focused = true"
      @blur="focused = false"
      @keydown.enter="$emit('enter')"
    />
    <textarea
      v-else
      ref="inputRef"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :maxlength="maxlength"
      :rows="rows"
      class="sf-input sf-textarea"
      @input="$emit('update:modelValue', $event.target.value)"
      @focus="focused = true"
      @blur="focused = false"
    />
    <div v-if="clearable && modelValue" class="sf-input-clear" @click="handleClear">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/></svg>
    </div>
    <div v-if="type === 'password'" class="sf-input-suffix" @click="showPassword = !showPassword" style="cursor:pointer">
      <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
    </div>
    <div v-if="$slots.suffix" class="sf-input-suffix">
      <slot name="suffix" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: { type: [String, Number], default: '' },
  placeholder: { type: String, default: '' },
  type: { type: String, default: 'text' },
  disabled: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  clearable: { type: Boolean, default: false },
  maxlength: { type: Number, default: undefined },
  textarea: { type: Boolean, default: false },
  rows: { type: Number, default: 3 },
})

const emit = defineEmits(['update:modelValue', 'enter', 'clear'])

const focused = ref(false)
const showPassword = ref(false)
const inputRef = ref(null)

function handleClear() {
  emit('update:modelValue', '')
  emit('clear')
}

function focus() {
  inputRef.value?.focus()
}

defineExpose({ focus })
</script>

<style scoped>
.sf-input-wrap {
  display: flex;
  align-items: center;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  transition: all var(--sf-duration-normal);
  overflow: hidden;
}

.sf-input--focused {
  border-color: var(--color-brand);
  box-shadow: 0 0 0 3px var(--color-brand-subtle);
}

.sf-input--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sf-input {
  flex: 1;
  height: 42px;
  padding: 0 14px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: transparent;
  border: none;
  outline: none;
  font-family: inherit;
  min-width: 0;
}

.sf-textarea {
  height: auto;
  padding: 10px 14px;
  resize: vertical;
  min-height: 80px;
  line-height: 1.5;
}

.sf-input::placeholder {
  color: var(--color-text-muted);
}

.sf-input-prefix,
.sf-input-suffix {
  display: flex;
  align-items: center;
  padding: 0 10px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.sf-input-prefix {
  padding-right: 0;
}

.sf-input-clear {
  display: flex;
  align-items: center;
  padding: 0 8px;
  color: var(--color-text-muted);
  cursor: pointer;
  flex-shrink: 0;
}
.sf-input-clear:hover { color: var(--color-text-secondary); }
</style>
