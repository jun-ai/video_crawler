<template>
  <div class="sf-progress">
    <div class="sf-progress-bar" :style="{ height: `${strokeWidth}px` }">
      <div
        class="sf-progress-fill"
        :class="`sf-progress-fill--${type}`"
        :style="{ width: `${percentage}%` }"
      />
    </div>
    <span v-if="showText" class="sf-progress-text">{{ Math.round(percentage) }}%</span>
  </div>
</template>

<script setup>
defineProps({
  percentage: { type: Number, default: 0 },
  strokeWidth: { type: Number, default: 6 },
  type: { type: String, default: 'brand' }, // brand, success, danger
  showText: { type: Boolean, default: false },
})
</script>

<style scoped>
.sf-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.sf-progress-bar {
  flex: 1;
  background: var(--color-bg-elevated);
  border-radius: 9999px;
  overflow: hidden;
}

.sf-progress-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width var(--sf-duration-slow) cubic-bezier(0.4, 0, 0.2, 1);
}

.sf-progress-fill--brand {
  background: linear-gradient(90deg, var(--color-brand), var(--color-accent));
}

.sf-progress-fill--success {
  background: var(--color-success);
}

.sf-progress-fill--danger {
  background: var(--color-danger);
}

.sf-progress-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  min-width: 36px;
  text-align: right;
}
</style>
