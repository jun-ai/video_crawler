<template>
  <div class="yt-materials">
    <!-- 页面标题 + 工具栏 -->
    <div class="materials-header">
      <PageHeader title="语料库" subtitle="浏览所有学习材料" />

      <!-- 右上角工具栏 -->
      <div class="header-tools">
        <!-- 移动/平板端筛选按钮 -->
        <button
          class="filter-toggle-btn"
          :class="{ 'show-filter-btn': isMobileOrTablet }"
          @click="mobileFilterOpen = true"
        >
          <SlidersHorizontal :size="18" />
          <span v-if="activeFilterCount > 0" class="filter-badge">{{ activeFilterCount }}</span>
          筛选
          <span v-if="activeFilterCount > 0" class="filter-count">({{ activeFilterCount }})</span>
        </button>

        <!-- 搜索框 -->
        <div class="header-search">
          <SfInput
            v-model="searchQuery"
            placeholder="搜索标题或描述..."
            clearable
            @input="debounceSearch"
            @clear="clearSearch"
          >
            <template #prefix>
              <Search :size="16" />
            </template>
          </SfInput>
        </div>

        <!-- 视图切换 -->
        <div class="view-toggle">
          <button
            :class="['toggle-btn', { active: viewMode === 'grid' }]"
            @click="setViewMode('grid')"
            title="网格视图"
          >
            <LayoutGrid :size="18" />
          </button>
          <button
            :class="['toggle-btn', { active: viewMode === 'list' }]"
            @click="setViewMode('list')"
            title="列表视图"
          >
            <List :size="18" />
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容区域：内容 + 桌面端侧边栏 -->
    <div class="materials-body">
      <!-- 左侧内容 -->
      <div class="materials-content">
        <!-- 加载骨架 -->
        <ListSkeleton
          v-if="loading"
          :count="8"
          :list-mode="viewMode === 'list'"
          :class="viewMode === 'grid' ? 'grid-skeleton' : 'list-skeleton-wrap'"
        />

        <!-- 视频网格/列表 -->
        <div
          v-else-if="materials.length > 0"
          :class="['video-grid', { 'video-list': viewMode === 'list' }]"
        >
          <VideoCard
            v-for="item in materials"
            :key="item.id"
            :id="item.id"
            :title="item.title"
            :cover="item.cover_path"
            :duration="item.duration"
            :difficulty="item.difficulty"
            :view-count="item.view_count || 0"
            :category="item.category"
            :description="item.description"
            :tags="item.tags || []"
            :favorited="isMaterialFavorited(item.id)"
            :completed="isMaterialCompleted(item.id)"
            :progress="getProgress(item.id)"
            :layout="viewMode"
            @click="goLearn"
          />
        </div>

        <!-- 空状态 -->
        <EmptyState
          v-if="!loading && materials.length === 0"
          type="no-results"
          title="没有找到结果"
          description="换个关键词或筛选条件试试"
        >
          <template #actions>
            <SfButton @click="clearFilters">清除筛选</SfButton>
          </template>
        </EmptyState>

        <!-- 分页 -->
        <div class="pagination" v-if="!loading && total > pageSize">
          <SfPagination
            :current-page="page"
            :page-size="pageSize"
            :total="total"
            @change="handlePageChange"
          />
        </div>
      </div>

      <!-- 桌面端筛选侧边栏 -->
      <aside class="filter-sidebar" v-if="!isMobileOrTablet">
        <div class="sidebar-inner">
          <div class="sidebar-header">
            <h3 class="sidebar-title">
              <SlidersHorizontal :size="16" />
              筛选
            </h3>
            <button
              v-if="activeFilterCount > 0"
              class="clear-btn"
              @click="clearFilters"
            >
              清除全部
            </button>
          </div>

          <!-- 类别 -->
          <div class="filter-section">
            <h4 class="filter-section-title">场景</h4>
            <div class="filter-options">
              <button
                :class="['filter-option', { active: !filters.category }]"
                @click="selectCategory('')"
              >全部</button>
              <button
                v-for="(label, key) in categoryLabels"
                :key="key"
                :class="['filter-option', { active: filters.category === key }]"
                @click="selectCategory(key)"
              >{{ label }}</button>
            </div>
          </div>

          <!-- 难度 -->
          <div class="filter-section">
            <h4 class="filter-section-title">难度</h4>
            <div class="filter-options">
              <button
                :class="['filter-option', { active: !filters.difficulty }]"
                @click="selectDifficulty(0)"
              >全部</button>
              <button
                v-for="(label, level) in difficultyLabels"
                :key="level"
                :class="['filter-option', { active: filters.difficulty === Number(level) }]"
                @click="selectDifficulty(Number(level))"
              >
                <span
                  v-if="Number(level)"
                  class="difficulty-dot"
                  :style="{ background: difficultyColors[level] }"
                ></span>
                {{ label }}
              </button>
            </div>
          </div>

          <!-- 时长 -->
          <div class="filter-section">
            <h4 class="filter-section-title">时长</h4>
            <div class="filter-options">
              <button
                v-for="opt in durationOptions"
                :key="opt.value"
                :class="['filter-option', { active: filters.duration === opt.value }]"
                @click="selectDuration(opt.value)"
              >{{ opt.label }}</button>
            </div>
          </div>

          <!-- 标签 -->
          <div class="filter-section" v-if="allTags.length > 0">
            <h4 class="filter-section-title">标签</h4>
            <div class="filter-tags">
              <span
                v-for="tag in allTags.slice(0, 12)"
                :key="tag.id"
                :class="['sidebar-tag', { active: selectedTagId === tag.id }]"
                :style="selectedTagId === tag.id
                  ? { background: tag.color || 'var(--color-brand)', color: '#fff', borderColor: tag.color || 'var(--color-brand)' }
                  : { borderColor: tag.color || 'var(--color-border)', color: tag.color || 'var(--color-text-secondary)' }"
                @click="toggleTag(tag.id)"
              >{{ tag.name }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- 移动端筛选 Sheet -->
    <Sheet v-model:open="mobileFilterOpen">
      <SheetContent side="top" class="mobile-filter-sheet">
        <SheetHeader>
          <SheetTitle class="sheet-filter-title">
            <SlidersHorizontal :size="18" />
            筛选条件
            <span v-if="activeFilterCount > 0" class="filter-count-badge">{{ activeFilterCount }}</span>
          </SheetTitle>
        </SheetHeader>

        <div class="mobile-filter-body">
          <!-- 搜索 -->
          <div class="mobile-filter-section">
            <SfInput
              v-model="searchQuery"
              placeholder="搜索标题或描述..."
              clearable
              @input="debounceSearch"
              @clear="clearSearch"
            >
              <template #prefix>
                <Search :size="16" />
              </template>
            </SfInput>
          </div>

          <!-- 类别 -->
          <div class="mobile-filter-section">
            <h4 class="mobile-section-title">场景</h4>
            <div class="mobile-chips">
              <button
                :class="['mobile-chip', { active: !filters.category }]"
                @click="selectCategory('')"
              >全部</button>
              <button
                v-for="(label, key) in categoryLabels"
                :key="key"
                :class="['mobile-chip', { active: filters.category === key }]"
                @click="selectCategory(key)"
              >{{ label }}</button>
            </div>
          </div>

          <!-- 难度 -->
          <div class="mobile-filter-section">
            <h4 class="mobile-section-title">难度</h4>
            <div class="mobile-chips">
              <button
                :class="['mobile-chip', { active: !filters.difficulty }]"
                @click="selectDifficulty(0)"
              >全部</button>
              <button
                v-for="(label, level) in difficultyLabels"
                :key="level"
                :class="['mobile-chip', { active: filters.difficulty === Number(level) }]"
                @click="selectDifficulty(Number(level))"
              >
                <span
                  v-if="Number(level)"
                  class="difficulty-dot"
                  :style="{ background: difficultyColors[level] }"
                ></span>
                {{ label }}
              </button>
            </div>
          </div>

          <!-- 时长 -->
          <div class="mobile-filter-section">
            <h4 class="mobile-section-title">时长</h4>
            <div class="mobile-chips">
              <button
                v-for="opt in durationOptions"
                :key="opt.value"
                :class="['mobile-chip', { active: filters.duration === opt.value }]"
                @click="selectDuration(opt.value)"
              >{{ opt.label }}</button>
            </div>
          </div>

          <!-- 标签 -->
          <div class="mobile-filter-section" v-if="allTags.length > 0">
            <h4 class="mobile-section-title">标签</h4>
            <div class="mobile-tags-wrap">
              <span
                v-for="tag in allTags.slice(0, 12)"
                :key="tag.id"
                :class="['sidebar-tag', { active: selectedTagId === tag.id }]"
                :style="selectedTagId === tag.id
                  ? { background: tag.color || 'var(--color-brand)', color: '#fff', borderColor: tag.color || 'var(--color-brand)' }
                  : { borderColor: tag.color || 'var(--color-border)', color: tag.color || 'var(--color-text-secondary)' }"
                @click="toggleTag(tag.id)"
              >{{ tag.name }}</span>
            </div>
          </div>
        </div>

        <!-- 底部操作栏 -->
        <div class="mobile-filter-footer">
          <SfButton variant="ghost" @click="clearFilters" :disabled="activeFilterCount === 0">
            清除筛选
          </SfButton>
          <SfButton @click="mobileFilterOpen = false">
            查看结果 ({{ total }})
          </SfButton>
        </div>
      </SheetContent>
    </Sheet>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { LayoutGrid, List, SlidersHorizontal, Search } from 'lucide-vue-next'
import SfInput from '@/components/ui/SfInput.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import SfButton from '@/components/ui/SfButton.vue'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle
} from '@/components/ui/sheet'
import { materialAPI, tagsAPI, favoriteAPI, learningStatsAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import PageHeader from '@/components/common/PageHeader.vue'
import VideoCard from '@/components/common/VideoCard.vue'
import ListSkeleton from '@/components/common/ListSkeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// ====== 视图模式 ======
const isMobile = ref(window.innerWidth < 768)
const isMobileOrTablet = ref(window.innerWidth < 1024)
const defaultView = () => {
  const saved = localStorage.getItem('materials-view-mode')
  if (saved === 'grid' || saved === 'list') return saved
  return isMobile.value ? 'list' : 'grid'
}
const viewMode = ref(defaultView())

const setViewMode = (mode) => {
  viewMode.value = mode
  localStorage.setItem('materials-view-mode', mode)
}

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  isMobileOrTablet.value = window.innerWidth < 1024
}
onMounted(() => window.addEventListener('resize', handleResize))
onBeforeUnmount(() => window.removeEventListener('resize', handleResize))

// ====== 数据状态 ======
const loading = ref(false)
const materials = ref([])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const searchQuery = ref(route.query.keyword || '')

// 用户学习数据
const favoritedMaterialIds = ref(new Set())
const learningProgress = ref({})

// 筛选
const mobileFilterOpen = ref(false)

const filters = reactive({
  category: route.query.category || '',
  difficulty: 0,
  duration: '',
  keyword: route.query.keyword || ''
})

// 标签
const creatorTags = ref([])
const topicTags = ref([])
const selectedTagId = ref(null)

const allTags = computed(() => [...creatorTags.value, ...topicTags.value])

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.category) count++
  if (filters.difficulty) count++
  if (filters.duration) count++
  if (filters.keyword) count++
  if (selectedTagId.value) count++
  return count
})

// ====== 标签映射 ======
const categoryLabels = {
  travel: '旅行',
  shopping: '购物',
  social: '社交',
  work: '工作',
  daily: '日常',
  food: '餐饮'
}

const difficultyLabels = {
  1: '入门',
  2: '基础',
  3: '中级',
  4: '进阶',
  5: '高级'
}

const difficultyColors = {
  1: '#6FA386',
  2: '#0F4C3A',
  3: '#E2725B',
  4: '#C95E47',
  5: '#C73E3A'
}

const durationOptions = [
  { label: '全部', value: '' },
  { label: '< 3 分钟', value: 'short' },
  { label: '3-10 分钟', value: 'medium' },
  { label: '> 10 分钟', value: 'long' }
]

// ====== 筛选操作 ======
const selectCategory = (category) => {
  filters.category = filters.category === category ? '' : category
  page.value = 1
  loadMaterials()
}

const selectDifficulty = (difficulty) => {
  filters.difficulty = filters.difficulty === difficulty ? 0 : difficulty
  page.value = 1
  loadMaterials()
}

const selectDuration = (duration) => {
  filters.duration = filters.duration === duration ? '' : duration
  page.value = 1
  loadMaterials()
}

// 搜索
let searchTimer = null
const debounceSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    filters.keyword = searchQuery.value
    page.value = 1
    loadMaterials()
  }, 300)
}

const clearSearch = () => {
  searchQuery.value = ''
  filters.keyword = ''
  page.value = 1
  loadMaterials()
}

// 标签
const toggleTag = (tagId) => {
  selectedTagId.value = selectedTagId.value === tagId ? null : tagId
  page.value = 1
  loadMaterials()
}

const loadTags = async () => {
  try {
    const [creators, topics] = await Promise.all([
      tagsAPI.getList({ type: 'creator' }),
      tagsAPI.getList({ type: 'topic' })
    ])
    creatorTags.value = creators || []
    topicTags.value = topics || []
  } catch (e) {
    console.error('加载标签失败', e)
  }
}

const clearFilters = () => {
  filters.category = ''
  filters.difficulty = 0
  filters.duration = ''
  filters.keyword = ''
  searchQuery.value = ''
  selectedTagId.value = null
  page.value = 1
  loadMaterials()
}

// ====== 数据加载 ======
const loadMaterials = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.category) params.category = filters.category
    if (filters.difficulty) params.difficulty = filters.difficulty
    if (filters.keyword) params.keyword = filters.keyword
    if (selectedTagId.value) params.tag_id = selectedTagId.value
    if (filters.duration) params.duration_range = filters.duration

    const res = await materialAPI.getList(params)
    materials.value = res.items
    total.value = res.total
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
  }
}

const goLearn = (id) => {
  router.push(`/learn/${id}`)
}

const handlePageChange = (newPage) => {
  page.value = newPage
  loadMaterials()
}

// 加载用户收藏和学习进度
const loadUserStatus = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const [favRes, statsRes] = await Promise.all([
      favoriteAPI.getList({ page_size: 1000 }),
      learningStatsAPI.getRecords({ limit: 200 })
    ])
    favoritedMaterialIds.value = new Set((favRes.items || []).map(f => f.id))
    const progressMap = {}
    ;(statsRes.items || []).forEach(item => {
      progressMap[item.material_id] = item.progress || 0
    })
    learningProgress.value = progressMap
  } catch (e) {
    console.debug('加载用户状态失败', e)
  }
}

const isMaterialFavorited = (materialId) => favoritedMaterialIds.value.has(materialId)
const isMaterialCompleted = (materialId) => (learningProgress.value[materialId] || 0) >= 95
const getProgress = (materialId) => learningProgress.value[materialId] || 0

onMounted(() => {
  loadMaterials()
  loadTags()
  loadUserStatus()
})
</script>

<style scoped>
/* ====== 页面容器 ====== */
.yt-materials {
  max-width: 1800px;
  margin: 0 auto;
}

/* ====== 顶部区域 ====== */
.materials-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.materials-header :deep(.page-header) {
  margin-bottom: 0;
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.header-search {
  width: 200px;
}

.header-search :deep(.sf-input-wrap) {
  border-radius: var(--radius-full, 9999px);
  background: var(--color-bg-elevated);
  box-shadow: none;
}

.header-search :deep(.sf-input-wrap:hover) {
  box-shadow: 0 0 0 1px var(--color-border) inset;
}

/* ====== 视图切换 ====== */
.view-toggle {
  display: flex;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md, 12px);
  padding: 3px;
  gap: 2px;
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.toggle-btn:hover {
  color: var(--color-text-secondary);
  background: var(--color-bg-card);
}

.toggle-btn.active {
  background: var(--color-bg-card);
  color: var(--color-brand);
  box-shadow: var(--shadow-sm);
}

/* ====== 移动端筛选按钮 ====== */
.filter-toggle-btn {
  display: none;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  border-radius: var(--radius-md, 12px);
  font-size: 14px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.filter-toggle-btn.show-filter-btn {
  display: flex;
}

.filter-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 18px;
  height: 18px;
  background: var(--color-accent);
  color: #fff;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-count {
  font-size: 12px;
  color: var(--color-brand);
  font-weight: 500;
}

/* ====== 主体布局 ====== */
.materials-body {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.materials-content {
  flex: 1;
  min-width: 0;
}

/* ====== 视频网格 ====== */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.video-grid.video-list {
  grid-template-columns: 1fr;
  gap: 12px;
}

/* ====== 桌面端筛选侧边栏 ====== */
.filter-sidebar {
  width: 260px;
  flex-shrink: 0;
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.sidebar-inner {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 16px);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.clear-btn {
  font-size: 12px;
  color: var(--color-accent);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm, 8px);
  transition: background 0.15s;
}

.clear-btn:hover {
  background: var(--color-accent-subtle);
}

/* 筛选区块 */
.filter-section {
  margin-bottom: 20px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 14px;
  border-radius: var(--radius-sm, 8px);
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
  width: 100%;
}

.filter-option:hover {
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
}

.filter-option.active {
  background: var(--color-brand-subtle);
  color: var(--color-brand);
  font-weight: 500;
}

.difficulty-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 侧边栏标签 */
.filter-tags,
.mobile-tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sidebar-tag {
  padding: 4px 12px;
  border-radius: var(--radius-full, 9999px);
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.sidebar-tag:hover {
  filter: brightness(0.9);
  transform: translateY(-1px);
}

.sidebar-tag.active {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

/* ====== 分页 ====== */
.pagination {
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

/* ====== 移动端筛选 Sheet ====== */
.mobile-filter-sheet {
  max-height: 85vh;
  border-radius: 0 0 var(--radius-xl, 24px) var(--radius-xl, 24px) !important;
  padding: 0 !important;
}

.sheet-filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}

.filter-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: var(--color-accent);
  color: #fff;
  border-radius: var(--radius-full, 9999px);
  font-size: 12px;
  font-weight: 600;
}

.mobile-filter-body {
  padding: 0 20px;
  max-height: 55vh;
  overflow-y: auto;
}

.mobile-filter-section {
  margin-bottom: 18px;
}

.mobile-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 10px;
}

.mobile-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.mobile-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  border-radius: var(--radius-full, 9999px);
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.mobile-chip:hover {
  border-color: var(--color-brand);
  color: var(--color-brand);
}

.mobile-chip.active {
  background: var(--color-brand-subtle);
  border-color: var(--color-brand);
  color: var(--color-brand);
  font-weight: 500;
}

.mobile-filter-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-card);
  position: sticky;
  bottom: 0;
}

.mobile-filter-footer .sf-button {
  flex: 1;
}

/* ====== 骨架网格模式 ====== */
.grid-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.list-skeleton-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ====== 响应式 ====== */
@media (max-width: 1200px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 1024px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .materials-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .header-tools {
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-search {
    width: 100%;
    order: 3;
  }

  .view-toggle {
    margin-left: auto;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  .video-grid.video-list {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .grid-skeleton {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  .list-skeleton-wrap {
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .video-grid {
    grid-template-columns: 1fr;
  }

  .grid-skeleton {
    grid-template-columns: 1fr;
  }

  .header-search {
    order: 1;
  }

  .filter-toggle-btn {
    order: 0;
  }

  .view-toggle {
    order: 2;
  }
}
</style>
