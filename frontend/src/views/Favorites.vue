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
        <h1 class="fav-page-title">我的收藏</h1>
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
        <!-- 5-P1-1: 视频收藏 Tab -->
        <div
          :class="['fav-tab', { active: activeTab === 'videos' }]"
          @click="activeTab = 'videos'"
        >
          <span>视频</span>
          <span class="tab-count" v-if="videoTotal">{{ videoTotal }}</span>
        </div>
        <div
          :class="['fav-tab', { active: activeTab === 'vocabulary' }]"
          @click="activeTab = 'vocabulary'"
        >
          <span>单词/短语</span>
          <span class="tab-count" v-if="vocabTotal">{{ vocabTotal }}</span>
        </div>
      </div>

      <!-- 4-P1-5: 批量操作工具栏 (选中 N 项时出现) -->
      <Transition name="fav-bar">
        <div v-if="selectedIds.size > 0" class="fav-batch-bar">
          <span class="fav-batch-count">已选 {{ selectedIds.size }} 项</span>
          <SfButton size="sm" type="ghost" @click="clearSelection">
            <X :size="14" />
            取消
          </SfButton>
          <SfButton size="sm" type="danger" @click="batchDelete">
            <Trash2 :size="14" />
            删除
          </SfButton>
        </div>
      </Transition>

      <!-- 4-P1-4: 字幕 Tab 搜索 + 视频筛选 -->
      <div v-if="activeTab === 'subtitles'" class="fav-filter-bar">
        <div class="fav-search-wrap">
          <Search :size="14" class="fav-search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            class="fav-search-input"
            placeholder="搜索字幕 (英文/中文)..."
            aria-label="搜索字幕"
            @input="onSearchInput"
          />
          <button v-if="searchQuery" class="fav-search-clear" @click="clearSearch" aria-label="清空搜索">
            <X :size="14" />
          </button>
        </div>
        <div class="fav-material-filter">
          <SfDropdown>
            <template #trigger>
              <SfButton type="ghost" size="sm">
                <Filter :size="14" />
                {{ filterMaterialTitle || '全部视频' }}
              </SfButton>
            </template>
            <div class="material-filter-menu">
              <div
                class="dropdown-item"
                :class="{ active: filterMaterialId === null }"
                @click="filterMaterialById(null)"
              >
                全部视频
              </div>
              <div
                v-for="m in availableMaterials"
                :key="m.id"
                class="dropdown-item"
                :class="{ active: filterMaterialId === m.id }"
                @click="filterMaterialById(m.id)"
              >
                {{ m.title }}
              </div>
            </div>
          </SfDropdown>
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
                :class="{ selected: selectedIds.has(item.id) }"
              >
                <!-- 4-P1-5: 多选 checkbox -->
                <label class="fav-checkbox">
                  <input
                    type="checkbox"
                    :checked="selectedIds.has(item.id)"
                    @change="toggleSelect(item.id)"
                    :aria-label="`选择 ${item.text_en}`"
                  />
                </label>
                <div class="fav-card-content">
                  <div class="fav-card-english">{{ item.text_en }}</div>
                  <div class="fav-card-chinese" v-if="item.text_cn">"{{ item.text_cn }}"</div>

                  <!-- 5-P1-2: 笔记展示 (有 note 时) -->
                  <div v-if="item.note && !isEditingNote(item.id)" class="fav-card-note">
                    <StickyNote :size="13" class="note-icon" />
                    <span class="note-text">{{ item.note }}</span>
                    <button class="note-edit-btn" @click="startEditNote(item)" aria-label="编辑笔记">
                      <Edit2 :size="12" />
                    </button>
                  </div>

                  <!-- 5-P1-2: 笔记编辑 (textarea) -->
                  <div v-else-if="isEditingNote(item.id)" class="fav-card-note-edit">
                    <textarea
                      v-model="editingNote"
                      class="note-textarea"
                      placeholder="记点什么…(比如:这句很扎心, 收藏)"
                      maxlength="500"
                      rows="3"
                    ></textarea>
                    <div class="note-edit-actions">
                      <SfButton size="sm" type="ghost" @click="cancelEditNote">取消</SfButton>
                      <SfButton size="sm" type="primary" :disabled="savingNote" @click="saveEditNote(item)">
                        {{ savingNote ? '保存中…' : '保存' }}
                      </SfButton>
                    </div>
                  </div>

                  <!-- 5-P1-2: 添加笔记按钮 (无 note 且未编辑) -->
                  <div v-else class="fav-card-note-add">
                    <SfButton type="ghost" size="sm" @click="startEditNote(item)">
                      <Plus :size="13" /> 添加笔记
                    </SfButton>
                  </div>

                  <!-- 5-P1-2: 用户标签 chips (可点击移除) + 添加按钮 -->
                  <div class="fav-card-tags">
                    <TransitionGroup name="tag-chip">
                      <span
                        v-for="tag in (item.tags || [])"
                        :key="tag.id"
                        class="user-tag-chip"
                        :style="{ '--tag-color': tag.color || '#5c6ef5' }"
                      >
                        <span class="user-tag-name">{{ tag.name }}</span>
                        <button
                          class="user-tag-remove"
                          @click="removeTagFromBookmark(item, tag.name)"
                          :aria-label="`移除标签 ${tag.name}`"
                        >×</button>
                      </span>
                    </TransitionGroup>
                    <button
                      v-if="!isAddingTag(item.id)"
                      class="add-tag-btn"
                      @click="startAddTag(item)"
                      aria-label="添加标签"
                    >+ 标签</button>
                    <div v-else class="add-tag-input-wrap">
                      <input
                        :ref="el => tagInputRefs[item.id] = el"
                        v-model="tagInputValue"
                        class="add-tag-input"
                        :list="`tag-suggestions-${item.id}`"
                        placeholder="标签名, 回车确认"
                        maxlength="50"
                        @keydown.enter="confirmAddTag(item)"
                        @keydown.esc="cancelAddTag"
                        @keydown="onTagInputKeydown($event, item)"
                      />
                      <datalist :id="`tag-suggestions-${item.id}`">
                        <option v-for="t in allUserTags" :key="t.id" :value="t.name" />
                      </datalist>
                    </div>
                  </div>

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
          <SfPagination
            :current-page="subtitlePage"
            :page-size="subtitlePageSize"
            :total="subtitleTotal"
            @change="loadSubtitleBookmarks"
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
          <SfPagination
            :current-page="vocabPage"
            :page-size="vocabPageSize"
            :total="vocabTotal"
            @change="loadVocabList"
          />
        </div>
      </div>

      <!-- 5-P1-1: 视频收藏 Tab -->
      <div v-show="activeTab === 'videos'" class="tab-content fav-videos-tab">
        <div v-if="videoLoading" class="video-skeleton-list">
          <div v-for="i in 3" :key="i" class="video-skeleton-card"></div>
        </div>
        <div v-else-if="videoFavorites.length > 0" class="video-fav-grid">
          <div
            v-for="video in videoFavorites"
            :key="video.id"
            class="video-fav-card"
            @click="goMaterial(video.id)"
          >
            <div class="video-cover">
              <img
                v-if="video.cover_path"
                :src="video.cover_path"
                :alt="video.title"
                loading="lazy"
              />
              <div v-else class="video-cover-placeholder">
                <Film :size="32" />
              </div>
              <div v-if="video.duration" class="video-duration">
                {{ formatVideoDuration(video.duration) }}
              </div>
            </div>
            <div class="video-info">
              <div class="video-title" :title="video.title">{{ video.title }}</div>
              <div class="video-meta">
                <span v-if="video.difficulty">难度 {{ video.difficulty }}</span>
                <span v-if="video.favorited_at" class="video-fav-time">
                  <Heart :size="12" />
                  {{ formatRelativeTime(video.favorited_at) }}收藏
                </span>
              </div>
            </div>
            <button
              class="video-remove-btn"
              @click.stop="removeVideoFav(video)"
              aria-label="取消收藏"
            >
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
        <EmptyState
          v-else
          title="还没有收藏视频"
          description="在视频详情页点星标即可收藏"
        >
          <template #actions>
            <SfButton type="primary" @click="$router.push('/materials')">去看看</SfButton>
          </template>
        </EmptyState>
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
  Headphones,
  // 4-P1-4: 搜索 + 视频筛选图标
  Search,
  X,
  Filter,
  // 5-P1-1: 视频收藏 Tab
  Film,
  Heart,
  // 5-P1-2: 笔记
  StickyNote,
  Edit2,
  Plus
} from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { favoriteAPI, vocabularyAPI, subtitleBookmarkAPI, materialAPI, bookmarkTagAPI } from '@/api'
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

// 4-P1-4: 搜索 + 视频筛选
const searchQuery = ref('')
const filterMaterialId = ref(null)
let searchDebounce = null

// 5-P1-1: 视频收藏 (Favorite material 级别)
const videoFavorites = ref([])
const videoLoading = ref(false)
const videoTotal = ref(0)

const goMaterial = (id) => {
  router.push(`/materials/${id}`)
}

const removeVideoFav = async (video) => {
  const confirmed = await showConfirm({
    title: '取消收藏',
    message: `确定要取消收藏视频「${video.title}」吗？`
  })
  if (!confirmed) return
  try {
    await favoriteAPI.remove(video.id)
    toast.success('已取消收藏')
    await loadVideoFavorites()
  } catch (e) {
    console.error('取消收藏失败', e)
    toast.error('取消收藏失败')
  }
}

const formatVideoDuration = (seconds) => {
  if (!seconds || seconds < 0) return ''
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const loadVideoFavorites = async () => {
  if (!userStore.isLoggedIn) return
  videoLoading.value = true
  try {
    const res = await favoriteAPI.getList({ page: 1, page_size: 50 })
    videoFavorites.value = res.items || []
    videoTotal.value = res.total || 0
  } catch (e) {
    console.error('加载视频收藏失败', e)
    videoFavorites.value = []
    videoTotal.value = 0
  } finally {
    videoLoading.value = false
  }
}

// 5-P1-2: 笔记编辑
const editingNoteId = ref(null)
const editingNote = ref('')
const savingNote = ref(false)

const isEditingNote = (id) => editingNoteId.value === id

const startEditNote = (item) => {
  editingNoteId.value = item.id
  editingNote.value = item.note || ''
}

const cancelEditNote = () => {
  editingNoteId.value = null
  editingNote.value = ''
}

const saveEditNote = async (item) => {
  savingNote.value = true
  try {
    const res = await subtitleBookmarkAPI.update(item.id, { note: editingNote.value })
    item.note = res.note
    cancelEditNote()
    toast.success('笔记已保存')
  } catch (e) {
    console.error('保存笔记失败', e)
    toast.error('保存失败')
  } finally {
    savingNote.value = false
  }
}

// ==================== 5-P1-2: 用户标签 ====================
// 用户自有标签 (bookmark 维度), 与全局 Tag (material 维度) 区分
const allUserTags = ref([])            // 所有标签 (含 usage_count, 用于 datalist 补全)
const addingTagBookmarkId = ref(null)  // 正在添加标签的 bookmark id
const tagInputValue = ref('')
const tagInputRefs = ref({})           // 多个 input 的 ref 收集

// 加载所有用户标签 (onMounted + add/remove 后刷新)
const loadUserTags = async () => {
  try {
    const res = await bookmarkTagAPI.list()
    allUserTags.value = res || []
  } catch (e) {
    console.error('加载标签失败', e)
  }
}

const isAddingTag = (id) => addingTagBookmarkId.value === id

const startAddTag = (item) => {
  addingTagBookmarkId.value = item.id
  tagInputValue.value = ''
  // nextTick 聚焦
  setTimeout(() => {
    const el = tagInputRefs.value[item.id]
    if (el && typeof el.focus === 'function') el.focus()
  }, 50)
}

const cancelAddTag = () => {
  addingTagBookmarkId.value = null
  tagInputValue.value = ''
}

const confirmAddTag = async (item) => {
  const name = tagInputValue.value.trim()
  if (!name) {
    cancelAddTag()
    return
  }
  // 拼接现有 + 新的, 一次性 setTags (replace-all)
  const currentNames = (item.tags || []).map(t => t.name)
  if (currentNames.includes(name)) {
    toast.info('已有此标签')
    cancelAddTag()
    return
  }
  const newNames = [...currentNames, name]
  try {
    await subtitleBookmarkAPI.setTags(item.id, newNames)
    // 乐观更新 (无需重新拉 list)
    item.tags = [...(item.tags || []), { id: Date.now(), name, color: '#5c6ef5' }]
    await loadUserTags()  // 刷新 allUserTags (usage_count)
    cancelAddTag()
  } catch (e) {
    console.error('添加标签失败', e)
    toast.error('添加失败')
  }
}

const removeTagFromBookmark = async (item, tagName) => {
  const newNames = (item.tags || []).filter(t => t.name !== tagName).map(t => t.name)
  try {
    await subtitleBookmarkAPI.setTags(item.id, newNames)
    item.tags = (item.tags || []).filter(t => t.name !== tagName)
    await loadUserTags()
  } catch (e) {
    console.error('移除标签失败', e)
    toast.error('移除失败')
  }
}

// datalist 不支持键盘补全确认, 这个是预留扩展点 (目前用原生 datalist)
const onTagInputKeydown = (e, item) => {
  // 未来如需自定义补全 dropdown, 在这里处理 ArrowUp/Down/Enter
}

// 4-P1-5: 批量选择
const selectedIds = ref(new Set())

const toggleSelect = (id) => {
  const next = new Set(selectedIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  selectedIds.value = next
}

const clearSelection = () => {
  selectedIds.value = new Set()
}

// 4-P1-5: 批量删除 + Undo
const batchDelete = async () => {
  const ids = Array.from(selectedIds.value)
  if (ids.length === 0) return
  const confirmed = await showConfirm({
    title: '批量删除',
    message: `确定删除选中的 ${ids.length} 项字幕收藏？`
  })
  if (!confirmed) return

  // 备份被删的 items (用于撤销)
  const backupItems = subtitleBookmarks.value.filter(b => ids.includes(b.id))
  try {
    const res = await subtitleBookmarkAPI.batchDelete(ids)
    const deletedCount = res.message.match(/\d+/)?.[0] || ids.length
    clearSelection()
    loadSubtitleBookmarks()
    toast.withAction(
      `已删除 ${deletedCount} 项`,
      {
        label: '撤销',
        onClick: async () => {
          // 字幕收藏没有 batch-create, 只能逐个调 add (字幕收藏 = SubtitleBookmark)
          // 由于后端不支持批量撤销, 提示用户手动重新收藏
          toast.warning(`请重新收藏这 ${backupItems.length} 句 (subtitles 旁星标)`)
        }
      },
      { type: 'success', duration: 5000 }
    )
  } catch (e) {
    console.error('批量删除失败', e)
    toast.error('批量删除失败')
  }
}

const availableMaterials = computed(() => {
  // 从已加载的 bookmarks 提取去重的视频列表
  const map = new Map()
  for (const item of subtitleBookmarks.value) {
    if (item.material_id && !map.has(item.material_id)) {
      map.set(item.material_id, { id: item.material_id, title: item.material_title })
    }
  }
  return Array.from(map.values()).sort((a, b) => a.title.localeCompare(b.title, 'zh'))
})

const filterMaterialTitle = computed(() => {
  if (!filterMaterialId.value) return null
  return availableMaterials.value.find(m => m.id === filterMaterialId.value)?.title || null
})

const onSearchInput = () => {
  // 防抖 300ms 避免连续输入狂触发
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => loadSubtitleBookmarks(), 300)
}

const clearSearch = () => {
  searchQuery.value = ''
  loadSubtitleBookmarks()
}

const filterMaterialById = (id) => {
  filterMaterialId.value = id
  loadSubtitleBookmarks()
}

const loadSubtitleBookmarks = async () => {
  if (!userStore.isLoggedIn) return
  subtitleLoading.value = true
  try {
    // 4-P1-4: 传 search + material_id 参数
    const params = {}
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterMaterialId.value) params.material_id = filterMaterialId.value
    const res = await subtitleBookmarkAPI.getAll(params)
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
    await Promise.all([
    loadSubtitleBookmarks(),
    loadVocabList(),
    loadVideoFavorites()  // 5-P1-1
  ])
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  preloadVoices()
  if (userStore.isLoggedIn) {
    loadSubtitleBookmarks()
    loadVocabList()
    loadUserTags()
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
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
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
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
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
  transition: color var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
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
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
  position: relative;
}

.subtitle-fav-card.selected {
  background: rgba(37, 99, 235, 0.04);
  outline: 2px solid var(--color-brand);
  outline-offset: -2px;
}

/* 4-P1-5: 多选 checkbox */
.fav-checkbox {
  display: flex;
  align-items: center;
  padding-top: 2px;
  cursor: pointer;
}
.fav-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-brand);
}

/* 4-P1-5: 批量操作工具栏 */
.fav-batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin-bottom: 12px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-brand);
  border-radius: 10px;
  position: sticky;
  top: 0;
  z-index: 5;
}
.fav-batch-count {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-brand);
  flex: 1;
}
.fav-bar-enter-active, .fav-bar-leave-active {
  transition: opacity var(--sf-duration-normal), transform var(--sf-duration-normal);
}
.fav-bar-enter-from, .fav-bar-leave-to {
  opacity: 0;
  transform: translateY(-8px);
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
  transition: opacity var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
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
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
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
  transition: all var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
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
  transition: opacity var(--sf-duration-normal) var(--ease-standard, cubic-bezier(0.4, 0, 0.2, 1));
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
  transition: background var(--sf-duration-fast);
  min-height: 44px;
}

:deep(.dropdown-item:hover) {
  background: var(--color-bg-elevated);
}

/* ====== 5-P1-2: 笔记展示/编辑 ====== */
.fav-card-note {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 8px 0;
  padding: 8px 10px;
  background: rgba(245, 158, 11, 0.08);  /* 琥珀色淡背景, 跟"笔记"语义匹配 */
  border-radius: 6px;
  font-size: 13px;
  color: var(--color-text-primary);
  border-left: 3px solid var(--color-warm, #F59E0B);
}
.note-icon {
  color: var(--color-warm, #F59E0B);
  flex-shrink: 0;
}
.note-text {
  flex: 1;
  line-height: 1.5;
  word-break: break-word;
}
.note-edit-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.note-edit-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--color-text-primary);
}

.fav-card-note-edit {
  margin: 8px 0;
}
.note-textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  font-family: inherit;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  min-height: 60px;
  box-sizing: border-box;
}
.note-textarea:focus {
  outline: none;
  border-color: var(--color-brand, #2563EB);
}
.note-edit-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 6px;
}

.fav-card-note-add {
  margin: 4px 0 8px 0;
}

/* ====== 5-P1-2: 用户标签 chips ====== */
.fav-card-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin: 4px 0 8px 0;
}
.user-tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 1px 4px 1px 8px;
  font-size: 11px;
  line-height: 18px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--tag-color, #5c6ef5) 12%, transparent);
  color: var(--tag-color, #5c6ef5);
  border: 1px solid color-mix(in srgb, var(--tag-color, #5c6ef5) 30%, transparent);
  transition: all 0.15s ease;
}
.user-tag-chip:hover {
  background: color-mix(in srgb, var(--tag-color, #5c6ef5) 18%, transparent);
}
.user-tag-name {
  font-weight: 500;
}
.user-tag-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border: none;
  background: transparent;
  color: inherit;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  border-radius: 50%;
  opacity: 0.5;
  padding: 0;
  transition: opacity 0.15s ease, background 0.15s ease;
}
.user-tag-remove:hover {
  opacity: 1;
  background: color-mix(in srgb, var(--tag-color, #5c6ef5) 25%, transparent);
}
.add-tag-btn {
  border: 1px dashed var(--color-border, #cbd5e1);
  background: transparent;
  color: var(--color-text-secondary, #64748b);
  font-size: 11px;
  line-height: 18px;
  padding: 1px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.add-tag-btn:hover {
  border-color: var(--color-primary, #5c6ef5);
  color: var(--color-primary, #5c6ef5);
  background: rgba(92, 110, 245, 0.06);
}
.add-tag-input-wrap {
  display: inline-flex;
}
.add-tag-input {
  border: 1px solid var(--color-primary, #5c6ef5);
  background: var(--color-bg-card, #fff);
  color: var(--color-text-primary, #1e293b);
  font-size: 12px;
  line-height: 18px;
  padding: 1px 8px;
  border-radius: 10px;
  outline: none;
  width: 140px;
}
.add-tag-input:focus {
  box-shadow: 0 0 0 2px rgba(92, 110, 245, 0.15);
}
/* TransitionGroup for tag chips */
.tag-chip-enter-active, .tag-chip-leave-active {
  transition: all 0.2s ease;
}
.tag-chip-enter-from {
  opacity: 0;
  transform: scale(0.8);
}
.tag-chip-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* ====== 5-P1-1: 视频收藏 Tab ====== */
.fav-videos-tab {
  padding: 4px 0;
}

.video-fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}

.video-fav-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg, 16px);
  border: 1px solid var(--color-border);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--sf-duration-normal), box-shadow var(--sf-duration-normal);
  position: relative;
}
.video-fav-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.video-cover {
  width: 100%;
  aspect-ratio: 16/9;
  background: var(--color-bg-elevated);
  position: relative;
  overflow: hidden;
}
.video-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.video-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}
.video-duration {
  position: absolute;
  right: 8px;
  bottom: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.video-info {
  padding: 12px;
}
.video-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}
.video-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.video-fav-time {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.video-remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity var(--sf-duration-normal), background var(--sf-duration-normal);
}
.video-fav-card:hover .video-remove-btn {
  opacity: 1;
}
.video-remove-btn:hover {
  background: var(--color-danger, #ef4444);
}

/* 5-P1-1: 视频骨架屏 (复用 P2-2 通用骨架样式) */
.video-skeleton-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}
.video-skeleton-card {
  aspect-ratio: 16/9;
  background: linear-gradient(90deg, var(--color-bg-elevated) 25%, #e5e7eb 50%, var(--color-bg-elevated) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-lg, 16px);
  animation: skeleton-shimmer 1.5s infinite;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
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
