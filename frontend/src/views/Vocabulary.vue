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
          :class="['vocab-card', { 'vocab-mastered': item.mastered }]"
        >
          <!-- 单词头部 -->
          <div class="vocab-card-top">
            <div class="vocab-word-area">
              <div class="vocab-word-row" @click="speakText(item.word)">
                <span class="vocab-word">{{ item.word }}</span>
                <Headphones :size="18" class="speak-icon-trigger" />
              </div>
              <!-- 查询到的音标和释义 -->
              <div class="vocab-phonetic" v-if="getWordInfo(item.word)?.phonetic">
                /{{ getWordInfo(item.word).phonetic }}/
              </div>
            </div>
            <div class="vocab-badges">
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
            <div class="vocab-time">
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
.yt-vocabulary {
  max-width: 1000px;
  margin: 0 auto;
}

/* 筛选条 */
.filter-bar {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
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
}

/* 生词列表 */
.vocab-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vocab-card {
  background: var(--color-bg-base);
  border-radius: 14px;
  padding: 20px;
  border: 1px solid var(--color-border);
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.vocab-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.15);
}

.vocab-card.vocab-mastered {
  border-left: 3px solid var(--color-success);
}

/* 单词头部 */
.vocab-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.vocab-word-area {
  flex: 1;
}

.vocab-word-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 10px;
  transition: background 0.2s;
}

.vocab-word-row:hover {
  background: rgba(16, 185, 129, 0.06);
}

.vocab-word-row:hover .speak-icon-trigger {
  opacity: 1;
  color: var(--color-brand);
}

.vocab-word {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: 0.5px;
}

.speak-icon-trigger {
  font-size: 18px;
  color: var(--color-text-muted);
  opacity: 0;
  transition: all 0.2s;
}

.vocab-phonetic {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-style: italic;
  margin-top: 2px;
  padding-left: 10px;
}

.vocab-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  align-items: center;
  flex-wrap: wrap;
}

/* 翻译 */
.vocab-translation {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: var(--color-bg-elevated);
  border-radius: 8px;
}

/* 语境 */
.vocab-context-area {
  margin-bottom: 12px;
}

.vocab-context {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  cursor: pointer;
  padding: 8px 12px;
  background: var(--color-bg-elevated);
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.vocab-context:hover .speak-icon-small {
  opacity: 1;
  color: var(--color-brand);
}

.context-label {
  color: var(--color-brand);
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
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
  line-height: 1.5;
  padding: 6px 12px;
  background: var(--color-bg-elevated);
  border-radius: 8px;
  margin-top: 6px;
}

/* 卡片底部 */
.vocab-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}

.vocab-source {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 3px 10px;
  background: var(--color-bg-elevated);
  border-radius: 12px;
  transition: all 0.2s;
}

.vocab-source:hover {
  background: rgba(16, 185, 129, 0.08);
  color: var(--color-brand);
}

.vocab-source .el-icon {
  font-size: 13px;
}

.vocab-time {
  font-size: 11px;
  color: var(--color-text-muted);
}

/* 操作按钮 */
.vocab-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 24px 0;
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

/* 响应式 */
@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }

  .filter-section {
    width: 100%;
  }

  .filter-section .el-select {
    width: 100% !important;
  }

  .filter-total {
    margin-left: 0;
  }

  .vocab-card {
    padding: 16px;
  }

  .vocab-word {
    font-size: 20px;
  }

  .vocab-card-top {
    flex-direction: column;
    gap: 8px;
  }

  .vocab-badges {
    align-self: flex-start;
  }

  .vocab-actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .vocab-word {
    font-size: 18px;
  }

  .vocab-actions {
    flex-direction: column;
  }

  .vocab-actions .sf-btn {
    width: 100%;
  }
}
</style>
