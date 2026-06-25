<template>
  <div class="sf-table-wrap">
    <table class="sf-table" :style="tableStyle">
      <thead>
        <tr>
          <th
            v-for="col in visibleColumns"
            :key="col.key"
            :style="getColStyle(col)"
            :class="{ 'sf-th-resizable': resizable, 'sf-th-noshrink': !col.width }"
          >
            <slot :name="`header-${col.key}`" :col="col">
              {{ col.label }}
            </slot>
            <!-- 列宽拖拽 handle -->
            <span
              v-if="resizable && col.resizable !== false"
              class="sf-col-resizer"
              @mousedown.stop="startResize($event, col)"
              @click.stop.prevent
            />
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in data" :key="rowKey ? row[rowKey] : i">
          <td v-for="col in visibleColumns" :key="col.key">
            <slot :name="col.key" :row="row" :index="i">
              {{ row[col.key] }}
            </slot>
          </td>
        </tr>
        <tr v-if="!data.length">
          <td :colspan="visibleColumns.length" class="sf-table-empty">暂无数据</td>
        </tr>
      </tbody>
    </table>

    <!-- 拖拽时禁用文本选择 + 跟随鼠标的 ghost line -->
    <div
      v-if="dragging"
      class="sf-col-dragline"
      :style="{ left: dragX + 'px' }"
    />
  </div>
</template>

<script setup>
import { computed, ref, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, default: () => [] }, // [{ key, label, width, minWidth, resizable, fixed }]
  data: { type: Array, default: () => [] },
  rowKey: { type: String, default: '' },
  resizable: { type: Boolean, default: true },
  // 外部传入的"用户偏好":每列宽度 (px) + 显隐
  widthOverrides: { type: Object, default: () => ({}) }, // { key: number }
  hiddenKeys: { type: Array, default: () => [] },
})

const emit = defineEmits(['column-resize'])

// 实际列宽:props.widthOverrides 优先,fallback 到 col.width
const colWidths = ref({ ...props.widthOverrides })
watch(() => props.widthOverrides, (v) => { colWidths.value = { ...v } }, { deep: true })

// 可见列:过滤掉 hiddenKeys
const visibleColumns = computed(() => {
  const hidden = new Set(props.hiddenKeys)
  return props.columns.filter(c => !hidden.has(c.key))
})

function getColStyle(col) {
  const w = colWidths.value[col.key] ?? parseWidth(col.width)
  return w ? { width: w + 'px', minWidth: w + 'px' } : {}
}

const tableStyle = computed(() => {
  // 总宽超过父容器时让 table 自适应滚动,否则用 auto
  return { tableLayout: 'fixed' }
})

// ===== 拖拽列宽 =====
const dragging = ref(false)
const dragX = ref(0)
let dragCol = null
let dragStartX = 0
let dragStartW = 0
let dragMinW = 40

function parseWidth(w) {
  if (!w) return null
  if (typeof w === 'number') return w
  const m = String(w).match(/^(\d+)/)
  return m ? parseInt(m[1], 10) : null
}

function startResize(e, col) {
  dragging.value = true
  dragCol = col
  dragStartX = e.clientX
  const th = e.target.parentElement
  dragStartW = th.offsetWidth
  dragMinW = parseWidth(col.minWidth) || 40
  dragX.value = e.clientX
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  window.addEventListener('mousemove', onDragMove)
  window.addEventListener('mouseup', endDrag)
}

function onDragMove(e) {
  if (!dragCol) return
  dragX.value = e.clientX
  const delta = e.clientX - dragStartX
  const newW = Math.max(dragMinW, dragStartW + delta)
  colWidths.value = { ...colWidths.value, [dragCol.key]: newW }
}

function endDrag() {
  if (dragCol) {
    emit('column-resize', { key: dragCol.key, width: colWidths.value[dragCol.key] })
  }
  dragging.value = false
  dragCol = null
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', endDrag)
}

onBeforeUnmount(() => {
  if (dragging.value) endDrag()
})
</script>

<style scoped>
.sf-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  position: relative;
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
  position: relative;
  /* overflow: hidden 让列宽精确生效,但要 text-overflow 截断看不全 */
}

/* 可调列宽的 th 右边 4px 拖拽条 */
.sf-col-resizer {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  background: transparent;
  user-select: none;
  z-index: 2;
}
.sf-col-resizer:hover,
.sf-col-resizer:active {
  background: var(--color-brand);
}

.sf-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
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

.sf-col-dragline {
  position: fixed;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--color-brand);
  pointer-events: none;
  z-index: 9999;
  opacity: 0.7;
}
</style>
