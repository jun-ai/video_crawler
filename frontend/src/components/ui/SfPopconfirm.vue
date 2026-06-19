<template>
  <div class="sf-popconfirm" ref="popRef">
    <div class="sf-popconfirm-trigger" @click="visible = !visible">
      <slot />
    </div>
    <Transition name="sf-popconfirm">
      <div v-if="visible" class="sf-popconfirm-popup">
        <p class="sf-popconfirm-text">{{ title }}</p>
        <div class="sf-popconfirm-actions">
          <button class="sf-popconfirm-btn sf-popconfirm-btn--cancel" @click="cancel">取消</button>
          <button class="sf-popconfirm-btn sf-popconfirm-btn--confirm" @click="confirm">确定</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

defineProps({
  title: { type: String, default: '确定要执行此操作吗？' },
})

const emit = defineEmits(['confirm', 'cancel'])
const visible = ref(false)
const popRef = ref(null)

function confirm() {
  visible.value = false
  emit('confirm')
}

function cancel() {
  visible.value = false
  emit('cancel')
}

function onClickOutside(e) {
  if (popRef.value && !popRef.value.contains(e.target)) {
    visible.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.sf-popconfirm {
  position: relative;
  display: inline-flex;
}

.sf-popconfirm-popup {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: var(--shadow-lg);
  padding: 14px 16px;
  z-index: var(--z-popover);
  min-width: 200px;
}

.sf-popconfirm-text {
  font-size: 14px;
  color: var(--color-text-primary);
  margin: 0 0 12px;
  line-height: 1.5;
}

.sf-popconfirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.sf-popconfirm-btn {
  padding: 5px 14px;
  font-size: 13px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all var(--sf-duration-fast);
}

.sf-popconfirm-btn--cancel {
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}
.sf-popconfirm-btn--cancel:hover {
  background: var(--color-border);
}

.sf-popconfirm-btn--confirm {
  background: var(--color-brand);
  color: #fff;
}
.sf-popconfirm-btn--confirm:hover {
  background: var(--color-brand-hover);
}

.sf-popconfirm-enter-active,
.sf-popconfirm-leave-active {
  transition: all var(--sf-duration-fast);
}
.sf-popconfirm-enter-from,
.sf-popconfirm-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(4px);
}
</style>
