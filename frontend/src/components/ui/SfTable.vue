<template>
  <div class="sf-table-wrap">
    <table class="sf-table">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" :style="{ width: col.width }">
            {{ col.label }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in data" :key="i">
          <td v-for="col in columns" :key="col.key">
            <slot :name="col.key" :row="row" :index="i">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
        <tr v-if="!data.length">
          <td :colspan="columns.length" class="sf-table-empty">暂无数据</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Array, default: () => [] }, // [{ key, label, width }]
  data: { type: Array, default: () => [] },
})
</script>

<style scoped>
.sf-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.sf-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.sf-table th {
  text-align: left;
  padding: 12px 16px;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.sf-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.sf-table tr:last-child td {
  border-bottom: none;
}

.sf-table tr:hover td {
  background: var(--color-bg-hover);
}

.sf-table-empty {
  text-align: center;
  color: var(--color-text-muted);
  padding: 40px 16px !important;
}
</style>
