<template>
  <div class="yt-favorites">
    <SfEmpty v-if="!userStore.isLoggedIn" description="请先登录查看收藏">
      <SfButton type="primary" @click="$router.push('/login')">去登录</SfButton>
    </SfEmpty>

    <template v-else>
      <!-- 页面头部 -->
      <div class="fav-page-header">
        <SfButton type="ghost" size="sm" class="fav-back-btn" @click="$router.back()">
          <ArrowLeft :size="18" />
        </SfButton>
        <h1 class="fav-page-title">收藏本</h1>
        <SfButton type="ghost" class="fav-manage-btn" @click="refreshData" :loading="refreshing">
          <RefreshCw :size="14" />
          刷新
        </SfButton>
      </div>

      <!-- Tab 导航 - 绿色下划线风格 -->
      <div class="fav-tabs">
        <div
          :class="['fav-tab', { active: activeTab === 'subtitles' }]"
          @click="activeTab = 'subtitles'"
        >
          <span>字幕</span>
          <span class="tab-count" v-if="subtitleTotal">{{ subtitleTotal }}</span>
        </div>
        <div
          :class="['fav-tab', { active: activeTab === 'vocabulary' }]"
          @click="activeTab = 'vocabulary'"
        >
          <span>单词/短语</span>
          <span class="tab-count" v-if="vocabTotal">{{ vocabTotal }}</span>
        </div>
      </div>

      <!-- 字幕收藏 Tab -->
      <div v-show="activeTab === 'subtitles'" class="tab-content">
        <div class="subtitle-fav-list" v-loading="subtitleLoading">
          <div v-for="group in groupedSubtitles" :key="group.label" class="date-group">
            <div class="date-label">{{ group.label }}</div>
            <div class="subtitle-cards">
              <div
                v-for="item in group.items"
                :key="item.id"
                class="subtitle-fav-card"
              >
                <div class="fav-card-content">
                  <div class="fav-card-english">{{ item.text_en }}</div>
                  <div class="fav-card-chinese" v-if="item.text_cn">"{{ item.text_cn }}"</div>
                  <div class="fav-card-meta">
                    <span class="fav-card-category">
                      <SfTag size="sm" type="default">{{ item.material_title || '未分类' }}</SfTag>
                    </span>
                    <span class="fav-card-duration">
                      {{ item.start_time ? formatDuration(item.start_time) : '' }}
                    </span>
                    <span v-if="item.practice_count > 0" class="fav-practice-count" :title="'已练习 ' + item.practice_count + ' 次'">
                      练习 {{ item.practice_count }} 次
                    </span>
                  </div>
                </div>
                <div class="fav-card-actions">
                  <SfDropdown>
                    <template #trigger>
                      <MoreHorizontal :size="16" class="fav-more-icon" />
                    </template>
                    <div class="dropdown-item" @click="handleSubtitleCommand('remove', item)">
                      <Trash2 :size="14" />
                      取消收藏
                    </div>
                  </SfDropdown>
                  <SfButton
                    type="primary"
                    size="sm"
                    @click="goLearnSubtitle(item)"
                    class="fav-practice-btn"
                  >
                    去练习
                    <ArrowRight :size="14" class="practice-arrow" />
                  </SfButton>
                </div>
              </div>
            </div>
          </div>
        </div>

        <EmptyState
          v-if="!subtitleLoading && subtitleBookmarks.length === 0"
          type="no-favorites"
          title="还没有收藏字幕"
          description="在学习过程中，点击字幕旁的星标图标收藏感兴趣的句子"
        >
          <template #actions>
            <SfButton type="primary" @click="$router.push('/materials')">去学习</SfButton>
          </template>
        </EmptyState>

        <div class="pagination" v-if="subtitleTotal > subtitlePageSize">
          <el-pagination
            v-model:current-page="subtitlePage"
            :page-size="subtitlePageSize"
            :total="subtitleTotal"
            layout="prev, pager, next"
            @current-change="loadSubtitleBookmarks"
          />
        </div>
      </div>

      <!-- 词汇收藏 Tab -->
      <div v-show="activeTab === 'vocabulary'" class="tab-content">
        <div class="vocab-list" v-loading="vocabLoading">
          <div v-for="item in vocabList" :key="item.id" class="vocab-card">
            <div class="vocab-main">
              <div class="vocab-content">
                <div class="vocab-word-row">
                  <span class="vocab-word">{{ item.word }}</span>
                  <span class="vocab-phonetic" v-if="item.phonetic">/{{ item.phonetic }}/</span>
                  <SfButton
                    class="vocab-speak-btn"
                    size="sm"
                    @click="speakWord(item.word)"
                  >
                    <Headphones :size="14" />
                  </SfButton>
                </div>
                <div class="vocab-translation" v-if="item.translation">{{ item.translation }}</div>
                <div class="vocab-context" v-if="item.context">
                  <span class="context-label">来源：</span>{{ item.context }}
                </div>
              </div>
              <div class="vocab-actions">
                <SfDropdown>
                  <template #trigger>
                    <MoreHorizontal :size="16" class="fav-more-icon" />
                  </template>
                  <div class="dropdown-item" @click="handleVocabCommand('remove', item.id)">
                    <Trash2 :size="14" />
                    删除
                  </div>
                </SfDropdown>
              </div>
            </div>
          </div>
        </div>

        <EmptyState
          v-if="!vocabLoading && vocabList.length === 0"
          type="no-vocabulary"
          title="生词本是空的"
          description="在学习过程中遇到的新单词可以添加到生词本"
        >
          <template #actions>
            <SfButton type="primary" @click="$router.push('/materials')">去学习</SfButton>
          </template>
        </EmptyState>

        <div class="pagination" v-if="vocabTotal > vocabPageSize">
          <el-pagination
            v-model:current-page="vocabPage"
            :page-size="vocabPageSize"
            :total="vocabTotal"
            layout="prev, pager, next"
            @current-change="loadVocabList"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { useTTS } from '@/composables/useTTS'
import { showConfirm } from '@/composables/useConfirm'
import {
  ArrowLeft,
  ArrowRight,
  RefreshCw,
  MoreHorizontal,
  Trash2,
  Headphones
} from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { favoriteAPI, vocabularyAPI, subtitleBookmarkAPI, materialAPI } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { speakWord, preloadVoices } = useTTS()

// Tab 控制
const activeTab = ref('subtitles')
const refreshing = ref(false)

// ====== 字幕收藏 ======
const subtitleLoading = ref(false)
const subtitleBookmarks = ref([])
// 分页由前端 slice（不依赖服务端分页，单次拉全部）
const subtitlePage = ref(1)
const subtitlePageSize = ref(20)
const subtitleTotal = ref(0)

// 按日期分组
const groupedSubtitles = computed(() => {
  const groups = {}
  subtitleBookmarks.value.forEach(item => {
    const date = item.created_at ? new Date(item.created_at) : new Date()
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    let label
    if (days === 0) label = '今天'
    else if (days === 1) label = '昨天'
    else if (days < 7) label = '近一周'
    else label = '更早'

    if (!groups[label]) groups[label] = { label, items: [] }
    groups[label].items.push(item)
  })

  const order = ['今天', '昨天', '近一周', '更早']
  return order.filter(l => groups[l]).map(l => groups[l])
})

// ====== 词汇收藏 ======
const vocabLoading = ref(false)
const vocabList = ref([])
const vocabPage = ref(1)
const vocabPageSize = ref(20)
const vocabTotal = ref(0)

const formatDuration = (ms) => {
  if (!ms && ms !== 0) return ''
  const seconds = Math.floor(ms / 1000)
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// ====== 字幕收藏操作 ======

const loadSubtitleBookmarks = async () => {
  if (!userStore.isLoggedIn) return
  subtitleLoading.value = true
  try {
    // 单次 API 拉全部（join Subtitle），不再 N+1
    const res = await subtitleBookmarkAPI.getAll()
    const items = Array.isArray(res) ? res : (res.items || [])
    // 字段映射：后端 subtitle_text_en → 前端 text_en
    subtitleBookmarks.value = items.map(item => ({
      id: item.id,
      subtitle_id: item.subtitle_id,
      material_id: item.material_id,
      material_title: item.material_title || '未分类',
      text_en: item.subtitle_text_en || '',
      text_cn: item.subtitle_text_cn || '',
      start_time: item.subtitle_start_time,
      practice_count: item.practice_count || 0,
      created_at: item.created_at,
    }))
    subtitleTotal.value = items.length
  } catch (e) {
    console.error('加载字幕收藏失败', e)
  } finally {
    subtitleLoading.value = false
  }
}

const goLearnSubtitle = (item) => {
  if (item.material_id) {
    // 3.7 带时间戳跳转, 避免用户点收藏后还要手动找
    const startTime = item.start_time
    const query = startTime != null ? `?start_time=${encodeURIComponent(startTime)}` : ''
    router.push(`/learn/${item.material_id}${query}`)
  }
}

const handleSubtitleCommand = async (command, item) => {
  if (command === 'remove') {
    const confirmed = await showConfirm({ title: '提示', message: '确定要取消收藏吗？' })
    if (confirmed) {
      try {
        await subtitleBookmarkAPI.remove(item.id)
        toast.success('已取消收藏')
        loadSubtitleBookmarks()
      } catch (e) {
        console.error('取消收藏失败', e)
      }
    }
  }
}

// ====== 词汇操作 ======

const loadVocabList = async () => {
  if (!userStore.isLoggedIn) return
  vocabLoading.value = true
  try {
    const res = await vocabularyAPI.getList({
      page: vocabPage.value,
      page_size: vocabPageSize.value
    })
    vocabList.value = res.items || []
    vocabTotal.value = res.total || 0
  } catch (e) {
    console.error('加载词汇失败', e)
  } finally {
    vocabLoading.value = false
  }
}

// speakWord 由 useTTS 提供

const handleVocabCommand = async (command, vocabId) => {
  if (command === 'remove') {
    const confirmed = await showConfirm({ title: '提示', message: '确定要删除这个词汇吗？' })
    if (confirmed) {
      try {
        await vocabularyAPI.delete(vocabId)
        toast.success('已删除')
        loadVocabList()
      } catch (e) {
        console.error('删除词汇失败', e)
      }
    }
  }
}

// ====== 刷新 ======
const refreshData = async () => {
  refreshing.value = true
  try {
    await Promise.all([loadSubtitleBookmarks(), loadVocabList()])
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  preloadVoices()
  if (userStore.isLoggedIn) {
    loadSubtitleBookmarks()
    loadVocabList()
  }
})
</script>

<style scoped>
/* ================================================
   Favorites — Phase 2 CSS-only redesign
   Design system: ink green #2563EB + warm orange #F59E0B
   ================================================ */

.yt-favorites {
  max-width: 900px;
  margin: 0 auto;
}

/* ====== Page header ====== */
.fav-page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0 24px;
  position: relative;
}

.fav-back-btn {
  color: var(--color-text-primary);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  transition: all 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.fav-back-btn:hover {
  background: var(--color-brand-subtle);
  border-color: var(--color-brand-bright);
  color: var(--color-brand-bright);
}

.fav-page-title {
  flex: 1;
  font-size: var(--text-2xl, 24px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.fav-manage-btn {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  border-color: var(--color-border);
  background: var(--color-bg-card);
  min-height: 44px;
  transition: all 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.fav-manage-btn:hover {
  color: var(--color-brand-bright);
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

/* ====== Tab navigation — underline style ====== */
.fav-tabs {
  display: flex;
  gap: 32px;
  padding: 0 4px;
  margin-bottom: 28px;
  border-bottom: 2px solid var(--color-border);
}

.fav-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 4px;
  font-size: var(--text-base, 16px);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
  transition: color 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  min-height: 44px;
}

.fav-tab:hover {
  color: var(--color-text-primary);
}

.fav-tab.active {
  color: var(--color-brand-bright);
  font-weight: 600;
}

.fav-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--yt-brand-gradient);
  border-radius: 3px 3px 0 0;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 20px;
  padding: 0 6px;
  font-size: var(--text-xs, 11px);
  font-weight: 600;
  border-radius: 10px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

.fav-tab.active .tab-count {
  background: var(--color-brand-subtle);
  color: var(--color-brand-bright);
}

.tab-content {
  min-height: 200px;
}

/* ====== Subtitle favorites list ====== */
.subtitle-fav-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.date-label {
  font-size: var(--text-xs, 12px);
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 14px;
  padding-left: 2px;
}

.subtitle-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.subtitle-fav-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--color-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--color-border);
  padding: 20px;
  gap: 16px;
  transition: all 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  position: relative;
}

.subtitle-fav-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  opacity: 0;
  transition: opacity 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.subtitle-fav-card:hover {
  border-color: var(--color-brand-bright);
  box-shadow: var(--shadow-sm);
}

.subtitle-fav-card:hover::before {
  opacity: 1;
}

.fav-card-content {
  flex: 1;
  min-width: 0;
}

.fav-card-english {
  font-size: var(--text-base, 15px);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: 6px;
}

.fav-card-chinese {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 10px;
  font-style: italic;
}

.fav-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.fav-card-category :deep(.sf-tag) {
  font-size: 11px;
}

.fav-card-duration {
  font-size: var(--text-xs, 12px);
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.fav-practice-count {
  font-size: 11px;
  color: #fff;
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  padding: 2px 10px;
  border-radius: var(--radius-full, 9999px);
  font-weight: 500;
}

.fav-card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.fav-more-icon {
  font-size: 16px;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 10px;
  border-radius: var(--radius-md, 12px);
  transition: all 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.fav-more-icon:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
}

.fav-practice-btn {
  font-size: var(--text-sm, 13px);
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%)) !important;
  border-color: var(--color-brand-bright) !important;
  min-height: 44px;
}

.fav-practice-btn:hover {
  background: var(--color-brand-hover) !important;
  border-color: var(--color-brand-hover) !important;
}

.practice-arrow {
  margin-left: 2px;
}

/* ====== Vocabulary list ====== */
.vocab-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vocab-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--color-border);
  padding: 20px;
  transition: all 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  position: relative;
}

.vocab-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--color-accent);
  opacity: 0;
  transition: opacity 0.2s var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
}

.vocab-card:hover {
  border-color: var(--color-brand-bright);
  background: var(--color-brand-subtle);
}

.vocab-card:hover::before {
  opacity: 1;
}

.vocab-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.vocab-content {
  flex: 1;
  min-width: 0;
}

.vocab-word-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.vocab-word {
  font-size: var(--text-lg, 18px);
  font-weight: 700;
  color: var(--color-text-primary);
}

.vocab-phonetic {
  font-size: var(--text-sm, 13px);
  color: var(--color-text-secondary);
  font-style: italic;
}

.vocab-speak-btn {
  width: 32px !important;
  height: 32px !important;
  background: var(--yt-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%)) !important;
  border-color: var(--color-brand-bright) !important;
  color: #fff !important;
  min-height: 44px !important;
  min-width: 44px !important;
}

.vocab-speak-btn:hover {
  background: var(--color-brand-hover) !important;
  border-color: var(--color-brand-hover) !important;
}

.vocab-translation {
  font-size: var(--text-sm, 14px);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.vocab-context {
  font-size: var(--text-xs, 12px);
  color: var(--color-text-muted);
  line-height: 1.5;
  background: var(--color-bg-elevated);
  padding: 8px 12px;
  border-radius: var(--radius-sm, 8px);
  display: inline-block;
}

.context-label {
  font-weight: 500;
}

.vocab-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* ====== Pagination ====== */
.pagination {
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

/* ====== Dropdown items ====== */
:deep(.dropdown-item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: var(--text-sm, 14px);
  color: var(--color-text-primary);
  cursor: pointer;
  border-radius: var(--radius-sm, 8px);
  transition: background 0.15s;
  min-height: 44px;
}

:deep(.dropdown-item:hover) {
  background: var(--color-bg-elevated);
}

/* ====== Mobile responsive ====== */
@media (max-width: 768px) {
  .yt-favorites {
    max-width: 100%;
  }

  .fav-page-header {
    padding: 8px 0 16px;
  }

  .fav-page-title {
    font-size: var(--text-xl, 20px);
  }

  .fav-tabs {
    gap: 24px;
  }

  .fav-tab {
    font-size: var(--text-sm, 14px);
  }

  .subtitle-fav-card {
    flex-direction: column;
    gap: 12px;
    padding: 16px;
  }

  .subtitle-fav-card::before {
    display: none;
  }

  .fav-card-actions {
    width: 100%;
    justify-content: space-between;
    padding-top: 12px;
    border-top: 1px solid var(--color-border);
  }

  .fav-card-english {
    font-size: var(--text-sm, 14px);
  }

  .fav-card-chinese {
    font-size: var(--text-xs, 13px);
  }

  .vocab-card {
    padding: 16px;
  }

  .vocab-card::before {
    display: none;
  }

  .vocab-word {
    font-size: var(--text-base, 16px);
  }
}

@media (max-width: 480px) {
  .fav-page-header {
    gap: 8px;
  }

  .fav-page-title {
    font-size: var(--text-lg, 18px);
  }

  .fav-manage-btn {
    font-size: var(--text-xs, 12px);
    padding: 6px 12px;
  }

  .fav-tabs {
    gap: 16px;
  }

  .fav-tab {
    font-size: var(--text-xs, 13px);
    padding: 10px 2px;
  }

  .subtitle-fav-card {
    padding: 14px;
  }

  .fav-card-meta {
    flex-wrap: wrap;
    gap: 6px;
  }

  .fav-more-icon {
    padding: 10px;
    min-width: 44px;
    min-height: 44px;
  }

  .vocab-speak-btn {
    min-width: 44px !important;
    min-height: 44px !important;
  }

  .vocab-context {
    font-size: 11px;
  }
}
</style>
