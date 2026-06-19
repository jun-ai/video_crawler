<template>
  <Teleport to="body">
    <div class="sf-toast-container">
      <TransitionGroup name="sf-toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="sf-toast"
          :class="`sf-toast--${t.type}`"
        >
          <span class="sf-toast-icon">
            <!-- success -->
            <svg v-if="t.type === 'success'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <!-- error -->
            <svg v-else-if="t.type === 'error'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            <!-- warning -->
            <svg v-else-if="t.type === 'warning'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <!-- info -->
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          </span>
          <span class="sf-toast-msg">{{ t.message }}</span>
          <!-- 4-P1-6: 可选 action 按钮 (撤销等) -->
          <button
            v-if="t.action"
            class="sf-toast-action"
            @click="onAction(t)"
          >
            {{ t.action.label }}
          </button>
          <button v-if="t.showClose" class="sf-toast-close" @click="removeToast(t.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { toasts, removeToast } from '@/composables/useToast'

const onAction = (t) => {
  if (t.action && typeof t.action.onClick === 'function') {
    try {
      t.action.onClick()
    } catch (e) {
      console.error('toast action failed:', e)
    }
  }
  removeToast(t.id)
}
</script>

<style scoped>
.sf-toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.sf-toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  min-width: 280px;
  max-width: 420px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: var(--shadow-lg);
  pointer-events: auto;
  font-size: 14px;
  color: var(--color-text-primary);
}

.sf-toast--success .sf-toast-icon { color: var(--color-success); }
.sf-toast--error .sf-toast-icon { color: var(--color-danger); }
.sf-toast--warning .sf-toast-icon { color: var(--color-warning); }
.sf-toast--info .sf-toast-icon { color: var(--color-brand); }

.sf-toast-icon {
  display: flex;
  flex-shrink: 0;
}

.sf-toast-msg {
  flex: 1;
  line-height: 1.4;
}

/* 4-P1-6: action 按钮 (撤销等) */
.sf-toast-action {
  padding: 4px 10px;
  border-radius: 6px;
  background: transparent;
  color: var(--color-brand);
  border: 1px solid var(--color-brand);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}
.sf-toast-action:hover {
  background: var(--color-brand);
  color: #fff;
}

.sf-toast-close {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 2px;
  flex-shrink: 0;
}
.sf-toast-close:hover {
  color: var(--color-text-primary);
}

.sf-toast-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.sf-toast-leave-active {
  transition: all 0.2s;
}
.sf-toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.sf-toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>
