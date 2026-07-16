<template>
  <!-- Phase 27: 始终渲染 — 没 currentSubtitle 时显示引导占位 (让用户一眼看到跟读功能入口) -->
  <div class="sf-shadowing-card">
    <!-- 空状态: 没选字幕时, 引导用户播放 -->
    <div v-if="!currentSubtitle" class="sf-shadowing-card__empty">
      <Mic :size="32" class="sf-shadowing-card__empty-icon" />
      <div class="sf-shadowing-card__empty-title">跟读模式</div>
      <div class="sf-shadowing-card__empty-desc">
        点击播放视频开始跟读 · 每句对照原文录音模仿<br/>
        支持 TTS 发音 / 发音评测 (按 R 键快速录音)
      </div>
    </div>
    <template v-else>
    <div class="sf-shadowing-card__display">
      <!-- 头部信息 -->
      <div class="sf-shadowing-card__header">
        <span class="sf-shadowing-card__index">{{ currentIndex + 1 }} / {{ totalSubtitles }}</span>
        <span class="sf-shadowing-card__time">{{ formatTime(currentSubtitle.start_time) }}</span>
      </div>

      <!-- 字幕内容 — font-size 由 props.fontSize 控制 (Phase 2 H5: 字幕设置 sheet 修 bug) -->
      <div class="sf-shadowing-card__body" :style="{ '--sf-subtitle-font-size': fontSize + 'px' }">
        <div class="sf-shadowing-card__en" v-if="!showOnlyChinese" v-html="enHtml"></div>
        <transition name="sf-fade">
          <div class="sf-shadowing-card__cn" v-if="showTranslation && currentSubtitle.text_cn && !showOnlyChinese">
            {{ currentSubtitle.text_cn }}
          </div>
        </transition>
        <transition name="sf-fade">
          <div class="sf-shadowing-card__cn-only" v-if="showOnlyChinese && currentSubtitle.text_cn">
            <span class="translate-hint">翻译练习模式</span>
            {{ currentSubtitle.text_cn }}
          </div>
        </transition>
      </div>

      <!-- 操作区 -->
      <div class="sf-shadowing-card__actions">
        <!-- 第一行：导航 + 快捷开关 -->
        <div class="sf-shadowing-card__row">
          <!-- 导航组 -->
          <div class="sf-shadowing-card__nav">
            <button class="sf-icon-btn" @click="$emit('prev')" :disabled="currentIndex <= 0" :title="'上一句'">
              <ArrowLeft :size="16" />
            </button>
            <button class="sf-icon-btn" @click="$emit('replay')" :disabled="currentIndex < 0" :title="'重播'">
              <RefreshCw :size="16" />
            </button>
            <button class="sf-icon-btn" @click="$emit('next')" :disabled="currentIndex >= totalSubtitles - 1" :title="'下一句'">
              <ArrowRight :size="16" />
            </button>
          </div>
          <!-- 快捷开关 -->
          <div class="sf-shadowing-card__toggles">
            <button
              :class="['sf-tool-btn', 'sf-tool-btn--compact', { active: showTranslation }]"
              @click="$emit('toggle-translation')"
              :disabled="showOnlyChinese"
              title="显示/隐藏翻译"
            >
              <MessageCircle :size="14" />
            </button>
            <button
              :class="['sf-tool-btn', 'sf-tool-btn--compact', { active: showMoreTools }]"
              @click="showMoreTools = !showMoreTools"
              title="更多工具"
            >
              <MoreHorizontal :size="14" />
            </button>
          </div>
        </div>

        <!-- 展开工具栏（低频功能） -->
        <transition name="sf-fade">
          <div v-if="showMoreTools" class="sf-shadowing-card__more">
            <button class="sf-tool-btn" @click="$emit('speak')" :disabled="currentIndex < 0">
              <Send :size="14" />
              TTS 发音
            </button>
            <button
              :class="['sf-tool-btn', { active: showOnlyChinese }]"
              @click="$emit('toggle-chinese-only')"
            >
              <FileText :size="14" />
              {{ showOnlyChinese ? '退出练习' : '翻译练习' }}
            </button>
            <button
              class="sf-tool-btn"
              @click="$emit('add-vocabulary')"
              :disabled="!isLoggedIn || !currentSubtitle"
            >
              <BookOpen :size="14" />
              加入生词本
            </button>
          </div>
        </transition>

        <!-- 第二行：核心操作 -->
        <div class="sf-shadowing-card__main">
          <button
            :class="['sf-record-btn', { recording: isRecording }]"
            @click="$emit('toggle-recording')"
          >
            <Pause v-if="isRecording" :size="16" />
            <Mic v-else :size="16" />
            {{ isRecording ? '停止录音' : '开始跟读' }}
          </button>
          <button
            v-if="recordedBlob"
            class="sf-eval-btn"
            @click="$emit('evaluate')"
            :disabled="evaluationLoading"
          >
            <BarChart3 :size="16" />
            评测发音
          </button>
        </div>
      </div>

      <!-- 录音状态指示器 -->
      <div v-if="isRecording" class="sf-recording-indicator">
        <div class="sf-recording-dot"></div>
        <span>正在录音，请跟读...</span>
      </div>

      <!-- 录音回放 -->
      <div v-if="audioUrl" class="sf-playback">
        <div class="sf-playback__header">
          <span class="sf-playback__title">你的录音</span>
          <button class="sf-clear-btn" @click="$emit('clear-recording')">清除</button>
        </div>
        <audio :src="audioUrl" controls class="sf-playback__audio"></audio>
      </div>

      <!-- 评测结果 -->
      <transition name="sf-slide">
        <div v-if="pronunciationResult" class="sf-eval-result">
          <div class="sf-eval-result__header">
            <div class="sf-eval-score" :class="getScoreClass(pronunciationResult.score)">
              {{ pronunciationResult.score }}
            </div>
            <div class="sf-eval-result__meta">
              <div class="sf-eval-meta-item">
                <span class="sf-eval-meta-item__label">准确度</span>
                <span class="sf-eval-meta-item__value">{{ pronunciationResult.accuracy }}</span>
              </div>
              <div class="sf-eval-meta-item">
                <span class="sf-eval-meta-item__label">流利度</span>
                <span class="sf-eval-meta-item__value">{{ pronunciationResult.fluency }}</span>
              </div>
            </div>
          </div>
          <div v-if="pronunciationResult.problems?.length" class="sf-eval-section">
            <div class="sf-eval-section__title">
              <Crosshair :size="14" class="sf-eval-section__icon" /> 发音问题
            </div>
            <ul class="sf-eval-section__list">
              <li v-for="(p, i) in pronunciationResult.problems" :key="i">{{ p }}</li>
            </ul>
          </div>
          <div v-if="pronunciationResult.suggestions?.length" class="sf-eval-section">
            <div class="sf-eval-section__title">
              <Lightbulb :size="14" class="sf-eval-section__icon" /> 改进建议
            </div>
            <ul class="sf-eval-section__list">
              <li v-for="(s, i) in pronunciationResult.suggestions" :key="i">{{ s }}</li>
            </ul>
          </div>
        </div>
      </transition>
    </div>
    </template>
  </div>
</template>

<script setup>
import {
  ArrowLeft, ArrowRight, Mic, Pause, RefreshCw,
  MessageCircle, BookOpen, BarChart3, FileText, Send, MoreHorizontal,
  Crosshair, Lightbulb
} from 'lucide-vue-next'
import { ref, computed } from 'vue'
import { highlightKeyWords as hlKeyWords } from '@/lib/highlightText'

const showMoreTools = ref(false)

const props = defineProps({
  currentSubtitle: { type: Object, default: null },
  currentIndex: { type: Number, default: -1 },
  totalSubtitles: { type: Number, default: 0 },
  showTranslation: { type: Boolean, default: true },
  showOnlyChinese: { type: Boolean, default: false },
  isRecording: { type: Boolean, default: false },
  audioUrl: { type: String, default: null },
  recordedBlob: { type: Object, default: null },
  pronunciationResult: { type: Object, default: null },
  evaluationLoading: { type: Boolean, default: false },
  isLoggedIn: { type: Boolean, default: false },
  // Phase 2 H5 字幕字号 (px): 14 / 16 / 18 / 20
  fontSize: { type: Number, default: 16 }
})

// Phase 22: 客户端启发式关键词高亮 (年份/专有名词/高频长词)
const enHtml = computed(() => {
  const text = props.currentSubtitle?.text_en || ''
  if (!text) return ''
  return hlKeyWords(text)
})

defineEmits([
  'prev', 'next', 'replay', 'speak', 'toggle-recording', 'evaluate', 'clear-recording',
  'toggle-translation', 'toggle-chinese-only', 'add-vocabulary'
])

const formatTime = (ms) => {
  const seconds = Math.floor(ms / 1000)
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}
</script>

<style scoped>
.sf-shadowing-card {
  background: var(--color-bg-card);
  overflow: hidden;
}

.sf-shadowing-card__display {
  padding: 20px 0;
}

/* 头部 */
.sf-shadowing-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.sf-shadowing-card__index {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-muted);
}

.sf-shadowing-card__time {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-brand-bright);
  background: var(--sf-brand-subtle);
  padding: 2px 10px;
  border-radius: var(--sf-radius-full);
  border: 1px solid rgba(37, 99, 235, 0.2);
}

/* 主体分区 */
.sf-shadowing-card__body {
  margin-bottom: 16px;
}

/* 英文区 — 用 CSS 变量控制字号 (Phase 2 H5: 字幕设置 sheet 修 bug) */
.sf-shadowing-card__en {
  font-size: var(--sf-subtitle-font-size, 16px);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.45;
  letter-spacing: -0.3px;
  position: relative;
  padding-bottom: 16px;
  margin-bottom: 0;
}

.sf-shadowing-card__en::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 48px;
  height: 3px;
  background: var(--sf-cta-gradient, linear-gradient(90deg, #60A5FA, #3B82F6));
  border-radius: 2px;
}

/* 中文翻译区 — 字号跟随主字号 (Phase 2 H5: 字幕设置 sheet 修 bug) */
.sf-shadowing-card__cn {
  font-size: calc(var(--sf-subtitle-font-size, 16px) * 0.78);
  color: var(--color-text-secondary);
  line-height: 1.6;
  padding: 12px 14px;
  background: var(--color-bg-elevated);
  border-radius: var(--sf-radius-lg);
  border-left: 3px solid var(--color-brand-bright);
  margin-top: 12px;
}

.sf-shadowing-card__cn-only {
  font-size: var(--sf-subtitle-font-size, 16px);
  color: var(--color-text-primary);
  line-height: 1.6;
}

.translate-hint {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: 6px;
  padding: 2px 10px;
  background: var(--color-bg-elevated);
  border-radius: var(--sf-radius-full);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 操作区 */
.sf-shadowing-card__actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 第一行：导航 + 快捷开关 */
.sf-shadowing-card__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.sf-shadowing-card__nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sf-shadowing-card__toggles {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 紧凑工具按钮（仅图标） */
.sf-tool-btn--compact {
  padding: 6px 8px;
  gap: 0;
}

/* 展开工具栏 */
.sf-shadowing-card__more {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px;
  background: var(--color-bg-pale, rgba(0,0,0,0.02));
  border-radius: var(--sf-radius-md, 10px);
}

.sf-shadowing-card__main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* 录音按钮 */
.sf-record-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--sf-radius-full);
  border: none;
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
  font-family: inherit;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.sf-record-btn:hover {
  filter: brightness(1.08);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
  transform: translateY(-1px);
}
.sf-record-btn.recording {
  background: var(--color-danger);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}
.sf-record-btn.recording::before,
.sf-record-btn.recording::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 3px;
  height: 16px;
  background: rgba(255,255,255,0.6);
  border-radius: 2px;
  transform: translateY(-50%);
  animation: waveform 0.8s ease-in-out infinite;
}
.sf-record-btn.recording::before { left: 50%; margin-left: -8px; animation-delay: 0s; }
.sf-record-btn.recording::after { right: 50%; margin-right: 8px; animation-delay: 0.2s; }
@keyframes waveform {
  0%, 100% { height: 8px; opacity: 0.5; }
  50% { height: 20px; opacity: 1; }
}
.sf-record-btn.recording:hover {
  background: #dc2626;
}

/* 评测按钮 */
.sf-eval-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--sf-radius-full);
  border: 1px solid var(--color-border-brand);
  background: var(--color-bg-mint);
  color: var(--color-brand-bright);
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
  font-family: inherit;
}
.sf-eval-btn:hover {
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  border-color: transparent;
  color: #fff;
  transform: translateY(-1px);
}

/* 工具按钮 */
.sf-tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--sf-radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
  font-family: inherit;
}
.sf-tool-btn:hover {
  border-color: var(--color-border-brand);
  color: var(--color-brand-bright);
}
.sf-tool-btn.active {
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  border-color: transparent;
  color: #fff;
}
.sf-tool-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 录音指示器 */
.sf-recording-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 12px;
  padding: 10px 16px;
  background: rgba(37, 99, 235, 0.08);
  border-radius: var(--sf-radius-full);
  color: var(--color-brand-bright);
  font-size: 13px;
  font-weight: 500;
  border: 1px solid rgba(37, 99, 235, 0.2);
}

.sf-recording-dot {
  width: 10px;
  height: 10px;
  background: var(--color-brand-bright);
  border-radius: 50%;
  animation: recordingPulse 1.2s ease infinite;
}

@keyframes recordingPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.9); }
}

/* 回放 */
.sf-playback {
  margin-top: 12px;
  padding: 12px;
  background: var(--color-bg-elevated);
  border-radius: var(--sf-radius-md);
}

.sf-playback__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.sf-playback__title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.sf-clear-btn {
  font-size: 12px;
  color: var(--color-danger);
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: inherit;
  padding: 2px 8px;
  border-radius: var(--sf-radius-sm);
  transition: background var(--sf-duration-fast);
}
.sf-clear-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

.sf-playback__audio {
  width: 100%;
  height: 36px;
  border-radius: var(--sf-radius-sm);
}

/* 评测结果 */
.sf-eval-result {
  margin-top: 12px;
  padding: 14px;
  background: var(--color-bg-elevated);
  border-radius: var(--sf-radius-lg);
  border: 1px solid var(--color-border);
}

.sf-eval-result__header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.sf-eval-score {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  height: 48px;
  padding: 0 14px;
  border-radius: var(--sf-radius-lg);
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-brand-bright), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.sf-eval-score.score-high { background: linear-gradient(135deg, #10b981, var(--color-accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.sf-eval-score.score-medium { background: linear-gradient(135deg, #f59e0b, #f97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.sf-eval-score.score-low { background: linear-gradient(135deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

.sf-eval-result__meta {
  display: flex;
  gap: 16px;
}

.sf-eval-meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sf-eval-meta-item__label {
  font-size: 11px;
  color: var(--color-text-muted);
}

.sf-eval-meta-item__value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.sf-eval-section {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}

.sf-eval-section__title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.sf-eval-section__icon {
  font-size: 14px;
  line-height: 1;
}

.sf-eval-section__list {
  margin: 0;
  padding-left: 16px;
}

.sf-eval-section__list li {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 3px 0;
}

/* ==================== Phase 1B Task 6: Mobile 适配 ==================== */
@media (max-width: 768px) {
  .sf-shadowing-card {
    padding: 12px;
  }
  .sf-shadowing-card__header {
    margin-bottom: 10px;
  }
  .sf-shadowing-card__en {
    font-size: 20px;
    line-height: 1.5;
    margin-bottom: 10px;
  }
  .sf-shadowing-card__cn {
    font-size: 15px;
    line-height: 1.6;
  }
  .sf-icon-btn {
    min-width: 44px;
    min-height: 44px;
  }
  .sf-record-btn {
    padding: 14px 32px;
    font-size: 16px;
    min-height: 48px;
  }
  .sf-tool-btn {
    min-height: 44px;
    padding: 10px 16px;
    font-size: 13px;
  }
  .sf-shadowing-card__nav,
  .sf-shadowing-card__main,
  .sf-shadowing-card__tools {
    gap: 10px;
  }
  .sf-eval-result {
    padding: 12px;
  }
  .sf-eval-score {
    font-size: 20px;
    min-width: 44px;
    height: 44px;
  }
}
@media (max-width: 480px) {
  .sf-shadowing-card__en {
    font-size: 18px;
  }
  .sf-record-btn {
    padding: 12px 24px;
    font-size: 15px;
  }
  .sf-tool-btn {
    font-size: 12px;
    padding: 8px 12px;
  }
}

/* Phase 27: 空状态 (未选字幕时引导用户播放) */
.sf-shadowing-card__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  text-align: center;
  min-height: 160px;
}
.sf-shadowing-card__empty-icon {
  color: var(--color-brand);
  margin-bottom: 12px;
  opacity: 0.7;
}
.sf-shadowing-card__empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 6px;
}
.sf-shadowing-card__empty-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.6;
}

/* (Phase 22: .kw-* 走 global.css, v-html 注入的 DOM 没有 data-v-hash 所以 scoped 不生效)
   这里加一份 :deep() 兜底, 防止用户切换主题时漂移 */
.sf-shadowing-card :deep(.kw-word),
.sf-shadowing-card :deep(.kw-prop),
.sf-shadowing-card :deep(.kw-year) {
  font-weight: 600;
  cursor: help;
}
.sf-shadowing-card :deep(.kw-year) {
  color: #B45309;
}
</style>
