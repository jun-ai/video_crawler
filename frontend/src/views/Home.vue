<template>
  <div class="home-page">
    <div class="home-container">
      <!-- 1. 筛选条 row（speakvlog 风格 chip 分组） -->
      <div class="filter-row" ref="filterBar">
        <div class="filter-group" v-if="categories.length > 0">
          <span class="filter-label">分类</span>
          <div class="chip-list">
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
        </div>

        <div class="filter-group" v-if="creatorTags.length > 0">
          <span class="filter-label">视频博主</span>
          <div class="chip-list">
            <div
              v-for="tag in creatorTags"
              :key="'c-' + tag.id"
              :class="['tag-chip', { active: selectedCreatorTag === tag.id }]"
              :style="{ '--chip-color': tag.color || 'var(--color-brand)' }"
              @click="toggleCreatorTag(tag.id)"
            >{{ tag.name }}</div>
          </div>
        </div>

        <div class="filter-group" v-if="topicTags.length > 0">
          <span class="filter-label">视频话题</span>
          <div class="chip-list">
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

      <!-- 2+3+4. 两栏布局: 左侧 stats 框 (固定不随筛选变) | 右侧 视频区 -->
      <div class="home-main">
        <!-- 左侧: 我的学习 stats 框 -->
        <aside class="stats-side" v-if="userStore.isLoggedIn">
          <div class="stats-box">
            <div class="stats-box-header">
              <BarChart3 :size="18" />
              <span>我的学习</span>
            </div>
            <div class="stats-grid">
              <div class="stat-mini-card">
                <div class="stat-mini-value">{{ stats.total }}</div>
                <div class="stat-mini-label">总期数</div>
              </div>
              <div class="stat-mini-card stat-mini-learned">
                <div class="stat-mini-value">{{ stats.learned }}</div>
                <div class="stat-mini-label">已学习</div>
              </div>
              <div class="stat-mini-card stat-mini-unlearned">
                <div class="stat-mini-value">{{ stats.unlearned }}</div>
                <div class="stat-mini-label">未学习</div>
              </div>
              <div class="stat-mini-card stat-mini-streak">
                <div class="stat-mini-value">
                  {{ calendarData.streak }}<span class="stat-mini-unit">天</span>
                </div>
                <div class="stat-mini-label">连续打卡</div>
              </div>
            </div>

            <div class="mini-calendar-card">
              <div class="cal-card-header">
                <span class="cal-card-month">
                  <Calendar :size="16" />
                  {{ currentMonth }}
                </span>
                <span class="cal-card-count">共 {{ calendarData.total_days }} 天</span>
              </div>
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
                    >{{ day.date }}</span>
                  </SfTooltip>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <!-- 右侧: featured + 视频网格 -->
        <div class="videos-side">
          <!-- Featured 视频 hero（大缩略图主视觉） -->
          <section
            v-if="featuredVideo"
            class="featured-hero"
            @click="goLearn(featuredVideo.id)"
          >
            <div class="featured-cover">
              <img
                v-if="featuredVideo.cover_path"
                :src="featuredVideo.cover_path"
                :alt="featuredVideo.title"
              />
              <div v-else class="featured-placeholder">
                <Play :size="64" />
              </div>
              <div class="featured-overlay"></div>
              <div class="featured-play"><Play :size="26" /></div>
              <span class="featured-duration" v-if="featuredVideo.duration">{{ featuredVideo.duration }}</span>
            </div>
            <div class="featured-info">
              <div class="featured-eyebrow">精选推荐</div>
              <h2 class="featured-title">{{ featuredVideo.title || '未命名视频' }}</h2>
              <div class="featured-meta">
                <span class="featured-tag" v-if="featuredVideo.category">{{ getCategoryLabel(featuredVideo.category) }}</span>
                <span class="featured-hint">点击开始学习 →</span>
              </div>
            </div>
          </section>

          <!-- 视频网格 3 列 -->
          <section class="video-grid-section">
            <div class="section-head">
              <h3 class="section-title">视频库</h3>
              <span class="section-count">共 {{ total }} 个视频</span>
            </div>

            <div class="video-grid" v-loading="loading">
              <VideoCard
                v-for="item in gridVideos"
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

            <EmptyState
              v-if="!loading && materials.length === 0"
              type="welcome"
              title="开始你的学习之旅"
              description="浏览语料库，选择感兴趣的视频开始学习吧"
            >
              <template #actions>
                <SfButton type="primary" @click="$router.push('/materials')">浏览全部视频</SfButton>
              </template>
            </EmptyState>

            <div class="load-more" v-if="hasMore && !loading">
              <SfButton @click="loadMore" :loading="loadingMore">加载更多</SfButton>
            </div>
          </section>
        </div>
      </div>

      <!-- 5. 底部（学习消息 / 学习指南 / 联系） -->
      <footer class="home-footer">
        <div class="footer-col">
          <div class="footer-col-title">学习消息</div>
          <p class="footer-text">坚持每天 15 分钟，三个月看到进步。</p>
        </div>
        <div class="footer-col">
          <div class="footer-col-title">学习指南</div>
          <p class="footer-text">看 → 听 → 读 → 说，四步走，循序渐进。</p>
        </div>
        <div class="footer-col">
          <div class="footer-col-title">联系我们</div>
          <p class="footer-text">微信：fluenty-study</p>
        </div>
      </footer>
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
import { BarChart3, Calendar, Clock, Play, Flame, Sprout, Dumbbell, Star, Trophy, Crown, Target, Sparkles, BookOpen, Headphones, Mic, Check, ChevronDown } from 'lucide-vue-next'
import SfTooltip from '@/components/ui/SfTooltip.vue'
import SfProgress from '@/components/ui/SfProgress.vue'
import SfButton from '@/components/ui/SfButton.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const loadingMore = ref(false)
const categories = ref([])
// 4 核心功能 — 大卡片(差异化:图标+标题+描述)
const coreFeatures = [
  { title: '真实视频语料', desc: '海外 YouTube / TED 精选，不是课本录音', icon: Play },
  { title: 'AI 智能解读', desc: '逐句翻译 + 重点词组 + 语法标注', icon: Sparkles },
  { title: '字幕跟读练习', desc: '影子跟读 + 语速调节 + 发音反馈', icon: Headphones },
  { title: '间隔重复复习', desc: '艾宾浩斯曲线，学过就不会忘', icon: Target }
]
// 8 次要功能 — 紧凑列表
const secondaryFeatures = [
  { title: '生词一键收藏' },
  { title: '连续打卡激励' },
  { title: '学习数据统计' },
  { title: '移动端友好' },
  { title: '收藏夹整理' },
  { title: '跟读 AI 打分' },
  { title: '永久云端保存' },
  { title: '免费体验' }
]
// 默认折叠，只展示前 4 项
const showAllFeatures = ref(false)
const displayFeatures = computed(() =>
  showAllFeatures.value ? secondaryFeatures : secondaryFeatures.slice(0, 4)
)
const materials = ref([])
const selectedCategory = ref(null)
const creatorTags = ref([])
const topicTags = ref([])
const selectedCreatorTag = ref(null)
const selectedTopicTag = ref(null)
const page = ref(1)
const pageSize = 12
const total = ref(0)            // 当前筛选下的视频数 (跟筛选走)
const globalTotal = ref(0)      // 全部视频总数 (不跟筛选走, 用于 stats.total)
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

// stats 用 globalTotal (固定不变), 不跟当前筛选走
const learnedCount = computed(() => Object.values(learningProgress.value).filter(p => p >= 80).length)
const stats = computed(() => ({
  total: globalTotal.value,
  learned: learnedCount.value,
  unlearned: Math.max(0, globalTotal.value - learnedCount.value)
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

const scrollToVideos = () => {
  const grid = document.querySelector('.video-grid')
  if (grid) grid.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
    // 首次无筛选加载时快照全库总数 — 之后筛选变化不影响 globalTotal
    const noFilter = !selectedCategory.value && !selectedCreatorTag.value && !selectedTopicTag.value
    if (globalTotal.value === 0 && noFilter && page.value === 1) {
      globalTotal.value = res.total
    }

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

// Featured 视频 hero（speakvlog library 风格）— 仅在浏览全部时展示最新一个
const featuredVideo = computed(() => {
  if (selectedCategory.value || selectedCreatorTag.value || selectedTopicTag.value) return null
  return materials.value[0] || null
})
const gridVideos = computed(() => {
  if (!featuredVideo.value) return materials.value
  return materials.value.slice(1)
})

onMounted(async () => {
  await Promise.all([
    loadCategories(),
    loadMaterials(),
    loadTags()
  ])
})
</script>

<style scoped>
/* ============================================================
   Home.vue — speakvlog library 风格重写
   米色背景 / featured hero / 4 统计卡 + 月历 / 3 列视频网格
   ============================================================ */

.home-page {
  min-height: 100vh;
  background: #F5F7F2;  /* 米色背景（speakvlog 风格） */
  padding: 24px 0 48px;
}

.home-container {
  max-width: 1380px;
  margin: 0 auto;
  padding: 0 32px;
}

/* ====== 1. 筛选条 row ====== */
.filter-row {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.filter-label {
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 64px;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  padding: 7px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.18s ease;
  user-select: none;
}

.tag-chip:hover {
  border-color: var(--color-border-strong);
  color: var(--color-text-primary);
  transform: translateY(-1px);
}

.tag-chip.active {
  color: #fff;
  background: var(--chip-color, var(--color-brand));
  border-color: var(--chip-color, var(--color-brand));
}

/* ====== 2. Featured hero ====== */
.featured-hero {
  position: relative;
  width: 100%;
  height: clamp(300px, 34vw, 440px);
  border-radius: 20px;
  overflow: hidden;
  background: var(--color-bg-card);
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.08);
  cursor: pointer;
  margin-bottom: 24px;
  display: block;
}

.featured-cover {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.featured-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.featured-hero:hover .featured-cover img {
  transform: scale(1.04);
}

.featured-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  background: linear-gradient(135deg, var(--color-bg-elevated), var(--color-bg-card));
}

/* 底部渐变遮罩 + 信息 */
.featured-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(15, 23, 42, 0.78) 0%,
    rgba(15, 23, 42, 0.30) 40%,
    transparent 70%
  );
  pointer-events: none;
}

.featured-play {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  color: var(--color-brand);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, background 0.2s ease;
}

.featured-hero:hover .featured-play {
  transform: translate(-50%, -50%) scale(1.08);
  background: #fff;
}

.featured-duration {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: rgba(15, 23, 42, 0.65);
  border-radius: 6px;
  backdrop-filter: blur(4px);
}

.featured-info {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 28px 32px;
  z-index: 2;
}

.featured-eyebrow {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1.5px;
  background: var(--color-brand);
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 12px;
}

.featured-title {
  font-size: clamp(22px, 2.4vw, 30px);
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
  margin: 0 0 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
}

.featured-meta {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.featured-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 999px;
  backdrop-filter: blur(6px);
}

.featured-hint {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.88);
}

/* ====== 2+3+4. 两栏布局: 左侧 stats 框 (固定不随筛选变) | 右侧 视频区 ====== */
.home-main {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;
  margin-bottom: 32px;
}

/* 左侧 stats 框 (sticky 让滚动视频时一直可见) */
.stats-side {
  position: sticky;
  top: 16px;
}

.stats-box {
  background: var(--color-bg-card);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-box-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border, rgba(15, 23, 42, 0.06));
}

/* 4 个 stat 改成 2x2 grid (左侧窄) */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stats-grid .stat-mini-card {
  padding: 16px 14px;
  border-radius: 12px;
  box-shadow: none;
  border: 1px solid rgba(15, 23, 42, 0.05);
  background: var(--color-bg, #FAFBF8);
}

.stats-grid .stat-mini-value {
  font-size: 24px;
}

.stats-grid .stat-mini-label {
  font-size: 12px;
}

/* 月历卡在 stats 框内, 去掉外层 box-shadow/border (已有 .stats-box 容器) */
.stats-box .mini-calendar-card {
  background: transparent;
  box-shadow: none;
  border: none;
  padding: 0;
}

.stats-box .mini-calendar {
  font-size: 12px;
}

.stats-box .cal-weekday {
  font-size: 10px;
}

.stats-box .cal-day {
  font-size: 11px;
  padding: 4px 0;
}

/* 右侧视频区 */
.videos-side {
  min-width: 0;  /* 防止 grid 子项溢出 */
}

.stat-mini-card {
  background: var(--color-bg-card);
  border-radius: 16px;
  padding: 22px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-mini-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
}

.stat-mini-value {
  font-size: 30px;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1;
  letter-spacing: -0.5px;
  display: flex;
  align-items: baseline;
  gap: 3px;
}

.stat-mini-unit {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-muted);
}

.stat-mini-learned .stat-mini-value { color: var(--color-brand); }
.stat-mini-unlearned .stat-mini-value { color: #F59E0B; }
.stat-mini-streak .stat-mini-value { color: #EF4444; }

.stat-mini-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

/* 月历卡 */
.mini-calendar-card {
  background: var(--color-bg-card);
  border-radius: 16px;
  padding: 18px 20px 16px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.04);
}

.cal-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.cal-card-month {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.cal-card-count {
  font-size: 12px;
  color: var(--color-text-muted);
}

.mini-calendar {
  width: 100%;
}

.cal-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 4px;
}

.cal-weekday {
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  padding: 2px 0;
}

.cal-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.cal-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  border-radius: 6px;
  transition: background 0.15s ease;
}

.cal-day.other-month {
  color: var(--color-text-quaternary);
}

.cal-day.today {
  font-weight: 700;
  color: #fff;
  background: var(--color-brand);
}

.cal-day.has-record:not(.today) {
  background: var(--color-brand-subtle);
  color: var(--color-brand-hover);
  font-weight: 600;
}

/* ====== 4. 视频网格 3 列 ====== */
.video-grid-section {
  margin-bottom: 40px;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.3px;
}

.section-count {
  font-size: 14px;
  color: var(--color-text-muted);
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  min-height: 120px;
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}

/* ====== 5. 底部 ====== */
.home-footer {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  padding: 28px 0 8px;
  border-top: 1px solid var(--color-border);
}

.footer-col-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.footer-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* ====== 响应式 ====== */
@media (max-width: 1100px) {
  .home-main {
    grid-template-columns: 280px 1fr;
    gap: 20px;
  }
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .home-main {
    grid-template-columns: 1fr;  /* 窄屏堆叠, stats 框在上 */
  }
  .stats-side {
    position: static;  /* 堆叠时不再 sticky */
  }
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .home-footer {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 640px) {
  .home-container { padding: 0 16px; }
  .filter-label { min-width: auto; }
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .video-grid {
    grid-template-columns: 1fr;
  }
  .featured-info { padding: 20px 18px; }
}
</style>
