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
            :src="item.thumbnail_path || '/default-thumb.png'"
            :alt="item.title"
            class="ec-sidebar-thumb"
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
          <!-- Words cards -->
          <template v-if="activeTab === 'words'">
            <div
              v-for="item in filteredItems"
              :key="item.id"
              class="ec-vocab-card"
              :class="{
                'ec-card-selected': selectedCardId === item.id,
                'ec-card-known': learningStatus[item.id] === 'known',
                'ec-card-unknown': learningStatus[item.id] === 'unknown'
              }"
              @click="selectedCardId = selectedCardId === item.id ? null : item.id"
            >
              <!-- Row 1: Word + Phonetic + POS tag -->
              <div class="ec-card-header">
                <div class="ec-card-word-row">
                  <span class="ec-card-word" @click.stop="speakWord(item.content_en)">{{ item.content_en }}</span>
                  <span class="ec-card-phonetic" v-if="item.phonetic" @click.stop="speakWord(item.content_en)">{{ item.phonetic }}</span>
                  <span class="ec-card-pos" v-if="item.part_of_speech">{{ item.part_of_speech }}</span>
                  <button class="ec-speak-btn" @click.stop="speakWord(item.content_en)" title="播放发音">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
                  </button>
                </div>
              </div>

              <!-- Row 2: Chinese meaning + English definition -->
              <div class="ec-card-meanings">
                <div class="ec-card-cn" v-if="!hideChinese && item.content_cn">{{ item.content_cn }}</div>
                <div class="ec-card-en-def" v-if="item.english_definition">{{ item.english_definition }}</div>
              </div>

              <!-- Row 3: Example sentence -->
              <div class="ec-card-example" v-if="item.example_sentence">
                <div class="ec-example-label">例句</div>
                <div class="ec-example-text">{{ item.example_sentence }}</div>
              </div>

              <!-- Quick action buttons -->
              <div class="ec-card-actions">
                <SfTooltip content="认识" placement="top">
                  <button
                    class="ec-circle-btn ec-btn-known"
                    :class="{ active: learningStatus[item.id] === 'known' }"
                    @click.stop="setStatus(item.id, 'known')"
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </button>
                </SfTooltip>
                <SfTooltip content="不认识" placement="top">
                  <button
                    class="ec-circle-btn ec-btn-unknown"
                    :class="{ active: learningStatus[item.id] === 'unknown' }"
                    @click.stop="setStatus(item.id, 'unknown')"
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                  </button>
                </SfTooltip>
              </div>

              <!-- Expand section -->
              <transition name="ec-expand">
                <div class="ec-card-expand" v-if="selectedCardId === item.id">
                  <div class="ec-expand-section" v-if="item.context_sentence">
                    <div class="ec-expand-label">语境</div>
                    <div class="ec-expand-text">{{ item.context_sentence }}</div>
                  </div>
                  <div class="ec-expand-section" v-if="!hideChinese && item.context_translation">
                    <div class="ec-expand-label">译文</div>
                    <div class="ec-expand-text">{{ item.context_translation }}</div>
                  </div>
                  <div class="ec-expand-section" v-if="item.other_pos_definitions && parseList(item.other_pos_definitions).length > 0">
                    <div class="ec-expand-label">其他释义</div>
                    <div class="ec-expand-text" v-for="(def, idx) in parseList(item.other_pos_definitions)" :key="idx">
                      {{ def }}
                    </div>
                  </div>
                </div>
              </transition>

              <!-- Expand arrow indicator -->
              <div class="ec-card-expand-indicator" v-if="hasExpandContent(item, 'word')">
                <ArrowRight :size="14" :class="{ rotated: selectedCardId === item.id }" />
              </div>
            </div>
          </template>

          <!-- Phrases cards -->
          <template v-if="activeTab === 'phrases'">
            <div
              v-for="item in filteredItems"
              :key="item.id"
              class="ec-vocab-card"
              :class="{
                'ec-card-selected': selectedCardId === item.id,
                'ec-card-known': learningStatus[item.id] === 'known',
                'ec-card-unknown': learningStatus[item.id] === 'unknown'
              }"
              @click="selectedCardId = selectedCardId === item.id ? null : item.id"
            >
              <!-- Row 1: Phrase + Phonetic -->
              <div class="ec-card-header">
                <div class="ec-card-word-row">
                  <span class="ec-card-word" @click.stop="speakWord(item.content_en)">{{ item.content_en }}</span>
                  <span class="ec-card-phonetic" v-if="item.phonetic" @click.stop="speakWord(item.content_en)">{{ item.phonetic }}</span>
                  <span class="ec-card-pos">短语</span>
                  <button class="ec-speak-btn" @click.stop="speakWord(item.content_en)" title="播放发音">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
                  </button>
                </div>
              </div>

              <!-- Row 2: Chinese + English definition -->
              <div class="ec-card-meanings">
                <div class="ec-card-cn" v-if="!hideChinese && item.content_cn">{{ item.content_cn }}</div>
                <div class="ec-card-en-def" v-if="item.english_definition">{{ item.english_definition }}</div>
              </div>

              <!-- Example sentence -->
              <div class="ec-card-example" v-if="item.example_sentence">
                <div class="ec-example-label">例句</div>
                <div class="ec-example-text" @click.stop="speakWord(item.example_sentence)" style="cursor:pointer">{{ item.example_sentence }}</div>
              </div>

              <!-- Quick action buttons -->
              <div class="ec-card-actions">
                <SfTooltip content="认识" placement="top">
                  <button
                    class="ec-circle-btn ec-btn-known"
                    :class="{ active: learningStatus[item.id] === 'known' }"
                    @click.stop="setStatus(item.id, 'known')"
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </button>
                </SfTooltip>
                <SfTooltip content="不认识" placement="top">
                  <button
                    class="ec-circle-btn ec-btn-unknown"
                    :class="{ active: learningStatus[item.id] === 'unknown' }"
                    @click.stop="setStatus(item.id, 'unknown')"
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                  </button>
                </SfTooltip>
              </div>

              <!-- Expand section -->
              <transition name="ec-expand">
                <div class="ec-card-expand" v-if="selectedCardId === item.id">
                  <div class="ec-expand-section" v-if="item.context_sentence">
                    <div class="ec-expand-label">语境</div>
                    <div class="ec-expand-text">{{ item.context_sentence }}</div>
                  </div>
                  <div class="ec-expand-section" v-if="!hideChinese && item.context_translation">
                    <div class="ec-expand-label">译文</div>
                    <div class="ec-expand-text">{{ item.context_translation }}</div>
                  </div>
                  <div class="ec-expand-section" v-if="item.synonyms && parseList(item.synonyms).length > 0">
                    <div class="ec-expand-label">近义词</div>
                    <div class="ec-expand-tags">
                      <span class="ec-expand-tag" v-for="(syn, idx) in parseList(item.synonyms)" :key="idx">{{ syn }}</span>
                    </div>
                  </div>
                </div>
              </transition>

              <!-- Expand arrow indicator -->
              <div class="ec-card-expand-indicator" v-if="hasExpandContent(item, 'phrase')">
                <ArrowRight :size="14" :class="{ rotated: selectedCardId === item.id }" />
              </div>
            </div>
          </template>

          <!-- Grammar / Idiomatic Expression cards — 直接展示富内容 -->
          <template v-if="activeTab === 'grammar'">
            <div
              v-for="item in filteredItems"
              :key="item.id"
              class="ec-vocab-card ec-grammar-card"
              :class="{
                'ec-card-known': learningStatus[item.id] === 'known',
                'ec-card-unknown': learningStatus[item.id] === 'unknown'
              }"
            >
              <!-- Expression text -->
              <div class="ec-card-header">
                <div class="ec-card-word-row">
                  <span class="ec-card-word" @click.stop="speakWord(item.content_en)">{{ item.content_en }}</span>
                  <span class="ec-card-pos">表达</span>
                  <button class="ec-speak-btn" @click.stop="speakWord(item.content_en)" title="播放发音">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
                  </button>
                </div>
                <!-- Quick action buttons -->
                <div class="ec-card-actions">
                  <SfTooltip content="认识" placement="top">
                    <button
                      class="ec-circle-btn ec-btn-known"
                      :class="{ active: learningStatus[item.id] === 'known' }"
                      @click.stop="setStatus(item.id, 'known')"
                    >
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                    </button>
                  </SfTooltip>
                  <SfTooltip content="不认识" placement="top">
                    <button
                      class="ec-circle-btn ec-btn-unknown"
                      :class="{ active: learningStatus[item.id] === 'unknown' }"
                      @click.stop="setStatus(item.id, 'unknown')"
                    >
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                    </button>
                  </SfTooltip>
                </div>
              </div>

              <!-- 字幕原句 -->
              <div class="ec-card-meanings" v-if="item.context_sentence">
                <div class="ec-expand-label">字幕原句</div>
                <div class="ec-expand-text">{{ item.context_sentence }}</div>
              </div>

              <!-- 中文翻译 -->
              <div class="ec-card-meanings" v-if="!hideChinese && item.context_translation">
                <div class="ec-expand-label">中文翻译</div>
                <div class="ec-expand-text">{{ item.context_translation }}</div>
              </div>

              <!-- 表达分析区域 -->
              <div class="ec-card-meanings ec-analysis-area" v-if="item.explanation || item.structure_analysis || item.similar_expressions || item.usage_scenario || item.alternative_phrasings">
                <div class="ec-expand-label"><Lightbulb :size="16" class="analysis-icon" /> 表达分析</div>
                <div class="ec-analysis-item" v-if="item.explanation">{{ item.explanation }}</div>
                <div class="ec-analysis-item" v-if="item.structure_analysis">
                  <span class="ec-analysis-label">结构解析：</span>{{ item.structure_analysis }}
                </div>
                <div class="ec-analysis-item" v-if="item.similar_expressions && parseList(item.similar_expressions).length > 0">
                  <span class="ec-analysis-label">举一反三：</span>
                  <div class="ec-expand-tags">
                    <span class="ec-expand-tag" v-for="(expr, idx) in parseList(item.similar_expressions)" :key="idx">{{ expr }}</span>
                  </div>
                </div>
                <div class="ec-analysis-item" v-if="item.usage_scenario">
                  <span class="ec-analysis-label">使用场景：</span>{{ item.usage_scenario }}
                </div>
                <div class="ec-analysis-item" v-if="item.alternative_phrasings && parseList(item.alternative_phrasings).length > 0">
                  <span class="ec-analysis-label">相似表达：</span>
                  <div class="ec-expand-tags">
                    <span class="ec-expand-tag" v-for="(phrase, idx) in parseList(item.alternative_phrasings)" :key="idx">{{ phrase }}</span>
                  </div>
                </div>
              </div>

              <!-- 例句 -->
              <div class="ec-card-example" v-if="item.example_sentence">
                <div class="ec-example-label">例句</div>
                <div class="ec-example-text">{{ item.example_sentence }}</div>
              </div>

              <!-- 点读跳转 -->
              <div class="ec-jump-row">
                <button class="ec-jump-btn" @click.stop="goLearn(selectedMaterialId)">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                  点读跳转
                </button>
              </div>
            </div>
          </template>

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

const userStore = useUserStore()
const router = useRouter()
const { speakWord, preloadVoices } = useTTS()

// ==================== State ====================
const searchQuery = ref('')
const materials = ref([])
const materialsLoading = ref(false)
const selectedMaterialId = ref(null)

const activeTab = ref('words')
const filterStatus = ref('all')
const hideChinese = ref(false)
const selectedCardId = ref(null)

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

/** Parse a string or array field into an array */
function parseList(val) {
  if (!val) return []
  if (Array.isArray(val)) return val
  if (typeof val === 'string') {
    return val.split(/[,，、;；]/).map(s => s.trim()).filter(Boolean)
  }
  return []
}

/** Check if an item has expand content */
function hasExpandContent(item, type) {
  if (type === 'word') {
    return !!(item.context_sentence || item.context_translation || (item.other_pos_definitions && parseList(item.other_pos_definitions).length > 0))
  }
  if (type === 'phrase') {
    return !!(item.context_sentence || item.context_translation || (item.synonyms && parseList(item.synonyms).length > 0))
  }
  if (type === 'grammar') {
    return !!(item.context_sentence || item.context_translation || item.structure_analysis ||
      (item.similar_expressions && parseList(item.similar_expressions).length > 0) ||
      item.usage_scenario || (item.alternative_phrasings && parseList(item.alternative_phrasings).length > 0))
  }
  return false
}

/** 点读跳转到 Learn 页面 */
const goLearn = (materialId) => {
  if (materialId) {
    router.push(`/learn/${materialId}`)
  }
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
  transition: border-color 0.2s, box-shadow 0.2s;
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
  transition: background 0.2s, border-color 0.15s;
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
  transition: all 0.2s;
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
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
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
  transition: all 0.2s ease;
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
  transition: color 0.2s;
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
  transition: all 0.2s;
  flex-shrink: 0;
  margin-left: 4px;
}

.ec-speak-btn:hover {
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
}

.ec-card-word {
  cursor: pointer;
  transition: color 0.2s;
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
  transition: all 0.2s;
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
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
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
  transition: transform 0.3s ease;
}

.ec-card-expand-indicator .el-icon.rotated {
  transform: rotate(90deg);
  color: var(--color-brand-bright);
}

/* ==================== Transitions ==================== */
.ec-expand-enter-active,
.ec-expand-leave-active {
  transition: all 0.25s ease;
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
