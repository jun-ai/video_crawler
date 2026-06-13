<template>
  <slot />
  <SfConfirmDialog />
  <SfToast />
</template>

<script setup>
import SfConfirmDialog from './SfConfirmDialog.vue'
import SfToast from './SfToast.vue'
</script>
