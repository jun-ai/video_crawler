<template>
  <div class="yt-materials">
    <!-- 页面标题 -->
    <PageHeader title="语料库" subtitle="浏览所有学习材料" />

    <!-- 筛选条 -->
    <div class="filter-bar" ref="filterBar">
      <div class="filter-row-top">
        <div class="filter-chips">
          <FilterChip
            :model-value="!filters.category && !filters.difficulty && !filters.keyword && !selectedTagId"
            :value="true"
            label="全部"
            @update:model-value="clearFilters"
          />
          <SfDropdown placement="bottom">
            <template #trigger>
              <div :class="['chip-dropdown', { active: filters.category }]">
                {{ filters.category ? getCategoryLabel(filters.category) : '场景' }}
                <ChevronDown class="chip-arrow" :size="14" />
              </div>
            </template>
            <div class="sf-dropdown-item" @click="selectCategory('travel')">旅行</div>
            <div class="sf-dropdown-item" @click="selectCategory('shopping')">购物</div>
            <div class="sf-dropdown-item" @click="selectCategory('social')">社交</div>
            <div class="sf-dropdown-item" @click="selectCategory('work')">工作</div>
            <div class="sf-dropdown-item" @click="selectCategory('daily')">日常</div>
            <div class="sf-dropdown-item" @click="selectCategory('food')">餐饮</div>
          </SfDropdown>
          <SfDropdown placement="bottom">
            <template #trigger>
              <div :class="['chip-dropdown', { active: filters.difficulty }]">
                {{ filters.difficulty ? getDifficultyLabel(filters.difficulty) : '难度' }}
                <ChevronDown class="chip-arrow" :size="14" />
              </div>
            </template>
            <div class="sf-dropdown-item" @click="selectDifficulty(1)">入门</div>
            <div class="sf-dropdown-item" @click="selectDifficulty(2)">基础</div>
            <div class="sf-dropdown-item" @click="selectDifficulty(3)">中级</div>
            <div class="sf-dropdown-item" @click="selectDifficulty(4)">进阶</div>
            <div class="sf-dropdown-item" @click="selectDifficulty(5)">高级</div>
          </SfDropdown>
        </div>
        <!-- 搜索框 -->
        <div class="filter-search">
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
      </div>

      <!-- 标签筛选 -->
      <div v-if="creatorTags.length > 0 || topicTags.length > 0" class="filter-tags-row">
        <div v-if="creatorTags.length > 0" class="tag-group">
          <span class="tag-group-label">创作者：</span>
          <div class="tag-chips">
            <span
              v-for="tag in creatorTags.slice(0, 8)"
              :key="tag.id"
              :class="['tag-chip-item', { active: selectedTagId === tag.id }]"
              :style="selectedTagId === tag.id ? { background: tag.color, color: '#fff', borderColor: tag.color } : { borderColor: tag.color, color: tag.color }"
              @click="toggleTag(tag.id)"
            >{{ tag.name }}</span>
          </div>
        </div>
        <div v-if="topicTags.length > 0" class="tag-group">
          <span class="tag-group-label">话题：</span>
          <div class="tag-chips">
            <span
              v-for="tag in topicTags.slice(0, 10)"
              :key="tag.id"
              :class="['tag-chip-item', { active: selectedTagId === tag.id }]"
              :style="selectedTagId === tag.id ? { background: tag.color, color: '#fff', borderColor: tag.color } : { borderColor: tag.color, color: tag.color }"
              @click="toggleTag(tag.id)"
            >{{ tag.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 视频网格 -->
    <div class="video-grid" v-loading="loading">
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
        @click="goLearn"
      />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > pageSize">
      <SfPagination
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        @change="handlePageChange"
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ChevronDown, Search } from 'lucide-vue-next'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import SfButton from '@/components/ui/SfButton.vue'
import { materialAPI, tagsAPI, favoriteAPI, learningStatsAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterChip from '@/components/common/FilterChip.vue'
import VideoCard from '@/components/common/VideoCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const materials = ref([])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const searchQuery = ref(route.query.keyword || '')

// 用户学习数据
const favoritedMaterialIds = ref(new Set())
const learningProgress = ref({})  // materialId -> progress

const filters = reactive({
  category: route.query.category || '',
  difficulty: 0,
  keyword: route.query.keyword || ''
})

// 标签筛选
const creatorTags = ref([])
const topicTags = ref([])
const selectedTagId = ref(null)

const categoryLabels = {
  travel: '旅行',
  shopping: '购物',
  social: '社交',
  work: '工作',
  daily: '日常',
  food: '餐饮'
}

const getCategoryLabel = (name) => categoryLabels[name] || name

const getDifficultyLabel = (level) => {
  const labels = ['', '入门', '基础', '中级', '进阶', '高级']
  return labels[level] || '基础'
}

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

// 标签筛选
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
  filters.keyword = ''
  searchQuery.value = ''
  selectedTagId.value = null
  page.value = 1
  loadMaterials()
}

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
.yt-materials {
  max-width: 1800px;
  margin: 0 auto;
}

/* 筛选条 */
.filter-bar {
  position: sticky;
  top: 60px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  z-index: var(--z-sticky, 10);
  padding: 14px 0;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
}

.filter-row-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-chips {
  display: flex;
  gap: var(--spacing-md, 12px);
  overflow-x: auto;
  padding: 0 var(--spacing-xs, 4px);
  scrollbar-width: none;
  flex-shrink: 0;
}

.filter-chips::-webkit-scrollbar {
  display: none;
}

.filter-search {
  margin-left: auto;
  width: 220px;
  flex-shrink: 0;
}

.filter-search :deep(.sf-input-wrap) {
  border-radius: 20px;
  background: var(--color-bg-elevated);
  box-shadow: none;
}

.filter-search :deep(.sf-input-wrap:hover) {
  box-shadow: 0 0 0 1px var(--color-border) inset;
}

/* 标签筛选行 */
.filter-tags-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}

.tag-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-group-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-chips {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
  padding: 2px 0;
}

.tag-chips::-webkit-scrollbar {
  display: none;
}

.tag-chip-item {
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-chip-item:hover {
  filter: brightness(0.9);
  transform: translateY(-1px);
}

.tag-chip-item.active {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

/* 下拉筛选器 */
.chip-dropdown {
  flex-shrink: 0;
  padding: var(--spacing-sm, 8px) var(--spacing-md, 12px);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md, 8px);
  font-size: var(--font-size-base, 14px);
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background var(--transition-normal, 0.2s);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs, 4px);
}

.chip-dropdown:hover {
  background: var(--color-border);
}

.chip-dropdown.active {
  background: var(--color-text-primary);
  color: #fff;
}

.chip-arrow {
  font-size: var(--font-size-xs, 12px);
}

/* 下拉菜单项 */
.sf-dropdown-item {
  padding: 8px 14px;
  font-size: 14px;
  color: var(--color-text-primary);
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
}

.sf-dropdown-item:hover {
  background: var(--color-bg-elevated);
}

/* 视频网格 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  padding: var(--spacing-2xl, 32px) 0;
}

/* 响应式 */
@media (max-width: 1200px) {
  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .filter-bar {
    top: 56px;
    margin: 0 0 12px;
    padding: 12px 16px;
    border-radius: 0;
  }

  .filter-row-top {
    flex-wrap: wrap;
  }

  .filter-search {
    width: 100%;
    margin-left: 0;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: var(--spacing-sm, 12px);
  }
}

@media (max-width: 480px) {
  .video-grid {
    grid-template-columns: 1fr;
  }
}
</style>
