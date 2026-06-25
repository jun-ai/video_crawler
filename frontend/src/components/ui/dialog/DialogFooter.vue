<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import { cn } from "@/lib/utils"

const props = defineProps<{ class?: HTMLAttributes["class"] }>()
</script>

<template>
  <div
    :class="
      cn(
        'sf-reka-dialog-footer',
        'flex flex-col-reverse sm:flex-row sm:justify-end sm:gap-x-2',
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>

<style>
.sf-reka-dialog-footer {
  display: flex;
  flex-direction: column-reverse;
  gap: 8px;
  padding-top: 20px;
  margin-top: 8px;
  border-top: 1px solid var(--color-border);
}

@media (min-width: 640px) {
  .sf-reka-dialog-footer {
    flex-direction: row;
    justify-content: flex-end;
  }
}

/* footer 里的按钮 — 增强"确定"按钮可点击感 */
.sf-reka-dialog-footer :where(button) {
  min-height: 38px;
  padding: 0 18px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 10px;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.15s, background-color 0.15s;
}

.sf-reka-dialog-footer :where(button):not(:disabled):active {
  transform: scale(0.97);
}

.sf-reka-dialog-footer :where(button):disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
