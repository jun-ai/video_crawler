<script setup lang="ts">
import { Badge as ShadcnBadge } from '@/components/ui/badge'

const props = defineProps({
  type: { type: String, default: 'default' }, // default, brand, success, warning, danger
  closable: { type: Boolean, default: false },
})

defineEmits(['close'])

// 映射 type 到 shadcn variant
const variantMap: Record<string, string> = {
  default: 'secondary',
  brand: 'default',
  success: 'default',
  warning: 'default',
  danger: 'destructive',
}
</script>

<template>
  <ShadcnBadge :class="`sf-tag sf-tag--${type}`" :variant="variantMap[type] || 'secondary'">
    <slot />
    <span v-if="closable" class="sf-tag-close" @click.stop="$emit('close')">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </span>
  </ShadcnBadge>
</template>

<style scoped>
.sf-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 24px;
  padding: 0 8px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  white-space: nowrap;
}

.sf-tag--default {
  background: var(--secondary);
  color: var(--secondary-foreground);
}

.sf-tag--brand {
  background: var(--primary);
  color: var(--primary-foreground);
}

.sf-tag--success {
  background: var(--color-success-light);
  color: var(--color-success);
}

.sf-tag--warning {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.sf-tag--danger {
  background: var(--destructive);
  color: var(--destructive-foreground);
}

.sf-tag-close {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  opacity: 0.6;
  margin-left: 2px;
}
.sf-tag-close:hover { opacity: 1; }
</style>
