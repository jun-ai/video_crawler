<script setup lang="ts">
import { watch, onMounted, onBeforeUnmount } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose,
  DialogTrigger,
} from '@/components/ui/dialog'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  width: { type: String, default: '480px' },
  maxWidth: { type: String, default: '90vw' },
  showClose: { type: Boolean, default: true },
  closeOnClickOverlay: { type: Boolean, default: true },
  closeOnEsc: { type: Boolean, default: true },
})

const emit = defineEmits(['update:modelValue', 'close'])

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function handleOverlayClick() {
  if (props.closeOnClickOverlay) close()
}

watch(() => props.modelValue, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onBeforeUnmount(() => {
  document.body.style.overflow = ''
})
</script>

<template>
  <Dialog :open="modelValue" @update:open="(val) => { if (!val) close() }">
    <DialogContent
      :style="{ '--sf-dialog-w': width, '--sf-dialog-mw': maxWidth }"
      class="sf-dialog-content"
      @pointer-down-outside="handleOverlayClick"
    >
      <DialogHeader v-if="title || $slots.header">
        <slot name="header">
          <DialogTitle>{{ title }}</DialogTitle>
        </slot>
        <DialogClose v-if="showClose" class="sf-dialog-close" @click="close">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </DialogClose>
      </DialogHeader>
      <div class="sf-dialog-body">
        <slot />
      </div>
      <DialogFooter v-if="$slots.footer">
        <slot name="footer" />
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

<style scoped>
.sf-dialog-content {
  max-height: calc(100vh - 32px);
}

.sf-dialog-body {
  padding: 0 24px 16px;
  overflow-y: auto;
  flex: 1;
}

.sf-dialog-close {
  position: absolute;
  right: 16px;
  top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 8px;
  color: var(--muted-foreground);
  cursor: pointer;
  transition: all var(--sf-duration-fast);
}
.sf-dialog-close:hover {
  background: var(--accent);
  color: var(--accent-foreground);
}

:deep(.sf-dialog-close) {
  position: absolute;
  right: 16px;
  top: 16px;
}
</style>
