<template>
  <div class="yt-home">
    <div class="home-layout">
      <!-- 左侧统计面板 -->
      <aside class="home-sidebar" v-if="userStore.isLoggedIn">
        <!-- 学习统计卡片 -->
        <div class="sidebar-card stats-card">
          <h3 class="sidebar-card-title">
            <BarChart3 />
            学习统计
          </h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ stats.total }}</span>
              <span class="stat-label">总期数</span>
            </div>
            <div class="stat-item stat-learned">
              <span class="stat-value">{{ stats.learned }}</span>
              <span class="stat-label">已学习</span>
            </div>
            <div class="stat-item stat-unlearned">
              <span class="stat-value">{{ stats.unlearned }}</span>
              <span class="stat-label">未学习</span>
            </div>
          </div>
        </div>

        <!-- 连续学习 & 月度统计 -->
        <div class="sidebar-card streak-card">
          <div class="streak-row">
            <div class="streak-item">
              <Flame :size="26" class="streak-emoji-icon" />
              <div class="streak-info">
                <span class="streak-value">{{ calendarData.streak }}</span>
                <span class="streak-label">天连续学习</span>
              </div>
            </div>
            <div class="streak-divider"></div>
            <div class="streak-extra">
              <div class="streak-extra-item">
                <span class="streak-extra-value">{{ calendarData.max_streak }}</span>
                <span class="streak-extra-label">最长连续</span>
              </div>
              <div class="streak-extra-item">
                <span class="streak-extra-value">{{ formatMinutes(calendarData.monthly_minutes) }}</span>
                <span class="streak-extra-label">本月学习</span>
              </div>
              <div class="streak-extra-item" v-if="calendarData.total_days > 0">
                <span class="streak-extra-value">{{ formatMinutes(avgDailyMinutes) }}<small>/天</small></span>
                <span class="streak-extra-label">日均学习</span>
              </div>
            </div>
          </div>
          <!-- 里程碑激励 -->
          <div class="streak-milestone" v-if="streakMilestone">
            <component :is="streakMilestone.icon" :size="18" class="milestone-icon" />
            <span class="milestone-text">{{ streakMilestone.text }}</span>
          </div>
        </div>

        <!-- 日历卡片 -->
        <div class="sidebar-card calendar-card">
          <h3 class="sidebar-card-title">
            <Calendar />
            {{ currentMonth }}
            <span class="calendar-total">共 {{ calendarData.total_days }} 天</span>
          </h3>
          <div class="mini-calendar">
            <div class="cal-header">
              <span v-for="d in weekDays" :key="d" class="cal-weekday">{{ d }}</span>
            </div>
            <div class="cal-body">
              <SfTooltip
                v-for="(day, idx) in calendarDays"
                :key="idx"
                :content="getDayTooltip(day)"
                placement="top"
              >
                <span
                  :class="['cal-day', {
                    'other-month': !day.currentMonth,
                    'today': day.isToday,
                    'has-record': day.hasRecord
                  }]"
                >
                  {{ day.date }}
                </span>
              </SfTooltip>
            </div>
          </div>
        </div>

        <!-- 最近学习 -->
        <div class="sidebar-card recent-card" v-if="recentItems.length > 0">
          <h3 class="sidebar-card-title">
            <Clock />
            最近学习
          </h3>
          <div class="recent-list">
            <div
              v-for="item in recentItems"
              :key="item.id"
              class="recent-item"
              @click="goLearn(item.material_id || item.id)"
            >
              <div class="recent-title">{{ item.title || item.material_title || '未命名' }}</div>
              <div class="recent-meta">
                <SfProgress :percentage="item.progress || 0" :stroke-width="4" :show-text="false" style="flex:1" />
                <span class="recent-progress">{{ item.progress || 0 }}%</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧主内容 -->
      <div class="home-main">
        <!-- 公告横幅 -->
        <AnnouncementBanner />

        <!-- 分类筛选条 -->
        <div class="filter-bar" ref="filterBar">
          <div class="filter-chips">
            <FilterChip
              :model-value="selectedCategory"
              :value="null"
              label="全部"
              @update:model-value="selectCategory"
            />
            <FilterChip
              v-for="cat in categories"
              :key="cat.name"
              :model-value="selectedCategory"
              :value="cat.name"
              :label="getCategoryLabel(cat.name)"
              @update:model-value="selectCategory"
            />
          </div>

          <!-- Creator 标签 -->
          <div class="tag-filter-section" v-if="creatorTags.length > 0">
            <span class="tag-filter-label">创作者</span>
            <div class="tag-chips">
              <div
                v-for="tag in creatorTags"
                :key="'c-' + tag.id"
                :class="['tag-chip', { active: selectedCreatorTag === tag.id }]"
                :style="{ '--chip-color': tag.color || 'var(--color-brand)' }"
                @click="toggleCreatorTag(tag.id)"
              >{{ tag.name }}</div>
            </div>
          </div>

          <!-- Topic 标签 -->
          <div class="tag-filter-section" v-if="topicTags.length > 0">
            <span class="tag-filter-label">主题</span>
            <div class="tag-chips">
              <div
                v-for="tag in topicTags"
                :key="'t-' + tag.id"
                :class="['tag-chip', { active: selectedTopicTag === tag.id }]"
                :style="{ '--chip-color': tag.color || 'var(--color-success)' }"
                @click="toggleTopicTag(tag.id)"
              >{{ tag.name }}</div>
            </div>
          </div>
        </div>

        <!-- 继续学习快捷入口 -->
        <div v-if="continueLearnItems.length > 0" class="continue-learn-section">
          <div class="section-header">
            <h3 class="section-title">
              <Play />
              继续学习
            </h3>
            <SfButton type="subtle" size="sm" @click="$router.push('/learning-center')">查看全部</SfButton>
          </div>
          <div class="continue-learn-scroll">
            <div
              v-for="item in continueLearnItems"
              :key="item.material_id"
              class="continue-learn-card"
              @click="goLearn(item.material_id)"
            >
              <div class="cl-card-cover">
                <img v-if="item.cover_path" :src="item.cover_path" :alt="item.title" />
                <div v-else class="cl-cover-placeholder">
                  <Play :size="24" />
                </div>
                <div class="cl-progress-overlay">
                  <SfProgress :percentage="item.progress" :stroke-width="3" :show-text="false" />
                </div>
              </div>
              <div class="cl-card-info">
                <div class="cl-card-title">{{ item.title || '未命名' }}</div>
                <div class="cl-card-meta">
                  <span class="cl-progress-text">{{ item.progress }}%</span>
                  <span class="cl-continue-btn">继续学习 →</span>
                </div>
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
            :progress="getProgress(item.id)"
            :difficulty="item.difficulty"
            :view-count="item.view_count || 0"
            :category="item.category"
            :description="item.description"
            :tags="item.tags || []"
            :favorited="isMaterialFavorited(item.id)"
            :completed="isMaterialCompleted(item.id)"
            @click="goLearn"
          />
        </div>

        <!-- 加载更多 -->
        <div class="load-more" v-if="hasMore && !loading">
          <SfButton @click="loadMore" :loading="loadingMore">
            加载更多
          </SfButton>
        </div>

        <!-- 空状态 -->
        <EmptyState
          v-if="!loading && materials.length === 0"
          type="welcome"
          title="开始你的学习之旅"
          description="浏览语料库，选择感兴趣的视频开始学习吧"
        >
          <template #actions>
            <SfButton type="primary" @click="loadMaterials">刷新</SfButton>
          </template>
        </EmptyState>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { materialAPI, learningStatsAPI, tagsAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import FilterChip from '@/components/common/FilterChip.vue'
import VideoCard from '@/components/common/VideoCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import AnnouncementBanner from '@/components/common/AnnouncementBanner.vue'
import { BarChart3, Calendar, Clock, Play, Flame, Sprout, Dumbbell, Star, Trophy, Crown, Target, Sparkles } from 'lucide-vue-next'
import SfTooltip from '@/components/ui/SfTooltip.vue'
import SfProgress from '@/components/ui/SfProgress.vue'
import SfButton from '@/components/ui/SfButton.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const loadingMore = ref(false)
const categories = ref([])
const materials = ref([])
const selectedCategory = ref(null)
const creatorTags = ref([])
const topicTags = ref([])
const selectedCreatorTag = ref(null)
const selectedTopicTag = ref(null)
const page = ref(1)
const pageSize = 12
const total = ref(0)
const learningProgress = ref({})
const learningRecords = ref({})  // materialId -> record（含 completed 等完整信息）
const favoritedMaterialIds = ref(new Set())  // 已收藏的材料ID集合
const recentItems = ref([])
const learningDates = ref(new Set())
const calendarData = ref({
  streak: 0,
  max_streak: 0,
  total_days: 0,
  monthly_minutes: 0
})
const dailyCounts = ref({})  // { 'YYYY-MM-DD': count }

const stats = computed(() => ({
  total: total.value,
  learned: Object.values(learningProgress.value).filter(p => p >= 80).length,
  unlearned: total.value - Object.values(learningProgress.value).filter(p => p >= 80).length
}))

const currentMonth = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月`
})

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const calendarDays = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const today = now.getDate()

  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()

  const days = []

  // 上月补齐
  for (let i = firstDay - 1; i >= 0; i--) {
    days.push({ date: daysInPrevMonth - i, currentMonth: false, isToday: false, hasRecord: false })
  }

  // 本月
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({
      date: d,
      dateStr,
      currentMonth: true,
      isToday: d === today,
      hasRecord: learningDates.value.has(dateStr),
      count: dailyCounts.value[dateStr] || 0
    })
  }

  // 下月补齐
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    days.push({ date: d, currentMonth: false, isToday: false, hasRecord: false })
  }

  return days
})

const hasMore = computed(() => {
  return materials.value.length < total.value
})

const avgDailyMinutes = computed(() => {
  if (!calendarData.value.total_days) return 0
  return Math.round(calendarData.value.monthly_minutes / calendarData.value.total_days)
})

const formatMinutes = (mins) => {
  if (!mins) return '0min'
  if (mins < 60) return `${mins}min`
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return m > 0 ? `${h}h${m}min` : `${h}h`
}

// 日历 tooltip
const getDayTooltip = (day) => {
  if (!day.currentMonth) return ''
  const month = new Date().getMonth() + 1
  if (day.hasRecord) {
    const count = day.count || 0
    return `${month}月${day.date}日：学了${count}个语料`
  }
  return `${month}月${day.date}日：未学习`
}

// 连续学习里程碑
const streakMilestones = [
  { days: 3, icon: 'Sprout', text: '初露锋芒！坚持3天了' },
  { days: 7, icon: 'Dumbbell', text: '一周达成！习惯正在养成' },
  { days: 14, icon: 'Star', text: '两周坚持！毅力非凡' },
  { days: 30, icon: 'Trophy', text: '月度达成！已是学习达人' },
  { days: 60, icon: 'Crown', text: '两个月！习惯已融入生活' },
  { days: 100, icon: 'Target', text: '百日学习！你是真正的学霸' }
]

const streakMilestone = computed(() => {
  const streak = calendarData.value.streak
  if (streak <= 0) return null
  // 找到当前达成或即将达成的里程碑
  let matched = null
  for (const m of streakMilestones) {
    if (streak >= m.days) {
      matched = m
    } else {
      break
    }
  }
  if (matched) return matched
  // 如果还没到第一个里程碑，显示鼓励
  if (streak > 0 && streak < 3) {
    return { icon: 'Sparkles', text: `再坚持${3 - streak}天就能解锁第一个成就！` }
  }
  return null
})

const categoryLabels = {
  travel: '旅行',
  shopping: '购物',
  social: '社交',
  work: '工作',
  daily: '日常',
  food: '餐饮'
}

const getCategoryLabel = (name) => categoryLabels[name] || name

const selectCategory = (category) => {
  selectedCategory.value = category
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

const toggleCreatorTag = (tagId) => {
  selectedCreatorTag.value = selectedCreatorTag.value === tagId ? null : tagId
  page.value = 1
  loadMaterials()
}

const toggleTopicTag = (tagId) => {
  selectedTopicTag.value = selectedTopicTag.value === tagId ? null : tagId
  page.value = 1
  loadMaterials()
}

const getProgress = (materialId) => {
  return learningProgress.value[materialId] || 0
}

const goLearn = (id) => {
  router.push(`/learn/${id}`)
}

// 继续学习 - 从学习记录中提取未完成的项目
const continueLearnItems = computed(() => {
  if (!recentItems.value?.length) return []
  return recentItems.value
    .filter(item => item.progress > 0 && item.progress < 95)
    .slice(0, 5)
    .map(item => ({
      material_id: item.material_id,
      title: item.material_title || item.title || '',
      cover_path: item.material_cover || '',
      progress: item.progress,
      last_position: item.last_position || 0
    }))
})

const loadCategories = async () => {
  try {
    const res = await materialAPI.getCategories()
    categories.value = res || []
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

const loadMaterials = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize
    }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    if (selectedCreatorTag.value) {
      params.tag_id = selectedCreatorTag.value
    } else if (selectedTopicTag.value) {
      params.tag_id = selectedTopicTag.value
    }

    const res = await materialAPI.getList(params)
    if (page.value === 1) {
      materials.value = res.items
    } else {
      materials.value = [...materials.value, ...res.items]
    }
    total.value = res.total

    if (userStore.isLoggedIn) {
      await loadLearningProgress()
    }
  } catch (e) {
    console.error('加载语料失败', e)
  } finally {
    loading.value = false
  }
}

const loadLearningProgress = async () => {
  try {
    const [recordsRes, calRes] = await Promise.all([
      learningStatsAPI.getRecords({ limit: 100 }),
      learningStatsAPI.getCalendar()
    ])

    const progressMap = {}
    const recordMap = {}
    const recent = []

    recordsRes.items.forEach(item => {
      progressMap[item.material_id] = item.progress
      recordMap[item.material_id] = item
      recent.push(item)
    })

    learningProgress.value = progressMap
    learningRecords.value = recordMap
    recentItems.value = recent.slice(0, 5)

    // 日历数据
    const dateSet = new Set(calRes.dates || [])
    learningDates.value = dateSet
    dailyCounts.value = calRes.daily_counts || {}
    calendarData.value = {
      streak: calRes.streak || 0,
      max_streak: calRes.max_streak || 0,
      total_days: calRes.total_days || 0,
      monthly_minutes: calRes.monthly_minutes || 0
    }

    // 加载收藏状态
    await loadFavoriteStatus()
  } catch (e) {
    console.error('加载学习进度失败', e)
  }
}

const loadFavoriteStatus = async () => {
  if (!userStore.isLoggedIn || !materials.value.length) return
  try {
    const ids = materials.value.map(m => m.id)
    const res = await favoriteAPI.getList({ page_size: 1000 })
    const favIds = new Set((res.items || []).map(f => f.id))
    favoritedMaterialIds.value = favIds
  } catch (e) {
    console.debug('加载收藏状态失败', e)
  }
}

const isMaterialCompleted = (materialId) => {
  const record = learningRecords.value[materialId]
  return record?.progress >= 95 || false
}

const isMaterialFavorited = (materialId) => {
  return favoritedMaterialIds.value.has(materialId)
}

const loadMore = async () => {
  loadingMore.value = true
  page.value++
  await loadMaterials()
  loadingMore.value = false
}

onMounted(async () => {
  await Promise.all([
    loadCategories(),
    loadMaterials(),
    loadTags()
  ])
})
</script>

<style scoped>
.yt-home {
  max-width: 1600px;
  margin: 0 auto;
}

/* ====== 两栏布局 ====== */
.home-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* ====== 左侧边栏 ====== */
.home-sidebar {
  flex: 0 0 300px;
  position: sticky;
  top: 84px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.sidebar-card {
  background: var(--color-bg-base);
  border-radius: var(--radius-lg);
  padding: 22px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-normal);
}

.sidebar-card:hover {
  box-shadow: var(--shadow-hover);
}

.sidebar-card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 16px;
  letter-spacing: -0.2px;
}

.sidebar-card-title svg {
  color: var(--color-brand);
  width: 18px;
  height: 18px;
}

/* ====== 统计卡片 ====== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 6px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: border-color var(--transition-normal);
}

.stat-item:hover {
  border-color: var(--color-border);
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-brand);
  line-height: 1;
}

.stat-learned .stat-value {
  color: var(--color-brand);
}

.stat-unlearned .stat-value {
  color: var(--color-text-muted);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-muted);
  font-weight: 500;
}

/* ====== 连续学习 ====== */
.streak-card {
  padding: 18px 22px;
}

.streak-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.streak-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.streak-emoji-icon {
  color: var(--color-brand);
}

.streak-info {
  display: flex;
  flex-direction: column;
}

.streak-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-warning);
  line-height: 1;
}

.streak-label {
  font-size: 11px;
  color: var(--color-text-muted);
  font-weight: 500;
  margin-top: 2px;
}

.streak-divider {
  width: 1px;
  height: 32px;
  background: var(--color-border);
}

.streak-extra {
  display: flex;
  gap: 14px;
  flex: 1;
}

.streak-extra-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.streak-extra-value {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1;
}

.streak-extra-value small {
  font-size: 10px;
  color: var(--color-text-muted);
  font-weight: 500;
}

.streak-extra-label {
  font-size: 10px;
  color: var(--color-text-muted);
  font-weight: 500;
}

/* 里程碑激励 */
.streak-milestone {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  padding: 10px 14px;
  background: var(--color-brand-subtle);
  border-radius: var(--radius-md);
  border: 1px solid rgba(16, 185, 129, 0.12);
}

.milestone-icon {
  color: var(--color-brand);
  flex-shrink: 0;
}

.milestone-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

/* 日历标题右侧统计 */
.calendar-total {
  margin-left: auto;
  font-size: 11px;
  font-weight: 400;
  color: var(--color-text-muted);
}

/* ====== 日历 ====== */
.mini-calendar {
  user-select: none;
}

.cal-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 6px;
}

.cal-weekday {
  font-size: 11px;
  color: var(--color-text-muted);
  font-weight: 600;
  padding: 4px 0;
}

.cal-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  gap: 2px;
}

.cal-day {
  width: 32px;
  height: 32px;
  line-height: 32px;
  border-radius: 50%;
  font-size: 12px;
  color: var(--color-text-primary);
  transition: background var(--transition-fast);
  margin: 0 auto;
}

.cal-day.other-month {
  color: var(--color-text-muted);
  opacity: 0.4;
}

.cal-day.today {
  background: var(--color-brand);
  color: #fff;
  font-weight: 700;
}

.cal-day.has-record {
  background: var(--color-brand-light);
  color: var(--color-brand);
  font-weight: 600;
}

.cal-day.today.has-record {
  background: var(--color-brand);
  color: #fff;
}

/* ====== 最近学习 ====== */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-item {
  padding: 12px 14px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-normal);
}

.recent-item:hover {
  background: var(--color-bg-elevated);
}

.recent-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recent-progress {
  font-size: 11px;
  color: var(--color-text-muted);
  font-weight: 600;
  min-width: 32px;
}

/* ====== 右侧主内容 ====== */
.home-main {
  flex: 1;
  min-width: 0;
}

/* 筛选条 */
.filter-bar {
  position: sticky;
  top: 60px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  z-index: 10;
  padding: 16px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--color-border);
}

.filter-chips {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 2px 4px;
  scrollbar-width: none;
}

.filter-chips::-webkit-scrollbar {
  display: none;
}

/* 标签筛选 */
.tag-filter-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.tag-filter-label {
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
  padding: 2px 0;
  scrollbar-width: none;
}

.tag-chips::-webkit-scrollbar {
  display: none;
}

.tag-chip {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-normal);
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-chip:hover {
  border-color: var(--color-brand);
  color: var(--color-brand);
}

.tag-chip.active {
  background: var(--color-brand);
  color: #fff;
  border-color: var(--color-brand);
}

/* 视频网格 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding-top: 4px;
}

/* 加载更多 */
.load-more {
  display: flex;
  justify-content: center;
  padding: 36px 0;
}

.load-more :deep(.sf-btn) {
  background: var(--color-bg-base);
  border: 1.5px solid var(--color-border);
  color: var(--color-text-secondary);
  font-weight: 600;
  border-radius: var(--radius-full);
  padding: 10px 32px;
  transition: all var(--transition-normal);
}

.load-more :deep(.sf-btn:hover) {
  border-color: var(--color-brand);
  color: var(--color-brand);
  background: var(--color-brand-subtle);
}

/* ====== 继续学习快捷入口 ====== */
.continue-learn-section {
  margin-bottom: 24px;
}
.continue-learn-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.continue-learn-section .section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}
.continue-learn-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}
.continue-learn-scroll::-webkit-scrollbar {
  height: 4px;
}
.continue-learn-scroll::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}
.continue-learn-card {
  flex-shrink: 0;
  width: 200px;
  background: var(--color-bg-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--color-border);
  transition: box-shadow var(--transition-normal), border-color var(--transition-normal);
  scroll-snap-align: start;
}
.continue-learn-card:hover {
  box-shadow: var(--shadow-hover);
  border-color: var(--color-brand);
}
.cl-card-cover {
  position: relative;
  width: 100%;
  height: 110px;
  background: var(--color-bg-elevated);
  overflow: hidden;
}
.cl-card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cl-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  background: var(--color-bg-elevated);
}
.cl-progress-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0 4px 4px;
}
.cl-card-info {
  padding: 8px 10px 10px;
}
.cl-card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
}
.cl-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cl-progress-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-brand);
}
.cl-continue-btn {
  font-size: 12px;
  color: var(--color-text-muted);
  transition: color var(--transition-fast);
}
.continue-learn-card:hover .cl-continue-btn {
  color: var(--color-brand);
}

/* ====== 响应式 ====== */
@media (max-width: 1200px) {
  .home-sidebar {
    flex: 0 0 260px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 1024px) {
  .home-layout {
    flex-direction: column;
  }

  .home-sidebar {
    flex: none;
    width: 100%;
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .sidebar-card {
    flex: 1;
    min-width: 250px;
    max-width: 100%;
  }

  .calendar-card {
    display: none;
  }
}

@media (max-width: 768px) {
  .home-sidebar {
    display: none;
  }

  .filter-bar {
    margin: 0 -16px 16px;
    padding: 12px 16px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}
</style>
