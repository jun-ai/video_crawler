<template>
  <div class="sf-subtitle-list">
    <div class="sf-subtitle-panel">
      <!-- 面板头部 -->
      <div class="sf-subtitle-panel__header">
        <h3 class="sf-subtitle-panel__title">
          <span class="sf-subtitle-panel__title-text">动态字幕</span>
          <span class="sf-subtitle-panel__count">{{ subtitles.length }} 句</span>
        </h3>
        <div class="sf-subtitle-panel__actions">
          <!-- 播放模式分段控制 -->
          <div class="sf-subtitle-play-mode">
            <button
              v-for="mode in playModes"
              :key="mode.value"
              :class="['sf-subtitle-play-mode__btn', { active: playMode === mode.value }]"
              @click="$emit('set-play-mode', mode.value)"
              :title="mode.label"
            >
              {{ mode.shortLabel }}
            </button>
          </div>

          <!-- 更多操作 -->
          <SfDropdown>
            <template #trigger>
              <button class="sf-btn sf-btn--ghost sf-btn--sm">
                更多
              </button>
            </template>
            <div class="sf-dropdown-item" :class="{ 'is-active': !showOnlyChinese && showTranslation }" @click="handleMoreAction('bilingual')">双语字幕</div>
            <div class="sf-dropdown-item" :class="{ 'is-active': !showOnlyChinese && !showTranslation }" @click="handleMoreAction('en-only')">仅英文</div>
            <div class="sf-dropdown-item" :class="{ 'is-active': showOnlyChinese }" @click="handleMoreAction('cn-only')">仅中文</div>
            <div class="sf-dropdown-item" @click="handleMoreAction('toggle-auto-scroll')">
              {{ autoScroll ? '关闭自动滚动' : '开启自动滚动' }}
            </div>
            <div class="sf-dropdown-item" v-if="!hasInterpretation" :class="{ disabled: isGenerating }" @click="!isGenerating && handleMoreAction('generate-interpretation')">
              {{ isGenerating ? '分析中...' : '生成解读' }}
            </div>
          </SfDropdown>
        </div>
      </div>

      <!-- 字幕列表 -->
      <div class="sf-subtitle-panel__list" ref="listRef">
        <div
          v-for="(sub, pageIndex) in paginatedSubtitles"
          :key="sub.id"
          :id="'subtitle-page-' + pageIndex"
          :class="['sf-subtitle-item', { active: currentSubtitleIndexInPage === pageIndex }]"
          @click="$emit('subtitle-click', sub, getGlobalIndex(pageIndex))"
        >
          <!-- 左侧状态指示条 -->
          <div :class="['sf-subtitle-item__indicator', { active: currentSubtitleIndexInPage === pageIndex }]"></div>

          <span class="sf-subtitle-item__time">{{ formatTime(sub.start_time) }}</span>
          <div class="sf-subtitle-item__content">
            <div
              class="sf-subtitle-item__text"
              v-if="!showOnlyChinese"
              @mouseup="$emit('text-selection', sub, $event)"
              @click.stop="$emit('annotation-click', $event)"
              v-html="getAnnotatedText(sub)"
            ></div>
            <div class="sf-subtitle-item__annotations" v-if="annotations[sub.id] && annotations[sub.id].length > 0">
              <span
                v-for="ann in annotations[sub.id]"
                :key="ann.id"
                class="sf-annotation-tag"
                :style="{ backgroundColor: ann.color + '15', borderColor: ann.color + '40' }"
              >
                <span class="sf-annotation-tag__text" :style="{ color: ann.color }">{{ ann.annotated_text }}</span>
                <span class="sf-annotation-tag__type">{{ getAnnotationTypeLabel(ann.annotation_type) }}</span>
                <X class="sf-annotation-tag__delete" :size="11" @click.stop="$emit('delete-annotation', ann.id, sub.id)" />
              </span>
            </div>
            <span v-if="showTranslation && sub.text_cn && !showOnlyChinese" class="sf-subtitle-item__cn">
              {{ sub.text_cn }}
            </span>
            <span v-if="showOnlyChinese && sub.text_cn" class="sf-subtitle-item__text sf-subtitle-item__text--cn">
              {{ sub.text_cn }}
            </span>
          </div>
          <div class="sf-subtitle-item__actions">
            <button class="sf-subtitle-action-btn" @click.stop="$emit('replay-subtitle', sub)" title="播放此句">
              <Play :size="13" />
            </button>
            <Star
              class="sf-bookmark-icon"
              :class="{ bookmarked: bookmarkedIds.has(sub.id) }"
              :size="13"
              :fill="bookmarkedIds.has(sub.id) ? 'currentColor' : 'none'"
              @click.stop="$emit('toggle-bookmark', sub)"
              :title="bookmarkedIds.has(sub.id) ? '取消收藏' : '收藏此句'"
            />
          </div>
        </div>
      </div>

      <!-- 单词弹出框 -->
      <slot name="word-popup"></slot>

      <!-- 标注弹出框 -->
      <slot name="annotation-popup"></slot>

      <!-- 分页 -->
      <div class="sf-subtitle-panel__footer" v-if="totalPages > 1">
        <SfPagination
          :current-page="currentPage"
          @update:current-page="$emit('update:currentPage', $event)"
          :page-size="pageSize"
          :total="subtitles.length"
          :pager-count="5"
        />
        <span class="sf-subtitle-panel__page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Star, Play, X } from 'lucide-vue-next'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import SfPagination from '@/components/ui/SfPagination.vue'

const props = defineProps({
  subtitles: { type: Array, default: () => [] },
  paginatedSubtitles: { type: Array, default: () => [] },
  currentSubtitleIndexInPage: { type: Number, default: -1 },
  showTranslation: { type: Boolean, default: true },
  showOnlyChinese: { type: Boolean, default: false },
  bookmarkedIds: { type: Set, default: () => new Set() },
  annotations: { type: Object, default: () => ({}) },
  hasInterpretation: { type: Boolean, default: false },
  isGenerating: { type: Boolean, default: false },
  autoScroll: { type: Boolean, default: true },
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  playMode: { type: String, default: 'single' },
  playModeLabel: { type: String, default: '单次播放' },
  getAnnotatedText: { type: Function, default: (sub) => sub.text_en }
})

const emit = defineEmits([
  'subtitle-click', 'replay-subtitle', 'record-subtitle', 'toggle-bookmark',
  'text-selection', 'annotation-click', 'delete-annotation',
  'prev', 'next', 'generate-interpretation',
  'set-subtitle-mode', 'set-play-mode',
  'update:autoScroll', 'update:currentPage'
])

const listRef = ref(null)

const playModes = [
  { value: 'single', label: '单次播放', shortLabel: '单次' },
  { value: 'single-loop', label: '单集循环', shortLabel: '循环' },
  { value: 'continuous', label: '连续播放', shortLabel: '连续' },
  { value: 'sentence-loop', label: '单句循环', shortLabel: '单句' }
]

const totalPages = computed(() => Math.ceil(props.subtitles.length / props.pageSize))

const getGlobalIndex = (pageIndex) => {
  return (props.currentPage - 1) * props.pageSize + pageIndex
}

const formatTime = (ms) => {
  const seconds = Math.floor(ms / 1000)
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getAnnotationTypeLabel = (type) => {
  const labels = { vocabulary: '重点词汇', phrase: '重点短语', important: '重点内容' }
  return labels[type] || type
}

const handleMoreAction = (command) => {
  if (command === 'toggle-auto-scroll') {
    emit('update:autoScroll', !props.autoScroll)
  } else if (command === 'generate-interpretation') {
    emit('generate-interpretation')
  } else {
    emit('set-subtitle-mode', command)
  }
}

defineExpose({ listRef })
</script>

<style scoped>
.sf-subtitle-list {
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sf-subtitle-panel {
  background: var(--sf-bg-card);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 面板头部 */
.sf-subtitle-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--sf-border);
  background: var(--sf-bg-elevated);
  flex-shrink: 0;
}

.sf-subtitle-panel__title {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin: 0;
}

.sf-subtitle-panel__title-text {
  font-size: 14px;
  font-weight: 700;
  color: var(--sf-text-primary);
}

.sf-subtitle-panel__count {
  font-size: 12px;
  color: var(--sf-text-muted);
  font-weight: 400;
}

.sf-subtitle-panel__actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 字幕列表 */
.sf-subtitle-panel__list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 0;
}

.sf-subtitle-panel__list::-webkit-scrollbar {
  width: 5px;
}
.sf-subtitle-panel__list::-webkit-scrollbar-track {
  background: transparent;
}
.sf-subtitle-panel__list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}
.dark .sf-subtitle-panel__list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
}

/* 字幕条目 */
.sf-subtitle-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all var(--sf-duration-fast);
  margin: 1px 8px;
  border-radius: var(--sf-radius-md);
  border: 1px solid transparent;
  position: relative;
}

.sf-subtitle-item:hover {
  background: var(--sf-bg-elevated);
  border-color: var(--sf-border);
}

.sf-subtitle-item.active {
  background: var(--color-bg-mint); /* Phase 0+ SpeakVlog 薄荷绿选中 */
  border-color: var(--color-brand-bright);
  box-shadow: inset 3px 0 0 0 var(--color-brand-bright);
}

/* 左侧状态指示条 */
.sf-subtitle-item__indicator {
  width: 4px;
  align-self: stretch;
  border-radius: 2px;
  background: var(--sf-border);
  flex-shrink: 0;
  margin: 2px 0;
  transition: background var(--sf-duration-fast);
}
.sf-subtitle-item__indicator.active {
  background: linear-gradient(180deg, var(--color-brand-bright) 0%, var(--color-accent) 100%);
}

/* 时间戳 */
.sf-subtitle-item__time {
  flex-shrink: 0;
  color: var(--sf-text-muted);
  font-size: 11px;
  font-weight: 600;
  font-family: var(--sf-font-mono);
  padding: 2px 8px;
  background: var(--sf-bg-elevated);
  border: 1px solid var(--sf-border);
  border-radius: var(--sf-radius-full);
  margin-top: 1px;
}
.sf-subtitle-item.active .sf-subtitle-item__time {
  background: rgba(63, 138, 91, 0.18);
  color: var(--color-brand-bright);
  border-color: rgba(15, 76, 58, 0.2);
}

/* 内容 */
.sf-subtitle-item__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.sf-subtitle-item__text {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.65;
  color: var(--sf-text-primary);
}

.sf-subtitle-item.active .sf-subtitle-item__text {
  font-weight: 600;
}

.sf-subtitle-item__cn {
  font-size: 12px;
  font-weight: 400;
  color: var(--sf-text-secondary);
  line-height: 1.6;
}
.sf-subtitle-item.active .sf-subtitle-item__cn {
  color: var(--sf-text-secondary);
}

/* 标注标签 */
.sf-subtitle-item__annotations {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 3px;
}

.sf-annotation-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--sf-radius-full);
  border: 1px solid;
  font-size: 11px;
  transition: all var(--sf-duration-fast);
}

.sf-annotation-tag__text {
  font-weight: 500;
  max-width: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sf-annotation-tag__type {
  color: var(--sf-text-muted);
  font-size: 10px;
}

.sf-annotation-tag__delete {
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--sf-duration-fast);
  font-size: 11px;
  color: var(--sf-text-muted);
}
.sf-annotation-tag:hover .sf-annotation-tag__delete {
  opacity: 1;
}
.sf-annotation-tag__delete:hover {
  color: var(--color-brand);
}

/* 操作按钮 */
.sf-subtitle-item__actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity var(--sf-duration-fast);
}
.sf-subtitle-item:hover .sf-subtitle-item__actions {
  opacity: 1;
}

.sf-subtitle-action-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid var(--sf-border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--sf-duration-fast);
  background: var(--sf-bg-card);
  color: var(--sf-text-secondary);
}
.sf-subtitle-action-btn:hover {
  background: var(--color-brand);
  border-color: var(--color-brand);
  color: #fff;
  transform: scale(1.05);
}

/* 播放模式分段控制 */
.sf-subtitle-play-mode {
  display: inline-flex;
  background: var(--sf-bg-elevated);
  border: 1px solid var(--sf-border);
  border-radius: var(--sf-radius-full);
  padding: 2px;
  gap: 2px;
}

.sf-subtitle-play-mode__btn {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  color: var(--sf-text-muted);
  background: transparent;
  border: none;
  border-radius: var(--sf-radius-full);
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-easing-bounce);
  font-family: inherit;
  white-space: nowrap;
}
.sf-subtitle-play-mode__btn:hover {
  color: var(--sf-text-primary);
  background: var(--sf-bg-card);
}
.sf-subtitle-play-mode__btn.active {
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(63, 138, 91, 0.35);
}

/* 收藏按钮旋转动画 */
.sf-bookmark-icon {
  font-size: 13px;
  color: var(--sf-text-muted);
  cursor: pointer;
  transition: all var(--sf-duration-fast);
}
.sf-bookmark-icon:hover {
  color: #f59e0b;
  transform: scale(1.1);
}
.sf-bookmark-icon.bookmarked {
  color: #f59e0b;
  animation: bookmarkSpin 0.4s var(--sf-easing-bounce);
}

@keyframes bookmarkSpin {
  0% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.3) rotate(15deg); }
  100% { transform: scale(1) rotate(360deg); }
}

/* 分页 */
.sf-subtitle-panel__footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 16px;
  border-top: 1px solid var(--sf-border);
  background: var(--sf-bg-elevated);
  flex-shrink: 0;
}

.sf-subtitle-panel__page-info {
  font-size: 12px;
  color: var(--sf-text-muted);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .sf-subtitle-panel__header {
    padding: 10px 12px;
  }
  .sf-subtitle-item {
    padding: 8px 10px;
  }
  .sf-subtitle-item__text {
    font-size: 13px;
  }
  .sf-subtitle-item__time {
    font-size: 10px;
    padding: 2px 6px;
  }
}

/* ==================== Phase 1B Task 7: Mobile 适配 ==================== */
@media (max-width: 768px) {
  .sf-subtitle-item {
    padding: 12px 14px;
    min-height: 56px;
    gap: 10px;
  }
  .sf-subtitle-item__time {
    font-size: 11px;
    padding: 3px 8px;
    min-width: 56px;
  }
  .sf-subtitle-item__text {
    font-size: 15px;
    line-height: 1.5;
  }
  .sf-subtitle-item__cn {
    font-size: 13px;
    margin-top: 4px;
  }
  .sf-subtitle-item__actions button {
    width: 32px;
    height: 32px;
  }
  .sf-pagination {
    padding: 12px 8px;
  }
}
@media (max-width: 480px) {
  .sf-subtitle-item {
    padding: 10px 12px;
    gap: 8px;
  }
  .sf-subtitle-item__time {
    font-size: 10px;
    padding: 2px 6px;
    min-width: 50px;
  }
  .sf-subtitle-item__text {
    font-size: 14px;
  }
  .sf-subtitle-item__cn {
    font-size: 12px;
  }
}
</style>
