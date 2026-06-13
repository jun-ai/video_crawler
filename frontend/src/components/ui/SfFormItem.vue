<template>
  <div class="sf-form-item">
    <label v-if="label" class="sf-form-label">
      {{ label }}
      <span v-if="required" class="sf-form-required">*</span>
    </label>
    <div class="sf-form-content">
      <slot />
      <p v-if="error" class="sf-form-error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
  required: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
</script>

<style scoped>
.sf-form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sf-form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.sf-form-required {
  color: var(--color-danger);
  margin-left: 2px;
}

.sf-form-error {
  font-size: 12px;
  color: var(--color-danger);
  margin: 4px 0 0;
}
</style>
