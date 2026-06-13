<template>
  <div class="page-header">
    <div class="header-left">
    <h1 class="page-title" v-if="title">{{ title }}</h1>
    <div class="page-subtitle" v-if="subtitle">{{ subtitle }}</div>
  </div>
    <div class="header-actions" v-if="$slots.actions">
    <slot name="actions"></slot>
  </div>
  <div class="header-extra" v-if="$slots.extra">
    <slot name="extra"></slot>
  </div>
  </div>
</template>

<script setup>
defineProps({
  // 页面标题
  title: {
    type: String,
    default: ''
  },
  // 副标题
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg, 24px);
  padding: var(--spacing-md, 16px) 0;
}

.header-left {
  flex: 1;
  min-width: 0;
}

.page-title {
  font-size: var(--font-size-3xl, 24px);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-primary);
  margin: 0;
  line-height: var(--line-height-tight, 1.25);
}

.page-subtitle {
  font-size: var(--font-size-sm, 14px);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs, 4px);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 8px);
  flex-shrink: 0;
}

.header-extra {
  margin-left: var(--spacing-md, 16px);
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm, 8px);
    margin-bottom: var(--spacing-md, 16px);
    padding: var(--spacing-sm, 8px) 0;
  }

  .page-title {
    font-size: var(--font-size-2xl, 20px);
  }

  .page-subtitle {
    font-size: var(--font-size-xs, 12px);
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: var(--font-size-xl, 18px);
  }
}
</style>
