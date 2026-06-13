<!--
  LearnHeader.vue - Phase 1B Task 4
  学习页头部：返回按钮 + 标题 + 收藏 + 进度条 + 统计徽章
-->
<template>
  <div class="sf-page-header">
    <div class="sf-header-top">
      <div class="sf-header-left">
        <button class="sf-icon-btn" type="button" @click="$emit('back')" aria-label="返回">
          <ArrowLeft :size="20" />
        </button>
        <h1 class="sf-title">{{ title }}</h1>
      </div>
      <div class="sf-header-right">
        <SfTooltip :content="isFavorited ? '取消收藏' : '收藏'" placement="bottom">
          <button
            type="button"
            :class="['sf-btn', isFavorited ? 'sf-btn--active' : 'sf-btn--ghost', 'sf-btn--sm']"
            @click="$emit('toggle-favorite')"
            :disabled="favoriteLoading"
          >
            <BookmarkCheck v-if="isFavorited" :size="16" />
            <Bookmark v-else :size="16" />
            <span>{{ isFavorited ? '已收藏' : '收藏' }}</span>
          </button>
        </SfTooltip>
      </div>
    </div>

    <!-- 学习进度条 + 统计 -->
    <div class="sf-header-meta">
      <div class="sf-progress-bar">
        <div class="sf-progress-bar__fill" :style="{ width: learningProgress + '%' }"></div>
      </div>
      <div class="sf-header-stats">
        <span class="sf-stat-badge">
          <FileText :size="14" />
          已学习 {{ currentIndex >= 0 ? currentIndex + 1 : 0 }} / {{ totalSubtitles }} 句
        </span>
        <span v-if="bookmarkedCount > 0" class="sf-stat-badge">
          <Star :size="14" />
          {{ bookmarkedCount }} 个重点
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ArrowLeft, FileText, Star, Bookmark, BookmarkCheck } from 'lucide-vue-next'
import SfTooltip from '@/components/ui/SfTooltip.vue'

defineProps({
  title: { type: String, default: '' },
  isFavorited: { type: Boolean, default: false },
  favoriteLoading: { type: Boolean, default: false },
  learningProgress: { type: Number, default: 0 },
  currentIndex: { type: Number, default: -1 },
  totalSubtitles: { type: Number, default: 0 },
  bookmarkedCount: { type: Number, default: 0 }
})

defineEmits(['back', 'toggle-favorite'])
</script>

<style scoped>
.sf-page-header {
  margin-bottom: 16px;
}

.sf-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 4px 0 12px;
}

.sf-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.sf-icon-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-fast);
  flex-shrink: 0;
}
.sf-icon-btn:hover {
  background: var(--color-brand-subtle);
  color: var(--color-brand);
  border-color: var(--color-border-brand);
}

.sf-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.sf-header-right {
  flex-shrink: 0;
}

.sf-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast);
  border: 1px solid transparent;
  white-space: nowrap;
}

.sf-btn--sm {
  padding: 6px 12px;
  font-size: 13px;
}

.sf-btn--ghost {
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}
.sf-btn--ghost:hover {
  color: var(--color-brand);
  border-color: var(--color-border-brand);
  background: var(--color-brand-subtle);
}

.sf-btn--active {
  background: var(--color-brand);
  color: #fff;
  border-color: var(--color-brand);
}
.sf-btn--active:hover {
  background: var(--color-brand-hover);
}

.sf-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 进度条 */
.sf-header-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sf-progress-bar {
  height: 6px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-full);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.sf-progress-bar__fill {
  height: 100%;
  background: var(--color-brand);
  border-radius: var(--radius-full);
  transition: width var(--duration-slow);
}

.sf-header-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sf-stat-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
}

/* 响应式 */
@media (max-width: 768px) {
  .sf-title {
    font-size: 16px;
  }
  .sf-icon-btn {
    width: 32px;
    height: 32px;
  }
  .sf-btn--sm {
    padding: 4px 10px;
    font-size: 12px;
  }
}
@media (max-width: 480px) {
  .sf-title {
    font-size: 15px;
  }
  .sf-header-top {
    padding-bottom: 8px;
  }
  .sf-stat-badge {
    font-size: 11px;
    padding: 2px 8px;
  }
}
</style>