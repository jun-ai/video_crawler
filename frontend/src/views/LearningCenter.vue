<template>
  <div class="yt-learning-center">
    <SfEmpty v-if="!userStore.isLoggedIn" description="请先登录查看学习记录">
      <SfButton type="primary" @click="$router.push('/login')">去登录</SfButton>
    </SfEmpty>

    <template v-else>
      <!-- 统计卡片 -->
      <div class="stats-section" v-loading="statsLoading">
        <div class="stats-header">
          <PageHeader title="学习统计">
            <template #actions>
              <div class="streak-badge" v-if="stats.streak_days > 0">
                <Flame :size="16" class="streak-flame-icon" />
                连续 {{ stats.streak_days }} 天
              </div>
            </template>
          </PageHeader>
        </div>
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_materials }}</div>
            <div class="stat-label">学习材料</div>
          </div>
          <div class="stat-card completed">
            <div class="stat-value">{{ stats.completed_materials }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-card progress">
            <div class="stat-value">{{ stats.in_progress_materials }}</div>
            <div class="stat-label">学习中</div>
          </div>
          <div class="stat-card vocabulary">
            <div class="stat-value">{{ stats.mastered_vocabulary }}/{{ stats.total_vocabulary }}</div>
            <div class="stat-label">已掌握生词</div>
          </div>
          <div class="stat-card watch-time" v-if="stats.total_watch_minutes > 0">
            <div class="stat-value" v-html="formatWatchTime(stats.total_watch_minutes)"></div>
            <div class="stat-label">总观看时长</div>
          </div>
        </div>
        <div class="streak-info">
          <div class="streak-item">
            <Calendar :size="16" />
            <span>累计学习 <strong>{{ stats.total_learning_days }}</strong> 天</span>
          </div>
          <div class="streak-item">
            <TrendingUp :size="16" />
            <span>本周学习 <strong>{{ stats.this_week_learning_days }}</strong> 天</span>
          </div>
          <div class="streak-item streak-hot" v-if="stats.streak_days > 0">
            <Flame :size="16" class="streak-fire-icon" />
            <span>连续 <strong class="streak-highlight">{{ stats.streak_days }}</strong> 天</span>
          </div>
        </div>

        <!-- 学习趋势图表 -->
        <div class="trend-chart-section" v-if="trendData.dates && trendData.dates.length > 0">
          <div class="trend-chart-header">
            <span class="trend-chart-title" id="trend-chart-title">近 7 天学习趋势</span>
          </div>
          <div class="trend-chart">
            <!-- 3.4 SVG 无障碍: role + aria-labelledby + title + desc + aria-hidden 装饰元素 -->
            <svg viewBox="0 0 100 50" preserveAspectRatio="none" class="chart-svg"
                 role="img" aria-labelledby="trend-chart-title trend-chart-desc">
              <title id="trend-chart-title">近 7 天学习趋势</title>
              <desc id="trend-chart-desc">{{ getChartDesc() }}</desc>
              <!-- 区域填充 (装饰, 屏幕阅读器跳过) -->
              <path :d="getAreaPath()" fill="rgba(37, 99, 235, 0.08)" aria-hidden="true" />
              <!-- 折线 (装饰) -->
              <path :d="getChartPath()" fill="none" stroke="var(--color-brand-bright)" stroke-width="0.6" stroke-linejoin="round" aria-hidden="true" />
              <!-- 数据点 (装饰) -->
              <circle
                v-for="(dot, i) in getChartDots()"
                :key="i"
                :cx="dot.x"
                :cy="dot.y"
                r="0.8"
                fill="var(--color-brand-bright)"
                aria-hidden="true"
              />
            </svg>
            <div class="chart-labels">
              <span
                v-for="(dot, i) in getChartDots()"
                :key="i"
                class="chart-label"
                :class="{ 'has-data': dot.v > 0 }"
              >
                <span class="chart-count" v-if="dot.v > 0">{{ dot.v }}</span>
                <span class="chart-date">{{ dot.label }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 导航 -->
      <div class="tab-section">
        <div class="tab-bar">
          <div
            :class="['tab-item', { active: activeTab === 'recent' }]"
            @click="activeTab = 'recent'"
          >
            <Play :size="14" />
            <span>最近学习</span>
            <span class="tab-count" v-if="recentList.length">{{ recentList.length }}</span>
          </div>
          <div
            :class="['tab-item', { active: activeTab === 'completed' }]"
            @click="activeTab = 'completed'"
          >
            <CircleCheck :size="14" />
            <span>已完成</span>
            <span class="tab-count" v-if="completedList.length">{{ completedList.length }}</span>
          </div>
          <div
            :class="['tab-item', { active: activeTab === 'all' }]"
            @click="activeTab = 'all'"
          >
            <List :size="14" />
            <span>全部记录</span>
            <span class="tab-count" v-if="recordsTotal">{{ recordsTotal }}</span>
          </div>
        </div>

        <!-- 筛选器（全部记录 Tab 下显示） -->
        <div class="tab-filters" v-if="activeTab === 'all'">
          <FilterChip
            :model-value="filterStatus"
            :value="null"
            label="全部"
            @update:model-value="setFilter"
          />
          <FilterChip
            :model-value="filterStatus"
            :value="false"
            label="学习中"
            @update:model-value="setFilter"
          />
          <FilterChip
            :model-value="filterStatus"
            :value="true"
            label="已完成"
            @update:model-value="setFilter"
          />
        </div>

        <!-- 最近学习 Tab -->
        <div v-show="activeTab === 'recent'" class="tab-content">
          <div class="video-grid" v-loading="recentLoading">
            <VideoCard
              v-for="item in recentList"
              :key="item.id"
              :id="item.material_id"
              :title="item.material_title"
              :cover="item.material_cover"
              :progress="item.progress"
              :difficulty="item.material_difficulty"
              :category="item.material_category"
              :show-avatar="false"
              show-play-icon
              :progress-text="getProgressText(item)"
              @click="goLearn"
            />
          </div>
          <EmptyState
            v-if="!recentLoading && recentList.length === 0"
            type="welcome"
            title="还没有学习记录"
            description="开始学习语料，记录你的学习进度"
          >
            <template #actions>
              <SfButton type="primary" @click="$router.push('/materials')">去发现语料</SfButton>
            </template>
          </EmptyState>
        </div>

        <!-- 已完成 Tab -->
        <div v-show="activeTab === 'completed'" class="tab-content">
          <div class="video-grid" v-loading="completedLoading">
            <VideoCard
              v-for="item in completedList"
              :key="item.id"
              :id="item.material_id"
              :title="item.material_title"
              :cover="item.material_cover"
              :difficulty="item.material_difficulty"
              :category="item.material_category"
              :show-avatar="false"
              show-play-icon
              completed
              @click="goLearn"
            />
          </div>
          <EmptyState
            v-if="!completedLoading && completedList.length === 0"
            title="暂无已完成的学习"
            description="完成学习材料后会显示在这里"
          />
        </div>

        <!-- 全部记录 Tab -->
        <div v-show="activeTab === 'all'" class="tab-content">
          <div class="video-grid" v-loading="recordsLoading">
            <VideoCard
              v-for="item in records"
              :key="item.id"
              :id="item.material_id"
              :title="item.material_title"
              :cover="item.material_cover"
              :progress="item.completed ? 100 : item.progress"
              :difficulty="item.material_difficulty"
              :category="item.material_category"
              :show-avatar="false"
              show-play-icon
              :completed="item.completed"
              :progress-text="getProgressText(item)"
              @click="goLearn"
            />
          </div>

          <EmptyState
            v-if="!recordsLoading && records.length === 0"
            title="暂无学习记录"
            description="开始学习语料，记录你的学习进度"
          >
            <template #actions>
              <SfButton type="primary" @click="$router.push('/materials')">去发现语料</SfButton>
            </template>
          </EmptyState>

          <!-- 分页 -->
          <div class="pagination" v-if="recordsTotal > recordsPageSize">
            <SfPagination
              :current-page="recordsPage"
              :page-size="recordsPageSize"
              :total="recordsTotal"
              @change="loadRecords"
            />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Calendar,
  TrendingUp,
  Play,
  Flame,
  List
} from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import { learningStatsAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterChip from '@/components/common/FilterChip.vue'
import VideoCard from '@/components/common/VideoCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const userStore = useUserStore()

// Tab 导航
const activeTab = ref('recent')

// 统计数据
const statsLoading = ref(false)
const stats = ref({
  total_materials: 0,
  completed_materials: 0,
  in_progress_materials: 0,
  total_vocabulary: 0,
  mastered_vocabulary: 0,
  total_learning_days: 0,
  this_week_learning_days: 0,
  streak_days: 0,
  total_watch_minutes: 0
})

// 最近学习
const recentLoading = ref(false)
const recentList = ref([])

// 已完成
const completedLoading = ref(false)
const completedList = ref([])

// 学习记录
const recordsLoading = ref(false)
const records = ref([])
const recordsPage = ref(1)
const recordsPageSize = ref(12)
const recordsTotal = ref(0)
const filterStatus = ref(null)

// 学习趋势
const trendData = ref({ dates: [], counts: [] })

const goLearn = (id) => {
  router.push(`/learn/${id}`)
}

const formatWatchTime = (minutes) => {
  if (!minutes) return '0<small>min</small>'
  if (minutes < 60) return `${minutes}<small>min</small>`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m > 0 ? `${h}<small>h</small>${m}<small>min</small>` : `${h}<small>h</small>`
}

// 获取进度文本
const getProgressText = (item) => {
  if (item.completed) return '已完成'
  if (item.last_learned_at) {
    const date = new Date(item.last_learned_at)
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    let timeLabel = ''
    if (days === 0) timeLabel = '今天'
    else if (days === 1) timeLabel = '昨天'
    else if (days < 7) timeLabel = `${days}天前`
    else timeLabel = date.toLocaleDateString()
    return `学习于${timeLabel}，看至${item.progress || 0}%`
  }
  return `进度 ${item.progress || 0}%`
}

// 设置筛选
const setFilter = (value) => {
  filterStatus.value = value
  recordsPage.value = 1
  loadRecords()
}

// 3.2 加载仪表盘: 一次 HTTP 拿 5 个视图 (stats + trend + recent + completed + records-首页)
const loadDashboard = async () => {
  statsLoading.value = true
  try {
    const data = await learningStatsAPI.getDashboard()
    stats.value = data.statistics
    trendData.value = data.trend
    recentList.value = data.recent
    completedList.value = data.completed
    records.value = data.records.items
    recordsTotal.value = data.records.total
  } catch (e) {
    console.error('加载仪表盘失败', e)
    toast.error('加载失败, 请重试')
  } finally {
    statsLoading.value = false
  }
}

// 生成 SVG 折线图数据
const getChartPath = () => {
  const { dates, counts } = trendData.value
  if (!dates || dates.length === 0) return ''
  const max = Math.max(...counts, 1)
  const w = 100
  const h = 100
  const points = counts.map((v, i) => {
    const x = (i / (dates.length - 1)) * w
    const y = h - (v / max) * h
    return `${x},${y}`
  })
  return `M ${points.join(' L ')}`
}

const getAreaPath = () => {
  const { counts } = trendData.value
  if (!counts || counts.length === 0) return ''
  const max = Math.max(...counts, 1)
  const w = 100
  const h = 100
  const points = counts.map((v, i) => {
    const x = (i / (counts.length - 1)) * w
    const y = h - (v / max) * h
    return `${x},${y}`
  })
  return `M 0,${h} L ${points.join(' L ')} L ${w},${h} Z`
}

const getChartDots = () => {
  const { dates, counts } = trendData.value
  if (!dates || dates.length === 0) return []
  const max = Math.max(...counts, 1)
  const w = 100
  const h = 100
  return counts.map((v, i) => {
    const x = (i / (counts.length - 1)) * w
    const y = h - (v / max) * h
    return { x, y, v, label: dates[i] }
  })
}

// 3.4 SVG 无障碍: 屏幕阅读器朗读, 包含数据摘要 + 每日明细
const getChartDesc = () => {
  const { dates, counts } = trendData.value
  if (!dates || dates.length === 0) return '暂无学习数据'
  const total = counts.reduce((a, b) => a + b, 0)
  const max = Math.max(...counts)
  const maxIdx = counts.indexOf(max)
  const summary = total === 0
    ? `近 7 天未学习`
    : `近 7 天共学习 ${total} 个材料, 最多 ${max} 个 (${dates[maxIdx]})`
  const detail = dates.map((d, i) => `${d}: ${counts[i]} 个`).join(', ')
  return `${summary}。每日明细: ${detail}`
}

// 加载学习记录 (翻页/过滤时调, 首屏数据由 dashboard 提供)
const loadRecords = async () => {
  recordsLoading.value = true
  try {
    const params = {
      page: recordsPage.value,
      page_size: recordsPageSize.value
    }
    if (filterStatus.value !== null) {
      params.completed = filterStatus.value
    }
    const res = await learningStatsAPI.getRecords(params)
    records.value = res.items
    recordsTotal.value = res.total
  } catch (e) {
    console.error('加载学习记录失败', e)
  } finally {
    recordsLoading.value = false
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    // 3.2 一次拿全: stats + trend + recent + completed + records 首屏
    loadDashboard()
  }
})
</script>

<style scoped>
.yt-learning-center {
  max-width: 1400px;
  margin: 0 auto;
}

/* 统计区域 */
.stats-section {
  background: var(--color-bg-base);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
}

.stats-header {
  margin-bottom: var(--spacing-md, 16px);
}

.streak-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 500;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md, 16px);
  margin-bottom: var(--spacing-md, 16px);
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: var(--color-bg-elevated);
  border-radius: 14px;
  border: 1px solid transparent;
  transition: border-color var(--sf-duration-normal), transform var(--sf-duration-normal);
}

.stat-card:hover {
  border-color: var(--color-border);
}

.stat-card .stat-value {
  font-size: var(--font-size-3xl, 28px);
  font-weight: var(--font-weight-bold, 700);
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.stat-card .stat-label {
  font-size: var(--font-size-sm, 13px);
  color: var(--color-text-secondary);
}

.stat-card.completed .stat-value {
  color: var(--color-brand-bright);
}

.stat-card.progress .stat-value {
  color: var(--color-accent);
}

.stat-card.vocabulary .stat-value {
  font-size: 22px;
  color: var(--color-brand-bright);
}

.stat-card.watch-time .stat-value {
  color: var(--color-brand-bright);
}

.stat-card.watch-time .stat-value :deep(small),
.stat-card.watch-time .stat-value small {
  color: var(--color-text-muted);
  font-size: 0.5em;
}

.streak-flame-icon {
  color: var(--color-brand-bright);
}

.streak-hot {
  color: var(--color-accent) !important;
}

.streak-highlight {
  color: var(--color-accent);
  font-size: 1.1em;
}

.streak-fire-icon {
  color: var(--color-danger);
}

.streak-info {
  display: flex;
  justify-content: center;
  gap: var(--spacing-2xl, 32px);
  padding-top: var(--spacing-md, 16px);
  border-top: 1px solid var(--color-border);
}

.streak-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 8px);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base, 14px);
}

.streak-item .el-icon {
  color: var(--color-brand-bright);
}

.streak-item strong {
  color: var(--color-text-primary);
}

/* 学习趋势图表 */
.trend-chart-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.trend-chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.trend-chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.trend-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-svg {
  width: 100%;
  height: 80px;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 0;
}

.chart-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex: 1;
}

.chart-count {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-brand-bright);
  min-height: 18px;
}

.chart-label:not(.has-data) .chart-count {
  color: transparent;
}

.chart-date {
  font-size: 10px;
  color: var(--color-text-muted);
}

/* Tab 导航区 - Pill Style */
.tab-section {
  background: var(--color-bg-base);
  border-radius: 16px;
  border: 1px solid var(--color-border);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.tab-bar {
  display: flex;
  gap: 6px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-base);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: 18px;
  background: var(--color-bg-elevated);
  border: 1px solid transparent;
  transition: all var(--sf-duration-normal);
  white-space: nowrap;
}

.tab-item:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
}

.tab-item.active {
  color: #fff;
  font-weight: 600;
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  border-color: var(--color-brand-bright);
}

.tab-item .el-icon {
  font-size: 14px;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 16px;
  padding: 0 4px;
  font-size: 10px;
  font-weight: 600;
  border-radius: 8px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}

.tab-item.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
}

/* 筛选器 */
.tab-filters {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
}

/* Tab 内容 */
.tab-content {
  padding: 16px;
  min-height: 200px;
}

/* 视频网格 */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--spacing-md, 16px);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  padding: var(--spacing-2xl, 24px) 0;
}

/* 响应式 */
@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-section {
    padding: var(--spacing-md, 16px);
    border-radius: var(--radius-md, 8px);
    margin-bottom: var(--spacing-md, 16px);
  }

  .stat-card {
    padding: var(--spacing-md, 16px);
  }

  .stat-card .stat-value {
    font-size: var(--font-size-2xl, 24px);
  }

  .streak-info {
    flex-wrap: wrap;
    gap: var(--spacing-md, 16px);
  }

  .streak-item {
    font-size: var(--font-size-sm, 13px);
  }

  .tab-bar {
    padding: 0 4px;
    overflow-x: auto;
  }

  .tab-item {
    padding: 12px 14px;
    font-size: 13px;
  }

  .tab-filters {
    padding: 10px 12px;
    flex-wrap: wrap;
  }

  .tab-content {
    padding: 12px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: var(--spacing-sm, 12px);
  }
}

@media (max-width: 480px) {
  .stats-cards {
    gap: var(--spacing-sm, 8px);
  }

  .stat-card {
    padding: var(--spacing-sm, 12px);
  }

  .stat-card .stat-value {
    font-size: var(--font-size-xl, 20px);
  }

  .stat-card .stat-label {
    font-size: var(--font-size-xs, 12px);
  }

  .streak-info {
    flex-direction: column;
    align-items: center;
  }

  .tab-item {
    padding: 10px 12px;
    font-size: 12px;
    gap: 4px;
  }

  .tab-item .el-icon {
    font-size: 14px;
  }
}
</style>
