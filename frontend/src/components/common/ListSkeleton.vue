<template>
  <div class="list-skeleton">
    <div
      v-for="i in count"
      :key="i"
      class="skeleton-item"
      :class="{ 'list-mode': listMode }"
    >
      <div class="skeleton-thumbnail skeleton-pulse" />
      <div class="skeleton-content">
        <div class="skeleton-title skeleton-pulse" />
        <div class="skeleton-text skeleton-pulse" />
        <div class="skeleton-meta skeleton-pulse" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  count: {
    type: Number,
    default: 6
  },
  listMode: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.list-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.list-mode {
  display: flex;
  gap: 12px;
}

.skeleton-item {
  background: var(--color-bg-card);
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.list-mode.skeleton-item {
  display: flex;
  border-radius: 10px;
}

.skeleton-thumbnail {
  width: 100%;
  padding-bottom: 56.25%;
  background: var(--color-bg-elevated);
}

.list-mode .skeleton-thumbnail {
  width: 160px;
  min-width: 160px;
  height: 90px;
  padding-bottom: 0;
  border-radius: 10px 0 0 10px;
}

.skeleton-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-title {
  height: 16px;
  background: var(--color-bg-elevated);
  border-radius: 4px;
  width: 80%;
}

.skeleton-text {
  height: 12px;
  background: var(--color-bg-elevated);
  border-radius: 4px;
  width: 60%;
}

.skeleton-meta {
  height: 12px;
  background: var(--color-bg-elevated);
  border-radius: 4px;
  width: 40%;
  margin-top: 4px;
}

.skeleton-pulse {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 响应式 */
@media (max-width: 768px) {
  .list-skeleton {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .list-skeleton {
    grid-template-columns: 1fr;
  }
}
</style>
