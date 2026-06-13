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
const subtitlePage = ref(1)
const subtitlePageSize = ref(20)
const subtitleTotal = ref(0)
// 缓存字幕详情
const subtitleDetailsMap = ref({})

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
    // 获取所有材料的字幕收藏
    // 先获取收藏的材料列表
    const matRes = await favoriteAPI.getList({ page: 1, page_size: 100 })
    const materials = matRes.items || []

    // 收集所有字幕收藏
    const allBookmarks = []
    for (const mat of materials) {
      try {
        const bookmarks = await subtitleBookmarkAPI.getList(mat.id)
        if (bookmarks && bookmarks.length) {
          // 获取字幕详情
          let subtitles = subtitleDetailsMap.value[mat.id]
          if (!subtitles) {
            try {
              subtitles = await materialAPI.getSubtitles(mat.id)
              subtitleDetailsMap.value[mat.id] = subtitles
            } catch (e) {
              subtitles = []
            }
          }

          for (const bm of bookmarks) {
            const sub = subtitles.find(s => s.id === bm.subtitle_id)
            allBookmarks.push({
              id: bm.id,
              subtitle_id: bm.subtitle_id,
              material_id: mat.id,
              material_title: mat.title,
              text_en: sub?.text_en || '',
              text_cn: sub?.text_cn || '',
              start_time: sub?.start_time,
              practice_count: bm.practice_count || 0,
              created_at: bm.created_at || new Date().toISOString()
            })
          }
        }
      } catch (e) {
        console.error('加载材料字幕收藏失败', mat.id, e)
      }
    }

    subtitleBookmarks.value = allBookmarks
    subtitleTotal.value = allBookmarks.length
  } catch (e) {
    console.error('加载字幕收藏失败', e)
  } finally {
    subtitleLoading.value = false
  }
}

const goLearnSubtitle = (item) => {
  if (item.material_id) {
    router.push(`/learn/${item.material_id}`)
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
.yt-favorites {
  max-width: 900px;
  margin: 0 auto;
}

/* ====== 页面头部 ====== */
.fav-page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0 20px;
}

.fav-back-btn {
  color: var(--color-text-primary);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  transition: all 0.2s;
}

.fav-back-btn:hover {
  background: var(--color-bg-elevated);
  border-color: var(--color-text-muted);
}

.fav-page-title {
  flex: 1;
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.fav-manage-btn {
  font-size: 13px;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
  background: var(--color-bg-base);
}

.fav-manage-btn:hover {
  color: var(--color-brand);
  border-color: var(--color-brand);
}

/* ====== Tab 导航 - 绿色下划线风格 ====== */
.fav-tabs {
  display: flex;
  gap: 32px;
  padding: 0 4px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--color-border);
}

.fav-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 4px;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.fav-tab:hover {
  color: var(--color-text-primary);
}

.fav-tab.active {
  color: var(--color-brand);
  font-weight: 600;
}

.fav-tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-brand);
  border-radius: 3px 3px 0 0;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}

.fav-tab.active .tab-count {
  background: rgba(63, 138, 91, 0.1);
  color: var(--color-brand);
}

.tab-content {
  min-height: 200px;
}

/* ====== 字幕收藏列表 ====== */
.subtitle-fav-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.date-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 12px;
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
  background: var(--color-bg-base);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 18px 20px;
  gap: 16px;
  transition: border-color 0.2s;
}

.subtitle-fav-card:hover {
  border-color: var(--color-brand);
}

.fav-card-content {
  flex: 1;
  min-width: 0;
}

.fav-card-english {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.5;
  margin-bottom: 4px;
}

.fav-card-chinese {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 8px;
  font-style: italic;
}

.fav-card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.fav-card-category .el-tag {
  background: var(--color-bg-elevated);
  border: none;
  color: var(--color-text-secondary);
  font-size: 11px;
}

.fav-card-duration {
  font-size: 12px;
  color: var(--color-text-muted);
  font-family: 'Roboto Mono', monospace;
}

.fav-practice-count {
  font-size: 11px;
  color: #fff;
  background: var(--color-brand);
  padding: 1px 8px;
  border-radius: 10px;
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
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  min-width: 36px;
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.fav-more-icon:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
}

.fav-practice-btn {
  font-size: 13px;
  background: var(--color-brand);
  border-color: var(--color-brand);
}

.fav-practice-btn:hover {
  background: var(--color-brand-dark);
  border-color: var(--color-brand-dark);
}

.practice-arrow {
  margin-left: 2px;
}

/* ====== 词汇收藏列表 ====== */
.vocab-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vocab-card {
  background: var(--color-bg-base);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 18px 20px;
  transition: border-color 0.2s;
}

.vocab-card:hover {
  border-color: var(--color-brand);
  background: var(--color-brand-subtle);
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
  gap: 8px;
  margin-bottom: 4px;
}

.vocab-word {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.vocab-phonetic {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-style: italic;
}

.vocab-speak-btn {
  width: 28px !important;
  height: 28px !important;
  background: var(--color-brand);
  border-color: var(--color-brand);
  color: #fff;
}

.vocab-speak-btn:hover {
  background: var(--color-brand-dark);
  border-color: var(--color-brand-dark);
}

.vocab-translation {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: 4px;
}

.vocab-context {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.5;
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

/* ====== 分页 ====== */
.pagination {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .yt-favorites {
    max-width: 100%;
  }

  .fav-page-header {
    padding: 4px 0 16px;
  }

  .fav-page-title {
    font-size: 18px;
  }

  .fav-tabs {
    gap: 24px;
  }

  .fav-tab {
    font-size: 14px;
  }

  .subtitle-fav-card {
    flex-direction: column;
    gap: 12px;
    padding: 14px;
  }

  .fav-card-actions {
    width: 100%;
    justify-content: space-between;
    padding-top: 8px;
    border-top: 1px solid var(--color-border);
  }

  .fav-card-english {
    font-size: 14px;
  }

  .fav-card-chinese {
    font-size: 13px;
  }

  .vocab-card {
    padding: 12px;
  }

  .vocab-word {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .fav-page-header {
    gap: 8px;
  }

  .fav-page-title {
    font-size: 16px;
  }

  .fav-manage-btn {
    font-size: 12px;
    padding: 6px 12px;
  }

  .fav-tabs {
    gap: 16px;
  }

  .fav-tab {
    font-size: 13px;
    padding: 10px 2px;
  }

  .subtitle-fav-card {
    padding: 12px;
  }

  .fav-card-meta {
    flex-wrap: wrap;
    gap: 6px;
  }

  .fav-more-icon {
    padding: 8px;
    min-width: 40px;
    min-height: 40px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .vocab-speak-btn {
    width: 36px !important;
    height: 36px !important;
  }
}
</style>
