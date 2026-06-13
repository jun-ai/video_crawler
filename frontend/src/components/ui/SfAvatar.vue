<template>
  <div class="sf-avatar" :class="[`sf-avatar--${size}`]" :style="avatarStyle">
    <img v-if="src" :src="src" :alt="alt" class="sf-avatar-img" />
    <span v-else class="sf-avatar-text">{{ initials }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  name: { type: String, default: '' },
  size: { type: String, default: 'md' }, // sm, md, lg
  alt: { type: String, default: '' },
  bgColor: { type: String, default: '' },
})

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name.charAt(0).toUpperCase()
})

const avatarStyle = computed(() => {
  if (props.bgColor) {
    return { backgroundColor: props.bgColor }
  }
  return {}
})
</script>

<style scoped>
.sf-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-brand-subtle);
  color: var(--color-brand);
  font-weight: 600;
  flex-shrink: 0;
}

.sf-avatar--sm { width: 32px; height: 32px; font-size: 13px; }
.sf-avatar--md { width: 40px; height: 40px; font-size: 16px; }
.sf-avatar--lg { width: 64px; height: 64px; font-size: 24px; }

.sf-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sf-avatar-text {
  line-height: 1;
}
</style>
