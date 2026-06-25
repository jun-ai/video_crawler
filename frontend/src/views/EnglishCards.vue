<template>
  <div class="ec-page">
    <!-- Left Sidebar -->
    <aside class="ec-sidebar">
      <div class="ec-sidebar-header">
        <div class="ec-search-box">
          <Search :size="14" class="ec-search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            class="ec-search-input"
            placeholder="搜索材料..."
          />
        </div>
      </div>
      <div class="ec-sidebar-list" v-loading="materialsLoading">
        <div
          v-for="item in filteredMaterials"
          :key="item.id"
          class="ec-sidebar-item"
          :class="{ active: selectedMaterialId === item.id }"
          @click="selectMaterial(item)"
        >
          <img
            :src="item.cover_path || defaultThumb"
            :alt="item.title"
            class="ec-sidebar-thumb"
            @error="onThumbError($event, item)"
          />
          <div class="ec-sidebar-info">
            <div class="ec-sidebar-title">{{ item.title }}</div>
            <div class="ec-sidebar-meta" v-if="item.category">
              <span class="ec-sidebar-category">{{ item.category }}</span>
            </div>
          </div>
          <span class="ec-sidebar-badge" v-if="getMaterialCount(item) > 0">
            {{ getMaterialCount(item) }}
          </span>
        </div>
        <EmptyState
          v-if="!materialsLoading && filteredMaterials.length === 0"
          title="暂无材料"
          description="请先添加学习材料"
        />
      </div>
    </aside>

    <!-- Right Main Area -->
    <main class="ec-main">
      <!-- No material selected state -->
      <div class="ec-empty-main" v-if="!selectedMaterialId">
        <EmptyState
          title="选择一个材料"
          description="从左侧列表中选择一个材料，开始学习其中的单词和短语"
          :icon="BookOpen"
        />
      </div>

      <!-- Main content -->
      <template v-else>
        <!-- Tab bar -->
        <div class="ec-tab-bar">
          <div class="ec-tabs">
            <div
              class="ec-tab"
              :class="{ active: activeTab === 'words' }"
              @click="activeTab = 'words'"
            >
              <span>单词</span>
              <span class="ec-tab-count" v-if="tabCounts.words > 0">({{ tabCounts.words }})</span>
            </div>
            <div
              class="ec-tab"
              :class="{ active: activeTab === 'phrases' }"
              @click="activeTab = 'phrases'"
            >
              <span>短语</span>
              <span class="ec-tab-count" v-if="tabCounts.phrases > 0">({{ tabCounts.phrases }})</span>
            </div>
            <div
              class="ec-tab"
              :class="{ active: activeTab === 'grammar' }"
              @click="activeTab = 'grammar'"
            >
              <span>地道表达</span>
              <span class="ec-tab-count" v-if="tabCounts.grammar > 0">({{ tabCounts.grammar }})</span>
            </div>
          </div>
          <div class="ec-tab-actions">
            <SfTooltip :content="hideChinese ? '显示中文' : '隐藏中文'" placement="bottom">
              <SfButton
                size="sm"
                :type="hideChinese ? 'primary' : 'ghost'"
                @click="hideChinese = !hideChinese"
              >
                <Eye :size="14" />
              </SfButton>
            </SfTooltip>
          </div>
        </div>

        <!-- Filter chips -->
        <div class="ec-filter-bar">
          <FilterChip
            v-model="filterStatus"
            value="all"
            label="全部"
            :count="filterCounts.all"
          />
          <FilterChip
            v-model="filterStatus"
            value="unmarked"
            label="未标记"
            :count="filterCounts.unmarked"
          />
          <FilterChip
            v-model="filterStatus"
            value="known"
            label="认识"
            :count="filterCounts.known"
          />
          <FilterChip
            v-model="filterStatus"
            value="unknown"
            label="不认识"
            :count="filterCounts.unknown"
          />
        </div>

        <!-- Card grid -->
        <div class="ec-card-grid" v-loading="interpretationLoading">
          <!-- 2.9 抽 CardItem 子组件: word/phrase/grammar 三类共用一个组件 -->
          <EnglishCardItem
            v-if="activeTab === 'words'"
            v-for="item in filteredItems"
            :key="item.id"
            :item="item"
            type="word"
            :status="learningStatus[item.id] || ''"
            :selected="selectedCardId === item.id"
            :hide-chinese="hideChinese"
            @toggle-select="onToggleSelect"
            @set-status="onSetStatus"
            @speak="speakWord"
          />

          <EnglishCardItem
            v-if="activeTab === 'phrases'"
            v-for="item in filteredItems"
            :key="item.id"
            :item="item"
            type="phrase"
            :status="learningStatus[item.id] || ''"
            :selected="selectedCardId === item.id"
            :hide-chinese="hideChinese"
            @toggle-select="onToggleSelect"
            @set-status="onSetStatus"
            @speak="speakWord"
          />

          <!-- 2.10 grammar 默认折叠: 展开状态由 expandedGrammarIds Set 管理 -->
          <EnglishCardItem
            v-if="activeTab === 'grammar'"
            v-for="item in filteredItems"
            :key="item.id"
            :item="item"
            type="grammar"
            :status="learningStatus[item.id] || ''"
            :selected="false"
            :hide-chinese="hideChinese"
            :grammar-expanded="expandedGrammarIds.has(item.id)"
            @toggle-select="onToggleSelect"
            @set-status="onSetStatus"
            @speak="speakWord"
            @toggle-grammar="onToggleGrammar"
            @jump-learn="onJumpLearn"
          />

          <!-- Empty state for current tab -->
          <EmptyState
            v-if="!interpretationLoading && filteredItems.length === 0"
            title="暂无内容"
            description="当前分类下没有数据"
          />
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { useTTS } from '@/composables/useTTS'
import { Search, ArrowRight, Headphones, BookOpen, Eye, Lightbulb } from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfTooltip from '@/components/ui/SfTooltip.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterChip from '@/components/common/FilterChip.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { materialAPI, interpretationAPI, vocabularyAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import EnglishCardItem from '@/components/learn/EnglishCardItem.vue'

const userStore = useUserStore()
const router = useRouter()
const { speakWord, preloadVoices } = useTTS()

// 默认缩略图 — 灰底 + Video icon SVG (data URI),避免 /default-thumb.png 404
const defaultThumb =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
      <rect width="48" height="48" rx="6" fill="#E2E8F0"/>
      <path d="M19 16 L33 24 L19 32 Z" fill="#94A3B8"/>
    </svg>`
  )
// 缩略图加载失败时,把 src 替换成 defaultThumb(防止 OSS 404 后 img 空白)
const failedThumbs = new Set()
const onThumbError = (e, item) => {
  if (failedThumbs.has(item.id)) return
  failedThumbs.add(item.id)
  e.target.src = defaultThumb
}

// ==================== State ====================
const searchQuery = ref('')
const materials = ref([])
const materialsLoading = ref(false)
const selectedMaterialId = ref(null)

const activeTab = ref('words')
const filterStatus = ref('all')
const hideChinese = ref(false)
const selectedCardId = ref(null)

// 2.10 grammar 展开状态 (Set, 默认全部折叠, 用户手动展开)
const expandedGrammarIds = ref(new Set())

const interpretationData = ref({ words: [], phrases: [], grammar: [] })
const interpretationLoading = ref(false)
const learningStatus = ref({})

// ==================== Computed ====================

/** Filter materials by search query */
const filteredMaterials = computed(() => {
  if (!searchQuery.value.trim()) return materials.value
  const q = searchQuery.value.toLowerCase().trim()
  return materials.value.filter(m =>
    m.title?.toLowerCase().includes(q)
  )
})

/** Current tab items */
const currentTabItems = computed(() => {
  return interpretationData.value[activeTab.value] || []
})

/** Tab counts */
const tabCounts = computed(() => ({
  words: (interpretationData.value.words || []).length,
  phrases: (interpretationData.value.phrases || []).length,
  grammar: (interpretationData.value.grammar || []).length
}))

/** Filter counts for the current tab */
const filterCounts = computed(() => {
  const items = currentTabItems.value
  const statusMap = learningStatus.value
  const all = items.length
  let known = 0
  let unknown = 0
  items.forEach(item => {
    if (statusMap[item.id] === 'known') known++
    else if (statusMap[item.id] === 'unknown') unknown++
  })
  return {
    all,
    unmarked: all - known - unknown,
    known,
    unknown
  }
})

/** Filtered items based on status filter */
const filteredItems = computed(() => {
  const items = currentTabItems.value
  const statusMap = learningStatus.value
  if (filterStatus.value === 'all') return items
  if (filterStatus.value === 'known') return items.filter(i => statusMap[i.id] === 'known')
  if (filterStatus.value === 'unknown') return items.filter(i => statusMap[i.id] === 'unknown')
  if (filterStatus.value === 'unmarked') return items.filter(i => !statusMap[i.id])
  return items
})

// ==================== Methods ====================

/** Get interpretation count for a material (cached or calculated) */
const materialInterpretationCounts = ref({})
function getMaterialCount(item) {
  return materialInterpretationCounts.value[item.id] || 0
}

/** Load materials list */
async function loadMaterials() {
  materialsLoading.value = true
  try {
    const result = await materialAPI.getList({ page_size: 100 })
    materials.value = result.items || []
  } catch (e) {
    console.error('Failed to load materials', e)
  } finally {
    materialsLoading.value = false
  }
}

/** Select a material and load its interpretation data */
async function selectMaterial(item) {
  if (selectedMaterialId.value === item.id) return
  selectedMaterialId.value = item.id
  selectedCardId.value = null
  filterStatus.value = 'all'
  activeTab.value = 'words'
  await loadInterpretation(item.id)
  await loadStatus(item.id)
}

/** Load interpretation data for a material */
async function loadInterpretation(materialId) {
  interpretationLoading.value = true
  try {
    const result = await materialAPI.getInterpretation(materialId)
    const data = result || {}
    interpretationData.value = {
      words: data.words || [],
      phrases: data.phrases || [],
      grammar: data.grammar || []
    }
    // Cache the total count
    const total = (data.words || []).length + (data.phrases || []).length + (data.grammar || []).length
    materialInterpretationCounts.value[materialId] = total
  } catch (e) {
    console.error('Failed to load interpretation', e)
    interpretationData.value = { words: [], phrases: [], grammar: [] }
  } finally {
    interpretationLoading.value = false
  }
}

/** Load learning status for a material */
async function loadStatus(materialId) {
  try {
    const result = await interpretationAPI.getStatus(materialId)
    const statusMap = {}
    if (Array.isArray(result)) {
      result.forEach(s => {
        statusMap[s.interpretation_id] = s.status
      })
    } else if (result && typeof result === 'object') {
      // Handle object format
      Object.keys(result).forEach(key => {
        statusMap[key] = result[key]
      })
    }
    learningStatus.value = statusMap
  } catch (e) {
    console.error('Failed to load status', e)
    learningStatus.value = {}
  }
}

/** Set learning status for an interpretation item */
async function setStatus(interpretationId, status) {
  // Optimistic update
  const prevStatus = learningStatus.value[interpretationId]
  learningStatus.value = { ...learningStatus.value, [interpretationId]: status }

  try {
    await interpretationAPI.setStatus({
      interpretation_id: interpretationId,
      material_id: selectedMaterialId.value,
      status
    })
    // 标 unknown 时同步入生词本（后端 LearningSignalService 也会做，前端做一次确保 UI 同步）
    if (status === 'unknown') {
      const allItems = [
        ...(interpretationData.value.words || []),
        ...(interpretationData.value.phrases || []),
        ...(interpretationData.value.grammar || []),
      ]
      const item = allItems.find(i => i.id === interpretationId)
      if (item) {
        vocabularyAPI.add({
          word: item.content_en || item.word || '',
          translation: item.content_cn || item.translation || '',
          context: item.context_sentence || item.context || '',
          material_id: selectedMaterialId.value,
        }).catch(err => console.warn('[EnglishCards] 同步生词本失败', err))
      }
    }
    toast.success(status === 'known' ? '已标记为认识' : '已标记为不认识')
  } catch (e) {
    // Revert on failure
    const newStatus = { ...learningStatus.value }
    if (prevStatus) {
      newStatus[interpretationId] = prevStatus
    } else {
      delete newStatus[interpretationId]
    }
    learningStatus.value = newStatus
    console.error('Failed to set status', e)
  }
}

/** speakWord 由 useTTS 提供 */

/** 点读跳转到 Learn 页面 */
const goLearn = (materialId) => {
  if (materialId) {
    router.push(`/learn/${materialId}`)
  }
}

// ==================== Event Handlers (2.9 CardItem 子组件) ====================

/** 2.9 CardItem 触发: 父组件管理 selectedCardId (null = 关闭) */
function onToggleSelect(id) {
  selectedCardId.value = (id === null || selectedCardId.value === id) ? null : id
}

/** 2.9 CardItem 触发: 父组件管理 learningStatus (复用原 setStatus) */
function onSetStatus({ id, status }) {
  setStatus(id, status)
}

/** 2.10 切换 grammar 卡片的折叠状态 */
function onToggleGrammar(id) {
  const next = new Set(expandedGrammarIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  expandedGrammarIds.value = next
}

/** 2.9 grammar 点读跳转: 跳到 Learn 页面 (复用原 goLearn) */
function onJumpLearn(_item) {
  goLearn(selectedMaterialId.value)
}

// ==================== Lifecycle ====================
onMounted(() => {
  preloadVoices()
  loadMaterials()
})
</script>

<style scoped>
/* ==================== Page Layout ==================== */
.ec-page {
  display: flex;
  height: calc(100vh - 120px);
  min-height: 500px;
  gap: 0;
  background: var(--color-bg-elevated);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

/* ==================== Left Sidebar ==================== */
.ec-sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--color-bg-base);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ec-sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.ec-search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.ec-search-icon {
  position: absolute;
  left: 10px;
  font-size: 14px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.ec-search-input {
  width: 100%;
  height: 36px;
  padding: 0 12px 0 34px;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-text-primary);
  background: var(--color-bg-base);
  outline: none;
  transition: border-color var(--sf-duration-normal), box-shadow var(--sf-duration-normal);
  box-sizing: border-box;
}

.ec-search-input::placeholder {
  color: var(--color-text-muted);
}

.ec-search-input:focus {
  border-color: var(--color-brand-bright);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.ec-sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

/* Custom thin scrollbar */
.ec-sidebar-list::-webkit-scrollbar {
  width: 4px;
}
.ec-sidebar-list::-webkit-scrollbar-track {
  background: transparent;
}
.ec-sidebar-list::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}

.ec-sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background var(--sf-duration-normal), border-color var(--sf-duration-fast);
  position: relative;
  margin-bottom: 2px;
  border-left: 3px solid transparent;
}

.ec-sidebar-item:hover {
  background: var(--color-bg-elevated);
}

.ec-sidebar-item.active {
  background: var(--color-brand-subtle);
  border-left-color: var(--color-brand-bright);
}

.ec-sidebar-thumb {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
  background: var(--color-bg-elevated);
}

.ec-sidebar-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.ec-sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ec-sidebar-item.active .ec-sidebar-title {
  color: var(--color-brand-bright);
}

.ec-sidebar-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ec-sidebar-category {
  font-size: 11px;
  color: var(--color-text-muted);
  background: var(--color-bg-elevated);
  padding: 1px 6px;
  border-radius: 4px;
}

.ec-sidebar-badge {
  flex-shrink: 0;
  min-width: 22px;
  height: 20px;
  line-height: 20px;
  padding: 0 6px;
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
  border-radius: 10px;
}

/* ==================== Right Main Area ==================== */
.ec-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-bg-base);
  min-width: 0;
}

.ec-empty-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ==================== Tab Bar - Pill Style ==================== */
.ec-tab-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  gap: 16px;
}

.ec-tabs {
  display: flex;
  gap: 6px;
  overflow-x: auto;
}

.ec-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: 20px;
  background: var(--color-bg-elevated);
  border: 1px solid transparent;
  transition: all var(--sf-duration-normal);
  white-space: nowrap;
  user-select: none;
}

.ec-tab:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
}

.ec-tab.active {
  color: #fff;
  font-weight: 600;
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  border-color: var(--color-brand-bright);
}

.ec-tab .el-icon {
  font-size: 14px;
}

.ec-tab-count {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-muted);
}

.ec-tab.active .ec-tab-count {
  color: rgba(255, 255, 255, 0.85);
}

.ec-tab-actions {
  flex-shrink: 0;
}

/* ==================== Filter Bar ==================== */
.ec-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  flex-wrap: wrap;
}

/* ==================== Card Grid ==================== */
.ec-card-grid {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  align-content: start;
}

/* Custom thin scrollbar */
.ec-card-grid::-webkit-scrollbar {
  width: 5px;
}
.ec-card-grid::-webkit-scrollbar-track {
  background: transparent;
}
.ec-card-grid::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

/* ==================== Vocab Card ==================== */
.ec-vocab-card {
  background: var(--color-bg-base);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all var(--sf-duration-normal) ease;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ec-vocab-card:hover {
  border-color: var(--color-brand-bright);
}

.ec-vocab-card.ec-card-known {
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

.ec-vocab-card.ec-card-unknown {
  border-color: var(--color-danger);
  background: var(--color-danger-subtle);
}

.ec-vocab-card.ec-card-selected {
  background: var(--color-brand-light);
  border-color: var(--color-brand-bright);
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.12);
}

/* Card Header */
.ec-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.ec-card-word-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.ec-card-word {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.3;
}

.ec-card-phonetic {
  font-size: 13px;
  font-style: italic;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color var(--sf-duration-normal);
}

.ec-card-phonetic:hover {
  color: var(--color-brand-bright);
}

/* Speak button */
.ec-speak-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: none;
  background: var(--color-bg-elevated);
  border-radius: 50%;
  cursor: pointer;
  color: var(--color-text-muted);
  transition: all var(--sf-duration-normal);
  flex-shrink: 0;
  margin-left: 4px;
}

.ec-speak-btn:hover {
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
}

.ec-card-word {
  cursor: pointer;
  transition: color var(--sf-duration-normal);
}

.ec-card-word:hover {
  color: var(--color-brand-bright);
}

.ec-card-pos {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;
}

/* Card Meanings */
.ec-card-meanings {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ec-card-cn {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.ec-card-en-def {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

/* Card Example */
.ec-card-example {
  background: var(--color-bg-elevated);
  border-left: 3px solid var(--color-brand-bright);
  padding: 8px 12px;
  border-radius: 0 6px 6px 0;
}

.ec-example-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-brand-bright);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.ec-example-text {
  font-size: 12.5px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* Card Actions - Circle Buttons */
.ec-card-actions {
  display: flex;
  gap: 6px;
  padding-top: 4px;
  align-items: center;
}

.ec-circle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-base);
  cursor: pointer;
  transition: all var(--sf-duration-normal);
  color: var(--color-text-muted);
}

.ec-circle-btn:hover {
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
}

.ec-btn-known {
  color: var(--color-success);
  border-color: var(--color-success);
}

.ec-btn-known:hover,
.ec-btn-known.active {
  background: var(--color-success);
  border-color: var(--color-success);
  color: #fff;
}

.ec-btn-unknown {
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.ec-btn-unknown:hover,
.ec-btn-unknown.active {
  background: var(--color-danger);
  border-color: var(--color-danger);
  color: #fff;
}

/* Card Expand */
.ec-card-expand {
  border-top: 1px solid var(--color-border);
  padding-top: 10px;
  margin-top: 2px;
}

.ec-expand-section {
  margin-bottom: 10px;
}

.ec-expand-section:last-child {
  margin-bottom: 0;
}

.ec-expand-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-brand-bright);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}

.ec-expand-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.ec-expand-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ec-expand-tag {
  display: inline-block;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  border-radius: 6px;
  border: 1px solid var(--color-border);
}

/* Grammar analysis area */
.ec-analysis-area {
  background: var(--color-bg-elevated);
  border-radius: 8px;
  padding: 10px 12px;
}

.ec-analysis-item {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 6px;
}

.ec-analysis-item:last-child {
  margin-bottom: 0;
}

.ec-analysis-label {
  font-weight: 600;
  color: var(--color-text-primary);
}

.analysis-icon {
  color: var(--color-warning);
  flex-shrink: 0;
}

/* Jump to learn button */
.ec-jump-row {
  display: flex;
  justify-content: flex-end;
  padding-top: 4px;
}

.ec-jump-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: all var(--sf-duration-normal);
}

.ec-jump-btn:hover {
  filter: brightness(1.1);
}

/* Expand arrow indicator */
.ec-card-expand-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
}

.ec-card-expand-indicator .el-icon {
  font-size: 14px;
  color: var(--color-text-muted);
  transition: transform var(--sf-duration-slow) ease;
}

.ec-card-expand-indicator .el-icon.rotated {
  transform: rotate(90deg);
  color: var(--color-brand-bright);
}

/* ==================== Transitions ==================== */
.ec-expand-enter-active,
.ec-expand-leave-active {
  transition: all var(--sf-duration-normal) ease;
  overflow: hidden;
}

.ec-expand-enter-from,
.ec-expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  margin-top: 0;
}

.ec-expand-enter-to,
.ec-expand-leave-from {
  opacity: 1;
  max-height: 500px;
}

/* ==================== Responsive ==================== */
@media (max-width: 1280px) {
  .ec-sidebar {
    width: 240px;
    min-width: 240px;
  }

  .ec-card-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }
}

@media (max-width: 1024px) {
  .ec-card-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    padding: 16px;
  }

  .ec-tab {
    padding: 12px 14px;
    font-size: 13px;
  }

  .ec-filter-bar {
    padding: 12px 16px;
  }
}

@media (max-width: 768px) {
  .ec-page {
    flex-direction: column;
    height: auto;
    min-height: auto;
    border-radius: 0;
  }

  .ec-sidebar {
    width: 100%;
    min-width: 100%;
    max-height: 220px;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }

  .ec-sidebar-list {
    display: flex;
    overflow-x: auto;
    overflow-y: hidden;
    flex-direction: row;
    gap: 8px;
    padding: 8px 12px;
    white-space: nowrap;
  }

  .ec-sidebar-item {
    flex-shrink: 0;
    flex-direction: column;
    align-items: center;
    border-left: none;
    border-bottom: 3px solid transparent;
    width: 100px;
    padding: 8px;
    margin-bottom: 0;
  }

  .ec-sidebar-item.active {
    border-left-color: transparent;
    border-bottom-color: var(--color-brand-bright);
  }

  .ec-sidebar-thumb {
    width: 56px;
    height: 56px;
  }

  .ec-sidebar-title {
    font-size: 11px;
    text-align: center;
    white-space: normal;
    -webkit-line-clamp: 2;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .ec-sidebar-badge {
    position: absolute;
    top: 4px;
    right: 4px;
  }

  .ec-card-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px;
  }

  .ec-tab-bar {
    padding: 0 12px;
    flex-wrap: wrap;
  }

  .ec-tabs {
    width: 100%;
    justify-content: space-around;
  }

  .ec-tab {
    padding: 10px 8px;
    font-size: 12px;
    flex: 1;
    justify-content: center;
  }

  .ec-filter-bar {
    padding: 10px 12px;
    gap: 6px;
  }

  .ec-card-word {
    font-size: 16px;
  }

  .ec-card-actions {
    flex-wrap: wrap;
    gap: 8px;
  }

  .ec-circle-btn {
    width: 36px;
    height: 36px;
  }

  .ec-search-input {
    height: 40px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .ec-sidebar-list {
    padding: 6px 8px;
  }

  .ec-sidebar-item {
    width: 80px;
  }

  .ec-sidebar-thumb {
    width: 44px;
    height: 44px;
  }

  .ec-card-grid {
    padding: 8px;
    gap: 10px;
  }

  .ec-vocab-card {
    padding: 12px;
  }

  .ec-circle-btn {
    width: 36px;
    height: 36px;
  }

  .ec-card-word {
    font-size: 15px;
  }

  .ec-tab {
    font-size: 11px;
    gap: 3px;
    padding: 8px 6px;
  }

  .ec-tab-count {
    font-size: 10px;
  }

  .ec-tab-actions {
    width: 100%;
    padding-bottom: 8px;
  }

  .ec-tab-actions .sf-btn {
    width: 100%;
  }
}

/* ==================== Dark Mode ==================== */
.dark .ec-page {
  background: var(--color-bg-elevated);
  border-color: var(--color-border);
}

.dark .ec-sidebar {
  background: var(--color-bg-base);
  border-right-color: var(--color-border);
}

.dark .ec-search-input {
  background: var(--color-bg-elevated);
  border-color: var(--color-border);
  color: var(--color-text-primary);
}

.dark .ec-sidebar-item:hover {
  background: var(--color-bg-elevated);
}

.dark .ec-sidebar-item.active {
  background: var(--color-brand-subtle);
}

.dark .ec-sidebar-category {
  background: var(--color-bg-elevated);
}

.dark .ec-sidebar-badge {
  background: var(--color-brand-subtle);
}

.dark .ec-main {
  background: var(--color-bg-base);
}

.dark .ec-vocab-card {
  background: var(--color-bg-base);
  border-color: var(--color-border);
}

.dark .ec-vocab-card:hover {
  border-color: var(--color-brand-bright);
}

.dark .ec-vocab-card.ec-card-known {
  background: rgba(37, 99, 235, 0.08);
  border-color: var(--color-brand-bright);
}

.dark .ec-vocab-card.ec-card-unknown {
  background: var(--color-danger-subtle);
  border-color: var(--color-danger);
}

.dark .ec-vocab-card.ec-card-selected {
  background: rgba(37, 99, 235, 0.12);
  border-color: var(--color-brand-bright);
}

.dark .ec-card-example {
  background: var(--color-bg-elevated);
}

.dark .ec-card-pos {
  background: var(--color-brand-subtle);
}

.dark .ec-expand-tag {
  background: var(--color-bg-elevated);
  border-color: var(--color-border);
}
</style>
