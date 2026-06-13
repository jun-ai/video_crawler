<template>
  <div class="yt-vocabulary">
    <!-- 页面标题 -->
    <PageHeader title="生词本">
      <template #actions>
        <SfSwitch
          v-model="showChinese"
        />
      </template>
    </PageHeader>

    <SfEmpty v-if="!userStore.isLoggedIn" description="请先登录查看生词本">
      <SfButton type="primary" @click="$router.push('/login')">去登录</SfButton>
    </SfEmpty>

    <template v-else>
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="filter-row">
          <!-- 语料筛选 -->
          <div class="filter-section">
            <span class="filter-label">来源：</span>
            <SfSelect
              v-model="filterMaterialId"
              :options="materialsList.map(m => ({ label: m.title, value: m.id }))"
              placeholder="全部语料"
            />
          </div>

          <!-- 排序 -->
          <div class="filter-section">
            <span class="filter-label">排序：</span>
            <SfSelect v-model="sortBy" :options="[
              { value: 'newest', label: '最近添加' },
              { value: 'oldest', label: '最早添加' },
              { value: 'word_asc', label: 'A → Z' },
              { value: 'word_desc', label: 'Z → A' },
              { value: 'review_count', label: '复习最多' }
            ]" />
          </div>

          <span class="filter-total" v-if="total > 0">共 {{ total }} 词</span>
        </div>

        <!-- 掌握状态筛选 -->
        <div class="filter-chips">
          <FilterChip
            :model-value="filterMastered"
            :value="null"
            label="全部"
            @update:model-value="setFilter"
          />
          <FilterChip
            :model-value="filterMastered"
            :value="false"
            label="学习中"
            @update:model-value="setFilter"
          />
          <FilterChip
            :model-value="filterMastered"
            :value="true"
            label="已掌握"
            @update:model-value="setFilter"
          />
        </div>
      </div>

      <div class="vocab-list" v-loading="loading">
        <div
          v-for="item in vocabularies"
          :key="item.id"
          :class="['vocab-card', {
            'vocab-mastered': item.mastered,
            'vocab-learning': !item.mastered && item.review_count > 0,
            'vocab-new': !item.mastered && item.review_count === 0
          }]"
        >
          <!-- 状态色条 -->
          <div class="vocab-status-bar" :class="item.mastered ? 'status-mastered' : (item.review_count > 0 ? 'status-review' : 'status-new')"></div>

          <div class="vocab-card-inner">
            <!-- 单词头部 -->
            <div class="vocab-card-top">
              <div class="vocab-word-area">
                <div class="vocab-word-row" @click="speakText(item.word)">
                  <span class="vocab-word">{{ item.word }}</span>
                </div>
                <!-- 查询到的音标和释义 -->
                <div class="vocab-phonetic" v-if="getWordInfo(item.word)?.phonetic">
                  /{{ getWordInfo(item.word).phonetic }}/
                </div>
              </div>

              <!-- TTS 发音按钮 — 圆形 44px touch target -->
              <button class="tts-btn" @click="speakText(item.word)" title="朗读发音">
                <Headphones :size="20" />
              </button>

              <!-- 状态标签 + 复习进度 -->
              <div class="vocab-status-group">
                <SfTag :type="item.mastered ? 'success' : 'warning'" size="sm">
                  {{ item.mastered ? '已掌握' : '学习中' }}
                </SfTag>
                <SfTag
                  v-if="item.review_count > 0"
                  size="sm"
                  type="default"
                >
                  复习 {{ item.review_count }} 次
                </SfTag>
              </div>
            </div>

            <!-- 查询到的翻译 -->
            <div class="vocab-translation" v-if="showChinese && getWordInfo(item.word)?.translation">
              {{ getWordInfo(item.word).translation }}
            </div>

            <!-- 复习进度可视化 -->
            <div class="vocab-progress-row" v-if="item.review_count > 0">
              <!-- 掌握度进度环 -->
              <div class="mastery-ring">
                <svg viewBox="0 0 36 36" class="mastery-ring-svg">
                  <path
                    class="mastery-ring-bg"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    class="mastery-ring-fill"
                    :style="{ strokeDasharray: `${Math.min(item.review_count * 15, 100)} ${100 - Math.min(item.review_count * 15, 100)}` }"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <span class="mastery-ring-text">{{ Math.min(item.review_count * 15, 100) }}%</span>
              </div>

              <!-- 复习强度 bar -->
              <div class="review-strength">
                <div class="review-strength-label">复习强度</div>
                <div class="review-strength-bar">
                  <div
                    class="review-strength-fill"
                    :class="{
                      'strength-low': item.review_count <= 2,
                      'strength-mid': item.review_count > 2 && item.review_count <= 5,
                      'strength-high': item.review_count > 5
                    }"
                    :style="{ width: Math.min(item.review_count * 15, 100) + '%' }"
                  ></div>
                </div>
                <div class="review-strength-count">{{ item.review_count }} 次</div>
              </div>

              <!-- 添加时间 -->
              <div class="vocab-next-review">
                {{ formatRelativeTime(item.created_at) }}添加
              </div>
            </div>

            <!-- 语境 -->
            <div class="vocab-context-area" v-if="item.context">
              <div class="vocab-context" @click="speakText(item.context)">
                <span class="context-label">语境</span>
                <span class="context-text">{{ item.context }}</span>
                <Headphones :size="14" class="speak-icon-small" />
              </div>
              <div class="vocab-context-cn" v-if="showChinese && item.context_cn">
                {{ item.context_cn }}
              </div>
            </div>

            <!-- 语料来源 -->
            <div class="vocab-card-footer">
              <div class="vocab-source" v-if="item.material_title" @click="goToMaterial(item.material_id)">
                <Play :size="13" />
                <span>{{ item.material_title }}</span>
              </div>
              <div class="vocab-time" v-if="!(item.review_count > 0)">
                {{ formatRelativeTime(item.created_at) }}
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="vocab-actions">
              <SfButton
                type="primary"
                size="sm"
                @click="lookupAndSpeak(item.word)"
                :loading="lookupLoading[item.word]"
              >
                <Headphones :size="14" /> 查询发音
              </SfButton>
              <SfButton
                v-if="!item.mastered"
                type="brand"
                size="sm"
                @click="markMastered(item.id)"
              >
                标记掌握
              </SfButton>
              <SfButton
                v-if="item.mastered"
                type="ghost"
                size="sm"
                @click="removeFromBook(item.id)"
              >
                移出
              </SfButton>
              <SfButton
                v-if="!item.mastered"
                type="danger"
                size="sm"
                @click="deleteVocab(item.id)"
              >
                删除
              </SfButton>
            </div>
          </div>
        </div>

        <EmptyState
          v-if="!loading && vocabularies.length === 0"
          type="no-vocabulary"
          title="生词本是空的"
          description="在学习视频时，遇到不认识的单词可以添加到这里"
        >
          <template #actions>
            <SfButton type="primary" @click="$router.push('/materials')">去发现语料</SfButton>
          </template>
        </EmptyState>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="total > 0">
        <div class="pagination-left">
          <span class="pagination-total">共 {{ total }} 条</span>
          <div class="page-size-select">
            <span class="page-size-label">每页</span>
            <SfSelect v-model="pageSize" :options="[
              { value: 10, label: '10' },
              { value: 20, label: '20' },
              { value: 50, label: '50' },
              { value: 100, label: '100' }
            ]" size="sm" />
          </div>
        </div>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          :pager-count="5"
          @current-change="loadVocabularies"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { useTTS } from '@/composables/useTTS'
import { showConfirm } from '@/composables/useConfirm'
import { Headphones, Play } from 'lucide-vue-next'
import SfSwitch from '@/components/ui/SfSwitch.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'
import SfButton from '@/components/ui/SfButton.vue'
import SfTag from '@/components/ui/SfTag.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterChip from '@/components/common/FilterChip.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { vocabularyAPI, materialAPI } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { speakText, speakWord, preloadVoices } = useTTS()

const loading = ref(false)
const vocabularies = ref([])
const showChinese = ref(true)
const filterMastered = ref(null)
const filterMaterialId = ref(null)
const sortBy = ref('newest')
const materialsList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 单词查询缓存
const wordInfoCache = reactive({})
const lookupLoading = reactive({})

// 获取缓存的单词信息
const getWordInfo = (word) => wordInfoCache[word.toLowerCase()]

// 加载语料列表（用于筛选）
const loadMaterialsList = async () => {
  try {
    const result = await materialAPI.getList({ page_size: 100 })
    materialsList.value = result.items || []
  } catch (e) {
    console.error('加载语料列表失败', e)
  }
}

const loadVocabularies = async () => {
  if (!userStore.isLoggedIn) return
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: sortBy.value
    }
    if (filterMastered.value !== null) {
      params.mastered = filterMastered.value
    }
    if (filterMaterialId.value) {
      params.material_id = filterMaterialId.value
    }
    const res = await vocabularyAPI.getList(params)
    vocabularies.value = res.items || []
    total.value = res.total || 0

    // 批量预查询前 10 个词的发音和释义
    vocabularies.value.slice(0, 10).forEach(item => {
      if (!wordInfoCache[item.word.toLowerCase()]) {
        lookupWordSilent(item.word)
      }
    })
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
  }
}

// 静默查询单词（不显示 loading）
const lookupWordSilent = async (word) => {
  const key = word.toLowerCase()
  if (wordInfoCache[key]) return
  try {
    const result = await vocabularyAPI.lookup(word)
    wordInfoCache[key] = {
      phonetic: result.phonetic || '',
      translation: result.translation || result.meaning || '',
      example: result.example || ''
    }
  } catch (e) {
    // 静默失败
  }
}

// 点击查询并朗读
const lookupAndSpeak = async (word) => {
  const key = word.toLowerCase()
  lookupLoading[word] = true
  try {
    if (!wordInfoCache[key]) {
      await lookupWordSilent(word)
    }
    speakText(word)
  } finally {
    lookupLoading[word] = false
  }
}

const setFilter = (value) => {
  filterMastered.value = value
  currentPage.value = 1
  loadVocabularies()
}

const onFilterChange = () => {
  currentPage.value = 1
  loadVocabularies()
}

const onPageSizeChange = () => {
  currentPage.value = 1
  loadVocabularies()
}

// 格式化相对时间
const formatRelativeTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  if (days < 365) return `${Math.floor(days / 30)}月前`
  return `${Math.floor(days / 365)}年前`
}

// 跳转到语料学习页
const goToMaterial = (materialId) => {
  if (materialId) {
    router.push(`/learn/${materialId}`)
  }
}

// useTTS 提供 speakText（已替换本地实现）

const markMastered = async (id) => {
  try {
    await vocabularyAPI.markMastered(id)
    toast.success('已标记为掌握')
    loadVocabularies()
  } catch (e) {
    console.error('操作失败', e)
  }
}

const removeFromBook = async (id) => {
  const confirmed = await showConfirm({ title: '确认移出', message: '确定要将该生词移出生词本吗？' })
  if (confirmed) {
    try {
      await vocabularyAPI.delete(id)
      toast.success('已移出生词本')
      loadVocabularies()
    } catch (e) {
      console.error('移出失败', e)
    }
  }
}

const deleteVocab = async (id) => {
  const confirmed = await showConfirm({ title: '确认删除', message: '确定要删除该生词吗？' })
  if (confirmed) {
    try {
      await vocabularyAPI.delete(id)
      toast.success('已删除')
      loadVocabularies()
    } catch (e) {
      console.error('删除失败', e)
    }
  }
}

onMounted(() => {
  preloadVoices()
  loadMaterialsList()
  loadVocabularies()
})
</script>

<style scoped>
/* ============================================
   Phase 1D — Vocabulary Redesign
   墨绿 #0F4C3A + 暖橙 #E2725B + Noto Sans SC
   ============================================ */

.yt-vocabulary {
  max-width: 960px;
  margin: 0 auto;
}

/* ---- 筛选条 ---- */
.filter-bar {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px 20px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 16px);
  box-shadow: var(--shadow-sm);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.filter-total {
  font-size: 13px;
  color: var(--color-text-muted);
  font-weight: 500;
  margin-left: auto;
}

.filter-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ---- 生词列表 ---- */
.vocab-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ---- 生词卡片 ---- */
.vocab-card {
  position: relative;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition:
    transform 0.25s var(--ease-bounce),
    box-shadow 0.25s var(--ease-standard),
    border-color 0.25s var(--ease-standard);
}

.vocab-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(15, 76, 58, 0.1);
  border-color: var(--color-brand-bright);
}

/* 状态色条 — 左侧竖线 */
.vocab-status-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 4px 0 0 4px;
}

.status-new {
  background: var(--color-accent, #E2725B);
}

.status-review {
  background: var(--color-brand, #0F4C3A);
}

.status-mastered {
  background: var(--color-success, #2D8659);
}

.vocab-card-inner {
  padding: 24px;
}

/* 已掌握卡片 */
.vocab-card.vocab-mastered {
  background: linear-gradient(
    135deg,
    var(--color-bg-card) 0%,
    var(--color-brand-subtle) 100%
  );
}

.vocab-card.vocab-mastered:hover {
  border-color: var(--color-success);
}

/* 学习中卡片 */
.vocab-card.vocab-learning {
  border-left: none; /* 由 status-bar 代替 */
}

/* 新词卡片 */
.vocab-card.vocab-new {
  border-left: none; /* 由 status-bar 代替 */
}

/* ---- 单词头部 ---- */
.vocab-card-top {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.vocab-word-area {
  flex: 1;
  min-width: 0;
}

.vocab-word-row {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  cursor: pointer;
  padding: 4px 0;
  transition: opacity 0.2s;
}

.vocab-word-row:hover {
  opacity: 0.75;
}

.vocab-word {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: -0.3px;
  line-height: 1.2;
}

.vocab-phonetic {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-style: italic;
  margin-top: 4px;
  letter-spacing: 0.3px;
}

/* ---- TTS 发音按钮 — 圆形 44px touch target ---- */
.tts-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-brand);
  cursor: pointer;
  flex-shrink: 0;
  transition:
    background 0.2s var(--ease-standard),
    border-color 0.2s var(--ease-standard),
    color 0.2s var(--ease-standard),
    transform 0.2s var(--ease-bounce);
}

.tts-btn:hover {
  background: var(--color-brand-subtle);
  border-color: var(--color-brand);
  color: var(--color-brand);
  transform: scale(1.08);
}

.tts-btn:active {
  transform: scale(0.95);
}

/* ---- 状态标签组 ---- */
.vocab-status-group {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  align-items: center;
  flex-wrap: wrap;
}

/* ---- 翻译 ---- */
.vocab-translation {
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 14px;
  padding: 12px 16px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-sm, 8px);
  border-left: 3px solid var(--color-brand);
}

/* ---- 复习进度可视化 ---- */
.vocab-progress-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 14px;
  padding: 12px 16px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-sm, 8px);
  flex-wrap: wrap;
}

/* 掌握度进度环 */
.mastery-ring {
  position: relative;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
}

.mastery-ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.mastery-ring-bg {
  fill: none;
  stroke: var(--color-border);
  stroke-width: 3;
}

.mastery-ring-fill {
  fill: none;
  stroke: var(--color-brand);
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dasharray 0.4s var(--ease-standard);
}

.vocab-mastered .mastery-ring-fill {
  stroke: var(--color-success);
}

.mastery-ring-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

/* 复习强度 bar */
.review-strength {
  flex: 1;
  min-width: 100px;
}

.review-strength-label {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-bottom: 4px;
  font-weight: 500;
}

.review-strength-bar {
  width: 100%;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
}

.review-strength-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s var(--ease-standard);
}

.strength-low {
  background: var(--color-accent, #E2725B);
}

.strength-mid {
  background: var(--color-brand, #0F4C3A);
}

.strength-high {
  background: var(--color-success, #2D8659);
}

.review-strength-count {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-top: 3px;
}

/* 下次复习时间提示 */
.vocab-next-review {
  font-size: 12px;
  color: var(--color-text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}

/* ---- 语境 ---- */
.vocab-context-area {
  margin-bottom: 14px;
}

.vocab-context {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  cursor: pointer;
  padding: 10px 14px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-sm, 8px);
  display: flex;
  align-items: flex-start;
  gap: 8px;
  transition: background 0.2s;
}

.vocab-context:hover {
  background: var(--color-brand-subtle);
}

.vocab-context:hover .speak-icon-small {
  opacity: 1;
  color: var(--color-brand);
}

.context-label {
  color: var(--color-brand);
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  font-size: 12px;
  padding: 2px 6px;
  background: var(--color-brand-subtle);
  border-radius: 4px;
}

.context-text {
  flex: 1;
}

.speak-icon-small {
  font-size: 14px;
  color: var(--color-text-muted);
  opacity: 0;
  transition: all 0.2s;
  cursor: pointer;
  flex-shrink: 0;
}

.vocab-context-cn {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.6;
  padding: 8px 14px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-sm, 8px);
  margin-top: 6px;
}

/* ---- 卡片底部 ---- */
.vocab-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}

.vocab-source {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 5px 12px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-full, 9999px);
  transition: all 0.2s var(--ease-standard);
  border: 1px solid transparent;
}

.vocab-source:hover {
  background: var(--color-brand-subtle);
  color: var(--color-brand);
  border-color: var(--color-border-brand, #B8D4C5);
}

.vocab-source svg {
  flex-shrink: 0;
}

.vocab-time {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* ---- 操作按钮 ---- */
.vocab-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
  flex-wrap: wrap;
}

/* 确保 touch target */
.vocab-actions :deep(.sf-btn) {
  min-height: 36px;
}

/* ---- 分页 ---- */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 32px 0;
  flex-wrap: wrap;
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-total {
  font-size: 13px;
  color: var(--color-text-muted);
  font-weight: 500;
  white-space: nowrap;
}

.page-size-select {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-size-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

/* ---- Loading skeleton ---- */
.vocab-list :deep(.el-loading-mask) {
  background: rgba(250, 250, 247, 0.85);
  border-radius: var(--radius-lg, 16px);
}

.vocab-list :deep(.el-loading-spinner .path) {
  stroke: var(--color-brand, #0F4C3A);
}

.vocab-list :deep(.el-loading-spinner .el-loading-text) {
  color: var(--color-brand, #0F4C3A);
}

/* ---- 空状态 ---- */
.vocab-list :deep(.empty-state) {
  padding: 64px 16px;
}

.vocab-list :deep(.empty-state .empty-title) {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.vocab-list :deep(.empty-state .empty-description) {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.vocab-list :deep(.empty-state .empty-actions .sf-btn) {
  min-height: 44px;
  padding: 0 24px;
  font-size: 15px;
}

/* ============================================
   响应式 — 移动端优化
   ============================================ */
@media (max-width: 768px) {
  .filter-bar {
    padding: 12px 14px;
    gap: 10px;
  }

  .filter-row {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
    gap: 10px;
  }

  .filter-section {
    width: 100%;
  }

  .filter-section :deep(.el-select),
  .filter-section :deep(.sf-select) {
    flex: 1;
  }

  .filter-total {
    margin-left: 0;
  }

  .filter-chips {
    width: 100%;
  }

  /* 单列布局 */
  .vocab-list {
    gap: 14px;
  }

  .vocab-card-inner {
    padding: 16px;
  }

  .vocab-card-top {
    gap: 12px;
  }

  .vocab-word {
    font-size: 22px;
  }

  .vocab-phonetic {
    font-size: 13px;
  }

  /* mobile TTS 按钮保持 44px */
  .tts-btn {
    width: 44px;
    height: 44px;
  }

  /* 翻译区 */
  .vocab-translation {
    font-size: 14px;
    padding: 10px 12px;
  }

  /* 进度行 mobile */
  .vocab-progress-row {
    gap: 12px;
    padding: 10px 12px;
  }

  .review-strength {
    min-width: 80px;
  }

  /* 操作按钮 44px touch target */
  .vocab-actions {
    gap: 6px;
  }

  .vocab-actions :deep(.sf-btn) {
    min-height: 44px;
    flex: 1;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .vocab-word {
    font-size: 20px;
  }

  .vocab-card-top {
    flex-wrap: wrap;
  }

  .vocab-status-group {
    width: 100%;
    order: 3;
  }

  /* mobile 操作按钮竖排 */
  .vocab-actions {
    flex-direction: column;
    gap: 6px;
  }

  .vocab-actions :deep(.sf-btn) {
    width: 100%;
  }

  .vocab-progress-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .review-strength {
    width: 100%;
  }
}
</style>
