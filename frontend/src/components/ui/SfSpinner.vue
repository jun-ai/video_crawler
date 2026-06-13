<template>
  <div class="sf-spinner" :class="[`sf-spinner--${size}`]" />
</template>

<script setup>
defineProps({
  size: { type: String, default: 'md' }, // sm, md, lg
})
</script>

<style scoped>
.sf-spinner {
  border: 2px solid var(--color-border);
  border-right-color: var(--color-brand);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.sf-spinner--sm { width: 16px; height: 16px; }
.sf-spinner--md { width: 24px; height: 24px; }
.sf-spinner--lg { width: 40px; height: 40px; border-width: 3px; }

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
