<template>
  <div class="yt-vocabulary">
    <!-- 页面标题 -->
    <PageHeader title="生词本">
      <template #actions>
        <!-- 5-P1-4: 导出按钮 (下拉 JSON / CSV) -->
        <SfDropdown v-if="total > 0">
          <template #trigger>
            <SfButton type="ghost" size="sm">
              <Download :size="14" /> 导出
            </SfButton>
          </template>
          <div class="vocab-dropdown-item" @click="exportVocabulary('json')">
            <FileJson :size="14" /> JSON (完整备份)
          </div>
          <div class="vocab-dropdown-item" @click="exportVocabulary('csv')">
            <FileText :size="14" /> CSV (Anki/Excel)
          </div>
        </SfDropdown>

        <!-- 5-P1-5: 视图切换 (列表/卡片) -->
        <SfButton
          v-if="total > 0"
          :type="viewMode === 'list' ? 'primary' : 'ghost'"
          size="sm"
          @click="toggleViewMode"
          :title="viewMode === 'list' ? '切换到卡片模式' : '切换到列表模式 (密度高)'"
        >
          <LayoutGrid v-if="viewMode === 'list'" :size="14" />
          <Rows3 v-else :size="14" />
          {{ viewMode === 'list' ? '卡片' : '列表' }}
        </SfButton>

        <!-- 5-P2-7: 分页/无限滚动切换 -->
        <SfButton
          v-if="total > 0"
          :type="infiniteScrollMode ? 'primary' : 'ghost'"
          size="sm"
          @click="infiniteScrollMode = !infiniteScrollMode"
          :title="infiniteScrollMode ? '切换到分页模式' : '切换到无限滚动 (滚到底自动加载)'"
        >
          <InfinityIcon v-if="!infiniteScrollMode" :size="14" />
          <ListOrdered v-else :size="14" />
          {{ infiniteScrollMode ? '无限滚动' : '分页' }}
        </SfButton>

        <!-- 5-P0-4: 批量操作模式开关 -->
        <SfButton
          v-if="total > 0"
          :type="batchMode ? 'primary' : 'ghost'"
          size="sm"
          @click="toggleBatchMode"
        >
          <CheckSquare v-if="batchMode" :size="14" />
          <Square v-else :size="14" />
          {{ batchMode ? '退出批量' : '批量操作' }}
        </SfButton>

        <!-- 5-P0-6: 显示中文开关加 label + localStorage 持久化 -->
        <SfSwitch
          v-model="showChinese"
          label="显示中文"
        />
      </template>
    </PageHeader>

    <SfEmpty v-if="!userStore.isLoggedIn" description="请先登录查看生词本">
      <SfButton type="primary" @click="$router.push('/login')">去登录</SfButton>
    </SfEmpty>

    <template v-else>
      <!-- 5-P0-5: 复习入口 banner (amber-gold 强调, 待复习>0 才显示) -->
      <div
        v-if="reviewStats.total_due > 0"
        class="vocab-review-banner"
        @click="goReview"
        role="button"
        tabindex="0"
        @keydown.enter="goReview"
        :aria-label="`今日待复习 ${reviewStats.total_due} 词, 点击开始复习`"
      >
        <div class="banner-icon-wrap">
          <Flame :size="22" :stroke-width="2.5" />
        </div>
        <div class="banner-content">
          <div class="banner-title">今日待复习 {{ reviewStats.total_due }} 词</div>
          <div class="banner-desc">开始复习，巩固记忆</div>
        </div>
        <div class="banner-arrow">→</div>
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <!-- 5-P0-3: 搜索框 (行内, 单词模糊搜索) -->
        <div class="filter-search">
          <SfInput
            v-model="searchKeyword"
            placeholder="搜索单词 (例: run)"
            clearable
            :maxlength="50"
          >
            <template #prefix>
              <Search :size="16" />
            </template>
          </SfInput>
        </div>

        <div class="filter-row">
          <!-- 5-P2-3: 语料 Combobox (可搜索, 语料多了下拉不好找) -->
          <div class="filter-section">
            <span class="filter-label">来源：</span>
            <SfCombobox
              v-model="filterMaterialId"
              :options="materialsList.map(m => ({ value: m.id, label: m.title }))"
              placeholder="全部语料 (可搜索)"
              :display-value="filterMaterialTitle"
              class="filter-combobox"
            />
          </div>

          <!-- 排序 -->
          <div class="filter-section">
            <span class="filter-label">排序：</span>
            <SfSelect v-model="sortBy" :options="[
              { value: 'starred_first', label: '⭐ 星标优先' },
              { value: 'next_review_asc', label: '🔥 最该复习' },
              { value: 'newest', label: '最近添加' },
              { value: 'oldest', label: '最早添加' },
              { value: 'word_asc', label: 'A → Z' },
              { value: 'word_desc', label: 'Z → A' },
              { value: 'next_review_desc', label: '最不急' },
              { value: 'review_count', label: '复习最多' }
            ]" />
          </div>

          <span class="filter-total" v-if="total > 0">共 {{ total }} 词</span>
        </div>

        <!-- 掌握状态筛选 -->
        <div class="filter-chips">
          <FilterChip
            :model-value="filterStatus"
            value="all"
            label="全部"
            @update:model-value="setFilter"
          />
          <FilterChip
            :model-value="filterStatus"
            value="learning"
            label="学习中"
            @update:model-value="setFilter"
          />
          <FilterChip
            :model-value="filterStatus"
            value="mastered"
            label="已掌握"
            @update:model-value="setFilter"
          />
          <!-- 4-P1-3: 新词独立筛选 (review_count=0) -->
          <FilterChip
            :model-value="filterStatus"
            value="new"
            label="新词"
            @update:model-value="setFilter"
          />
          <!-- 5-P0-5: 待复习 chip (next_review_at <= now, 未 mastered) -->
          <FilterChip
            :model-value="filterStatus"
            value="due"
            :label="`待复习 (${reviewStats.total_due})`"
            @update:model-value="setFilter"
          />
        </div>
      </div>

      <!-- 5-P0-4: 批量操作浮动工具栏 (选中>0 才显示, sticky 顶部) -->
      <transition name="vocab-batch-bar">
        <div v-if="batchMode && selectedIds.size > 0" class="vocab-batch-bar">
          <span class="vocab-batch-count">
            已选 <strong>{{ selectedIds.size }}</strong> / {{ total }} 词
          </span>
          <SfButton size="sm" type="ghost" @click="selectAllOnPage">
            <CheckCheck :size="14" /> 全选当前页
          </SfButton>
          <SfButton size="sm" type="ghost" @click="clearSelection">
            <X :size="14" /> 清空
          </SfButton>
          <SfButton size="sm" type="primary" @click="batchMaster">
            <Check :size="14" /> 标记掌握
          </SfButton>
          <SfButton size="sm" type="warning" @click="batchUnmaster">
            <RotateCcw :size="14" /> 取消掌握
          </SfButton>
          <SfButton size="sm" type="primary" @click="batchStar">
            <Star :size="14" /> 标记重点
          </SfButton>
          <SfButton size="sm" type="ghost" @click="batchUnstar">
            <Star :size="14" /> 取消重点
          </SfButton>
          <SfButton size="sm" type="danger" @click="batchDelete">
            <Trash2 :size="14" /> 删除
          </SfButton>
        </div>
      </transition>

      <div :class="['vocab-list', { 'vocab-list-list-mode': viewMode === 'list' }]" v-loading="loading">
        <TransitionGroup name="vocab-card" tag="div" class="vocab-list-inner">
        <div
          v-for="(item, index) in vocabularies"
          :key="item.id"
          :style="{ '--vocab-stagger': index * 30 + 'ms' }"
          :class="['vocab-card', {
            'vocab-mastered': item.mastered,
            'vocab-learning': !item.mastered && item.review_count > 0,
            'vocab-new': !item.mastered && item.review_count === 0,
            'vocab-selected': batchMode && selectedIds.has(item.id),
            'vocab-focused': focusedIndex === index
          }]"
        >
          <!-- 状态色条 -->
          <div class="vocab-status-bar" :class="item.mastered ? 'status-mastered' : (item.review_count > 0 ? 'status-review' : 'status-new')"></div>

          <!-- 5-P0-4: 批量模式 checkbox (卡片左上角, status-bar 旁边) -->
          <label v-if="batchMode" class="vocab-checkbox" @click.stop>
            <input
              type="checkbox"
              :checked="selectedIds.has(item.id)"
              @change="toggleSelect(item.id)"
              :aria-label="`选择 ${item.word}`"
            />
          </label>

          <div class="vocab-card-inner">
            <!-- 单词头部 -->
            <div class="vocab-card-top">
              <div class="vocab-word-area">
                <div class="vocab-word-row" @click="speakText(item.word)">
                  <span class="vocab-word">{{ item.word }}</span>
                </div>
                <!-- 查询到的音标 (5-P2-2: lookup 失败显示 '?' tooltip) -->
                <div
                  :class="['vocab-phonetic', { 'lookup-failed': isLookupFailed(item.word) }]"
                  v-if="getWordInfo(item.word)?.phonetic || isLookupAttempted(item.word)"
                >
                  <span v-if="getWordInfo(item.word)?.phonetic">/{{ getWordInfo(item.word).phonetic }}/</span>
                  <span v-else-if="isLookupFailed(item.word)" title="单词查询失败, 点击重试" @click.stop="retryLookup(item.word)">? 重试</span>
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
                <!-- 4-P1-2: 下次复习时间徽标 (SM-2 算法产出) -->
                <SfTag
                  v-if="!item.mastered && getNextReviewInfo(item.next_review_at)"
                  size="sm"
                  :type="getNextReviewInfo(item.next_review_at).type"
                  :aria-label="`下次复习: ${getNextReviewInfo(item.next_review_at).label}`"
                >
                  {{ getNextReviewInfo(item.next_review_at).label }}
                </SfTag>
                <!-- 4-P1-2: 复习难度星标 (ease_factor 2.5 -> 3 星) -->
                <span
                  v-if="item.review_count > 0 && item.ease_factor !== undefined"
                  class="vocab-difficulty"
                  :title="`难度 ${item.ease_factor.toFixed(2)} (越高越简单)`"
                  :aria-label="`难度 ${item.ease_factor.toFixed(2)}`"
                >
                  <span class="vocab-difficulty-stars">{{ getDifficultyStars(item.ease_factor) }}</span>
                </span>
                <SfTag
                  v-if="item.review_count > 0"
                  size="sm"
                  type="default"
                >
                  复习 {{ item.review_count }} 次
                </SfTag>
              </div>
            </div>

            <!-- 查询到的翻译 (5-P2-2: 失败显示 '?') -->
            <div
              :class="['vocab-translation', { 'lookup-failed': isLookupFailed(item.word) }]"
              v-if="showChinese && (getWordInfo(item.word)?.translation || isLookupFailed(item.word))"
              :title="isLookupFailed(item.word) ? '单词查询失败, 点击重试' : ''"
              @click.stop="isLookupFailed(item.word) && retryLookup(item.word)"
            >
              <span v-if="getWordInfo(item.word)?.translation">{{ getWordInfo(item.word).translation }}</span>
              <span v-else-if="isLookupFailed(item.word)">? 翻译查询失败</span>
            </div>

            <!-- 5-P2-1: 例句 (lookup cache 的 example 字段, 之前从未渲染过) -->
            <div class="vocab-example" v-if="showChinese && getWordInfo(item.word)?.example">
              <span class="example-label">例句</span>
              <span class="example-text">「{{ getWordInfo(item.word).example }}」</span>
            </div>

            <!-- 复习进度可视化 -->
            <div class="vocab-progress-row" v-if="item.review_count > 0">
              <!-- 4-P1-1: 删 mastery-ring (进度环), 保留 review-strength bar (颜色低/中/高更直观) -->
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

            <!-- 5-P1-7: 原句 (引文) - 左 border 引用条样式 -->
            <div class="vocab-context-area" v-if="item.context">
              <div class="vocab-context" @click="speakText(item.context)">
                <span class="context-label">原句</span>
                <span class="context-text">「{{ item.context }}」</span>
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
              <!-- 5-P2-5: 星标按钮 (amber-gold 实心/空心) -->
              <button
                :class="['star-btn', { 'starred': item.starred }]"
                @click.stop="toggleStar(item)"
                :title="item.starred ? '取消重点' : '标记重点'"
                :aria-label="item.starred ? `取消 ${item.word} 的重点标记` : `将 ${item.word} 标记为重点`"
              >
                <Star :size="16" :fill="item.starred ? 'currentColor' : 'none'" />
              </button>
              <!-- 5-P0-2: 单词点击查释义 (替代 '查询发音' 按钮) -->
              <SfButton
                type="primary"
                size="sm"
                @click="lookupAndSpeak(item.word)"
                :loading="lookupLoading[item.word]"
                title="查释义: 未缓存时走 lookup API, 已缓存时直接朗读"
              >
                <Headphones :size="14" /> 查释义
              </SfButton>
              <SfButton
                v-if="!item.mastered"
                type="brand"
                size="sm"
                @click="markMastered(item.id)"
              >
                标记掌握
              </SfButton>
              <!-- 5-P0-1: 已掌握项 '移出' 改 '取消掌握', 调 unmark 端点 (保留 SM-2 历史) -->
              <SfButton
                v-if="item.mastered"
                type="ghost"
                size="sm"
                @click="unmarkVocab(item.id)"
              >
                取消掌握
              </SfButton>
              <SfButton
                v-if="!item.mastered"
                type="danger"
                size="sm"
                @click="deleteVocab(item)"
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
        </TransitionGroup>
      </div>

      <!-- 分页 (5-P2-7: 无限滚动模式时隐藏) -->
      <div class="pagination" v-if="total > 0 && !infiniteScrollMode">
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
        <SfPagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @change="loadVocabularies"
        />
      </div>

      <!-- 5-P2-7: 无限滚动 sentinel + 加载状态 (滚到底时 observer 触发 loadMore) -->
      <div v-if="infiniteScrollMode" ref="loadMoreSentinel" class="vocab-load-more-sentinel">
        <div v-if="loading && vocabularies.length > 0" class="vocab-loading-more">
          <SfSpinner :size="20" /> 加载中…
        </div>
        <div v-else-if="vocabularies.length >= total" class="vocab-all-loaded">
          ✓ 已加载全部 {{ total }} 词
        </div>
        <div v-else class="vocab-scroll-hint">
          ↓ 继续滚动加载更多
        </div>
      </div>

      <!-- 5-P2-6: 键盘快捷键提示 (右下角悬浮) -->
      <div class="vocab-kbd-hint" aria-label="键盘快捷键">
        <span><kbd>j</kbd>/<kbd>k</kbd> 上下</span>
        <span><kbd>m</kbd> 掌握</span>
        <span><kbd>u</kbd> 取消</span>
        <span><kbd>d</kbd> 删除</span>
        <span><kbd>↵</kbd> 朗读</span>
        <span><kbd>Esc</kbd> 退出</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { useTTS } from '@/composables/useTTS'
import { showConfirm } from '@/composables/useConfirm'
import { Headphones, Play, Flame, Search, X, CheckSquare, Square, CheckCheck, Check, RotateCcw, Trash2, Download, FileJson, FileText, LayoutGrid, Rows3, Star, Infinity as InfinityIcon, ListOrdered } from 'lucide-vue-next'
import SfSwitch from '@/components/ui/SfSwitch.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfCombobox from '@/components/ui/SfCombobox.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'
import SfButton from '@/components/ui/SfButton.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import SfSpinner from '@/components/ui/SfSpinner.vue'
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
// 5-P0-6: 从 localStorage 恢复 (回退默认 true)
try {
  const stored = localStorage.getItem('vocab-show-chinese')
  if (stored !== null) showChinese.value = stored === 'true'
} catch (e) { /* localStorage 不可用时忽略 */ }
// 5-P0-6: 持久化
watch(showChinese, (val) => {
  try { localStorage.setItem('vocab-show-chinese', String(val)) } catch (e) { /* ignore */ }
})

// 5-P1-5: 视图模式 ('card' | 'list'), 列表模式隐藏翻译/进度/语境, 提升密度
const viewMode = ref('card')
try {
  const stored = localStorage.getItem('vocab-view-mode')
  if (stored === 'list' || stored === 'card') viewMode.value = stored
} catch (e) { /* ignore */ }
watch(viewMode, (val) => {
  try { localStorage.setItem('vocab-view-mode', val) } catch (e) { /* ignore */ }
})
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'card' ? 'list' : 'card'
}

const filterStatus = ref('all')  // 4-P1-3: 'all'/'learning'/'mastered'/'new' (原 filterMastered bool 升级为 string)

// 5-P2-7: 无限滚动模式 (与分页互斥, 默认分页)
const infiniteScrollMode = ref(false)
try {
  const stored = localStorage.getItem('vocab-infinite-scroll')
  if (stored !== null) infiniteScrollMode.value = stored === 'true'
} catch (e) { /* ignore */ }
watch(infiniteScrollMode, (val) => {
  try { localStorage.setItem('vocab-infinite-scroll', String(val)) } catch (e) { /* ignore */ }
  // 切换模式时重置页码并刷新
  currentPage.value = 1
  loadVocabularies()
})

// 5-P0-4: 批量操作状态
const batchMode = ref(false)
const selectedIds = ref(new Set())

// 5-P2-6: 键盘快捷键焦点索引 (j/k 上下移动)
// batchMode=false 时单个聚焦, batchMode=true 时多选切换
const focusedIndex = ref(-1)

// 5-P2-7: 无限滚动 sentinel ref + IntersectionObserver
const loadMoreSentinel = ref(null)
let loadMoreObserver = null
const filterMaterialId = ref(null)
const sortBy = ref('newest')
const materialsList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 5-P2-3: 当前选中的语料标题 (用于 combobox 显示)
const filterMaterialTitle = computed(() => {
  if (!filterMaterialId.value) return ''
  return materialsList.value.find(m => m.id === filterMaterialId.value)?.title || ''
})

// 5-P0-3: 单词模糊搜索 (前端 debounce 300ms, 推送给后端 ?keyword=)
const searchKeyword = ref('')

// 5-P0-5: 复习统计 (banner + 待复习 chip 都用)
const reviewStats = ref({ total_due: 0, total_learning: 0, total_mastered: 0 })

// 单词查询缓存
const wordInfoCache = reactive({})
const lookupLoading = reactive({})
// 5-P2-2: 跟踪 lookup 失败 (key=word.toLowerCase(), value=true 时表示失败)
// 失败的卡片显示 '? 重试', 点击可手动 retry
const lookupFailed = reactive({})
// 5-P2-2: 跟踪是否已尝试 lookup (成功的不会有 phonetic 但也不显示 '?')
const lookupAttempted = reactive({})

const getWordInfo = (word) => wordInfoCache[word.toLowerCase()]
const isLookupFailed = (word) => lookupFailed[word.toLowerCase()] === true
const isLookupAttempted = (word) => lookupAttempted[word.toLowerCase()] === true

const retryLookup = async (word) => {
  const key = word.toLowerCase()
  delete lookupFailed[key]
  await lookupWordSilent(word)
}

// 加载语料列表（用于筛选）
const loadMaterialsList = async () => {
  try {
    const result = await materialAPI.getList({ page_size: 100 })
    materialsList.value = result.items || []
  } catch (e) {
    console.error('加载语料列表失败', e)
  }
}

const loadVocabularies = async ({ append = false } = {}) => {
  if (!userStore.isLoggedIn) return
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: sortBy.value
    }
    if (filterStatus.value === 'mastered') {
      params.mastered = true
    } else if (filterStatus.value === 'learning') {
      params.mastered = false
    } else if (filterStatus.value === 'new') {
      // 4-P1-3: 新词 = review_count=0
      params.is_new = true
    } else if (filterStatus.value === 'due') {
      // 5-P0-5: 待复习 (next_review_at <= now, 未 mastered)
      params.is_due = true
    }
    // 'all' 不加任何 filter
    if (filterMaterialId.value) {
      params.material_id = filterMaterialId.value
    }
    // 5-P0-3: 单词模糊搜索
    const kw = searchKeyword.value.trim()
    if (kw) {
      params.keyword = kw
    }
    const res = await vocabularyAPI.getList(params)
    // 5-P2-7: append=true 时拼接到现有列表 (无限滚动), 否则替换
    if (append) {
      vocabularies.value = [...vocabularies.value, ...(res.items || [])]
    } else {
      vocabularies.value = res.items || []
    }
    total.value = res.total || 0

    // 5-P0-5: 列表刷新后, 顺手刷新复习统计 (banner + chip 同步)
    await loadReviewStats()

    // 不再批量预查 10 个词，改为用户点击时才查（省 API 调用）
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
  }
}

// 5-P2-7: 无限滚动加载下一页
const loadMore = async () => {
  if (!infiniteScrollMode.value) return
  if (vocabularies.value.length >= total.value) return  // 已加载完
  if (loading.value) return  // 防并发
  currentPage.value += 1
  await loadVocabularies({ append: true })
}

// 5-P0-5: 加载复习统计 (banner + 待复习 chip 用)
const loadReviewStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const result = await vocabularyAPI.getReviewStats()
    reviewStats.value = {
      total_due: result.total_due || 0,
      total_learning: result.total_learning || 0,
      total_mastered: result.total_mastered || 0
    }
  } catch (e) {
    console.error('加载复习统计失败', e)
  }
}

// 5-P0-5: 跳转到复习页
const goReview = () => {
  router.push('/vocabulary-review')
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
    lookupAttempted[key] = true
    // 成功后清除失败标记
    if (lookupFailed[key]) delete lookupFailed[key]
  } catch (e) {
    // 5-P2-2: 不再静默, 标记失败让前端显示 '? 重试'
    console.warn(`lookup failed for "${word}":`, e.message)
    lookupAttempted[key] = true
    lookupFailed[key] = true
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

// 5-P0-3: 搜索框 debounce 300ms (输入停止 300ms 后再请求, 避免每按一键打一次 API)
let searchDebounceTimer = null
watch(searchKeyword, () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
    loadVocabularies()
  }, 300)
})

// 格式化相对时间
const formatRelativeTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days} 天前`
  if (days < 30) return `${Math.floor(days / 7)} 周前`
  return `${Math.floor(days / 30)} 个月前`
}

// 4-P1-2: 下次复习时间显示 (SM-2 算法产出 next_review_at)
// 返回 {label, type, daysDiff}, type 用于徽标颜色:
// - danger: 已过期 N 天 (红色, 立即复习)
// - warning: 今天到期 (橙色, 紧迫)
// - normal: 未来 X 天 (灰色, 计划)
// - null: 不显示 (已掌握或未复习过)
const getNextReviewInfo = (nextReviewAt) => {
  if (!nextReviewAt) return null
  const due = new Date(nextReviewAt)
  due.setHours(0, 0, 0, 0)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const diffMs = due.getTime() - today.getTime()
  const daysDiff = Math.round(diffMs / (1000 * 60 * 60 * 24))

  if (daysDiff < 0) {
    return { label: `已过期 ${-daysDiff} 天`, type: 'danger', daysDiff }
  }
  if (daysDiff === 0) {
    return { label: '今天复习', type: 'warning', daysDiff }
  }
  if (daysDiff === 1) {
    return { label: '明天复习', type: 'normal', daysDiff }
  }
  if (daysDiff <= 7) {
    return { label: `${daysDiff} 天后`, type: 'normal', daysDiff }
  }
  return { label: `${daysDiff} 天后`, type: 'normal', daysDiff }
}

// 4-P1-2: 难度星标 (ease_factor 1.3-3.0 映射到 1-5 星)
// SM-2: ease_factor < 1.5 = 困难, 1.5-2.0 = 较难, 2.0-2.5 = 一般, > 2.5 = 简单
const getDifficultyStars = (easeFactor) => {
  const ef = Number(easeFactor) || 2.5
  if (ef < 1.5) return '★☆☆☆☆'
  if (ef < 2.0) return '★★☆☆☆'
  if (ef < 2.5) return '★★★☆☆'
  if (ef < 3.0) return '★★★★☆'
  return '★★★★★'
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

// 5-P0-1: 取消掌握 (toggle mastered=False, 保留 SM-2 历史)
const unmarkVocab = async (id) => {
  try {
    await vocabularyAPI.unmarkMastered(id)
    toast.success('已取消掌握, 重新进入学习中')
    loadVocabularies()
  } catch (e) {
    console.error('取消掌握失败', e)
  }
}

// ==================== 5-P2-5: 词汇星标 ====================
const toggleStar = async (item) => {
  try {
    if (item.starred) {
      await vocabularyAPI.unstar(item.id)
      item.starred = false
      // toast.success('已取消重点')
    } else {
      await vocabularyAPI.star(item.id)
      item.starred = true
      // toast.success('已标记重点')
    }
    // 不调 toast, 避免频繁点击时弹窗爆炸; UI 已即时反馈 (图标实心/空心)
  } catch (e) {
    console.error('星标操作失败', e)
    toast.error('星标操作失败')
  }
}

const deleteVocab = async (item) => {
  const confirmed = await showConfirm({ title: '确认删除', message: '确定要删除该生词吗？' })
  if (confirmed) {
    // 4-P1-6: Undo 撤销 (保存原数据, 5s 内可点撤销按钮恢复)
    const backup = { ...item }
    try {
      await vocabularyAPI.delete(item.id)
      // 刷新列表前, 先弹撤销 toast
      toast.withAction(
        '已删除',
        {
          label: '撤销',
          onClick: async () => {
            try {
              // 重新创建 (material/subtitle 关联恢复; SM-2 + translation 字段丢失 - 用户刚加的词影响极小)
              await vocabularyAPI.add({
                word: backup.word,
                context: backup.context,
                material_id: backup.material_id,
                subtitle_id: backup.subtitle_id
              })
              toast.success('已恢复')
            } catch (e) {
              toast.error('恢复失败, 请重新添加')
              console.error('undo delete failed:', e)
            }
            loadVocabularies()
          }
        },
        { type: 'success', duration: 5000 }
      )
      loadVocabularies()
    } catch (e) {
      console.error('删除失败', e)
      toast.error('删除失败')
    }
  }
}

// ==================== 5-P0-4: 词汇批量操作 ====================
const toggleBatchMode = () => {
  batchMode.value = !batchMode.value
  if (!batchMode.value) {
    // 退出批量模式时清空选择
    selectedIds.value = new Set()
  }
}

const toggleSelect = (id) => {
  const next = new Set(selectedIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  selectedIds.value = next
}

const selectAllOnPage = () => {
  const next = new Set(selectedIds.value)
  for (const v of vocabularies.value) {
    next.add(v.id)
  }
  selectedIds.value = next
}

const clearSelection = () => {
  selectedIds.value = new Set()
}

const batchMaster = async () => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return
  try {
    const res = await vocabularyAPI.batchMaster(ids)
    toast.success(res.message || `已标记 ${ids.length} 词为已掌握`)
    clearSelection()
    loadVocabularies()
    loadReviewStats()  // 复习统计可能变化 (已掌握不算待复习)
  } catch (e) {
    console.error('批量标记失败', e)
    toast.error('批量标记失败')
  }
}

const batchUnmaster = async () => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return
  try {
    const res = await vocabularyAPI.batchUnmaster(ids)
    toast.success(res.message || `已取消 ${ids.length} 词的掌握状态`)
    clearSelection()
    loadVocabularies()
    loadReviewStats()
  } catch (e) {
    console.error('批量取消失败', e)
    toast.error('批量取消失败')
  }
}

// 5-P2-5: 批量星标 / 取消星标
const batchStar = async () => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return
  try {
    const res = await vocabularyAPI.batchStar(ids)
    toast.success(res.message || `已标记 ${ids.length} 词为重点`)
    clearSelection()
    loadVocabularies()
  } catch (e) {
    console.error('批量星标失败', e)
    toast.error('批量星标失败')
  }
}

const batchUnstar = async () => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return
  try {
    const res = await vocabularyAPI.batchUnstar(ids)
    toast.success(res.message || `已取消 ${ids.length} 词的重点`)
    clearSelection()
    loadVocabularies()
  } catch (e) {
    console.error('批量取消星标失败', e)
    toast.error('批量取消星标失败')
  }
}

const batchDelete = async () => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return
  const confirmed = await showConfirm({
    title: '批量删除',
    message: `确定要删除选中的 ${ids.length} 个生词？此操作不可撤销。`
  })
  if (!confirmed) return
  try {
    const res = await vocabularyAPI.batchDelete(ids)
    toast.success(res.message || `已删除 ${ids.length} 词`)
    clearSelection()
    loadVocabularies()
    loadReviewStats()
  } catch (e) {
    console.error('批量删除失败', e)
    toast.error('批量删除失败')
  }
}

// ==================== 5-P1-4: 词汇导出 ====================
const exportVocabulary = async (format) => {
  // 共享当前 filter (与 /vocabulary 列表一致: 搜索/语料/掌握状态都带上)
  const params = { format }
  if (filterMaterialId.value) {
    params.material_id = filterMaterialId.value
  }
  if (filterStatus.value === 'mastered') {
    params.mastered = true
  } else if (filterStatus.value === 'learning') {
    params.mastered = false
  } else if (filterStatus.value === 'new') {
    params.is_new = true
  } else if (filterStatus.value === 'due') {
    params.is_due = true
  }
  const kw = searchKeyword.value.trim()
  if (kw) params.keyword = kw

  try {
    const blob = await vocabularyAPI.export(params)
    // 从 Content-Disposition 拿后端给的文件名
    const disposition = blob.headers?.['content-disposition'] || ''
    const match = disposition.match(/filename="?([^";]+)"?/)
    const filename = match?.[1] || `vocabulary.${format}`

    // 触发浏览器下载
    const url = URL.createObjectURL(blob.data)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.success(`已导出 ${vocabularies.value.length} 词为 ${format.toUpperCase()}`)
  } catch (e) {
    console.error('导出失败', e)
    toast.error('导出失败')
  }
}

// ==================== 5-P2-6: 键盘快捷键 ====================
const handleKeyboard = (e) => {
  // 输入框/textarea 中不拦截
  const tag = e.target.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || e.target.isContentEditable) return
  // 修饰键不拦截 (Ctrl+J 是浏览器快捷键)
  if (e.ctrlKey || e.metaKey || e.altKey) return

  const list = vocabularies.value
  if (!list || list.length === 0) return

  switch (e.key.toLowerCase()) {
    case 'j':
    case 'arrowdown':
      e.preventDefault()
      focusedIndex.value = Math.min(focusedIndex.value + 1, list.length - 1)
      break
    case 'k':
    case 'arrowup':
      e.preventDefault()
      focusedIndex.value = Math.max(focusedIndex.value - 1, 0)
      break
    case 'm':
      // 标记当前 focus 为掌握
      if (focusedIndex.value >= 0 && focusedIndex.value < list.length) {
        const item = list[focusedIndex.value]
        if (!item.mastered) {
          e.preventDefault()
          markMastered(item.id)
        }
      }
      break
    case 'u':
      // 取消当前 focus 的掌握
      if (focusedIndex.value >= 0 && focusedIndex.value < list.length) {
        const item = list[focusedIndex.value]
        if (item.mastered) {
          e.preventDefault()
          unmarkVocab(item.id)
        }
      }
      break
    case 'd':
      // 删除当前 focus
      if (focusedIndex.value >= 0 && focusedIndex.value < list.length) {
        const item = list[focusedIndex.value]
        e.preventDefault()
        deleteVocab(item)
      }
      break
    case 'enter':
      // 查释义 + 朗读
      if (focusedIndex.value >= 0 && focusedIndex.value < list.length) {
        const item = list[focusedIndex.value]
        e.preventDefault()
        lookupAndSpeak(item.word)
      }
      break
    case 'escape':
      // 退出批量模式 / 清空焦点
      if (batchMode.value) {
        toggleBatchMode()
      } else {
        focusedIndex.value = -1
      }
      break
  }
}

// focusedIndex 变化时滚动到可视区域
watch(focusedIndex, () => {
  // 用 nextTick 等 DOM 更新
  setTimeout(() => {
    const el = document.querySelector('.vocab-focused')
    if (el && typeof el.scrollIntoView === 'function') {
      el.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, 50)
})

// 5-P2-7: 监听 sentinel DOM 变化 (模式切换 / 首次加载)
// onMounted 时 observer 还不存在, 用 watch 配合 nextTick
watch(loadMoreSentinel, (el) => {
  if (loadMoreObserver) {
    loadMoreObserver.disconnect()
    loadMoreObserver = null
  }
  if (el && infiniteScrollMode.value) {
    loadMoreObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && infiniteScrollMode.value) {
          loadMore()
        }
      },
      { rootMargin: '300px' }  // 提前 300px 触发, 体验更顺滑
    )
    loadMoreObserver.observe(el)
  }
})

onMounted(() => {
  preloadVoices()
  loadMaterialsList()
  loadVocabularies()
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboard)
  if (loadMoreObserver) {
    loadMoreObserver.disconnect()
    loadMoreObserver = null
  }
})
</script>

<style scoped>
/* ============================================
   Phase 1D — Vocabulary Redesign
   墨绿 #2563EB + 暖橙 #F59E0B + Noto Sans SC
   ============================================ */

.yt-vocabulary {
  max-width: 960px;
  margin: 0 auto;
}

/* ---- 5-P0-5: 复习入口 banner (amber-gold 强调卡) ---- */
.vocab-review-banner {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: var(--radius-lg, 16px);
  cursor: pointer;
  transition: transform var(--sf-duration-fast) var(--sf-ease-standard),
              box-shadow var(--sf-duration-fast) var(--sf-ease-standard);
  box-shadow: 0 1px 2px rgba(245, 158, 11, 0.08);
}
.vocab-review-banner:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
}
.vocab-review-banner:focus-visible {
  outline: 2px solid var(--color-accent, #F59E0B);
  outline-offset: 2px;
}
.vocab-review-banner:active {
  transform: translateY(0);
}

.banner-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(245, 158, 11, 0.35);
}

.banner-content {
  flex: 1;
  min-width: 0;
}

.banner-title {
  font-size: 15px;
  font-weight: 600;
  color: #92400E;
  margin-bottom: 2px;
}

.banner-desc {
  font-size: 13px;
  color: #B45309;
  font-weight: 500;
}

.banner-arrow {
  font-size: 22px;
  color: #D97706;
  flex-shrink: 0;
  transition: transform var(--sf-duration-fast) var(--sf-ease-standard);
}
.vocab-review-banner:hover .banner-arrow {
  transform: translateX(4px);
}

/* 暗色模式适配 */
:global(.dark) .vocab-review-banner {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.18) 0%, rgba(217, 119, 6, 0.22) 100%);
  border-color: rgba(245, 158, 11, 0.4);
}
:global(.dark) .banner-title {
  color: #FCD34D;
}
:global(.dark) .banner-desc {
  color: #FBBF24;
}
:global(.dark) .banner-arrow {
  color: #FCD34D;
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

/* 5-P0-3: 搜索框 - 上方独立行, 移动端宽度自适应 */
.filter-search {
  display: flex;
  width: 100%;
  max-width: 360px;
}
.filter-search :deep(.sf-input) {
  width: 100%;
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
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.1);
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
  background: var(--color-accent, #F59E0B);
}

.status-review {
  background: var(--color-brand, #2563EB);
}

.status-mastered {
  background: var(--color-success, #16A34A);
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
  transition: opacity var(--sf-duration-normal);
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
  color: var(--color-brand-bright);
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
  border-color: var(--color-brand-bright);
  color: var(--color-brand-bright);
  transform: scale(1.08);
}

.tts-btn:active {
  transform: scale(0.95);
}

/* ---- 状态标签组 ---- */
.vocab-status-group {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
  flex-shrink: 0;
}

/* 4-P1-2: SM-2 难度星标 (ease_factor) */
.vocab-difficulty {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  line-height: 1;
  letter-spacing: 1px;
}
.vocab-difficulty-stars {
  color: var(--color-brand-warm, #F59E0B);
  font-size: 12px;
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
  border-left: 3px solid var(--color-brand-bright);
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
  transition: width var(--sf-duration-slower) var(--ease-standard);
}

.strength-low {
  background: var(--color-accent, #F59E0B);
}

.strength-mid {
  background: var(--color-brand, #2563EB);
}

.strength-high {
  background: var(--color-success, #16A34A);
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

/* ---- 5-P1-7: 原句 (引用条) ---- */
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
  border-left: 3px solid var(--color-brand);  /* 5-P1-7: 引用条样式 */
  display: flex;
  align-items: flex-start;
  gap: 8px;
  transition: background var(--sf-duration-normal);
}

.vocab-context:hover {
  background: var(--color-brand-subtle);
}

.vocab-context:hover .speak-icon-small {
  opacity: 1;
  color: var(--color-brand-bright);
}

.context-label {
  color: var(--color-brand-bright);
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
  transition: all var(--sf-duration-normal);
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
  transition: all var(--sf-duration-normal) var(--ease-standard);
  border: 1px solid transparent;
}

.vocab-source:hover {
  background: var(--color-brand-subtle);
  color: var(--color-brand-bright);
  border-color: var(--color-border-brand, #93C5FD);
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

/* ==================== 5-P0-4: 批量操作 ==================== */
/* 选中状态卡片: 蓝色边框 + 浅蓝背景 */
.vocab-card.vocab-selected {
  outline: 2px solid var(--color-brand);
  outline-offset: -2px;
  background: rgba(37, 99, 235, 0.04);
}

/* 批量 checkbox: 卡片左上角, status-bar 旁边 */
.vocab-checkbox {
  position: absolute;
  top: 12px;
  left: 14px;  /* status-bar 4px + 间距 */
  z-index: 2;
  display: flex;
  align-items: center;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 4px;
  padding: 2px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}
.vocab-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-brand);
}

/* 批量模式时, vocab-card-inner 左 padding 让出 checkbox 位置 */
.vocab-card:has(.vocab-checkbox) .vocab-card-inner {
  padding-left: 40px;
}

/* 批量操作浮动工具栏 (sticky 顶部) */
.vocab-batch-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  margin-bottom: 14px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-brand);
  border-radius: 10px;
  position: sticky;
  top: 0;
  z-index: 5;
  flex-wrap: wrap;
}
.vocab-batch-count {
  font-size: 14px;
  color: var(--color-text-secondary, #475569);
  margin-right: 8px;
  flex-shrink: 0;
}
.vocab-batch-count strong {
  color: var(--color-brand);
  font-weight: 700;
  margin: 0 2px;
}

/* 工具栏显示/隐藏过渡 */
.vocab-batch-bar-enter-active,
.vocab-batch-bar-leave-active {
  transition: opacity var(--sf-duration-fast) var(--sf-ease-standard),
              transform var(--sf-duration-fast) var(--sf-ease-standard);
}
.vocab-batch-bar-enter-from,
.vocab-batch-bar-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* ==================== 5-P1-5: 列表模式 (高密度) ==================== */
.vocab-list-list-mode {
  display: flex;
  flex-direction: column;
  gap: 6px;  /* 卡片间距缩小 */
}
/* 列表模式: 卡片水平布局, 紧凑 */
.vocab-list-list-mode .vocab-card {
  display: flex;
  align-items: center;
  padding: 0;
  min-height: 56px;
}
.vocab-list-list-mode .vocab-status-bar {
  position: relative;  /* 列表模式改为左侧窄条 (不再 absolute) */
  width: 4px;
  height: 100%;
  align-self: stretch;
  border-radius: 0;
}
.vocab-list-list-mode .vocab-card-inner {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
}
/* 列表模式: 单词区占主体 */
.vocab-list-list-mode .vocab-card-top {
  flex: 1;
  min-width: 0;  /* 允许 truncation */
}
.vocab-list-list-mode .vocab-word-area {
  display: flex;
  align-items: center;
  gap: 10px;
}
.vocab-list-list-mode .vocab-word-row {
  margin: 0;
}
.vocab-list-list-mode .vocab-word {
  font-size: 18px;
}
.vocab-list-list-mode .vocab-phonetic {
  font-size: 12px;
  color: var(--color-text-tertiary, #94a3b8);
}
.vocab-list-list-mode .vocab-phonetic::before {
  content: '/';
}
.vocab-list-list-mode .vocab-phonetic::after {
  content: '/';
}
/* 列表模式: 隐藏详情区 (翻译/进度/语境/来源) */
.vocab-list-list-mode .vocab-translation,
.vocab-list-list-mode .vocab-progress-row,
.vocab-list-list-mode .vocab-context-area,
.vocab-list-list-mode .vocab-card-footer,
.vocab-list-list-mode .tts-btn {
  display: none;
}
/* 列表模式: 状态标签紧凑 */
.vocab-list-list-mode .vocab-status-group {
  display: flex;
  gap: 4px;
  align-items: center;
}
/* 列表模式: 操作按钮行, 不换行 */
.vocab-list-list-mode .vocab-actions {
  flex-direction: row;
  gap: 4px;
  flex-shrink: 0;
}
.vocab-list-list-mode .vocab-actions :deep(.sf-btn) {
  padding: 4px 10px;
  font-size: 12px;
}
/* 列表模式 checkbox 不需要让出位置 */
.vocab-list-list-mode .vocab-card:has(.vocab-checkbox) .vocab-card-inner {
  padding-left: 50px;
}

/* ==================== 5-P1-4: 导出下拉菜单样式 ==================== */
.vocab-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-primary, #1e293b);
  transition: background var(--sf-duration-fast) var(--sf-ease-standard);
  white-space: nowrap;
}
.vocab-dropdown-item:hover {
  background: var(--color-bg-hover, rgba(37, 99, 235, 0.06));
}
.vocab-dropdown-item :deep(svg) {
  flex-shrink: 0;
  color: var(--color-text-secondary, #475569);
}

/* ==================== 5-P2-1: 例句样式 ==================== */
.vocab-example {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 6px;
  padding: 8px 12px;
  background: rgba(245, 158, 11, 0.04);
  border-left: 3px solid var(--color-accent, #F59E0B);
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.5;
}
.vocab-example .example-label {
  flex-shrink: 0;
  font-weight: 600;
  color: var(--color-accent, #F59E0B);
  font-size: 12px;
}
.vocab-example .example-text {
  color: var(--color-text-secondary, #475569);
  font-style: italic;
}

/* ==================== 5-P2-2: lookup 失败提示 ==================== */
.lookup-failed {
  color: var(--color-text-tertiary, #94a3b8);
  cursor: pointer;
  font-style: italic;
}
.lookup-failed:hover {
  color: var(--color-brand, #2563EB);
  text-decoration: underline;
}

/* ==================== 5-P2-4: 列表入场动画 (stagger) ==================== */
.vocab-list-inner {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.vocab-list-list-mode > .vocab-list-inner {
  gap: 6px;
}
/* 卡片入场动画 */
.vocab-card-enter-active {
  transition: opacity 280ms var(--sf-ease-standard),
              transform 280ms var(--sf-ease-standard);
  transition-delay: var(--vocab-stagger, 0ms);
}
.vocab-card-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.vocab-card-leave-active {
  transition: opacity 180ms var(--sf-ease-standard),
              transform 180ms var(--sf-ease-standard);
  position: absolute;  /* leave 时脱离布局 */
}
.vocab-card-leave-to {
  opacity: 0;
  transform: translateX(-12px);
}
.vocab-card-move {
  transition: transform 280ms var(--sf-ease-standard);
}

/* ==================== 5-P2-6: 键盘焦点高亮 ==================== */
.vocab-card.vocab-focused {
  outline: 2px dashed var(--color-brand, #2563EB);
  outline-offset: 2px;
  background: rgba(37, 99, 235, 0.02);
}
/* 列表模式: 焦点样式稍弱 (避免抢戏) */
.vocab-list-list-mode .vocab-card.vocab-focused {
  outline-offset: -1px;
}

/* 键盘快捷键提示 (右下角悬浮) */
.vocab-kbd-hint {
  position: fixed;
  bottom: 16px;
  right: 16px;
  padding: 8px 12px;
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  font-size: 11px;
  color: var(--color-text-secondary, #475569);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  z-index: 50;
  display: flex;
  gap: 8px;
  align-items: center;
}
.vocab-kbd-hint kbd {
  display: inline-block;
  padding: 1px 6px;
  background: var(--color-bg-hover, rgba(37, 99, 235, 0.06));
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 3px;
  font-family: ui-monospace, monospace;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-primary, #1e293b);
}

/* ==================== 5-P2-5: 星标按钮 ==================== */
.star-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--color-text-tertiary, #94a3b8);
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-standard);
}
.star-btn:hover {
  background: rgba(245, 158, 11, 0.08);
  color: #F59E0B;  /* amber-gold */
  transform: scale(1.08);
}
.star-btn:active {
  transform: scale(0.95);
}
/* 已星标: amber-gold 实心 */
.star-btn.starred {
  color: #F59E0B;
  background: rgba(245, 158, 11, 0.06);
}
.star-btn.starred:hover {
  background: rgba(245, 158, 11, 0.14);
}
/* 列表模式: star-btn 缩小尺寸 */
.vocab-list-list-mode .star-btn {
  width: 28px;
  height: 28px;
}

/* ==================== 5-P2-7: 无限滚动 sentinel ==================== */
.vocab-load-more-sentinel {
  padding: 24px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}
.vocab-loading-more {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary, #475569);
  font-size: 13px;
}
.vocab-all-loaded {
  color: var(--color-text-tertiary, #94a3b8);
  font-size: 12px;
  letter-spacing: 0.5px;
}
.vocab-scroll-hint {
  color: var(--color-text-tertiary, #94a3b8);
  font-size: 12px;
  animation: vocab-scroll-hint-pulse 2s ease-in-out infinite;
}
@keyframes vocab-scroll-hint-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
</style>
