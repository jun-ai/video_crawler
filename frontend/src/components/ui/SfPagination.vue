<template>
  <div class="sf-pagination">
    <button class="sf-pagination-btn" :disabled="currentPage <= 1" @click="change(currentPage - 1)">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
    </button>

    <template v-for="page in displayedPages" :key="page">
      <span v-if="page === '...'" class="sf-pagination-ellipsis">...</span>
      <button
        v-else
        class="sf-pagination-btn sf-pagination-num"
        :class="{ 'sf-pagination-num--active': page === currentPage }"
        @click="change(page)"
      >
        {{ page }}
      </button>
    </template>

    <button class="sf-pagination-btn" :disabled="currentPage >= totalPages" @click="change(currentPage + 1)">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  total: { type: Number, default: 0 },
})

const emit = defineEmits(['update:currentPage', 'change'])

const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1)

const displayedPages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = props.currentPage

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

function change(page) {
  if (page < 1 || page > totalPages.value || page === props.currentPage) return
  emit('update:currentPage', page)
  emit('change', page)
}
</script>

<style scoped>
.sf-pagination {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sf-pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.15s;
  font-size: 14px;
}

.sf-pagination-btn:hover:not(:disabled) {
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
}

.sf-pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.sf-pagination-num--active {
  background: var(--color-brand) !important;
  color: #fff !important;
  font-weight: 600;
}

.sf-pagination-ellipsis {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  color: var(--color-text-muted);
  font-size: 14px;
}
</style>
