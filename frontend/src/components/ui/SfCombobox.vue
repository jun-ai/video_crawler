<template>
  <div class="sf-combobox" :class="{ open: isOpen }" v-click-outside="closeDropdown">
    <!-- 输入框 (显示选中项或可输入搜索) -->
    <div class="sf-combobox-input-wrap" @click="openDropdown">
      <Search v-if="searchable" :size="14" class="sf-combobox-search-icon" />
      <input
        ref="inputRef"
        v-model="searchText"
        type="text"
        class="sf-combobox-input"
        :placeholder="displayText || placeholder"
        :readonly="!searchable"
        @input="onSearchInput"
        @focus="openDropdown"
        @keydown.down.prevent="moveHighlight(1)"
        @keydown.up.prevent="moveHighlight(-1)"
        @keydown.enter.prevent="selectHighlighted"
        @keydown.esc="closeDropdown"
        @keydown.tab="closeDropdown"
      />
      <button
        v-if="modelValue !== null && modelValue !== undefined && modelValue !== ''"
        class="sf-combobox-clear"
        @click.stop="clearValue"
        aria-label="清除"
      >
        <X :size="12" />
      </button>
      <ChevronDown :size="14" class="sf-combobox-chevron" :class="{ rotated: isOpen }" />
    </div>

    <!-- 下拉列表 -->
    <Transition name="sf-combobox-dropdown">
      <div v-if="isOpen" class="sf-combobox-dropdown">
        <div v-if="filteredOptions.length === 0" class="sf-combobox-empty">
          {{ searchText ? `没找到 "${searchText}"` : '没有可选项' }}
        </div>
        <div
          v-for="(opt, idx) in filteredOptions"
          :key="opt.value"
          :class="['sf-combobox-option', { highlighted: idx === highlightedIndex, selected: opt.value === modelValue }]"
          @mousedown.prevent="selectOption(opt)"
          @mouseenter="highlightedIndex = idx"
        >
          <slot name="option" :option="opt">
            <span class="sf-combobox-option-label">{{ opt.label }}</span>
            <span v-if="opt.sublabel" class="sf-combobox-option-sublabel">{{ opt.sublabel }}</span>
          </slot>
          <Check v-if="opt.value === modelValue" :size="14" class="sf-combobox-option-check" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Search, X, ChevronDown, Check } from 'lucide-vue-next'

const props = defineProps({
  modelValue: { type: [String, Number, null], default: null },
  options: { type: Array, required: true },  // [{ value, label, sublabel? }]
  placeholder: { type: String, default: '请选择...' },
  searchable: { type: Boolean, default: true },
  displayValue: { type: String, default: '' }  // 当 modelValue 不为空时, 输入框显示什么 (空=自动从 options 找)
})

const emit = defineEmits(['update:modelValue', 'change'])

const inputRef = ref(null)
const isOpen = ref(false)
const searchText = ref('')
const highlightedIndex = ref(0)

const displayText = computed(() => {
  if (props.displayValue) return props.displayValue
  if (props.modelValue === null || props.modelValue === undefined) return ''
  const opt = props.options.find(o => o.value === props.modelValue)
  return opt ? opt.label : ''
})

// 当选中值变化时, 同步显示文字
watch(() => props.modelValue, () => {
  searchText.value = displayText.value
}, { immediate: true })

const filteredOptions = computed(() => {
  if (!searchText.value) return props.options
  const lower = searchText.value.toLowerCase()
  return props.options.filter(o =>
    (o.label || '').toLowerCase().includes(lower) ||
    (o.sublabel || '').toLowerCase().includes(lower)
  )
})

const openDropdown = async () => {
  isOpen.value = true
  // 打开时, 如果有值, 把光标放到末尾方便追加搜索
  await nextTick()
  if (inputRef.value) {
    const len = inputRef.value.value.length
    inputRef.value.setSelectionRange(len, len)
  }
}

const closeDropdown = () => {
  isOpen.value = false
  // 关闭时恢复显示
  searchText.value = displayText.value
  highlightedIndex.value = 0
}

const onSearchInput = () => {
  isOpen.value = true
  highlightedIndex.value = 0
}

const moveHighlight = (dir) => {
  if (!isOpen.value) openDropdown()
  const max = filteredOptions.value.length - 1
  if (max < 0) return
  highlightedIndex.value = Math.max(0, Math.min(max, highlightedIndex.value + dir))
}

const selectHighlighted = () => {
  const opt = filteredOptions.value[highlightedIndex.value]
  if (opt) selectOption(opt)
}

const selectOption = (opt) => {
  emit('update:modelValue', opt.value)
  emit('change', opt)
  searchText.value = opt.label
  isOpen.value = false
}

const clearValue = () => {
  emit('update:modelValue', null)
  emit('change', null)
  searchText.value = ''
  inputRef.value?.focus()
}

// v-click-outside 自定义指令
const vClickOutside = {
  mounted(el, binding) {
    el._handler = (e) => {
      if (!el.contains(e.target)) binding.value()
    }
    document.addEventListener('mousedown', el._handler)
  },
  unmounted(el) {
    document.removeEventListener('mousedown', el._handler)
  }
}
</script>

<style scoped>
.sf-combobox {
  position: relative;
  display: inline-block;
  width: 100%;
}

.sf-combobox-input-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  background: var(--color-bg-card, #fff);
  cursor: pointer;
  transition: border-color 0.15s;
  min-height: 32px;
}
.sf-combobox-input-wrap:hover {
  border-color: var(--color-text-tertiary, #9ca3af);
}
.sf-combobox.open .sf-combobox-input-wrap {
  border-color: var(--color-brand, #3b82f6);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-brand, #3b82f6) 15%, transparent);
}

.sf-combobox-search-icon {
  color: var(--color-text-tertiary, #9ca3af);
  flex-shrink: 0;
}

.sf-combobox-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  color: var(--color-text-primary, #111827);
  min-width: 0;
}
.sf-combobox-input::placeholder {
  color: var(--color-text-tertiary, #9ca3af);
}
.sf-combobox-input:read-only {
  cursor: pointer;
}

.sf-combobox-clear {
  border: none;
  background: transparent;
  color: var(--color-text-tertiary, #9ca3af);
  cursor: pointer;
  padding: 2px;
  display: flex;
  border-radius: 4px;
}
.sf-combobox-clear:hover {
  background: var(--color-bg-page, #f3f4f6);
  color: var(--color-text-primary, #111827);
}

.sf-combobox-chevron {
  color: var(--color-text-tertiary, #9ca3af);
  flex-shrink: 0;
  transition: transform var(--sf-duration-fast);
}
.sf-combobox-chevron.rotated {
  transform: rotate(180deg);
}

.sf-combobox-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 280px;
  overflow-y: auto;
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 100;
  padding: 4px;
}

.sf-combobox-empty {
  padding: 12px;
  text-align: center;
  color: var(--color-text-tertiary, #9ca3af);
  font-size: 13px;
}

.sf-combobox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-primary, #111827);
  transition: background var(--sf-duration-fast);
}
.sf-combobox-option.highlighted {
  background: var(--color-bg-page, #f3f4f6);
}
.sf-combobox-option.selected {
  color: var(--color-brand, #3b82f6);
  font-weight: 500;
}

.sf-combobox-option-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sf-combobox-option-sublabel {
  font-size: 11px;
  color: var(--color-text-tertiary, #9ca3af);
}
.sf-combobox-option-check {
  flex-shrink: 0;
  color: var(--color-brand, #3b82f6);
}

/* 过渡 */
.sf-combobox-dropdown-enter-active,
.sf-combobox-dropdown-leave-active {
  transition: opacity var(--sf-duration-fast), transform var(--sf-duration-fast);
}
.sf-combobox-dropdown-enter-from,
.sf-combobox-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
