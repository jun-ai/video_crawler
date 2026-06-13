<template>
  <div class="yt-home">
    <!-- Hero Section — SpeakVlog 风格：全宽大标题 + 4 组统计 -->
    <section class="home-hero">
      <div class="hero-inner">
        <div class="hero-eyebrow">— speak · every day —</div>
        <h1 class="hero-title">
          <span class="hero-title-a">看视频</span>
          <span class="hero-title-b">学英语</span>
        </h1>
        <p class="hero-subtitle">沉浸式练口语 · 真实语料 · AI 解读</p>
        <div class="hero-actions">
          <button class="hero-cta-primary" @click="$router.push('/learning-center')">
            开始学习
            <span class="hero-cta-arrow">→</span>
          </button>
          <button class="hero-cta-secondary" @click="scrollToVideos">查看视频库</button>
        </div>

        <!-- 4 组统计 (SpeakVlog 风格) -->
        <div class="hero-stats">
          <div class="hero-stat">
            <div class="hero-stat-value">{{ stats.total }}</div>
            <div class="hero-stat-label">总期数</div>
          </div>
          <div class="hero-stat-divider"></div>
          <div class="hero-stat">
            <div class="hero-stat-value hero-stat-learned">{{ stats.learned }}</div>
            <div class="hero-stat-label">已学习</div>
          </div>
          <div class="hero-stat-divider"></div>
          <div class="hero-stat">
            <div class="hero-stat-value hero-stat-unlearned">{{ stats.unlearned }}</div>
            <div class="hero-stat-label">未学习</div>
          </div>
          <div class="hero-stat-divider"></div>
          <div class="hero-stat">
            <div class="hero-stat-value hero-stat-streak">
              {{ calendarData.streak }}
              <span class="hero-stat-unit">天</span>
            </div>
            <div class="hero-stat-label">连续打卡</div>
          </div>
        </div>
      </div>

      <div class="hero-decor" aria-hidden="true">
        <BookOpen :size="56" class="decor-icon decor-icon-1" />
        <Sparkles :size="36" class="decor-icon decor-icon-2" />
        <Headphones :size="44" class="decor-icon decor-icon-3" />
      </div>
    </section>

    <!-- Mobile Top Stats (visible < 768px) -->
    <div class="mobile-stats-bar" v-if="userStore.isLoggedIn">
      <div class="mobile-stats-scroll">
        <div class="mobile-stat-chip">
          <BarChart3 :size="14" />
          <span>{{ stats.learned }}/{{ stats.total }}</span>
        </div>
        <div class="mobile-stat-chip mobile-stat-streak">
          <Flame :size="14" />
          <span>{{ calendarData.streak }}天连续</span>
        </div>
        <div class="mobile-stat-chip mobile-stat-month">
          <span>{{ formatMinutes(calendarData.monthly_minutes) }}本月</span>
        </div>
      </div>
    </div>

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

        <!-- 继续学习快捷入口 — SpeakVlog 免费试看风格（Phase 0+） -->
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
                  <Play :size="32" />
                </div>
                <!-- 暗色遮罩 + 标题 -->
                <div class="cl-cover-overlay">
                  <div class="cl-cover-title">{{ item.title || '未命名' }}</div>
                </div>
                <!-- 进度条 -->
                <div class="cl-progress-bar">
                  <div class="cl-progress-fill" :style="{ width: item.progress + '%' }"></div>
                </div>
              </div>
              <div class="cl-card-info">
                <div class="cl-card-meta">
                  <span class="cl-progress-text">{{ item.progress }}%</span>
                  <span class="cl-continue-btn">继续学习 →</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 学习功能清单 — SpeakVlog 风格（Phase 0+） -->
        <section class="features-section">
          <div class="features-grid">
            <div class="features-intro">
              <div class="features-eyebrow">为什么选 Fluenty</div>
              <h2 class="features-title">不只是看视频，<br/>是真正用英语</h2>
              <p class="features-desc">真实语料 · AI 解读 · 间隔重复，<br/>把被动刷剧变成主动输出。</p>
            </div>
            <div class="features-list">
              <div v-for="feat in features" :key="feat.title" class="feature-item">
                <div class="feature-check">
                  <Check :size="18" />
                </div>
                <div class="feature-text">
                  <div class="feature-title">{{ feat.title }}</div>
                  <div class="feature-desc-sm">{{ feat.desc }}</div>
                </div>
              </div>
            </div>
          </div>
        </section>

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

        <!-- FAQ 手风琴 — SpeakVlog 风格（Phase 0+） -->
        <section class="faq-section">
          <div class="faq-header">
            <div class="faq-eyebrow">FAQ</div>
            <h2 class="faq-title">常见问题</h2>
            <p class="faq-desc">刚开始？这里有你需要知道的。</p>
          </div>
          <div class="faq-list">
            <div
              v-for="(item, idx) in faqs"
              :key="idx"
              class="faq-item"
              :class="{ open: openFaqIdx === idx }"
            >
              <button
                class="faq-question"
                @click="toggleFaq(idx)"
                :aria-expanded="openFaqIdx === idx"
              >
                <span>{{ item.q }}</span>
                <ChevronDown :size="20" class="faq-icon" />
              </button>
              <div class="faq-answer" v-show="openFaqIdx === idx">
                <div class="faq-answer-inner">{{ item.a }}</div>
              </div>
            </div>
          </div>
        </section>

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
import { BarChart3, Calendar, Clock, Play, Flame, Sprout, Dumbbell, Star, Trophy, Crown, Target, Sparkles, BookOpen, Headphones, Check, ChevronDown } from 'lucide-vue-next'
import SfTooltip from '@/components/ui/SfTooltip.vue'
import SfProgress from '@/components/ui/SfProgress.vue'
import SfButton from '@/components/ui/SfButton.vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const loadingMore = ref(false)
const categories = ref([])
// Phase 0+ FAQ 手风琴
const faqs = [
  {
    q: 'Fluenty 怎么用？',
    a: '三步：选感兴趣的视频 → 边看边学（字幕 / 跟读 / AI 解读）→ 自动收词复习。每天 10 分钟就能积累。'
  },
  {
    q: '视频内容从哪来？',
    a: '我们从 YouTube / TED 等海外平台精选真实语料，覆盖访谈、演讲、科普、生活等场景，所有视频都有人工审核。'
  },
  {
    q: '适合什么英语水平？',
    a: 'CET-4 以上即可流畅使用。每个视频有难度标签，从 A2（基础）到 C1（高级）都有，可按自己水平选。'
  },
  {
    q: '免费还是收费？',
    a: '注册即送 7 天会员，全功能可体验。会员按月 / 年订阅，解锁全部视频 + 高级 AI 解读。'
  },
  {
    q: '手机上能用吗？',
    a: '完美支持。网页 PWA 体验，地铁 / 通勤路上都能用。视频支持倍速 / 字幕跟读切换。'
  },
  {
    q: '学习进度会丢吗？',
    a: '不会。所有进度 / 笔记 / 收藏都云端永久保存。换设备登录就能继续。'
  }
]
const openFaqIdx = ref(null)
const toggleFaq = (idx) => {
  openFaqIdx.value = openFaqIdx.value === idx ? null : idx
}

// Phase 0+ SpeakVlog 风格 — 学习功能清单（首页介绍用）
const features = [
  { title: '真实视频语料', desc: '海外 YouTube / TED 精选' },
  { title: 'AI 智能解读', desc: '逐句翻译 + 重点标注' },
  { title: '字幕跟读练习', desc: '影子跟读 + 语速调节' },
  { title: '生词一键收藏', desc: '自动收录到词汇本' },
  { title: '间隔重复复习', desc: '艾宾浩斯曲线不遗忘' },
  { title: '连续打卡激励', desc: '每天 10 分钟养成习惯' },
  { title: '学习数据统计', desc: '日 / 周 / 月多维图表' },
  { title: '移动端友好', desc: '通勤路上也能学' },
  { title: '收藏夹整理', desc: '喜欢的视频分类存' },
  { title: '跟读 AI 打分', desc: '发音准确度反馈' },
  { title: '永久云端保存', desc: '进度 / 笔记不丢失' },
  { title: '免费体验', desc: '注册即送 7 天会员' }
]
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
/* ============================================================
   Home.vue — Phase 1A CSS-only Redesign
   Hero + Mobile sidebar + Chip + Video card Bento
   ============================================================ */

.yt-home {
  max-width: 1600px;
  margin: 0 auto;
}

/* ====== Hero Section — SpeakVlog 风格（Phase 0+） ====== */
.home-hero {
  position: relative;
  background: var(--yt-brand-gradient, linear-gradient(135deg, #0F4C3A 0%, #1A6B4F 50%, #E2725B 100%));
  border-radius: 0; /* 全宽：去掉圆角包裹 */
  padding: 88px 48px 64px;
  margin-bottom: 0;
  overflow: hidden;
  min-height: 420px;
  display: flex;
  align-items: center;
}

.home-hero::before {
  /* 顶部薄荷绿光晕，呼应 SpeakVlog section 过渡 */
  content: '';
  position: absolute;
  top: -40%;
  right: -10%;
  width: 60%;
  height: 180%;
  background: radial-gradient(circle, rgba(63, 138, 91, 0.18) 0%, transparent 60%);
  pointer-events: none;
}

.hero-inner {
  position: relative;
  z-index: 2;
  max-width: 720px;
  width: 100%;
}

/* Eyebrow 小标签 */
.hero-eyebrow {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 2px;
  text-transform: lowercase;
  margin-bottom: 20px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

/* 大标题 — 分色 */
.hero-title {
  font-size: var(--text-hero, clamp(48px, 6vw, 84px));
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -2px;
  margin: 0 0 18px;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.15);
}

.hero-title-a {
  color: #4DA06C; /* 品牌亮绿 */
  display: inline-block;
}

.hero-title-b {
  color: #fff;
  display: inline-block;
  margin-left: 0.15em;
}

.hero-subtitle {
  font-size: 18px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.85);
  margin: 0 0 32px;
  line-height: 1.5;
  letter-spacing: 0.3px;
  max-width: 480px;
}

/* CTA 按钮组 */
.hero-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 56px;
}

.hero-cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  border: none;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(63, 138, 91, 0.4);
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.25s ease;
  min-height: 48px;
}

.hero-cta-primary:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 10px 28px rgba(63, 138, 91, 0.5);
}

.hero-cta-primary:active {
  transform: translateY(0) scale(1);
}

.hero-cta-arrow {
  display: inline-block;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  font-size: 18px;
  line-height: 1;
}

.hero-cta-primary:hover .hero-cta-arrow {
  transform: translateX(4px);
}

.hero-cta-secondary {
  display: inline-flex;
  align-items: center;
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  border: 1.5px solid rgba(255, 255, 255, 0.35);
  border-radius: 999px;
  cursor: pointer;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.25s ease;
  min-height: 48px;
}

.hero-cta-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.55);
  transform: translateY(-2px);
}

/* 4 组统计 — SpeakVlog 大数字风格 */
.hero-stats {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 24px 28px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  max-width: 640px;
}

.hero-stat {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hero-stat-value {
  font-size: 36px;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  letter-spacing: -1px;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.hero-stat-unit {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0;
}

.hero-stat-learned {
  color: #6FE89A; /* 已学 — 浅亮绿 */
}

.hero-stat-unlearned {
  color: #FFB89C; /* 未学 — 暖橙 */
}

.hero-stat-streak {
  color: #FFD27A; /* 连续打卡 — 暖黄 */
}

.hero-stat-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.65);
  letter-spacing: 0.5px;
}

.hero-stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
}

/* Hero 装饰图标 */
.hero-decor {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  pointer-events: none;
}

.decor-icon {
  position: absolute;
  color: rgba(255, 255, 255, 0.12);
}

.decor-icon-1 {
  right: 0;
  top: -40px;
}

.decor-icon-2 {
  right: 130px;
  top: 30px;
  animation: float-slow 6s ease-in-out infinite;
}

.decor-icon-3 {
  right: 30px;
  top: 80px;
  animation: float-slow 5s ease-in-out infinite reverse;
}

@keyframes float-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

/* ====== Mobile Stats Bar ====== */
.mobile-stats-bar {
  display: none;
  margin-bottom: 16px;
  background: var(--color-brand-subtle, #E8F0EB);
  border-radius: var(--radius-lg, 16px);
  padding: 10px 14px;
  border: 1px solid var(--color-border, #E5E5DE);
}

.mobile-stats-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.mobile-stats-scroll::-webkit-scrollbar {
  display: none;
}

.mobile-stat-chip {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 14px;
  background: var(--color-bg-card, #FFFFFF);
  border: 1px solid var(--color-border, #E5E5DE);
  border-radius: var(--radius-md, 12px);
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary, #1A2B22);
  white-space: nowrap;
  scroll-snap-align: start;
}

.mobile-stat-chip svg {
  color: var(--color-brand, #0F4C3A);
}

.mobile-stat-streak svg {
  color: var(--color-accent, #E2725B);
}

.mobile-stat-month {
  color: var(--color-text-secondary, #5A6B62);
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
  transition: box-shadow var(--transition-normal), border-color var(--transition-normal);
}

.sidebar-card:hover {
  box-shadow: var(--shadow-hover);
  border-color: color-mix(in srgb, var(--color-brand) 25%, var(--color-border));
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
  border: 1px solid color-mix(in srgb, var(--color-brand) 12%, transparent);
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
  transition: background var(--transition-normal), border-color var(--transition-normal);
  border: 1px solid transparent;
}

.recent-item:hover {
  background: var(--color-brand-subtle);
  border-color: var(--color-border);
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
  gap: 8px;
  overflow-x: auto;
  padding: 2px 0;
  scrollbar-width: none;
}

.tag-chips::-webkit-scrollbar {
  display: none;
}

.tag-chip {
  padding: 8px 16px;
  border-radius: 999px; /* Phase 0+ 药丸 */
  font-size: 13px;
  font-weight: 500;
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1.5px solid var(--color-border);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  white-space: nowrap;
  flex-shrink: 0;
  user-select: none;
}

.tag-chip:hover {
  border-color: var(--color-brand-bright);
  color: var(--color-brand-bright);
  background: var(--color-bg-pale);
  transform: translateY(-1px);
}

.tag-chip.active {
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(63, 138, 91, 0.3);
}

/* ====== 学习功能清单 — SpeakVlog 风格 ====== */
.features-section {
  padding: 80px 32px;
  background: var(--color-bg-pale);
  margin: 32px 0;
  border-radius: 24px;
}

.features-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 64px;
  align-items: start;
}

.features-intro {
  position: sticky;
  top: 88px;
}

.features-eyebrow {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-brand-bright);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 16px;
  padding-top: 6px;
  border-top: 2px solid var(--color-brand-bright);
}

.features-title {
  font-size: var(--text-section, clamp(30px, 3.5vw, 44px));
  font-weight: 800;
  color: var(--color-text-primary);
  margin: 0 0 16px;
  line-height: 1.15;
  letter-spacing: -1px;
}

.features-desc {
  font-size: 16px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

.features-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px 24px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  background: var(--color-bg-card);
  border-radius: 14px;
  border: 1px solid var(--color-border);
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  border-color: var(--color-brand-bright);
  box-shadow: 0 8px 20px rgba(15, 76, 58, 0.08);
}

.feature-check {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-mint);
  color: var(--color-brand-bright);
  border-radius: 10px;
  font-weight: 700;
}

.feature-text {
  flex: 1;
  min-width: 0;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.3;
  margin-bottom: 2px;
}

.feature-desc-sm {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.4;
}

/* ====== FAQ 手风琴 — SpeakVlog 风格 ====== */
.faq-section {
  padding: 80px 32px;
  margin: 32px 0;
  background: var(--color-bg-card);
  border-radius: 24px;
  border: 1px solid var(--color-border);
}

.faq-header {
  text-align: center;
  margin-bottom: 48px;
}

.faq-eyebrow {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-brand-bright);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.faq-title {
  font-size: var(--text-section, clamp(30px, 3.5vw, 44px));
  font-weight: 800;
  color: var(--color-text-primary);
  margin: 0 0 8px;
  letter-spacing: -1px;
}

.faq-desc {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin: 0;
}

.faq-list {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-item {
  background: var(--color-bg-base);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

.faq-item.open {
  border-color: var(--color-brand-bright);
  box-shadow: 0 4px 16px rgba(15, 76, 58, 0.06);
}

.faq-question {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  padding: 18px 22px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: inherit;
  transition: color 0.2s ease;
}

.faq-question:hover {
  color: var(--color-brand-bright);
}

.faq-icon {
  flex-shrink: 0;
  color: var(--color-brand-bright);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.faq-item.open .faq-icon {
  transform: rotate(180deg);
}

.faq-answer {
  overflow: hidden;
}

.faq-answer-inner {
  padding: 0 22px 20px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--color-text-secondary);
}

/* 视频网格 — Bento 化 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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

/* ====== 继续学习快捷入口 — SpeakVlog 免费试看风格（Phase 0+） ====== */
.continue-learn-section {
  margin-bottom: 24px;
}
.continue-learn-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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
  gap: 16px;
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
  width: 320px; /* Phase 0+ 放大 */
  background: var(--color-bg-card);
  border-radius: 24px; /* Phase 0+ 大圆角 */
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--color-border);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease, border-color 0.3s ease;
  scroll-snap-align: start;
}
.continue-learn-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 16px 40px rgba(15, 76, 58, 0.15);
  border-color: var(--color-brand-bright);
}
.cl-card-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9; /* Phase 0+ 强制 16:9 */
  background: var(--color-bg-elevated);
  overflow: hidden;
}
.cl-card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.continue-learn-card:hover .cl-card-cover img {
  transform: scale(1.05);
}
.cl-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  background: linear-gradient(135deg, var(--color-bg-pale) 0%, var(--color-bg-mint) 100%);
}
.cl-cover-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  padding: 14px 16px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75) 0%, rgba(0, 0, 0, 0.2) 50%, transparent 100%);
  pointer-events: none;
}
.cl-cover-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
.cl-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
  z-index: 2;
}
.cl-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4DA06C 0%, #6FE89A 100%);
  transition: width 0.3s ease;
  border-radius: 0 2px 2px 0;
}
.cl-card-info {
  padding: 10px 14px 12px;
}
.cl-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cl-progress-text {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-brand-bright);
}
.cl-continue-btn {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-muted);
  transition: color 0.2s ease, transform 0.2s ease;
}
.continue-learn-card:hover .cl-continue-btn {
  color: var(--color-brand-bright);
  transform: translateX(2px);
}

/* ====== 响应式 ====== */
@media (max-width: 1200px) {
  .home-sidebar {
    flex: 0 0 260px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
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

  .features-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .features-intro {
    position: static;
  }
}

@media (max-width: 768px) {
  /* Hero — 全宽 SpeakVlog 风格（mobile） */
  .home-hero {
    padding: 56px 20px 40px;
    min-height: 360px;
  }

  .hero-eyebrow {
    font-size: 11px;
    padding: 5px 12px;
    margin-bottom: 14px;
  }

  .hero-title {
    font-size: clamp(36px, 9vw, 48px);
    letter-spacing: -1px;
    margin-bottom: 14px;
  }

  .hero-subtitle {
    font-size: 15px;
    margin-bottom: 24px;
  }

  .hero-actions {
    margin-bottom: 36px;
    gap: 10px;
  }

  .hero-cta-primary,
  .hero-cta-secondary {
    padding: 13px 24px;
    font-size: 14px;
    min-height: 48px;
    flex: 1;
    justify-content: center;
  }

  .hero-stats {
    padding: 18px 16px;
    gap: 12px;
    border-radius: 16px;
  }

  .hero-stat-value {
    font-size: 24px;
  }

  .hero-stat-unit {
    font-size: 12px;
  }

  .hero-stat-label {
    font-size: 11px;
  }

  .hero-stat-divider {
    height: 28px;
  }

  .hero-decor {
    display: none;
  }

  /* Mobile stats bar 可见 */
  .mobile-stats-bar {
    display: block;
  }

  /* 隐藏桌面 sidebar */
  .home-sidebar {
    display: none;
  }

  .filter-bar {
    margin: 0 -16px 16px;
    padding: 12px 16px;
  }

  .tag-chip {
    padding: 6px 12px;
    font-size: 12px;
    border-radius: 12px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }

  /* Features mobile */
  .features-section {
    padding: 48px 20px;
    border-radius: 18px;
  }

  .features-list {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .features-title {
    font-size: 26px;
  }

  /* FAQ mobile */
  .faq-section {
    padding: 48px 20px;
    border-radius: 18px;
  }

  .faq-header {
    margin-bottom: 32px;
  }

  .faq-question {
    padding: 14px 18px;
    font-size: 14px;
  }

  .faq-answer-inner {
    padding: 0 18px 16px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .home-hero {
    padding: 44px 16px 32px;
    min-height: 320px;
  }

  .hero-eyebrow {
    font-size: 10px;
    padding: 4px 10px;
    letter-spacing: 1.5px;
  }

  .hero-title {
    font-size: 32px;
    letter-spacing: -0.5px;
  }

  .hero-subtitle {
    font-size: 13px;
    margin-bottom: 20px;
  }

  .hero-actions {
    flex-direction: column;
    margin-bottom: 28px;
  }

  .hero-cta-primary,
  .hero-cta-secondary {
    width: 100%;
  }

  .hero-stats {
    padding: 14px 12px;
    gap: 8px;
  }

  .hero-stat-value {
    font-size: 20px;
  }

  .hero-stat-label {
    font-size: 10px;
  }

  .hero-stat-divider {
    height: 24px;
  }

  .video-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}
</style>
