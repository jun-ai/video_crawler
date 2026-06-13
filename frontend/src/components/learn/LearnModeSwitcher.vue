<!--
  LearnModeSwitcher.vue - Phase 1B Task 3
  跟读 / 听写 模式切换控件
-->
<template>
  <div class="sf-segment">
    <button
      type="button"
      :class="['sf-segment__item', { active: modelValue === 'shadowing' }]"
      @click="$emit('update:modelValue', 'shadowing')"
    >
      <Mic :size="16" />
      <span>跟读模式</span>
    </button>
    <button
      type="button"
      :class="['sf-segment__item', { active: modelValue === 'dictation' }]"
      @click="$emit('update:modelValue', 'dictation')"
    >
      <Edit3 :size="16" />
      <span>听写模式</span>
    </button>
  </div>
</template>

<script setup>
import { Mic, Edit3 } from 'lucide-vue-next'

defineProps({
  modelValue: {
    type: String,
    required: true,
    validator: (v) => ['shadowing', 'dictation'].includes(v)
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.sf-segment {
  display: inline-flex;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-full);
  padding: 4px;
  gap: 2px;
  margin: 0 0 16px;
  border: 1px solid var(--color-border);
}

.sf-segment__item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: var(--radius-full);
  background: transparent;
  border: none;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast);
  -webkit-tap-highlight-color: transparent;
}

.sf-segment__item:hover {
  color: var(--color-text-primary);
}

.sf-segment__item.active {
  background: var(--color-brand);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.sf-segment__item:active {
  transform: scale(0.97);
}
</style>