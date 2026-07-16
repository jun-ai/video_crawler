<template>
  <div class="home-page">
    <div class="home-container">
      <!-- ===== Phase 23b: H5 简化首页 (移动端独占)
           砍月历条 + 砍双层 chip = 纯视频流
           顶部 brand bar (H5Header) 含 ☰ + logo + 🕐 占位
           设计目标: 内容驱动,5 秒开始看视频 ===== -->
      <div class="home-h5-block" v-if="isMobileView">
        <H5Header />

        <!-- Phase 24 P0: 单层分类 chip (horizontal scroll, 不超过 8 项) -->
        <div class="h5-home-chips" v-if="categories.length > 0">
          <button
            v-for="cat in categories.slice(0, 8)"
            :key="cat.name"
            :class="['h5-home-chip', { 'is-active': selectedCategory === cat.name }]"
            @click="selectCategory(cat.name)"
          >
            {{ getCategoryLabel(cat.name) }}
          </button>
        </div>

        <!-- 视频流卡片列表 -->
        <div class="h5-home-list" v-loading="loading">
          <article
            v-for="item in h5ListVideos"
            :key="item.id"
            class="h5-home-card"
            @click="goLearn(item.id)"
          >
            <div class="h5-home-card__cover">
              <img v-if="item.cover_path" :src="item.cover_path" :alt="item.title" loading="lazy" />
              <div v-else class="h5-home-card__cover-fallback">
                <Play :size="20" />
              </div>
              <span v-if="item.duration" class="h5-home-card__duration">
                {{ formatDuration(item.duration) }}
              </span>
              <span class="h5-home-card__diff" :data-diff="item.difficulty">
                {{ difficultyLabel(item.difficulty) }}
              </span>
            </div>
            <div class="h5-home-card__body">
              <div class="h5-home-card__title">{{ item.title }}</div>
              <div class="h5-home-card__meta">
                <span class="h5-home-card__cat">{{ getCategoryLabel(item.category) }}</span>
                <span class="h5-home-card__views">{{ item.view_count || 0 }} 次观看</span>
              </div>
              <div class="h5-home-card__progress" v-if="getProgress(item.id) > 0">
                <div class="h5-home-card__progress-fill" :style="{ width: getProgress(item.id) + '%' }" />
              </div>
            </div>
          </article>

          <EmptyState
            v-if="!loading && h5ListVideos.length === 0"
            type="welcome"
            title="挑个视频开始吧"
            description="看完一段换下一段"
          >
            <template #actions>
              <SfButton type="primary" @click="selectCategory(null)">看全部</SfButton>
            </template>
          </EmptyState>

          <div class="h5-home-loadmore" v-if="hasMore && !loading">
            <button class="h5-home-loadmore__btn" @click="loadMore" :disabled="loadingMore">
              {{ loadingMore ? '加载中…' : '加载更多' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ===== 以下是桌面端原始布局 (H5 隐藏) ===== -->
      <!-- 2+3+4. 两栏布局: 左侧 stats 面板 (固定不随筛选变) | 右侧 视频区 (含筛选) -->
      <!-- 改动: .stats-side 作为 .home-container direct child (不再包在 .home-main 内)
           .home-container grid 320+1fr, stats-side 占第 1 列, home-main (装 videos-side) 占第 2 列 -->
      <!-- 左侧: 我的学习 stats 面板 -->
      <aside class="stats-side" v-if="userStore.isLoggedIn">
        <div class="stats-panel">
            <!-- 顶部带渐变条 + 标题 -->
            <div class="panel-header">
              <div class="panel-header-icon"><BarChart3 :size="18" /></div>
              <span class="panel-header-title">我的学习</span>
              <span class="panel-header-tag">{{ stats.total }} 期</span>
            </div>

            <!-- 主进度: 已学习 / 总数 + 进度条 -->
            <div class="panel-progress">
              <div class="progress-top">
                <span class="progress-label">已学习</span>
                <span class="progress-value">
                  {{ stats.learned }}<span class="progress-sep">/</span><span class="progress-total">{{ stats.total }}</span>
                </span>
              </div>
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
              </div>
              <div class="progress-bottom">
                <span class="progress-pct">{{ progressPct }}%</span>
                <span class="progress-hint">还差 {{ stats.unlearned }} 期</span>
              </div>
            </div>

            <!-- 3 列紧凑 stats -->
            <div class="panel-quick-stats">
              <div class="qs-item">
                <div class="qs-icon qs-icon-total"><BookOpen :size="14" /></div>
                <div class="qs-value">{{ stats.total }}</div>
                <div class="qs-label">总期数</div>
              </div>
              <div class="qs-divider"></div>
              <div class="qs-item">
                <div class="qs-icon qs-icon-unlearned"><Clock :size="14" /></div>
                <div class="qs-value">{{ stats.unlearned }}</div>
                <div class="qs-label">未学</div>
              </div>
              <div class="qs-divider"></div>
              <div class="qs-item">
                <div class="qs-icon qs-icon-streak"><Flame :size="14" /></div>
                <div class="qs-value">
                  {{ calendarData.streak }}<span class="qs-unit">天</span>
                </div>
                <div class="qs-label">连续打卡</div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="panel-divider"></div>

            <!-- 月历 -->
            <div class="panel-calendar">
              <div class="cal-row-head">
                <span class="cal-title">
                  <Calendar :size="14" />
                  {{ currentMonth }}
                </span>
                <span class="cal-stat">
                  <span class="cal-stat-dot"></span>
                  已学 {{ calendarData.total_days }} 天
                </span>
              </div>
              <div class="mini-calendar">
                <div class="cal-weekdays">
                  <span v-for="d in weekDays" :key="d" class="cal-weekday">{{ d }}</span>
                </div>
                <div class="cal-days">
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

                    <!-- 继续学习 (孤儿代码复活) -->
                    <section class="continue-learning-section panel-continue" data-audit="continue-learning">
                    <div class="pc-head">
                    <Play :size="14" />
                    <span class="pc-title">继续学习</span>
                    <span v-if="continueLearnItems.length > 0" class="pc-count">{{ continueLearnItems.length }} 个</span>
                    </div>

                    <div v-if="continueLearnItems.length > 0" class="pc-list">
                    <div
                    v-for="item in continueLearnItems"
                    :key="item.material_id"
                    class="pc-item"
                    @click="goLearn(item.material_id)"
                    >
                    <div class="pc-cover">
                    <img v-if="item.cover_path" :src="item.cover_path" :alt="item.title" />
                    <div v-else class="pc-cover-fallback">
                     <Play :size="14" />
                    </div>
                    </div>
                    <div class="pc-info">
                    <div class="pc-title-text">{{ item.title }}</div>
                    <div class="pc-progress-row">
                     <div class="pc-progress-track">
                       <div class="pc-progress-fill" :style="{ width: item.progress + '%' }"></div>
                     </div>
                     <span class="pc-pct">{{ item.progress }}%</span>
                    </div>
                    </div>
                    </div>
                    </div>

                    <div v-else class="pc-empty" @click="$refs.filterBar?.$el?.scrollIntoView({behavior: 'smooth'})">
                    <div class="pc-empty-text">
                    <div class="pc-empty-title">开始你的第一次学习</div>
                    <div class="pc-empty-sub">下方挑一个感兴趣的视频开始</div>
                    </div>
                    </div>
                    </section>

                    </div>
                    </aside>
                    <!-- 右侧: 筛选 + featured + 视频网格 -->
                    <!-- home-main 包住 videos-side (放第 2 列) -->
                    <div class="home-main">
                    <div class="videos-side">
          <!-- 7. P0 商业化: 激活码引导横幅 — 未登录用户第一眼看到 -->
          <div v-if="!userStore.isLoggedIn" class="activation-banner">
            <div class="activation-banner__content">
              <div class="activation-banner__icon">
                <Key :size="20" />
              </div>
              <div class="activation-banner__text">
                <h3 class="activation-banner__title">刚拿到激活码？</h3>
                <p class="activation-banner__sub">3 步开账号：输入激活码 → 设置密码 → 开始学习</p>
              </div>
            </div>
            <div class="activation-banner__actions">
              <SfButton
                type="primary"
                size="md"
                @click="$router.push('/register')"
              >
                立即注册
              </SfButton>
              <SfButton
                type="ghost"
                size="md"
                @click="$router.push('/login')"
              >
                已有账号
              </SfButton>
            </div>
          </div>

          <!-- 筛选条 (放在视频上方, 用户筛选视频用) -->
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
          </div>

          <!-- 视频网格 3 列 (砍掉 featured hero, 避免重复展示) -->
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
            <!-- home-main 结束 -->

            <!-- 5. 底部（学习消息 / 学习指南 / 联系） — H5 端隐藏 (核心 only) -->
      <!-- 5. 底部（学习消息 / 学习指南 / 联系） — H5 端隐藏 (核心 only) -->
      <footer class="home-footer home-footer--h5-hide">
        <div class="footer-col">
          <div class="footer-col-title">学习消息</div>
          <p class="footer-text">坚持每天 15 分钟，三个月看到进步。</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { materialAPI, learningStatsAPI, favoriteAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import FilterChip from '@/components/common/FilterChip.vue'
import VideoCard from '@/components/common/VideoCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import AnnouncementBanner from '@/components/common/AnnouncementBanner.vue'
import { BarChart3, Calendar, Clock, Play, Flame, Sprout, Dumbbell, Star, Trophy, Crown, Target, Sparkles, BookOpen, Headphones, Mic, Check, ChevronDown, Key, Users } from 'lucide-vue-next'
import SfTooltip from '@/components/ui/SfTooltip.vue'
import SfProgress from '@/components/ui/SfProgress.vue'
import SfButton from '@/components/ui/SfButton.vue'
// Phase 23b: 砍 H5CalendarStrip import (月历已删, 组件文件保留后续复用)
import H5Header from '@/components/h5/H5Header.vue'
import { useMobileView } from '@/composables/useMobileView'

const router = useRouter()
const userStore = useUserStore()

// H5 视口判断
const { isMobile: isMobileView } = useMobileView()

const loading = ref(true)
const loadingMore = ref(false)
const categories = ref([])
// 4 核心功能 — 大卡片(差异化:图标+标题+描述)
const coreFeatures = [
  { title: '真实视频语料', desc: '海外 YouTube / TED 精选，不是课本录音', icon: Play },
  { title: '智能解读', desc: '逐句翻译 + 重点词组 + 语法标注', icon: Sparkles },
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
  { title: '跟读 智能打分' },
  { title: '永久云端保存' },
  { title: '免费体验' }
]
// 默认折叠，只展示前 4 项
const showAllFeatures = ref(false)
const displayFeatures = computed(() =>
  showAllFeatures.value ? secondaryFeatures : secondaryFeatures.slice(0, 4)
)
// Phase 25 P2-C: 7 天 streak 条数据 (基于学习日期 + today)
const streakWeekDays = computed(() => {
  const days = []
  const today = new Date()
  const labels = ['日', '一', '二', '三', '四', '五', '六']
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    days.push({
      label: labels[d.getDay()],
      day: d.getDate(),
      isToday: i === 0,
      active: learningDates.value.has(dateStr)
    })
  }
  return days
})

const materials = ref([])
const selectedCategory = ref(null)
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
// 已学习进度百分比 — 左侧 panel 进度条用
const progressPct = computed(() => {
  if (!globalTotal.value) return 0
  return Math.round((learnedCount.value / globalTotal.value) * 100)
})

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

// Phase 23b: 砍 selectedDifficulty / difficultyLevels / selectDifficulty / onPickDate (双层 chip 已删)
const difficultyLabel = (d) => {
  // 难度标签映射 (1-5: 入门/基础/中级/进阶/高级), 兼容历史难度值
  const map = { 1: '入门', 2: '基础', 3: '中级', 4: '进阶', 5: '高级' }
  if (!d) return ''
  return map[d] || `Lv${d}`
}
// H5 列表: 现阶段跟桌面共用 materials, 后续可单独翻页
const h5ListVideos = computed(() => materials.value || [])
function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${String(s).padStart(2, '0')}`
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
    // Phase 23b: 砍难度筛选 (双层 chip 已删, selectedDifficulty 不存在)

    const res = await materialAPI.getList(params)
    if (page.value === 1) {
      materials.value = res.items
    } else {
      materials.value = [...materials.value, ...res.items]
    }
    total.value = res.total
    // 首次无筛选加载时快照全库总数 — 之后筛选变化不影响 globalTotal
    const noFilter = !selectedCategory.value
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
  if (selectedCategory.value) return null
  return materials.value[0] || null
})
const gridVideos = computed(() => {
  // featured hero 已在模板里移除(避免重复展示),这里直接返回全部
  // 如以后恢复 featured hero,改回: if (!featuredVideo.value) return materials.value; return materials.value.slice(1)
  return materials.value
})

onMounted(async () => {
  await Promise.all([
    loadCategories(),
    loadMaterials()
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
  background: var(--color-bg-base);  /* 跟视频库 (Materials.vue) 一致, 不再覆写米色 */
  padding: 24px 0 48px;
}

/* ====== 7. 激活码引导横幅 (P0 商业化 — 未登录用户第一眼看到) ====== */
.activation-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 24px;
  margin-bottom: 22px;
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 1px solid #FCD34D;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.10);
  position: relative;
  overflow: hidden;
}

.activation-banner::before {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.18) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.activation-banner__content {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.activation-banner__icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}

.activation-banner__text {
  min-width: 0;
}

.activation-banner__title {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 700;
  color: #92400E;
  letter-spacing: -0.01em;
}

.activation-banner__sub {
  margin: 0;
  font-size: 13px;
  color: #B45309;
  line-height: 1.4;
}

.activation-banner__actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

@media (max-width: 640px) {
  .activation-banner {
    flex-direction: column;
    align-items: stretch;
    padding: 16px;
  }
  .activation-banner__actions {
    width: 100%;
  }
  .activation-banner__actions > * {
    flex: 1;
  }
  .activation-banner__title {
    font-size: 15px;
  }
  .activation-banner__sub {
    font-size: 12px;
  }
}

.home-container {
  max-width: 1536px;       /* Phase 23b+1: 1440 视口几乎贴边 */
  margin: 0 auto;
  padding: 0 32px;
  /* Phase 23b+2: 改 grid 双栏让 stats-side 在左列 (我的学习) */
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
}
@media (max-width: 1100px) {
  .home-container {
    grid-template-columns: 280px 1fr;
    gap: 20px;
  }
}
@media (max-width: 900px) {
  .home-container {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .home-main {
    grid-column: 1;       /* 单列时回到 col 1 */
  }
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

/* ====== 2+3+4. 两栏布局: 左侧 stats 面板 (固定不随筛选变) | 右侧 视频区 ======
   改动: .stats-side 移出 .home-main 作为 .home-container direct child
   .home-container 用 grid 320+1fr, .home-main 现在只装 videos-side */
.home-main {
  /* Phase 23b+1: sidebar 是 fixed 不占位, 不再让 margin-left:344 */
  min-width: 0;
  margin-bottom: 32px;
}

/* Phase 23b+2: 我的学习在 grid 流左列(非 fixed)
   桌面 grid 320+1fr, stats-side 第 1 列, home-main 第 2 列 */
.stats-side {
  grid-column: 1;
  position: relative;
  top: auto;
  left: auto;
  width: 320px;
  align-self: start;
  flex-shrink: 0;
  max-height: none;
  overflow: visible;
}
.home-main {
  grid-column: 2;       /* Phase 23b+2: 显式占第 2 列,即使 stats-side 不渲染也固定位置 */
  min-width: 0;
  margin-bottom: 32px;
}
@media (max-width: 1100px) {
  .stats-side {
    width: 280px;
  }
}
@media (max-width: 640px) {
  .stats-side {
    display: none;  /* 移动端走 H5 独立首页 */
  }
}

/* ============ 单 panel, 去嵌套, 轻量设计 ============ */
.stats-panel {
  background: var(--color-bg-card);
  border-radius: 18px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.05);
  border: 1px solid rgba(15, 23, 42, 0.05);
  overflow: hidden;
}

/* 顶部 header (轻量: 浅底 + 图标 + 标题 + 期数 tag) */
.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: var(--color-bg-base, #F8FAFC);
  border-bottom: 1px solid rgba(15,23,42,0.04);
}
.panel-header-icon {
  display: flex;
  width: 30px;
  height: 30px;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-brand), #1A6B52);
  color: #fff;
  border-radius: 9px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(47, 61, 53, 0.2);
}
.panel-header-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  flex: 1;
  letter-spacing: 0.2px;
}
.panel-header-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 9px;
  background: var(--color-brand-subtle)  /* Phase 24 was rgba(47,61,53,0.08) */;
  color: var(--color-brand);
  border-radius: 999px;
  letter-spacing: 0.3px;
}

/* 主进度区 (hero) */
.panel-progress {
  padding: 22px 18px 20px;
  border-bottom: 1px solid rgba(15,23,42,0.05);
  background: linear-gradient(180deg, var(--color-bg-card), #FAFBF8);
}
.progress-top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}
.progress-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}
.progress-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: -0.5px;
  line-height: 1;
}
.progress-sep {
  font-size: 18px;
  color: var(--color-text-muted);
  font-weight: 400;
  margin: 0 2px;
}
.progress-total {
  font-size: 17px;
  color: var(--color-text-muted);
  font-weight: 600;
}
.progress-track {
  height: 10px;
  background: rgba(15,23,42,0.05);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 10px;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand) 0%, #10B981 60%, #34D399 100%);
  border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: 0 0 0 1px rgba(47, 61, 53, 0.1), 0 0 12px rgba(16, 185, 129, 0.4);
  position: relative;
}
.progress-fill::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
  animation: shimmer 2.4s linear infinite;
}
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
.progress-bottom {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}
.progress-pct {
  color: var(--color-brand);
  font-weight: 700;
}
.progress-hint {
  color: var(--color-text-muted);
}

/* 3 列紧凑 stats (浅色填充卡片) */
.panel-quick-stats {
  display: flex;
  align-items: stretch;
  padding: 14px 14px;
  gap: 8px;
}
.qs-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  text-align: center;
  padding: 12px 6px;
  border-radius: 12px;
  background: #FAFBF8;
  transition: transform 0.18s ease;
}
.qs-item:hover {
  transform: translateY(-1px);
}
.qs-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-bottom: 2px;
}
.qs-icon-total { background: var(--color-brand-subtle)  /* Phase 24 was rgba(47,61,53,0.10) */; color: var(--color-brand); }
.qs-icon-unlearned { background: rgba(217, 119, 6, 0.10); color: #D97706; }
.qs-icon-streak { background: rgba(239, 68, 68, 0.10); color: #EF4444; }
.qs-value {
  font-size: 19px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.1;
  letter-spacing: -0.3px;
}
.qs-unit {
  font-size: 11px;
  color: var(--color-text-muted);
  font-weight: 500;
  margin-left: 1px;
}
.qs-label {
  font-size: 11px;
  color: var(--color-text-muted);
  font-weight: 500;
}
/* 去掉分隔线 (卡片各自有底色, 不需要分隔) */
.qs-divider {
  display: none;
}

/* 分割线 */
.panel-divider {
  height: 1px;
  background: rgba(15,23,42,0.05);
}

/* 月历 (紧凑) */
.panel-calendar {
  padding: 14px 18px 16px;
}
.cal-row-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.cal-title {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-primary);
}
.cal-stat {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--color-text-muted);
}
.cal-stat-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
}

.mini-calendar {
  width: 100%;
}
.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 3px;
}
.cal-weekday {
  text-align: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-muted);
  padding: 2px 0;
}
.cal-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}
.cal-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-secondary);
  border-radius: 6px;
  cursor: default;
  transition: all 0.15s ease;
}
.cal-day.other-month {
  color: rgba(15,23,42,0.18);
}
.cal-day.has-record {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
  font-weight: 700;
}
.cal-day.today {
  background: linear-gradient(135deg, var(--color-brand), #10B981);
  color: #fff;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(47, 61, 53, 0.3);
}

/* ====== 继续学习 mini-card ====== */
/* 7-1: 顶层 section — 桌面横排, H5 满宽列表 (从 stats-side 挪出, H5 不再被隐藏) */
.continue-learning-section {
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border, rgba(15, 23, 42, 0.06));
  border-radius: 14px;
  padding: 16px 18px 18px;
  margin-bottom: 20px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}
@media (max-width: 640px) {
  .continue-learning-section {
    border-radius: 10px;
    padding: 12px 14px 14px;
    margin-bottom: 14px;
  }
}
.panel-continue {
  padding: 0;
}
.pc-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--color-text-secondary);
}
.pc-head svg { color: var(--color-brand); }
.pc-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  flex: 1;
  letter-spacing: 0.2px;
}
.pc-count {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  background: var(--color-brand-subtle)  /* Phase 24 was rgba(47,61,53,0.08) */;
  color: var(--color-brand);
  border-radius: 999px;
}
.pc-list { display: flex; flex-direction: column; gap: 10px; }
.pc-item {
  display: flex;
  gap: 11px;
  align-items: center;
  padding: 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.15s ease;
  background: transparent;
}
.pc-item:hover {
  background: var(--color-brand-subtle)  /* Phase 24 was rgba(47,61,53,0.04) */;
  transform: translateX(2px);
}
.pc-cover {
  position: relative;
  width: 56px;
  height: 40px;
  border-radius: 7px;
  overflow: hidden;
  background: linear-gradient(135deg, #C9D6BE, #94A88B);
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.1);
}
.pc-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.pc-cover-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.85);
}
.pc-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 5px; }
.pc-title-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}
.pc-progress-row { display: flex; align-items: center; gap: 8px; }
.pc-progress-track {
  flex: 1;
  height: 4px;
  background: var(--color-brand-subtle)  /* Phase 24 was rgba(47,61,53,0.08) */;
  border-radius: 2px;
  overflow: hidden;
}
.pc-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand), #10B981);
  border-radius: 2px;
  transition: width 0.4s ease;
}
.pc-pct {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
.pc-empty {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(47, 61, 53, 0.04), rgba(16, 185, 129, 0.04));
  border: 1px dashed rgba(47, 61, 53, 0.18);
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-brand);
}
.pc-empty:hover {
  background: linear-gradient(135deg, rgba(47, 61, 53, 0.08), rgba(16, 185, 129, 0.08));
  border-color: rgba(47, 61, 53, 0.3);
}
.pc-empty-text { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.pc-empty-title { font-size: 13px; font-weight: 600; }
.pc-empty-sub { font-size: 11px; color: var(--color-text-muted); font-weight: 500; }

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
  grid-template-columns: repeat(3, minmax(0, 1fr));
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
  display: block;
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
    margin-left: 0;  /* H5: 取消 PC 的 344px margin,占满 viewport */
  }
  .stats-side {
    display: none;  /* H5: 隐藏 stats-side (mobile 不显示) */
  }
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .home-footer {
    display: block;
  }
}

/* ====== Phase 5 (H5): Home 16:9 视频通栏 ====== */
/* H5 (≤ 640px): 视频网格本身扩展到屏幕边缘 (通栏 16:9) — YouTube/B站 风格
   .home-container 有 16px 横向 padding, 用负 margin 抵消让 .video-grid 真正"贴边"
   标题/计数 (.section-head) 保留在容器内, 只视频卡片通栏
   同时增加卡片间距, 大标题字体, 适配手机阅读 */
@media (max-width: 640px) {
  .video-grid {
    grid-template-columns: 1fr;
    gap: 22px;                /* 卡片之间留呼吸空间 */
    margin: 0 -16px;          /* 抵消 .home-container padding: 0 16px — 通栏 */
  }
  /* 卡片在 H5 端去掉圆角阴影外框, 走"视频流"风 */
  .video-grid .video-card {
    border-radius: 0;
    border: none;
    box-shadow: none;
    background: transparent;
  }
  .video-grid .video-card:hover {
    transform: none;
    box-shadow: none;
  }
  .video-grid .video-info {
    padding: 12px 16px 8px;
  }
  .video-grid .video-title {
    font-size: 18px;
    line-height: 1.4;
    margin-bottom: 6px;
  }
  .video-grid .video-description {
    font-size: 13px;
  }
  .video-grid .duration {
    bottom: 10px;
    right: 10px;
    font-size: 12px;
    padding: 4px 8px;
  }
  .video-grid .fav-heart {
    top: 10px;
    right: 10px;
    width: 34px;
    height: 34px;
  }
}

/* H5 (≤ 640px): 隐藏"我的学习"面板 — H5 不要这块, 留出空间给视频流 */
@media (max-width: 640px) {
  .stats-side {
    display: none;
  }
  .home-main {
    grid-template-columns: 1fr;
  }
  /* 隐藏底部"学习消息/学习指南/联系我们" — H5 端不要这堆引导内容 */
  .home-footer--h5-hide {
    display: none;
  }
}

@media (max-width: 640px) {
  .home-container { padding: 0 16px; }
  .filter-label { min-width: auto; }
  .panel-quick-stats {
    padding: 12px 14px;
  }
  .panel-progress {
    padding: 16px 14px 14px;
  }
  .progress-value {
    font-size: 22px;
  }
  .video-grid {
    grid-template-columns: 1fr;
  }
  .featured-info { padding: 20px 18px; }
}

/* ============================================================ */
/* Phase 22: H5 端 (iPhone 等 ≤768px) — 独立紧凑单列布局          */
/* 设计原则:                                                     */
/*   - 月历条驱动 (H5 学习闭环可视化)                            */
/*   - 双层 Tag (场景 + 难度, 替代桌面横排)                      */
/*   - 单列大图卡 (16:9 封面 + 原图无蒙层, 跟现有飘绿蒙层划清)  */
/*   - 进度条 (已学视频显示绿色细线)                            */
/* ============================================================ */
.home-h5-block { display: none; }
@media (max-width: 768px) {
  .home-h5-block {
    display: block;
    padding-top: 8px;
  }
  /* 桌面端 stats-side / home-main / activation-banner / video-grid-section
     / filter-row / home-footer 等在 H5 时全部隐藏 */
  .stats-side,
  .home-main,
  .home-footer,
  .filter-row,
  .video-grid-section,
  .activation-banner {
    display: none !important;
  }
  /* H5 时 home-container 取消 grid, 单列流 */
  .home-container {
    display: block !important;
    max-width: 100% !important;
    padding: 0 !important;
    gap: 0 !important;
    /* Phase 25 P2-B: H5 整页 mint 渐变底色 (对标 speakvlog 范式;
       Vision 反馈略加深让品牌感更强) */  }
}

/* 标题区 */
.h5-home-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 8px 16px 12px;
}
.h5-home-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text-primary, #0F172A);
  letter-spacing: -0.01em;
  margin: 0;
}
.h5-home-count {
  font-size: 12px;
  color: var(--color-text-muted, #94A3B8);
  font-weight: 500;
}

/* Phase 24 P0: H5 Hero banner — 简洁文字引导 + 草绿底纹 */
.h5-home-hero {
  padding: 24px 20px 20px;
  margin: 0 16px 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--color-brand-subtle) 0%, #E8F3EA 100%);
  border: 1px solid var(--color-brand-light);
}
.h5-home-hero__title {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.25;
  color: var(--color-brand);
  letter-spacing: -0.01em;
  margin-bottom: 6px;
}
.h5-home-hero__sub {
  font-size: 13px;
  color: var(--color-text-secondary, #5A6B62);
  line-height: 1.5;
}

/* Phase 25 P1: H5 4 项 stats 论据 (speakvlog 范式: 数字 + 标签) */


/* Phase 25 P1: H5 社会证明 (头像簇 + "X 名同学") */
.h5-home-social {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin: 0 0 16px;
}
.h5-home-social__avatars {
  display: flex;
  flex-shrink: 0;
}
.h5-home-social__avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--color-bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-left: -8px;  /* 重叠 */
}
.h5-home-social__avatar:first-child { margin-left: 0; }
.h5-home-social__text {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}
.h5-home-social__text strong {
  color: var(--color-text-primary);
  font-weight: 700;
}

/* Phase 24 P0: H5 单层分类 chip horizontal scroll */
.h5-home-chips {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 0 16px 16px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.h5-home-chips::-webkit-scrollbar { display: none; }
.h5-home-chip {
  flex-shrink: 0;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 9999px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 150ms ease;
  white-space: nowrap;
}
.h5-home-chip:active { transform: scale(0.96); }
.h5-home-chip.is-active {
  background: var(--color-brand);
  color: #fff;
  border-color: var(--color-brand);
}
.h5-home-feature {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
}

/* 单列视频卡片流 */
.h5-home-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 0 16px 16px;
}

.h5-home-card {
  background: white;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 120ms ease, box-shadow 120ms ease;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 0 0 1px rgba(15, 23, 42, 0.04);
  -webkit-tap-highlight-color: transparent;
}
.h5-home-card:active {
  transform: scale(0.99);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06), 0 0 0 1px rgba(15, 23, 42, 0.06);
}

.h5-home-card__cover {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%);
  overflow: hidden;
}
.h5-home-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.h5-home-card__cover-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted, #94A3B8);
}

.h5-home-card__duration {
  position: absolute;
  right: 8px;
  bottom: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.02em;
}

.h5-home-card__diff {
  position: absolute;
  left: 8px;
  top: 8px;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.95);
  color: var(--color-text-primary, #0F172A);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
/* Phase 25 P2-D: 难度 chip 5 色 → 3 组 (初级/中级/高级), 视觉一致 */
.h5-home-card__diff[data-diff="1"] { background: rgba(77, 160, 108, 0.15); color: #2F3D35; }     /* 初级 - 草绿底 + 墨绿字 */
.h5-home-card__diff[data-diff="2"] { background: rgba(245, 158, 11, 0.15); color: #B45309; }   /* 中级 - 琥珀 */
.h5-home-card__diff[data-diff="3"] { background: rgba(245, 158, 11, 0.15); color: #B45309; }   /* 中级 - 琥珀 */
.h5-home-card__diff[data-diff="4"] { background: rgba(220, 38, 38, 0.12); color: #B91C1C; }    /* 高级 - 红 */
.h5-home-card__diff[data-diff="5"] { background: rgba(220, 38, 38, 0.12); color: #B91C1C; }    /* 高级 - 红 */

.h5-home-card__body {
  padding: 12px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.h5-home-card__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary, #0F172A);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.h5-home-card__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-muted, #94A3B8);
}
.h5-home-card__cat {
  padding: 2px 6px;
  background: rgba(15, 23, 42, 0.04);
  border-radius: 4px;
  font-weight: 500;
  color: var(--color-text-secondary, #475569);
}
.h5-home-card__views::before {
  content: '·';
  margin-right: 6px;
  opacity: 0.5;
}

.h5-home-card__progress {
  height: 4px;
  background: rgba(15, 23, 42, 0.05);
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 4px;
}
.h5-home-card__progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #34D399 0%, #10B981 100%);
  border-radius: 9999px;
  transition: width 200ms ease;
}

/* 加载更多按钮 */
.h5-home-loadmore {
  display: flex;
  justify-content: center;
  margin-top: 4px;
}
.h5-home-loadmore__btn {
  padding: 10px 24px;
  background: white;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary, #475569);
  cursor: pointer;
  transition: background 120ms ease;
}
.h5-home-loadmore__btn:active { background: rgba(15, 23, 42, 0.04); }
.h5-home-loadmore__btn:disabled { opacity: 0.5; }
</style>
