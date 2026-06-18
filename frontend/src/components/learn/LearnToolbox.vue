<template>
  <div class="sf-toolbox">
    <!-- 学习进度 -->
    <div class="sf-toolbox__progress">
      <div class="sf-progress-ring">
        <svg viewBox="0 0 80 80" class="sf-progress-ring__svg">
          <circle class="sf-progress-ring__track" cx="40" cy="40" r="34" fill="none" stroke-width="6" />
          <circle
            class="sf-progress-ring__fill"
            cx="40" cy="40" r="34" fill="none" stroke-width="6"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            stroke-linecap="round"
            :transform="'rotate(-90 40 40)'"
          />
        </svg>
        <div class="sf-progress-ring__text">
          <span class="sf-progress-ring__num">{{ Math.round(learningProgress) }}</span>
          <span class="sf-progress-ring__pct">%</span>
        </div>
      </div>
      <span class="sf-toolbox__label">学习进度</span>
    </div>

    <!-- 统计卡片 -->
    <div class="sf-toolbox__stats">
      <button
        class="sf-stat-item"
        :class="{ active: activeStat === 'vocab' }"
        @click="$emit('open-interpretation'); activeStat = 'vocab'"
      >
        <div class="sf-stat-item__icon sf-stat-item__icon--vocab">
          <BookOpen :size="18" />
        </div>
        <div class="sf-stat-item__info">
          <span class="sf-stat-item__num">{{ vocabCount }}</span>
          <span class="sf-stat-item__label">生词解读</span>
        </div>
      </button>

      <button
        class="sf-stat-item"
        :class="{ active: activeStat === 'bookmark' }"
        @click="$emit('scroll-to-bookmarks'); activeStat = 'bookmark'"
      >
        <div class="sf-stat-item__icon sf-stat-item__icon--bookmark">
          <Star :size="18" />
        </div>
        <div class="sf-stat-item__info">
          <span class="sf-stat-item__num">{{ bookmarkCount }}</span>
          <span class="sf-stat-item__label">收藏句子</span>
        </div>
      </button>

      <div class="sf-stat-item sf-stat-item--static">
        <div class="sf-stat-item__icon sf-stat-item__icon--annot">
          <Edit3 :size="18" />
        </div>
        <div class="sf-stat-item__info">
          <span class="sf-stat-item__num">{{ annotationCount }}</span>
          <span class="sf-stat-item__label">重点标注</span>
        </div>
      </div>
    </div>

    <!-- AI 解读 CTA -->
    <button
      class="sf-toolbox__ai-btn"
      :class="{ generating: isGenerating }"
      @click="$emit('open-interpretation')"
      :disabled="isGenerating"
    >
      <Sparkles :size="16" />
      <span>{{ isGenerating ? 'AI 分析中...' : (hasInterpretation ? '查看词汇解读' : 'AI 智能解读') }}</span>
      <ChevronRight v-if="!isGenerating" :size="14" />
    </button>

    <!-- 快捷提示 -->
    <div class="sf-toolbox__tips">
      <div class="sf-toolbox__tip">
        <kbd>Space</kbd>
        <span>播放/暂停</span>
      </div>
      <div class="sf-toolbox__tip">
        <kbd>←</kbd><kbd>→</kbd>
        <span>切换字幕</span>
      </div>
      <div class="sf-toolbox__tip">
        <kbd>R</kbd>
        <span>跟读录音</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { BookOpen, Star, Edit3, Sparkles, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  learningProgress: { type: Number, default: 0 },
  vocabCount: { type: Number, default: 0 },
  bookmarkCount: { type: Number, default: 0 },
  annotationCount: { type: Number, default: 0 },
  hasInterpretation: { type: Boolean, default: false },
  isGenerating: { type: Boolean, default: false }
})

defineEmits(['open-interpretation', 'scroll-to-bookmarks'])

const activeStat = ref('vocab')

const circumference = 2 * Math.PI * 34
const dashOffset = computed(() => {
  return circumference - (props.learningProgress / 100) * circumference
})
</script>

<style scoped>
.sf-toolbox {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 16px;
}

/* 进度环 */
.sf-toolbox__progress {
  background: var(--color-brand, #2563EB);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  position: relative;
  overflow: hidden;
}
.sf-toolbox__progress::before {
  content: '';
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
}

.sf-progress-ring {
  position: relative;
  width: 80px;
  height: 80px;
}
.sf-progress-ring__svg {
  width: 100%;
  height: 100%;
}
.sf-progress-ring__track {
  stroke: rgba(255,255,255,0.12);
}
.sf-progress-ring__fill {
  stroke: var(--color-brand-bright, #3B82F6);
  transition: stroke-dashoffset 0.5s ease;
}
.sf-progress-ring__text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: baseline;
  justify-content: center;
  color: #fff;
}
.sf-progress-ring__num {
  font-size: 24px;
  font-weight: 800;
  font-family: 'Inter', sans-serif;
}
.sf-progress-ring__pct {
  font-size: 12px;
  opacity: 0.6;
  margin-left: 1px;
}

.sf-toolbox__label {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  letter-spacing: 0.05em;
}

/* 统计项 */
.sf-toolbox__stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sf-stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--sf-bg-card, #fff);
  border: 1px solid var(--color-border, rgba(0,0,0,0.06));
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
  font-family: inherit;
}
.sf-stat-item:hover {
  border-color: var(--color-brand-bright, #3B82F6);
  transform: translateX(2px);
}
.sf-stat-item.active {
  border-color: var(--color-brand-bright, #3B82F6);
  background: var(--color-bg-mint, #E8F5EE);
}
.sf-stat-item--static {
  cursor: default;
}
.sf-stat-item--static:hover {
  transform: none;
  border-color: var(--color-border, rgba(0,0,0,0.06));
}

.sf-stat-item__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.sf-stat-item__icon--vocab {
  background: rgba(37, 99, 235, 0.1);
  color: var(--color-brand, #2563EB);
}
.sf-stat-item__icon--bookmark {
  background: rgba(245, 158, 11, 0.12);
  color: #F59E0B;
}
.sf-stat-item__icon--annot {
  background: rgba(63, 138, 91, 0.12);
  color: var(--color-brand-bright, #3B82F6);
}

.sf-stat-item__info {
  display: flex;
  flex-direction: column;
}
.sf-stat-item__num {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text, #1A2820);
  font-family: 'Inter', sans-serif;
  line-height: 1.2;
}
.sf-stat-item__label {
  font-size: 11px;
  color: var(--color-text-muted, #6b7280);
}

/* AI CTA */
.sf-toolbox__ai-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, var(--color-brand-bright, #3B82F6), var(--color-brand, #2563EB));
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  box-shadow: 0 2px 12px rgba(37, 99, 235, 0.2);
}
.sf-toolbox__ai-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
}
.sf-toolbox__ai-btn.generating {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 快捷键提示 */
.sf-toolbox__tips {
  background: var(--sf-bg-card, #fff);
  border: 1px solid var(--color-border, rgba(0,0,0,0.06));
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sf-toolbox__tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--color-text-muted, #6b7280);
}
.sf-toolbox__tip kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 5px;
  background: var(--color-bg-pale, #f5f5f4);
  border: 1px solid var(--color-border, rgba(0,0,0,0.1));
  border-radius: 4px;
  font-size: 10px;
  font-family: 'Inter', monospace;
  color: var(--color-text, #1A2820);
}
.sf-toolbox__tip span {
  margin-left: 4px;
}
</style>
