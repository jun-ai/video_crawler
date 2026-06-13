<template>
  <div class="sf-dictation-mode">
    <!-- 进度条 -->
    <div class="sf-dictation-progress">
      <div class="sf-dictation-progress__info">
        <span class="sf-dictation-progress__label">听写进度</span>
        <span class="sf-dictation-progress__count">{{ currentIndex + 1 }} / {{ subtitles.length }}</span>
      </div>
      <div class="sf-dictation-progress__bar-wrapper">
        <div class="sf-dictation-progress__bar">
          <div class="sf-dictation-progress__fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <span class="sf-dictation-progress__percent">{{ progressPercentage }}%</span>
      </div>
    </div>

    <!-- 音频播放区 -->
    <div class="sf-dictation-audio">
      <div class="sf-dictation-audio__icon" :class="{ playing: isPlaying }">
        <Headphones :size="36" />
      </div>
      <div class="sf-dictation-audio__info">
        <h3 class="sf-dictation-audio__title">听写练习</h3>
        <p class="sf-dictation-audio__desc">点击播放按钮，听音频并填写缺失的单词</p>
      </div>
      <div class="sf-dictation-audio__actions">
        <button class="sf-btn sf-btn--primary" @click="playAudio" :disabled="isPlaying">
          <Play />
          {{ isPlaying ? '播放中...' : '播放音频' }}
        </button>
        <button class="sf-btn sf-btn--ghost" @click="playAudio" :disabled="isPlaying || playCount >= maxPlayCount">
          <RefreshCw />
          重听 ({{ maxPlayCount - playCount }}/3)
        </button>
      </div>
      <div class="sf-dictation-audio__status" v-if="playCount > 0">
        <span class="sf-dictation-status-tag">已播放 {{ playCount }} 次</span>
      </div>
    </div>

    <!-- 填空区域 -->
    <div class="sf-dictation-fill" v-if="!isSubmitted">
      <!-- 模式切换 Tab -->
      <div class="sf-dictation-mode-select">
        <button :class="['sf-segment__item', { active: answerMode === 'input' }]" @click="answerMode = 'input'">
          <PenLine /> 填空模式
        </button>
        <button :class="['sf-segment__item', { active: answerMode === 'choice' }]" @click="answerMode = 'choice'">
          <List /> 选择模式
        </button>
      </div>

      <!-- 句子填空显示 -->
      <div class="sf-dictation-sentence">
        <template v-for="(part, i) in sentenceParts" :key="i">
          <span v-if="part.type === 'text'" class="sf-dictation-text">{{ part.content }}</span>
          <span v-else class="sf-dictation-blank">
            <input
              class="sf-dictation-input"
              :class="{
                'sf-dictation-input--correct': isSubmitted && isWordCorrect(part.wordIndex),
                'sf-dictation-input--wrong': isSubmitted && !isWordCorrect(part.wordIndex)
              }"
              v-model="userAnswers[part.wordIndex]"
              :placeholder="'(' + (part.wordIndex + 1) + ')'"
              @keyup.enter="focusNextBlank(part.wordIndex)"
            />
          </span>
        </template>
      </div>

      <!-- 选择模式 -->
      <div class="sf-dictation-choices" v-if="answerMode === 'choice'">
        <div v-for="(blank, bIndex) in blankWords" :key="bIndex" class="sf-dictation-choice-row">
          <span class="sf-dictation-choice-label">第 {{ bIndex + 1 }} 空</span>
          <div class="sf-dictation-choice-options">
            <button
              v-for="(option, oIndex) in blank.options"
              :key="oIndex"
              :class="['sf-dictation-choice-btn', { selected: selectedChoices[bIndex] === oIndex }]"
              @click="selectChoice(bIndex, oIndex)"
            >
              {{ option }}
            </button>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="sf-dictation-actions">
        <button class="sf-btn sf-btn--primary" @click="submitAnswer" :disabled="!canSubmit || submitting">
          <Check /> 提交答案
        </button>
        <button class="sf-btn sf-btn--ghost" @click="showAnswer">
          <Eye /> 查看答案
        </button>
        <button class="sf-btn sf-btn--ghost" @click="skipCurrent">
          <ChevronRight /> 跳过
        </button>
      </div>
    </div>

    <!-- 结果展示 -->
    <div class="sf-dictation-result" v-if="isSubmitted">
      <div class="sf-dictation-result__header">
        <div class="sf-dictation-score" :class="scoreClass">
          {{ result?.score }}
          <span class="sf-dictation-score__unit">分</span>
        </div>
        <div class="sf-dictation-result__feedback">
          <p>{{ result?.feedback }}</p>
        </div>
      </div>

      <!-- 答案对比 -->
      <div class="sf-dictation-comparison">
        <div class="sf-dictation-comparison__row">
          <span class="sf-dictation-comparison__label">正确答案</span>
          <div class="sf-dictation-comparison__text">
            <span v-for="(part, i) in sentenceParts" :key="i">
              <span v-if="part.type === 'text'">{{ part.content }} </span>
              <span v-else class="sf-word-tag sf-word-tag--correct">{{ part.answer }}</span>
            </span>
          </div>
        </div>
        <div class="sf-dictation-comparison__row">
          <span class="sf-dictation-comparison__label">你的答案</span>
          <div class="sf-dictation-comparison__text">
            <span v-for="(part, i) in sentenceParts" :key="i">
              <span v-if="part.type === 'text'">{{ part.content }} </span>
              <span v-else :class="['sf-word-tag', isWordCorrect(part.wordIndex) ? 'sf-word-tag--correct' : 'sf-word-tag--wrong']">
                {{ getUserAnswer(part.wordIndex) || '(未填)' }}
              </span>
            </span>
          </div>
        </div>
      </div>

      <!-- 单词结果标签 -->
      <div class="sf-dictation-word-tags">
        <div
          v-for="(blank, index) in blankWords"
          :key="index"
          :class="['sf-word-tag-row', isWordCorrect(index) ? 'sf-word-tag-row--correct' : 'sf-word-tag-row--wrong']"
        >
          <span class="sf-word-tag-row__num">{{ index + 1 }}</span>
          <span class="sf-word-tag-row__answer">{{ blank.word }}</span>
          <CheckCircle2 v-if="isWordCorrect(index)" :size="16" />
          <XCircle v-else :size="16" />
          <span class="sf-word-tag-row__yours">{{ getUserAnswer(index) || '未填' }}</span>
        </div>
      </div>

      <!-- 结果操作按钮 -->
      <div class="sf-dictation-result__actions">
        <button v-if="result?.score < 80" class="sf-btn sf-btn--ghost" @click="retryCurrent">
          <RefreshCw /> 再试一次
        </button>
        <button class="sf-btn sf-btn--primary" @click="nextSentence">
          {{ isLastSentence ? '完成练习' : '下一句' }}
          <ChevronRight />
        </button>
      </div>
    </div>

    <!-- 完成弹窗 -->
    <SfDialog
      v-model="showCompleteDialog"
      width="420px"
    >
      <div class="sf-complete-modal__body">
        <div class="sf-complete-modal__icon">
          <Trophy :size="56" />
        </div>
        <h3 class="sf-complete-modal__title">练习完成</h3>
        <p class="sf-complete-modal__desc">你已完成本次听写练习</p>
        <div class="sf-complete-modal__stats">
          <div class="sf-complete-modal__stat">
            <span class="sf-complete-modal__stat-value">{{ completedCount }}</span>
            <span class="sf-complete-modal__stat-label">完成句数</span>
          </div>
          <div class="sf-complete-modal__stat">
            <span class="sf-complete-modal__stat-value">{{ averageScore }}</span>
            <span class="sf-complete-modal__stat-label">平均得分</span>
          </div>
          <div class="sf-complete-modal__stat">
            <span class="sf-complete-modal__stat-value">{{ correctRate }}%</span>
            <span class="sf-complete-modal__stat-label">正确率</span>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="sf-complete-modal__footer">
          <button class="sf-btn sf-btn--ghost" @click="showCompleteDialog = false">关闭</button>
          <button class="sf-btn sf-btn--primary" @click="restartDictation">重新开始</button>
        </div>
      </template>
    </SfDialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { toast } from '@/composables/useToast'
import { useTTS } from '@/composables/useTTS'
import {
  Play,
  RefreshCw,
  Headphones,
  CheckCircle2,
  XCircle,
  Trophy,
  PenLine,
  Check,
  Eye,
  ChevronRight,
  List
} from 'lucide-vue-next'
import SfDialog from '@/components/ui/SfDialog.vue'

const props = defineProps({
  material: Object,
  subtitles: Array,
  currentIndex: Number
})

const emit = defineEmits(['update-progress', 'complete'])
const { speakText, preloadVoices } = useTTS()

// 状态
const isPlaying = ref(false)
const playCount = ref(0)
const maxPlayCount = 3
const answerMode = ref('input')
const userAnswers = ref({})
const selectedChoices = ref({})
const isSubmitted = ref(false)
const submitting = ref(false)
const result = ref(null)
const completedSentences = ref(new Set())
const showCompleteDialog = ref(false)
const scoreHistory = ref([])
const totalWords = ref(0)
const correctWords = ref(0)

// 当前字幕
const currentSubtitle = computed(() => {
  return props.subtitles[props.currentIndex] || null
})

// 从句子中提取关键词
const extractKeyWords = (text) => {
  const simpleWords = [
    'a', 'an', 'the', 'is', 'am', 'are', 'was', 'were', 'be', 'been',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'this', 'that', 'these', 'those',
    'and', 'or', 'but', 'so', 'because', 'if', 'when', 'where', 'how',
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'down',
    'not', 'no', 'yes', 'do', 'does', 'did', 'have', 'has', 'had',
    'will', 'would', 'can', 'could', 'shall', 'should', 'may', 'might', 'must',
    'just', 'very', 'too', 'also', 'only', 'even', 'here', 'there', 'now', 'then'
  ]

  const words = text.toLowerCase().split(/\s+/).map(w => w.replace(/[.,!?;:'"]/g, '')).filter(w => w)
  const keyWords = words.filter(w => !simpleWords.includes(w) && w.length >= 2)
  const count = Math.min(4, Math.max(2, Math.ceil(keyWords.length * 0.4)))

  const selectedIndices = []
  const shuffled = [...keyWords.map((w, i) => i)].sort(() => Math.random() - 0.5)
  for (let i = 0; i < count && i < shuffled.length; i++) {
    selectedIndices.push(shuffled[i])
  }

  return keyWords.filter((w, i) => selectedIndices.includes(i))
}

// 挖空单词列表
const blankWords = computed(() => {
  if (!currentSubtitle.value) return []

  const text = currentSubtitle.value.text_en
  const keyWords = extractKeyWords(text)
  const words = text.split(/\s+/)

  const blanks = []
  keyWords.forEach(keyWord => {
    const cleanKeyWord = keyWord.toLowerCase()
    for (let i = 0; i < words.length; i++) {
      const cleanWord = words[i].toLowerCase().replace(/[.,!?;:'"]/g, '')
      if (cleanWord === cleanKeyWord) {
        const options = generateOptions(keyWord)
        blanks.push({
          word: words[i].replace(/[.,!?;:'"]/g, ''),
          index: i,
          options: options
        })
        break
      }
    }
  })

  return blanks
})

// 生成选择题选项
const generateOptions = (correctWord) => {
  const options = [correctWord]
  const distractors = [
    'make', 'take', 'give', 'have', 'come', 'go', 'see', 'know', 'think', 'find',
    'want', 'need', 'like', 'love', 'try', 'use', 'work', 'call', 'ask', 'tell',
    'time', 'year', 'people', 'way', 'day', 'thing', 'man', 'woman', 'child', 'world',
    'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old',
    'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young',
    'important', 'few', 'public', 'bad', 'same', 'able', 'sure', 'free', 'clear',
    'place', 'case', 'week', 'company', 'system', 'program', 'question', 'work'
  ]

  const shuffled = distractors.sort(() => Math.random() - 0.5)
  for (let i = 0; i < 3 && i < shuffled.length; i++) {
    if (shuffled[i].toLowerCase() !== correctWord.toLowerCase()) {
      options.push(shuffled[i])
    }
  }

  return options.sort(() => Math.random() - 0.5)
}

// 将句子分割成填空部分
const sentenceParts = computed(() => {
  if (!currentSubtitle.value || blankWords.value.length === 0) return []

  const text = currentSubtitle.value.text_en
  const words = text.split(/\s+/)
  const parts = []
  let blankIndex = 0

  words.forEach((word, index) => {
    const cleanWord = word.replace(/[.,!?;:'"]/g, '')
    const blank = blankWords.value.find(b => b.index === index)

    if (blank) {
      parts.push({
        type: 'blank',
        wordIndex: blankIndex,
        answer: cleanWord,
        punctuation: word.replace(cleanWord, '')
      })
      blankIndex++
    } else {
      if (parts.length > 0 && parts[parts.length - 1].type === 'text') {
        parts[parts.length - 1].content += ' ' + word
      } else {
        parts.push({
          type: 'text',
          content: word
        })
      }
    }
  })

  return parts
})

// 是否可以提交
const canSubmit = computed(() => {
  if (answerMode.value === 'input') {
    return Object.keys(userAnswers.value).length > 0
  } else {
    return Object.keys(selectedChoices.value).length > 0
  }
})

// 进度
const progressPercentage = computed(() => {
  return Math.round((completedSentences.value.size / props.subtitles.length) * 100)
})

// 是否是最后一句
const isLastSentence = computed(() => {
  return props.currentIndex >= props.subtitles.length - 1
})

// 完成统计
const completedCount = computed(() => completedSentences.value.size)
const averageScore = computed(() => {
  if (scoreHistory.value.length === 0) return 0
  const sum = scoreHistory.value.reduce((a, b) => a + b, 0)
  return Math.round(sum / scoreHistory.value.length)
})

const correctRate = computed(() => {
  if (totalWords.value === 0) return 0
  return Math.round((correctWords.value / totalWords.value) * 100)
})

// 得分样式类
const scoreClass = computed(() => {
  if (!result.value) return ''
  if (result.value.score >= 80) return 'score-high'
  if (result.value.score >= 60) return 'score-medium'
  return 'score-low'
})

// 播放音频 - 使用统一的 useTTS
const playAudio = () => {
  if (!currentSubtitle.value) return

  if (playCount.value >= maxPlayCount) {
    toast.warning('播放次数已达上限')
    return
  }

  isPlaying.value = true
  speakText(currentSubtitle.value.text_en, 0.85)

  // 由于 speakText 不暴露 onend/onerror，改用定时器模拟
  setTimeout(() => {
    if (isPlaying.value) {
      isPlaying.value = false
      playCount.value++
    }
  }, 3000) // 假设平均句子长度约 3 秒
}

// 选择选项
const selectChoice = (blankIndex, optionIndex) => {
  selectedChoices.value[blankIndex] = optionIndex
  const blank = blankWords.value[blankIndex]
  userAnswers.value[blankIndex] = blank.options[optionIndex]
}

// 聚焦下一个空
const focusNextBlank = (currentIndex) => {
  const nextIndex = currentIndex + 1
  if (nextIndex < blankWords.value.length) {
    const inputs = document.querySelectorAll('.sf-dictation-input')
    if (inputs[nextIndex]) {
      inputs[nextIndex].focus()
    }
  }
}

// 获取用户答案
const getUserAnswer = (wordIndex) => {
  return userAnswers.value[wordIndex] || ''
}

// 判断单词是否正确
const isWordCorrect = (wordIndex) => {
  const blank = blankWords.value[wordIndex]
  if (!blank) return false
  const userAnswer = (userAnswers.value[wordIndex] || '').toLowerCase().trim()
  const correctAnswer = blank.word.toLowerCase()
  return userAnswer === correctAnswer
}

// 提交答案
const submitAnswer = async () => {
  if (!canSubmit.value) {
    toast.warning('请填写至少一个单词')
    return
  }

  submitting.value = true

  try {
    let correct = 0
    blankWords.value.forEach((blank, index) => {
      if (isWordCorrect(index)) correct++
    })

    const total = blankWords.value.length
    const score = Math.round((correct / total) * 100)

    let feedback = ''
    if (score === 100) {
      feedback = '完美！全部正确！'
    } else if (score >= 80) {
      feedback = '很棒！大部分都对了！'
    } else if (score >= 60) {
      feedback = '还不错，继续加油！'
    } else {
      feedback = '需要多练习，再接再厉！'
    }

    result.value = {
      score,
      feedback,
      correct,
      total
    }

    totalWords.value += total
    correctWords.value += correct
    isSubmitted.value = true
    completedSentences.value.add(props.currentIndex)
    scoreHistory.value.push(score)

  } catch (e) {
    toast.error('提交失败')
    console.error(e)
  } finally {
    submitting.value = false
  }
}

// 显示答案
const showAnswer = () => {
  isSubmitted.value = true
  result.value = {
    score: 0,
    feedback: '你查看了答案，建议多听几遍加深印象~',
    correct: 0,
    total: blankWords.value.length
  }

  blankWords.value.forEach((blank, index) => {
    userAnswers.value[index] = blank.word
  })

  completedSentences.value.add(props.currentIndex)
  scoreHistory.value.push(0)
}

// 跳过当前
const skipCurrent = () => {
  nextSentence()
}

// 重试当前
const retryCurrent = () => {
  userAnswers.value = {}
  selectedChoices.value = {}
  isSubmitted.value = false
  result.value = null
  playCount.value = 0
  completedSentences.value.delete(props.currentIndex)
  if (scoreHistory.value.length > 0) {
    scoreHistory.value.pop()
  }
}

// 下一句
const nextSentence = () => {
  if (isLastSentence.value) {
    showCompleteDialog.value = true
    emit('complete', {
      completedCount: completedCount.value,
      averageScore: averageScore.value
    })
    return
  }

  emit('update-progress', props.currentIndex + 1)
  retryCurrent()
}

// 重新开始
const restartDictation = () => {
  completedSentences.value.clear()
  scoreHistory.value = []
  totalWords.value = 0
  correctWords.value = 0
  showCompleteDialog.value = false
  emit('update-progress', 0)
  retryCurrent()
}

// 监听当前索引变化
watch(() => props.currentIndex, () => {
  retryCurrent()
})
</script>

<style scoped>
/* ================================================
   DictationMode — Phase 2 CSS-only redesign
   Design system: ink green #0F4C3A + warm orange #E2725B
   ================================================ */

.sf-dictation-mode {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: relative;
  overflow: hidden;
}

/* subtle brand accent stripe at top */
.sf-dictation-mode::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--yt-brand-gradient);
}

/* ====== Progress ====== */
.sf-dictation-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sf-dictation-progress__info {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.sf-dictation-progress__label {
  font-size: var(--text-sm, 14px);
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: 0.02em;
}

.sf-dictation-progress__count {
  font-size: var(--text-xs, 12px);
  font-weight: 600;
  color: var(--color-brand-bright);
  font-variant-numeric: tabular-nums;
}

.sf-dictation-progress__bar-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sf-dictation-progress__bar {
  flex: 1;
  height: 6px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-full, 9999px);
  overflow: hidden;
}

.sf-dictation-progress__fill {
  height: 100%;
  background: var(--yt-brand-gradient);
  border-radius: inherit;
  transition: width 0.4s var(--ease-bounce, cubic-bezier(0.34, 1.56, 0.64, 1));
}

.sf-dictation-progress__percent {
  font-size: var(--text-xs, 12px);
  font-weight: 700;
  color: var(--color-brand-bright);
  min-width: 36px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

/* ====== Audio playback area ====== */
.sf-dictation-audio {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 32px;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(15, 76, 58, 0.08) 0%, transparent 70%),
    var(--color-bg-elevated);
  border-radius: var(--radius-xl, 24px);
  text-align: center;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.sf-dictation-audio__icon {
  width: 80px;
  height: 80px;
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 24px;
  box-shadow:
    0 6px 20px rgba(63, 138, 91, 0.3),
    0 2px 6px rgba(63, 138, 91, 0.15);
  transition: transform 0.25s var(--ease-bounce, cubic-bezier(0.34, 1.56, 0.64, 1));
}

.sf-dictation-audio__icon.playing {
  animation: audioPulse 1.5s ease infinite;
}

@keyframes audioPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 4px 12px rgba(15, 76, 58, 0.25); }
  50% { transform: scale(1.08); box-shadow: 0 0 0 14px rgba(15, 76, 58, 0.12); }
}

.sf-dictation-audio__title {
  font-size: var(--text-lg, 18px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 6px;
}

.sf-dictation-audio__desc {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  margin: 0 0 24px;
  max-width: 320px;
}

.sf-dictation-audio__actions {
  display: flex;
  gap: 12px;
}

.sf-dictation-audio__status {
  margin-top: 16px;
}

.sf-dictation-status-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 14px;
  font-size: var(--text-xs, 12px);
  font-weight: 500;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full, 9999px);
  color: var(--color-text-muted);
}

/* ====== Mode selector (fill-in / multiple-choice) ====== */
.sf-dictation-mode-select {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md, 12px);
  padding: 4px;
}

/* ====== Sentence with blanks ====== */
.sf-dictation-sentence {
  font-size: var(--text-lg, 18px);
  line-height: 2.4;
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
  padding: 24px;
  border-radius: var(--radius-lg, 16px);
  margin-bottom: 20px;
  word-break: break-word;
  border: 1px solid transparent;
  transition: border-color 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.sf-dictation-sentence:focus-within {
  border-color: var(--color-brand-bright);
}

.sf-dictation-text {
  margin-right: 4px;
}

.sf-dictation-blank {
  display: inline-flex;
  align-items: center;
  min-width: 80px;
  max-width: 160px;
  border-bottom: 2px solid var(--color-brand-light);
  margin: 0 4px;
  transition: border-color 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.sf-dictation-blank:focus-within {
  border-bottom-color: var(--color-brand-bright);
}

.sf-dictation-input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  font-size: var(--text-lg, 18px);
  font-weight: 600;
  color: var(--color-text-primary);
  text-align: center;
  padding: 2px 4px;
  font-family: var(--font-sans, inherit);
}

.sf-dictation-input::placeholder {
  color: var(--color-text-muted);
  font-size: var(--text-xs, 12px);
  font-weight: 400;
}

.sf-dictation-input--correct {
  border-bottom-color: var(--color-success) !important;
  color: var(--color-success);
}

.sf-dictation-input--wrong {
  border-bottom-color: var(--color-danger) !important;
  color: var(--color-danger);
  animation: shake 0.35s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-4px); }
  40% { transform: translateX(4px); }
  60% { transform: translateX(-3px); }
  80% { transform: translateX(2px); }
}

/* ====== Choice mode ====== */
.sf-dictation-choices {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg, 16px);
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid var(--color-border);
}

.sf-dictation-choice-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.sf-dictation-choice-row:last-child {
  margin-bottom: 0;
}

.sf-dictation-choice-label {
  font-size: var(--text-xs, 12px);
  font-weight: 600;
  color: var(--color-text-secondary);
  width: 50px;
  flex-shrink: 0;
}

.sf-dictation-choice-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sf-dictation-choice-btn {
  padding: 8px 20px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full, 9999px);
  font-size: var(--text-sm, 14px);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.18s var(--ease-bounce, cubic-bezier(0.34, 1.56, 0.64, 1));
  font-family: inherit;
  font-weight: 500;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.sf-dictation-choice-btn:hover {
  border-color: var(--color-brand-bright);
  color: var(--color-brand-bright);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.sf-dictation-choice-btn.selected {
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  border-color: var(--color-brand-bright);
  color: #fff;
}

/* ====== Action buttons ====== */
.sf-dictation-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.sf-dictation-actions .sf-btn {
  min-height: 44px;
}

/* ====== Result section ====== */
.sf-dictation-result {
  padding-top: 24px;
  border-top: 1px solid var(--color-border);
  animation: fadeUp 0.35s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.sf-dictation-result__header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.sf-dictation-score {
  display: flex;
  align-items: baseline;
  justify-content: center;
  min-width: 88px;
  height: 88px;
  padding: 0 20px;
  border-radius: var(--radius-xl, 24px);
  flex-shrink: 0;
  font-size: 40px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.sf-dictation-score.score-high {
  background: rgba(45, 134, 89, 0.12);
  color: var(--color-success);
}

.sf-dictation-score.score-medium {
  background: rgba(226, 114, 91, 0.12);
  color: var(--color-accent);
}

.sf-dictation-score.score-low {
  background: rgba(199, 62, 58, 0.1);
  color: var(--color-danger);
}

.sf-dictation-score__unit {
  font-size: var(--text-base, 16px);
  font-weight: 500;
  margin-left: 2px;
}

.sf-dictation-result__feedback {
  flex: 1;
}

.sf-dictation-result__feedback p {
  margin: 0;
  font-size: var(--text-base, 16px);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.5;
}

/* ====== Answer comparison ====== */
.sf-dictation-comparison {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg, 16px);
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid var(--color-border);
}

.sf-dictation-comparison__row {
  margin-bottom: 14px;
}

.sf-dictation-comparison__row:last-child {
  margin-bottom: 0;
}

.sf-dictation-comparison__label {
  font-size: var(--text-xs, 12px);
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 8px;
  display: block;
}

.sf-dictation-comparison__text {
  font-size: var(--text-sm, 14px);
  line-height: 2;
  color: var(--color-text-primary);
  word-break: break-word;
}

/* Word tags (inline) */
.sf-word-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-sm, 8px);
  font-weight: 600;
  font-size: var(--text-sm, 14px);
  margin: 0 3px;
}

.sf-word-tag--correct {
  background: rgba(45, 134, 89, 0.12);
  color: var(--color-success);
}

.sf-word-tag--wrong {
  background: rgba(199, 62, 58, 0.1);
  color: var(--color-danger);
}

/* ====== Word tag rows ====== */
.sf-dictation-word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

.sf-word-tag-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: var(--radius-full, 9999px);
  font-size: var(--text-xs, 12px);
  border: 1px solid;
  min-height: 44px;
}

.sf-word-tag-row--correct {
  background: rgba(45, 134, 89, 0.08);
  border-color: rgba(45, 134, 89, 0.3);
  color: var(--color-success);
}

.sf-word-tag-row--wrong {
  background: rgba(199, 62, 58, 0.08);
  border-color: rgba(199, 62, 58, 0.3);
  color: var(--color-danger);
}

.sf-word-tag-row__num {
  font-weight: 700;
  min-width: 16px;
}

.sf-word-tag-row__answer {
  font-weight: 600;
}

.sf-word-tag-row__yours {
  color: inherit;
  opacity: 0.7;
  font-size: 11px;
}

.sf-word-tag-row__yours::before {
  content: '\2190';
  margin-right: 4px;
}

/* ====== Result actions ====== */
.sf-dictation-result__actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.sf-dictation-result__actions .sf-btn {
  min-height: 44px;
}

/* ====== Complete modal ====== */
.sf-complete-modal__body {
  text-align: center;
  padding: 12px 0;
}

.sf-complete-modal__icon {
  color: var(--color-accent);
  margin-bottom: 16px;
  animation: bounceIn 0.5s var(--ease-bounce, cubic-bezier(0.34, 1.56, 0.64, 1));
}

@keyframes bounceIn {
  0% { transform: scale(0.5); opacity: 0; }
  60% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

.sf-complete-modal__title {
  font-size: var(--text-xl, 20px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 8px;
}

.sf-complete-modal__desc {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  margin: 0 0 24px;
}

.sf-complete-modal__stats {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.sf-complete-modal__stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.sf-complete-modal__stat-value {
  font-size: var(--text-2xl, 24px);
  font-weight: 800;
  color: var(--color-brand-bright);
  font-variant-numeric: tabular-nums;
}

.sf-complete-modal__stat-label {
  font-size: var(--text-xs, 12px);
  color: var(--color-text-muted);
}

.sf-complete-modal__footer {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* ====== Mobile responsive ====== */
@media (max-width: 768px) {
  .sf-dictation-mode {
    padding: 20px 16px;
    gap: 20px;
    border-radius: var(--radius-md, 12px);
  }

  .sf-dictation-audio {
    padding: 28px 16px;
  }

  .sf-dictation-audio__icon {
    width: 64px;
    height: 64px;
  }

  .sf-dictation-audio__actions {
    flex-direction: column;
    width: 100%;
  }

  .sf-dictation-audio__actions .sf-btn {
    width: 100%;
    justify-content: center;
    min-height: 44px;
  }

  .sf-dictation-mode-select {
    flex-direction: column;
  }

  .sf-dictation-mode-select .sf-segment__item {
    min-height: 44px;
  }

  .sf-dictation-sentence {
    font-size: var(--text-base, 16px);
    padding: 16px;
  }

  .sf-dictation-blank {
    min-width: 60px;
    max-width: 120px;
  }

  .sf-dictation-input {
    font-size: var(--text-base, 16px);
  }

  .sf-dictation-choice-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .sf-dictation-actions {
    flex-direction: column;
  }

  .sf-dictation-actions .sf-btn {
    width: 100%;
    justify-content: center;
    min-height: 44px;
  }

  .sf-dictation-result__header {
    flex-direction: column;
    text-align: center;
  }

  .sf-dictation-score {
    font-size: 32px;
    height: 72px;
    min-width: 72px;
  }

  .sf-dictation-comparison__text {
    font-size: var(--text-sm, 14px);
  }

  .sf-dictation-word-tags {
    flex-direction: column;
  }

  .sf-dictation-result__actions {
    flex-direction: column;
  }

  .sf-dictation-result__actions .sf-btn {
    width: 100%;
    justify-content: center;
    min-height: 44px;
  }

  .sf-complete-modal__stats {
    gap: 20px;
  }

  .sf-complete-modal__stat-value {
    font-size: var(--text-xl, 20px);
  }
}

@media (max-width: 480px) {
  .sf-dictation-mode {
    padding: 16px 12px;
    gap: 16px;
  }

  .sf-dictation-audio {
    padding: 20px 12px;
  }

  .sf-dictation-sentence {
    padding: 12px;
    line-height: 2;
  }

  .sf-dictation-blank {
    min-width: 50px;
  }
}
</style>
