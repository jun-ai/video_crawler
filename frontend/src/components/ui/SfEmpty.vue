<template>
  <div class="sf-empty">
    <div class="sf-empty-icon">
      <slot name="icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
          <line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>
      </slot>
    </div>
    <p class="sf-empty-text">{{ description || '暂无数据' }}</p>
    <div v-if="$slots.default" class="sf-empty-action">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  description: { type: String, default: '' },
})
</script>

<style scoped>
.sf-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
}

.sf-empty-icon {
  color: var(--color-text-muted);
  opacity: 0.5;
  margin-bottom: 16px;
}

.sf-empty-text {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0 0 16px;
}

.sf-empty-action {
  margin-top: 4px;
}
</style>
