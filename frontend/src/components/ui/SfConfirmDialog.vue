<template>
  <Teleport to="body">
    <Transition name="sf-confirm">
      <div v-if="confirmState.visible" class="sf-confirm-overlay" @click.self="confirmState.onCancel?.()">
        <div class="sf-confirm-dialog">
          <h4 class="sf-confirm-title">{{ confirmState.title }}</h4>
          <p class="sf-confirm-msg">{{ confirmState.message }}</p>
          <div class="sf-confirm-actions">
            <button class="sf-confirm-btn sf-confirm-btn--cancel" @click="confirmState.onCancel?.()">
              {{ confirmState.cancelText }}
            </button>
            <button
              class="sf-confirm-btn"
              :class="`sf-confirm-btn--${confirmState.type}`"
              @click="confirmState.onConfirm?.()"
            >
              {{ confirmState.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { confirmState } from '@/composables/useConfirm'
</script>

<style scoped>
.sf-confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
}

.sf-confirm-dialog {
  background: var(--color-bg-card);
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18), 0 4px 8px rgba(0, 0, 0, 0.10);
  padding: 24px;
  width: 400px;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
  /* 单一 scale 动画,去掉 opacity 避免双层透明叠加造成的"虚化"感 */
  animation: sf-confirm-scale-in 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes sf-confirm-scale-in {
  from { transform: scale(0.95); }
  to { transform: scale(1); }
}

.sf-confirm-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px;
}

.sf-confirm-msg {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0 0 20px;
  line-height: 1.5;
}

.sf-confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.sf-confirm-btn {
  padding: 9px 20px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  min-height: 38px;
  transition: all var(--sf-duration-fast);
}
.sf-confirm-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.sf-confirm-btn--cancel {
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}
.sf-confirm-btn--cancel:hover {
  background: var(--color-border);
}

.sf-confirm-btn--warning {
  background: var(--color-warning);
  color: #fff;
}
.sf-confirm-btn--warning:hover { background: #d97706; }

.sf-confirm-btn--danger {
  background: var(--color-danger);
  color: #fff;
}
.sf-confirm-btn--danger:hover { background: #dc2626; }

/* Overlay 用纯背景淡入,不再动 dialog 本身 opacity (避免双层透明) */
.sf-confirm-enter-active,
.sf-confirm-leave-active {
  transition: background-color var(--sf-duration-normal);
}
.sf-confirm-enter-from,
.sf-confirm-leave-to {
  background-color: rgba(0, 0, 0, 0);
}
</style>
