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
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
}

.sf-confirm-dialog {
  background: var(--color-bg-card);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  padding: 24px;
  width: 400px;
  max-width: 90vw;
  animation: scale-in 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
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
  padding: 8px 18px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--sf-duration-fast);
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

.sf-confirm-enter-active,
.sf-confirm-leave-active {
  transition: opacity var(--sf-duration-normal);
}
.sf-confirm-enter-from,
.sf-confirm-leave-to {
  opacity: 0;
}
</style>
