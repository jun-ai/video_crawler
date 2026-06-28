<template>
  <div class="sf-popconfirm" ref="popRef">
    <div class="sf-popconfirm-trigger" @click="toggle">
      <slot />
    </div>
    <Teleport to="body">
      <Transition name="sf-popconfirm">
        <div
          v-if="visible"
          class="sf-popconfirm-popup"
          :style="popupStyle"
        >
          <p class="sf-popconfirm-text">{{ title }}</p>
          <div class="sf-popconfirm-actions">
            <button class="sf-popconfirm-btn sf-popconfirm-btn--cancel" @click="cancel">取消</button>
            <button class="sf-popconfirm-btn sf-popconfirm-btn--confirm" @click="confirm">确定</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  title: { type: String, default: '确定要执行此操作吗？' },
  placement: { type: String, default: 'top' },  // 'top' = 弹在 trigger 上方, 'bottom' = 下方
})

const emit = defineEmits(['confirm', 'cancel'])
const visible = ref(false)
const popRef = ref(null)
const popupStyle = ref({})

// 计算弹层位置 (基于 trigger 的 getBoundingClientRect, 弹在 viewport 坐标系)
async function updatePosition() {
  await nextTick()
  if (!popRef.value) return
  const triggerEl = popRef.value.querySelector('.sf-popconfirm-trigger')
  if (!triggerEl) return
  const rect = triggerEl.getBoundingClientRect()
  const popupWidth = 240  // min-width + padding, 用于居中
  const offset = 8
  let top, left
  if (props.placement === 'bottom') {
    top = rect.bottom + offset
  } else {
    // top: 弹在 trigger 上方
    top = rect.top - offset
    // 高度未知 (弹层渲染后), 默认 90px (大致估算: title 一行 + actions 一行 + padding)
    top -= 90
  }
  left = rect.left + rect.width / 2 - popupWidth / 2
  // viewport 边界保护 (避免超出屏幕)
  const vw = window.innerWidth
  if (left < 8) left = 8
  if (left + popupWidth > vw - 8) left = vw - popupWidth - 8
  popupStyle.value = {
    position: 'fixed',
    top: `${top}px`,
    left: `${left}px`,
    width: `${popupWidth}px`,
  }
}

function toggle(e) {
  e?.stopPropagation()
  visible.value = !visible.value
  if (visible.value) {
    updatePosition()
  }
}

function confirm(e) {
  e?.stopPropagation()
  visible.value = false
  emit('confirm')
}

function cancel(e) {
  e?.stopPropagation()
  visible.value = false
  emit('cancel')
}

function onClickOutside(e) {
  if (!visible.value) return
  if (popRef.value && !popRef.value.contains(e.target)) {
    // 也检查弹层本身 (Teleport 到 body, 不在 popRef 里)
    const popup = document.querySelector('.sf-popconfirm-popup')
    if (popup && popup.contains(e.target)) return
    visible.value = false
  }
}

function onScrollOrResize() {
  if (visible.value) {
    updatePosition()
  }
}

// 绑定 document 事件 (click outside + scroll + resize)
import { onMounted, onBeforeUnmount } from 'vue'
onMounted(() => {
  // capture phase 防止 trigger click 立刻被 onClickOutside 关掉
  document.addEventListener('click', onClickOutside, true)
  window.addEventListener('scroll', onScrollOrResize, true)
  window.addEventListener('resize', onScrollOrResize)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside, true)
  window.removeEventListener('scroll', onScrollOrResize, true)
  window.removeEventListener('resize', onScrollOrResize)
})
</script>

<style scoped>
.sf-popconfirm {
  position: relative;
  display: inline-flex;
}

.sf-popconfirm-popup {
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 10px;
  box-shadow: var(--shadow-lg, 0 12px 32px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06));
  padding: 14px 16px;
  z-index: 9999;  /* 高 z-index, 覆盖一切 (Teleport 到 body) */
}

.sf-popconfirm-text {
  font-size: 14px;
  color: var(--color-text-primary, #1e293b);
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
  transition: all var(--sf-duration-fast, 0.15s);
}

.sf-popconfirm-btn--cancel {
  background: var(--color-bg-elevated, #f1f5f9);
  color: var(--color-text-secondary, #64748b);
}
.sf-popconfirm-btn--cancel:hover {
  background: var(--color-border, #e2e8f0);
}

.sf-popconfirm-btn--confirm {
  background: var(--color-brand, #2563eb);
  color: #fff;
}
.sf-popconfirm-btn--confirm:hover {
  background: var(--color-brand-hover, #1d4ed8);
}

.sf-popconfirm-enter-active,
.sf-popconfirm-leave-active {
  transition: all var(--sf-duration-fast, 0.15s);
}
.sf-popconfirm-enter-from,
.sf-popconfirm-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
