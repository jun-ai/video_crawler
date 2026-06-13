<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] }, // [{ label, value }]
  placeholder: { type: String, default: '请选择' },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'change'])

function handleChange(value) {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<template>
  <Select :model-value="String(modelValue)" @update:model-value="handleChange" :disabled="disabled">
    <SelectTrigger class="sf-select-trigger">
      <SelectValue :placeholder="placeholder" />
    </SelectTrigger>
    <SelectContent class="sf-select-content">
      <SelectGroup v-if="$slots.label">
        <SelectLabel><slot name="label" /></SelectLabel>
      </SelectGroup>
      <SelectItem v-for="opt in options" :key="opt.value" :value="String(opt.value)">
        {{ opt.label }}
      </SelectItem>
      <slot />
    </SelectContent>
  </Select>
</template>

<style scoped>
.sf-select-trigger {
  width: 100%;
  height: 42px;
  border-radius: 10px;
  border-color: var(--border);
  background: var(--card);
}

:deep(.sf-select-content) {
  border-radius: 10px;
  box-shadow: var(--shadow-lg);
}
</style>
