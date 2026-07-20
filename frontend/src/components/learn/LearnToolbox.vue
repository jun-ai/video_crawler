<template>
  <div class="sf-toolbox">
    <!-- 学习进度 (Phase 28+2: 横条 — 原 148px 圆环 → ~60px 横条, 腾出空间给 stats/tips) -->
    <div class="sf-toolbox__progress">
      <div class="sf-toolbox__progress-head">
        <span class="sf-toolbox__label">学习进度</span>
        <span class="sf-toolbox__progress-num">{{ Math.round(learningProgress) }}%</span>
      </div>
      <div class="sf-progress-bar">
        <div class="sf-progress-bar__fill" :style="{ width: learningProgress + '%' }"></div>
      </div>
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
          <span class="sf-stat-item__label">解读</span>
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

    <!-- 智能解读 CTA -->
    <button
      class="sf-toolbox__ai-btn"
      :class="{ generating: isGenerating }"
      @click="$emit('open-interpretation')"
      :disabled="isGenerating"
    >
      <Sparkles :size="16" />
      <span>{{ isGenerating ? '智能分析中...' : (hasInterpretation ? '查看词汇解读' : '智能解读') }}</span>
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
import { ref } from 'vue'
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
</script>

<style scoped>
.sf-toolbox {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 16px;
}

/* 进度条 (Phase 28+2: 圆环 → 横条, 卡从 148px 降到 ~70px) */
.sf-toolbox__progress {
  background: var(--color-brand, #2563EB);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  overflow: hidden;
}
.sf-toolbox__progress::before {
  content: '';
  position: absolute;
  top: -20px;
  right: -20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
}

.sf-toolbox__progress-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}

.sf-toolbox__progress-num {
  font-size: 18px;
  font-weight: 800;
  color: #fff;
  font-family: 'Inter', sans-serif;
  line-height: 1;
}

.sf-progress-bar {
  position: relative;
  height: 6px;
  background: rgba(255,255,255,0.18);
  border-radius: var(--radius-full, 999px);
  overflow: hidden;
}
.sf-progress-bar__fill {
  /* Phase 28+2: content-box + 父容器 border-box, width % 严格按父 content 算
     (原本 border-box 跟 bar 的 9999px radius + box-sizing 互相影响, 渲染 100% 实为 ~88%) */
  box-sizing: content-box;
  height: 100%;
  background: #fff;
  border-radius: var(--radius-full, 999px);
  transition: width var(--sf-duration-slower, 0.4s) ease;
  box-shadow: 0 0 6px rgba(255,255,255,0.5);
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
  transition: all var(--sf-duration-normal);
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
  background: rgba(37, 99, 235, 0.12);
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
  transition: all var(--sf-duration-normal);
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
/* 7-20: H5 端太小只展示主要功能, 隐藏工具箱里的 AI 解读按钮 (PC 不动) */
@media (max-width: 768px) {
  .sf-toolbox__ai-btn {
    display: none !important;
  }
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
