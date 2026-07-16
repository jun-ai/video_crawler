<!--
  H5CalendarStrip — Phase 22: H5 月历周条
  对标 SpeakVlog 个人中心 "June 2026 + 月历" 视觉,但简化成 H5 顶部单行周日期

  数据源: GET /api/learning/calendar?year&month
  返回: dates[], streak, max_streak, monthly_minutes, daily_counts[date]

  视觉: 水平 7 日 + < > 切换月份; 已学日期有绿色小圆点; "今天" 用蓝色环形高亮
       streak 数字以 "Day X" 形式显示在右侧

  设计原则:
  - 不使用 emoji 作为图标 (AGENTS.md 禁止)
  - streak 用 lucide Flame 图标
  - 已学日期用 Tailwind bg-amber-200 (日历暖色), 今天用 ring-2 ring-blue-500
-->
<template>
  <div class="h5-cal-strip">
    <div class="h5-cal-head">
      <button class="h5-cal-nav" @click="prevMonth" aria-label="上一月">
        <ChevronLeft :size="16" />
      </button>
      <div class="h5-cal-title">
        <span class="h5-cal-year">{{ year }} 年 {{ month }} 月</span>
        <span class="h5-cal-streak" v-if="streak > 0">
          <Flame :size="14" />
          {{ streak }} 天
        </span>
      </div>
      <button class="h5-cal-nav" @click="nextMonth" aria-label="下一月">
        <ChevronRight :size="16" />
      </button>
    </div>
    <div class="h5-cal-week">
      <div
        v-for="(d, i) in days"
        :key="d.key"
        :class="['h5-cal-day', {
          'is-today': d.isToday,
          'is-learned': d.isLearned,
          'is-future': d.isFuture,
        }]"
        @click="onPick(d)"
      >
        <span class="h5-cal-daylabel">{{ WEEK_LABELS[i] }}</span>
        <span class="h5-cal-daynum">{{ d.day }}</span>
        <span class="h5-cal-dot" v-if="d.isLearned" />
      </div>
    </div>
    <div class="h5-cal-monthstats" v-if="monthMinutes > 0 || totalDays > 0">
      本月已学 <b>{{ totalDays }}</b> 天 · 累计 <b>{{ monthMinutes }}</b> 分钟
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ChevronLeft, ChevronRight, Flame } from 'lucide-vue-next'
import { learningAPI } from '@/api'

const props = defineProps({
  initialYear: { type: Number, default: 0 },
  initialMonth: { type: Number, default: 0 },
})

const emit = defineEmits(['pick-date'])

const WEEK_LABELS = ['一', '二', '三', '四', '五', '六', '日']

const today = new Date()
const year = ref(props.initialYear || today.getFullYear())
const month = ref(props.initialMonth || today.getMonth() + 1)
const allDates = ref([]) // 后端返回所有有学习记录的日期
const streak = ref(0)
const totalDays = ref(0)
const monthMinutes = ref(0)
const dailyCounts = ref({})
const loading = ref(false)

async function fetchCalendar() {
  loading.value = true
  try {
    const data = await learningAPI.getCalendar(year.value, month.value)
    allDates.value = data.dates || []
    streak.value = data.streak || 0
    totalDays.value = (data.daily_counts && Object.keys(data.daily_counts).length) || 0
    monthMinutes.value = data.monthly_minutes || 0
    dailyCounts.value = data.daily_counts || {}
  } catch (e) {
    // 静默失败 (未登录/网络错误), 显示空态
    allDates.value = []
    streak.value = 0
    totalDays.value = 0
    monthMinutes.value = 0
    dailyCounts.value = {}
  } finally {
    loading.value = false
  }
}

watch([year, month], fetchCalendar, { immediate: true })

function prevMonth() {
  if (month.value === 1) { year.value--; month.value = 12 }
  else { month.value-- }
}
function nextMonth() {
  if (month.value === 12) { year.value++; month.value = 1 }
  else { month.value++ }
}

// 当周 7 天 (从周一开始)
const days = computed(() => {
  const list = []
  // 找到本周一的日期 (当前月内的某天)
  const todayDate = new Date()
  const todayDayNum = todayDate.getDate()
  const todayMonth = todayDate.getMonth() + 1
  const todayYear = todayDate.getFullYear()
  // 计算当前月本月内的某天 = todayDayNum (如果本月), 否则用月份最后一天
  const sampleDay = (year.value === todayYear && month.value === todayMonth) ? todayDayNum : 1
  const sampleDate = new Date(year.value, month.value - 1, sampleDay)
  // 把 sampleDate 调到本周一
  const dayOfWeek = sampleDate.getDay() // 0 = Sun
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
  sampleDate.setDate(sampleDate.getDate() + diffToMonday)

  for (let i = 0; i < 7; i++) {
    const d = new Date(sampleDate)
    d.setDate(d.getDate() + i)
    const key = formatDateKey(d)
    const isLearned = allDates.value.includes(key)
    const isToday = (d.getDate() === todayDayNum && d.getMonth() + 1 === todayMonth && d.getFullYear() === todayYear)
    const isFuture = d > todayDate
    list.push({
      key,
      day: d.getDate(),
      isToday,
      isLearned,
      isFuture,
      iso: key,
    })
  }
  return list
})

function formatDateKey(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

function onPick(d) {
  if (d.isFuture) return
  emit('pick-date', d.iso)
}
</script>

<style scoped>
.h5-cal-strip {
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
  border-radius: 16px;
  padding: 14px 16px 12px;
  margin: 0 16px 12px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 0 0 1px rgba(15, 23, 42, 0.04);
}

.h5-cal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.h5-cal-nav {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  border: none;
  background: rgba(15, 23, 42, 0.04);
  color: var(--color-text-secondary, #475569);
  cursor: pointer;
  transition: background 120ms ease;
}
.h5-cal-nav:active { background: rgba(15, 23, 42, 0.1); }

.h5-cal-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.h5-cal-year {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary, #0F172A);
}

.h5-cal-streak {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 700;
  color: #F97316;
  padding: 2px 8px;
  border-radius: 9999px;
  background: rgba(249, 115, 22, 0.08);
}

.h5-cal-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.h5-cal-day {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 0 8px;
  border-radius: 12px;
  cursor: pointer;
  background: transparent;
  transition: background 150ms ease;
}

.h5-cal-day:active { background: rgba(15, 23, 42, 0.04); }

.h5-cal-daylabel {
  font-size: 10px;
  color: var(--color-text-muted, #94A3B8);
  letter-spacing: 0.02em;
}

.h5-cal-daynum {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-secondary, #475569);
  line-height: 1;
}

.h5-cal-dot {
  width: 5px;
  height: 5px;
  border-radius: 9999px;
  background: #10B981; /* 绿色点 = 已学 */
  margin-top: 2px;
}

.h5-cal-day.is-today .h5-cal-daynum {
  color: white;
  background: linear-gradient(135deg, #4DA06C 0%, #3F8A5B 100%);
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin-top: -1px;
}

.h5-cal-day.is-today .h5-cal-daylabel {
  color: var(--color-brand, #2F3D35);
  font-weight: 600;
}

/* 已学日 + 今天: 绿点保留 (今天也算已学, 双标记) */
.h5-cal-day.is-learned .h5-cal-daynum:not(:has(+ *)) { /* 兜底 */ }

.h5-cal-day.is-future .h5-cal-daynum,
.h5-cal-day.is-future .h5-cal-daylabel {
  opacity: 0.4;
}
.h5-cal-day.is-future { cursor: default; }

.h5-cal-monthstats {
  margin-top: 10px;
  font-size: 12px;
  color: var(--color-text-muted, #94A3B8);
  text-align: center;
  padding-top: 10px;
  border-top: 1px dashed rgba(15, 23, 42, 0.06);
}

.h5-cal-monthstats b {
  color: var(--color-text-primary, #0F172A);
  font-weight: 700;
}
</style>
