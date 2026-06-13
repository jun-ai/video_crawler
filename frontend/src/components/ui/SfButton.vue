<script setup lang="ts">
import { computed } from 'vue'
import { Button as ShadcnButton } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const props = defineProps({
  type: { type: String, default: 'default' }, // primary, ghost, danger, subtle, default
  size: { type: String, default: 'md' },      // sm, md, lg
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
  htmlType: { type: String, default: 'button' },
  round: { type: Boolean, default: false },
})

defineEmits(['click'])

// 映射 type 到 shadcn variant
const variantMap: Record<string, string> = {
  primary: 'default',
  default: 'outline',
  ghost: 'ghost',
  danger: 'destructive',
  subtle: 'secondary',
}

const computedVariant = computed(() => variantMap[props.type] || 'outline')

// 映射 size
const sizeMap: Record<string, string> = {
  sm: 'sm',
  md: 'default',
  lg: 'lg',
}

const computedSize = computed(() => sizeMap[props.size] || 'default')

// 额外类名
const extraClass = computed(() => cn(
  props.block && 'w-full',
  props.round && 'rounded-full'
))
</script>

<template>
  <ShadcnButton
    :variant="computedVariant"
    :size="computedSize"
    :disabled="disabled || loading"
    :type="htmlType"
    :class="extraClass"
    @click="$emit('click', $event)"
  >
    <template v-if="loading">
      <span class="sf-btn-spinner" />
    </template>
    <slot />
  </ShadcnButton>
</template>

<style scoped>
.sf-btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 4px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
