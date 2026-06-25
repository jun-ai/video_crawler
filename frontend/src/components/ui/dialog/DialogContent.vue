<script setup lang="ts">
import type { DialogContentEmits, DialogContentProps } from "reka-ui"
import type { HTMLAttributes } from "vue"
import { reactiveOmit } from "@vueuse/core"
import { X } from "lucide-vue-next"
import {
  DialogClose,
  DialogContent,
  DialogOverlay,
  DialogPortal,
  useForwardPropsEmits,
} from "reka-ui"
import { cn } from "@/lib/utils"

const props = defineProps<DialogContentProps & { class?: HTMLAttributes["class"]; style?: HTMLAttributes["style"] }>()
const emits = defineEmits<DialogContentEmits>()

const delegatedProps = reactiveOmit(props, "class")

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <DialogPortal>
    <DialogOverlay class="sf-reka-dialog-overlay" />
    <DialogContent
      v-bind="forwarded"
      :class="cn('sf-reka-dialog-content', props.class)"
      :style="props.style"
    >
      <slot />

      <DialogClose class="sf-reka-dialog-close">
        <X class="w-4 h-4" />
        <span class="sr-only">Close</span>
      </DialogClose>
    </DialogContent>
  </DialogPortal>
</template>

<!-- unscoped: Reka UI Teleport 到 body,scoped 属性不传递 -->
<style>
.sf-reka-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 1040;
  background-color: rgba(0, 0, 0, 0.7);
}

.sf-reka-dialog-content {
  position: fixed;
  left: 50%;
  top: 50%;
  z-index: 1050;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  width: var(--sf-dialog-w, 480px);
  max-width: var(--sf-dialog-mw, 90vw);
  max-height: 85vh;
  overflow-y: auto;
  gap: 16px;
  border: 1px solid var(--color-border);
  background-color: var(--color-bg-card);
  padding: 24px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18), 0 4px 8px rgba(0, 0, 0, 0.10);
  border-radius: 16px;
  animation: sf-reka-dialog-in 0.18s ease-out;
}

.sf-reka-dialog-content[data-state="open"] {
  animation: sf-reka-dialog-in 0.18s ease-out;
}

.sf-reka-dialog-content[data-state="closed"] {
  animation: sf-reka-dialog-out 0.15s ease-in;
}

@keyframes sf-reka-dialog-in {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.96); }
  to   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

@keyframes sf-reka-dialog-out {
  from { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  to   { opacity: 0; transform: translate(-50%, -50%) scale(0.96); }
}

.sf-reka-dialog-close {
  position: absolute;
  right: 16px;
  top: 16px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  opacity: 0.7;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: opacity 0.15s, background-color 0.15s;
  padding: 0;
}
.sf-reka-dialog-close:hover {
  opacity: 1;
  background-color: var(--color-bg-elevated);
}
.sf-reka-dialog-close:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
}
</style>
