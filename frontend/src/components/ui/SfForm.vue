<template>
  <form class="sf-form" @submit.prevent="$emit('submit')">
    <slot />
  </form>
</template>

<script setup>
defineEmits(['submit'])
</script>

<style scoped>
.sf-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
