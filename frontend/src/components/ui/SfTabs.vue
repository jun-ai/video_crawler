<script setup lang="ts">
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  tabs: { type: Array, default: () => [] }, // [{ key, label }]
})

const emit = defineEmits(['update:modelValue'])

function handleUpdate(value) {
  emit('update:modelValue', value)
}
</script>

<template>
  <Tabs :model-value="String(modelValue)" @update:model-value="handleUpdate" class="sf-tabs">
    <TabsList class="sf-tabs-nav">
      <TabsTrigger
        v-for="tab in tabs"
        :key="tab.key"
        :value="String(tab.key)"
        class="sf-tabs-tab"
      >
        {{ tab.label }}
      </TabsTrigger>
    </TabsList>
    <slot />
  </Tabs>
</template>

<style scoped>
.sf-tabs {
  width: 100%;
}

.sf-tabs-nav {
  display: flex;
  gap: 4px;
  background: transparent;
  border-bottom: 1px solid var(--border);
  padding: 0;
  border-radius: 0;
}

.sf-tabs-tab {
  position: relative;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--muted-foreground);
  background: none;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: color 0.2s;
  white-space: nowrap;
}

.sf-tabs-tab:hover {
  color: var(--foreground);
}

.sf-tabs-tab[data-state="active"] {
  color: var(--primary);
}

.sf-tabs-tab[data-state="active"]::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary);
  border-radius: 1px;
}
</style>
