<template>
  <div class="review-page">
    <!-- Phase 6 (H5): 极简 header + 返回按钮 -->
    <header v-if="isMobileView" class="sf-h5-header">
      <button class="sf-h5-back" type="button" @click="$router.back()" aria-label="返回">
        <ArrowLeft :size="22" />
      </button>
      <h1 class="sf-h5-title">生词复习</h1>
    </header>
    <!-- 复习统计头部 -->
    <div v-else class="review-header">
      <SfButton type="ghost" size="sm" @click="$router.back()" aria-label="返回上一页">
        <ArrowLeft :size="20" />
      </SfButton>
      <div class="header-info">
        <h1>生词复习</h1>
        <div class="review-stats-bar" role="status" aria-label="复习队列统计">
          <span class="stat-badge due" v-if="stats.total_due > 0">{{ stats.total_due }} 待复习</span>
          <span class="stat-badge learning">{{ stats.total_learning }} 学习中</span>
          <span class="stat-badge mastered">{{ stats.total_mastered }} 已掌握</span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state" role="status" aria-live="polite">
      <Loader2 :size="32" class="is-loading" />
      <span>加载复习队列...</span>
    </div>

    <!-- 空状态 -->
    <div v-else-if="queue.length === 0" class="empty-state">
      <PartyPopper :size="48" class="empty-emoji-icon" />
      <h2>复习完成！</h2>
      <p>所有生词都已复习过了，稍后再来吧</p>
      <SfButton type="primary" @click="$router.push('/vocabulary')">返回生词本</SfButton>
    </div>

    <!-- 复习卡片区域 -->
    <div v-else class="review-content">
      <!-- 进度条 -->
      <div class="progress-bar" role="progressbar" :aria-valuenow="progressPercent"
           aria-valuemin="0" aria-valuemax="100"
           :aria-label="`复习进度 ${reviewedCount} / ${totalCount}`">
        <SfProgress
          :percentage="progressPercent"
          type="brand"
          :show-text="false"
        />
        <span class="progress-text" aria-hidden="true">{{ reviewedCount }} / {{ totalCount }}</span>
      </div>

      <!-- 翻转卡片 -->
      <div class="flashcard-container">
        <button
          type="button"
          :class="['flashcard', { flipped: isFlipped }]"
          :aria-pressed="isFlipped"
          :aria-label="isFlipped ? '点击翻转回英文单词' : '点击翻转查看释义'"
          @click="isFlipped = !isFlipped"
        >
          <!-- 正面：英文单词 -->
          <div class="flashcard-front">
            <div class="card-word">{{ currentItem.word }}</div>
            <div class="card-context" v-if="currentItem.context">
              "{{ currentItem.context }}"
            </div>
            <div class="card-hint">点击翻转查看释义</div>
          </div>

          <!-- 背面：中文释义 -->
          <div class="flashcard-back">
            <div class="card-word-en">{{ currentItem.word }}</div>
            <div class="card-divider"></div>
            <div class="card-context" v-if="currentItem.context">
              <span class="context-label">语境：</span>{{ currentItem.context }}
            </div>
            <div class="card-translation" v-if="currentItem.context_cn">
              <span class="translation-label">翻译：</span>{{ currentItem.context_cn }}
            </div>
            <div class="card-meta">
              <span v-if="currentItem.review_count > 0">已复习 {{ currentItem.review_count }} 次</span>
              <span v-if="currentItem.interval_days > 0">间隔 {{ currentItem.interval_days }} 天</span>
            </div>
          </div>
        </button>
      </div>

      <!-- 评分按钮 -->
      <div class="rating-buttons" role="group" aria-label="评分按钮组">
        <button class="rating-btn btn-forget" @click="rate(0)" :disabled="submitting"
          aria-label="评 0 分 - 忘记了,1 天后再来">
          <XCircle :size="22" />
          <span class="rating-label">忘记了</span>
          <span class="rating-interval">1天</span>
        </button>
        <button class="rating-btn btn-vague" @click="rate(2)" :disabled="submitting"
          aria-label="评 2 分 - 模糊,1 天后再来">
          <HelpCircle :size="22" />
          <span class="rating-label">模糊</span>
          <span class="rating-interval">1天</span>
        </button>
        <button class="rating-btn btn-recall" @click="rate(3)" :disabled="submitting"
          :aria-label="`评 3 分 - 想起来了,${intervalFor(3)} 后再来`">
          <Lightbulb :size="22" />
          <span class="rating-label">想起来了</span>
          <span class="rating-interval">{{ intervalFor(3) }}</span>
        </button>
        <button class="rating-btn btn-easy" @click="rate(4)" :disabled="submitting"
          :aria-label="`评 4 分 - 容易,${intervalFor(4)} 后再来`">
          <Smile :size="22" />
          <span class="rating-label">容易</span>
          <span class="rating-interval">{{ intervalFor(4) }}</span>
        </button>
        <button class="rating-btn btn-perfect" @click="rate(5)" :disabled="submitting"
          :aria-label="`评 5 分 - 完美,${intervalFor(5)} 后再来`">
          <Target :size="22" />
          <span class="rating-label">完美</span>
          <span class="rating-interval">{{ intervalFor(5) }}</span>
        </button>
      </div>
    </div>

    <!-- 复习完成统计 -->
    <div v-if="showSummary" class="summary-overlay">
      <div class="summary-card">
        <h2 class="summary-title">
          <PartyPopper :size="24" />
          本次复习完成
        </h2>
        <div class="summary-stats">
          <div class="summary-item">
            <span class="summary-value">{{ sessionStats.total }}</span>
            <span class="summary-label">复习总数</span>
          </div>
          <div class="summary-item perfect">
            <span class="summary-value">{{ sessionStats.perfect }}</span>
            <span class="summary-label">完美</span>
          </div>
          <div class="summary-item recall">
            <span class="summary-value">{{ sessionStats.recall }}</span>
            <span class="summary-label">想起来</span>
          </div>
          <div class="summary-item forget">
            <span class="summary-value">{{ sessionStats.forget }}</span>
            <span class="summary-label">忘记了</span>
          </div>
        </div>
        <div class="summary-actions">
          <SfButton type="primary" @click="startNewSession">继续复习</SfButton>
          <SfButton type="ghost" @click="$router.push('/vocabulary')">返回生词本</SfButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { toast } from '@/composables/useToast'
import { ArrowLeft, Loader2, PartyPopper, XCircle, HelpCircle, Lightbulb, Smile, Target } from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfProgress from '@/components/ui/SfProgress.vue'
import { vocabularyAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

// Phase 6 (H5): 移动端检测
const isMobileView = ref(typeof window !== 'undefined' && window.matchMedia('(max-width: 768px)').matches)
const updateIsMobile = () => {
  isMobileView.value = window.matchMedia('(max-width: 768px)').matches
}
onMounted(() => window.addEventListener('resize', updateIsMobile))
onUnmounted(() => window.removeEventListener('resize', updateIsMobile))

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const submitting = ref(false)
const queue = ref([])
const currentIndex = ref(0)
const isFlipped = ref(false)
const showSummary = ref(false)

const stats = ref({
  total_due: 0,
  total_learning: 0,
  total_mastered: 0
})

const sessionStats = ref({
  total: 0,
  perfect: 0,
  recall: 0,
  forget: 0
})

const currentItem = computed(() => queue.value[currentIndex.value] || {})
const reviewedCount = computed(() => currentIndex.value)
const totalCount = computed(() => queue.value.length)
const progressPercent = computed(() =>
  totalCount.value > 0 ? Math.round((reviewedCount.value / totalCount.value) * 100) : 0
)

// P0-6: 间隔天数从后端 review-queue 响应里的 next_intervals 字典读,
// 前端不再重算 SM-2,避免"用户点想起来了 UI 显示 6 天,后端 EF 调整后实际 5 或 7 天"的信任问题
const intervalFor = (quality) => {
  const item = currentItem.value
  if (!item || !item.next_intervals) return '1天'  // fallback(老数据/错误响应)
  const days = item.next_intervals[String(quality)]
  return days ? `${days}天` : '1天'
}

const loadQueue = async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  loading.value = true
  try {
    const [queueRes, statsRes] = await Promise.all([
      vocabularyAPI.getReviewQueue(20),
      vocabularyAPI.getReviewStats()
    ])
    queue.value = queueRes.items || []
    stats.value = statsRes
  } catch (e) {
    console.error('加载复习队列失败', e)
    toast.error('加载失败')
  } finally {
    loading.value = false
  }
}

const rate = async (quality) => {
  if (submitting.value) return
  submitting.value = true

  try {
    await vocabularyAPI.submitReview({
      vocabulary_id: currentItem.value.id,
      quality
    })

    // 统计
    sessionStats.value.total++
    if (quality >= 4) sessionStats.value.perfect++
    else if (quality >= 3) sessionStats.value.recall++
    else sessionStats.value.forget++

    // 下一个
    isFlipped.value = false
    if (currentIndex.value < queue.value.length - 1) {
      currentIndex.value++
    } else {
      showSummary.value = true
    }
  } catch (e) {
    console.error('提交复习失败', e)
    toast.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const startNewSession = async () => {
  showSummary.value = false
  sessionStats.value = { total: 0, perfect: 0, recall: 0, forget: 0 }
  currentIndex.value = 0
  isFlipped.value = false
  await loadQueue()
}

// 2.4 快捷键: Space/Enter 翻转, 0/2/3/4/5 打分(只在已翻转后允许打分)
const handleKeydown = (e) => {
  // 防止在输入框/按钮焦点时误触 (Space 翻页很常见)
  const tag = (e.target?.tagName || '').toLowerCase()
  if (tag === 'input' || tag === 'textarea') return

  // Space / Enter: 翻转卡片
  if (e.key === ' ' || e.key === 'Enter') {
    e.preventDefault()  // 阻止 Space 滚屏
    if (!loading.value && queue.value.length > 0 && !showSummary.value) {
      isFlipped.value = !isFlipped.value
    }
    return
  }

  // 数字键打分: 仅在已翻转 + 队列非空 + 未在提交中时生效
  const qualityMap = { '0': 0, '2': 2, '3': 3, '4': 4, '5': 5 }
  const q = qualityMap[e.key]
  if (q === undefined) return
  if (!isFlipped.value) return  // 强制先看答案
  if (loading.value || submitting.value || showSummary.value) return
  if (queue.value.length === 0) return
  e.preventDefault()
  rate(q)
}

onMounted(() => {
  loadQueue()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.review-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 0 16px;
  min-height: 80vh;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 24px;
}

.header-info h1 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px;
}

.review-stats-bar {
  display: flex;
  gap: 8px;
}

.stat-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 12px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}

.stat-badge.due {
  background: rgba(220, 38, 38, 0.1);
  color: var(--color-danger);
}

.stat-badge.learning {
  background: var(--color-brand-subtle);
  color: var(--color-brand-bright);
}

.stat-badge.mastered {
  background: var(--color-brand-subtle);
  color: var(--color-success);
}

/* 加载 & 空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 12px;
  color: var(--color-text-secondary);
}

.empty-emoji-icon {
  color: var(--color-brand-bright);
  margin-bottom: 8px;
}

.empty-state h2 {
  margin: 0;
  color: var(--color-text-primary);
}

.empty-state p {
  color: var(--color-text-secondary);
  margin: 0;
}

/* 进度条 */
.progress-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.progress-bar :deep(.el-progress) {
  flex: 1;
}

.progress-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: 600;
  min-width: 48px;
  text-align: right;
}

/* 翻转卡片 */
.flashcard-container {
  perspective: 1000px;
  margin-bottom: 32px;
}

.flashcard {
  width: 100%;
  min-height: 280px;
  position: relative;
  cursor: pointer;
  transform-style: preserve-3d;
  transition: transform var(--sf-duration-slower) ease;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.flashcard.flipped {
  transform: rotateY(180deg);
}

.flashcard-front,
.flashcard-back {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  min-height: 280px;
  backface-visibility: hidden;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  background: var(--color-bg-base);
  border: 1px solid var(--color-border);
}

.flashcard-back {
  transform: rotateY(180deg);
}

.card-word {
  font-size: 36px;
  font-weight: 800;
  color: var(--color-text-primary);
  text-align: center;
  letter-spacing: 0.5px;
}

.card-word-en {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  text-align: center;
}

.card-divider {
  width: 40px;
  height: 2px;
  background: var(--color-border);
  margin: 12px 0;
  border-radius: 1px;
}

.card-context {
  font-size: 14px;
  color: var(--color-text-secondary);
  text-align: center;
  margin-top: 12px;
  line-height: 1.6;
  max-width: 90%;
  font-style: italic;
}

.card-translation {
  font-size: 16px;
  color: var(--color-text-primary);
  text-align: center;
  margin-top: 8px;
  font-weight: 500;
}

.context-label,
.translation-label {
  font-size: 12px;
  color: var(--color-text-muted);
  font-weight: 500;
  margin-right: 4px;
}

.card-meta {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  font-size: 12px;
  color: var(--color-text-muted);
}

.card-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 24px;
}

/* 评分按钮 */
.rating-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.rating-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-base);
  cursor: pointer;
  transition: all var(--sf-duration-normal);
  min-width: 80px;
}

.rating-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rating-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rating-btn svg {
  margin-bottom: 4px;
  color: currentColor;
}

.rating-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.rating-interval {
  font-size: 10px;
  color: var(--color-text-muted);
  font-weight: 500;
}

.btn-forget:hover:not(:disabled) {
  border-color: var(--color-danger);
  background: rgba(220, 38, 38, 0.05);
}

.btn-vague:hover:not(:disabled) {
  border-color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.btn-recall:hover:not(:disabled) {
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

.btn-easy:hover:not(:disabled) {
  border-color: var(--color-success);
  background: var(--color-brand-subtle);
}

.btn-perfect:hover:not(:disabled) {
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

/* 完成统计 */
.summary-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.summary-card {
  background: var(--color-bg-base);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
}

.summary-card h2 {
  font-size: 24px;
  margin: 0 0 24px;
  color: var(--color-text-primary);
}

.summary-stats {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 28px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.summary-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.summary-item.perfect .summary-value {
  color: var(--color-brand-bright);
}

.summary-item.recall .summary-value {
  color: var(--color-info);
}

.summary-item.forget .summary-value {
  color: var(--color-danger);
}

.summary-label {
  font-size: 12px;
  color: var(--color-text-muted);
  font-weight: 500;
}

.summary-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.summary-actions .sf-btn--primary {
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  border-color: var(--color-brand-bright);
}

/* 响应式 */
@media (max-width: 768px) {
  .review-page {
    padding: 0 12px 72px;
  }
}

@media (max-width: 640px) {
  .review-page {
    padding: 0 12px 72px;
  }

  .flashcard {
    min-height: 220px;
  }

  .flashcard-front,
  .flashcard-back {
    min-height: 220px;
    padding: 24px 16px;
  }

  .card-word {
    font-size: 28px;
  }

  .rating-buttons {
    gap: 6px;
  }

  .rating-btn {
    padding: 10px 12px;
    min-width: 64px;
  }
}
</style>
