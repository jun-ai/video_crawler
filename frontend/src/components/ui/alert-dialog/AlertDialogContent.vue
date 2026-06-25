<script setup lang="ts">
import type { AlertDialogContentEmits, AlertDialogContentProps } from "reka-ui"
import type { HTMLAttributes } from "vue"
import { reactiveOmit } from "@vueuse/core"
import {
  AlertDialogContent,
  AlertDialogOverlay,
  AlertDialogPortal,
  useForwardPropsEmits,
} from "reka-ui"
import { cn } from "@/lib/utils"

const props = defineProps<AlertDialogContentProps & { class?: HTMLAttributes["class"] }>()
const emits = defineEmits<AlertDialogContentEmits>()

const delegatedProps = reactiveOmit(props, "class")

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <AlertDialogPortal>
    <AlertDialogOverlay class="sf-reka-alert-dialog-overlay" />
    <AlertDialogContent
      v-bind="forwarded"
      :class="cn('sf-reka-dialog-content', props.class)"
    >
      <slot />
    </AlertDialogContent>
  </AlertDialogPortal>
</template>

<style>
.sf-reka-alert-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 1040;
  background-color: rgba(0, 0, 0, 0.7);
}
</style>
