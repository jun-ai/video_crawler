<script setup lang="ts">
import type { PrimitiveProps } from "reka-ui"
import type { HTMLAttributes } from "vue"
import type { ButtonVariants } from "."
import { Primitive } from "reka-ui"
import { cn } from "@/lib/utils"
import { buttonVariants } from "."

interface Props extends PrimitiveProps {
  variant?: ButtonVariants["variant"]
  size?: ButtonVariants["size"]
  class?: HTMLAttributes["class"]
}

const props = withDefaults(defineProps<Props>(), {
  as: "button",
})
</script>

<template>
  <Primitive
    :as="as"
    :as-child="asChild"
    :class="cn(buttonVariants({ variant, size }), 'btn-press', props.class)"
  >
    <slot />
  </Primitive>
</template>

<style scoped>
.btn-press {
  transition: transform 0.1s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}
.btn-press:active:not(:disabled) {
  transform: scale(0.97);
}
.btn-press:disabled {
  opacity: 0.5;
}
</style>
