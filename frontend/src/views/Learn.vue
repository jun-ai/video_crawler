<template>
  <div class="sf-learn-page">
    <!-- 骨架屏加载态 -->
    <template v-if="loading">
      <div class="sf-skeleton-header">
        <div class="sf-skeleton-line" style="width: 60px; height: 36px; border-radius: var(--sf-radius-md);"></div>
        <div class="sf-skeleton-line" style="width: 220px; height: 20px; border-radius: var(--sf-radius-md);"></div>
        <div class="sf-skeleton-line" style="width: 80px; height: 32px; border-radius: var(--sf-radius-full);"></div>
      </div>
      <div class="sf-skeleton-segment">
        <div class="sf-skeleton-line" style="width: 110px; height: 36px; border-radius: var(--sf-radius-full);"></div>
        <div class="sf-skeleton-line" style="width: 110px; height: 36px; border-radius: var(--sf-radius-full);"></div>
      </div>
      <div class="sf-main-content">
        <div class="sf-left-column">
          <div class="sf-card-inner">
            <div class="sf-skeleton-block" style="aspect-ratio: 16/9; border-radius: var(--sf-radius-lg);"></div>
          </div>
          <div class="sf-card-inner sf-card-inner--secondary">
            <div class="sf-skeleton-block" style="height: 220px; border-radius: var(--sf-radius-lg);"></div>
          </div>
        </div>
        <div class="sf-middle-column">
          <div class="sf-card-inner">
            <div class="sf-skeleton-line" style="height: 48px; border-radius: var(--sf-radius-md);" v-for="i in 8" :key="i"></div>
          </div>
        </div>
        <div class="sf-right-column">
          <div class="sf-card-inner">
            <div class="sf-skeleton-block" style="height: 320px; border-radius: var(--sf-radius-lg);"></div>
          </div>
        </div>
      </div>
    </template>

    <!-- 主内容（加载完成后） -->
    <template v-else>
      <!-- 页面头部 — Phase 1B Task 4: 提取到独立组件 -->
            <LearnHeader
              :title="material?.title"
              :is-favorited="isFavorited"
              :favorite-loading="favoriteLoading"
              :learning-progress="learningProgress"
              :current-index="currentIndex"
              :total-subtitles="subtitles.length"
              :bookmarked-count="bookmarkedSubtitleIds.size"
              @back="$router.back()"
              @toggle-favorite="toggleFavorite"
            />

      <!-- 学习模式切换 — Phase 1B Task 3: 提取到独立组件 -->
      <LearnModeSwitcher v-model="learningMode" />

      <!-- 听写模式 -->
      <div class="sf-main-content" v-if="learningMode === 'dictation'">
        <div class="sf-dictation-wrapper">
          <div class="sf-card-inner">
            <DictationMode
              class="sf-mode-content"
              :material="material"
              :subtitles="subtitles"
              :current-index="dictationIndex"
              @update-progress="onDictationUpdateProgress"
              @complete="onDictationComplete"
            />
          </div>
        </div>
      </div>

      <!-- 主内容区（跟读模式） -->
      <div class="sf-main-content" :data-mobile-tab="mobileActiveTab" v-if="learningMode === 'shadowing'">
        <!-- 左栏：视频区域 -->
        <div class="sf-left-column">
          <div class="sf-card-inner">
            <LearnVideoPlayer
            ref="videoPlayerRef"
            :material="material"
            :cover="material?.cover_path"
            :playback-rate="playbackRate"
            :loop-current="loopCurrent"
            :current-subtitle="currentSubtitle"
            @timeupdate="onTimeUpdate"
            @loadedmetadata="onVideoLoaded"
            @seeked="onSeeked"
            @ended="onVideoEnded"
            @play="startWatchDurationTimer"
            @pause="stopWatchDurationTimer"
            @update:playback-rate="playbackRate = $event; setPlaybackRate()"
            @update:loop-current="loopCurrent = $event"
            />

          </div>

          <!-- 当前字幕卡片（跟读练习区） -->
          <div class="sf-card-inner sf-card-inner--secondary">
            <LearnShadowingCard
              :current-subtitle="currentSubtitle"
              :current-index="currentIndex"
              :total-subtitles="subtitles.length"
              :show-translation="showTranslation"
              :show-only-chinese="showOnlyChinese"
              :is-recording="isRecording"
              :audio-url="audioUrl"
              :recorded-blob="recordedBlob"
              :pronunciation-result="pronunciationResult"
              :evaluation-loading="evaluationLoading"
              :is-logged-in="userStore.isLoggedIn"
              @prev="prevSubtitle"
              @next="nextSubtitle"
              @replay="replaySubtitle"
              @speak="speakCurrentSubtitle"
              @toggle-recording="toggleRecording"
              @evaluate="evaluatePronunciation"
              @clear-recording="clearRecording"
              @toggle-translation="toggleTranslation"
              @toggle-chinese-only="toggleOnlyChinese"
              @add-vocabulary="addSubtitleToVocabulary"
            />
          </div>
        </div>

        <!-- 中栏：字幕列表区域 -->
        <div class="sf-middle-column">
          <div class="sf-card-inner">
            <LearnSubtitleList
            ref="subtitleListRef"
            :subtitles="subtitles"
            :paginated-subtitles="paginatedSubtitles"
            :current-subtitle-index-in-page="currentSubtitleIndexInPage"
            :show-translation="showTranslation"
            :show-only-chinese="showOnlyChinese"
            :bookmarked-ids="bookmarkedSubtitleIds"
            :annotations="annotations"
            :has-interpretation="hasInterpretation"
            :is-generating="isGenerating"
            :auto-scroll="autoScroll"
            :current-page="subtitleCurrentPage"
            :page-size="subtitlePageSize"
            :play-mode="playMode"
            :play-mode-label="playModeLabel"
            :get-annotated-text="getAnnotatedText"
            @subtitle-click="handleSubtitleClick"
            @replay-subtitle="replaySpecificSubtitle"
            @record-subtitle="startRecordingForSubtitle"
            @toggle-bookmark="toggleBookmark"
            @text-selection="handleTextSelection"
            @annotation-click="handleAnnotationClick"
            @delete-annotation="deleteAnnotation"
            @prev="prevSubtitle"
            @next="nextSubtitle"
            @generate-interpretation="generateInterpretation"
            @set-subtitle-mode="setSubtitleMode"
            @set-play-mode="setPlayMode"
            @update:auto-scroll="autoScroll = $event"
            @update:current-page="subtitleCurrentPage = $event"
          >
            <template #word-popup>
              <LearnWordPopup
                v-model:visible="wordPopupVisible"
                :word="currentWord"
                :loading="wordLoading"
                :word-info="wordInfo"
                :adding-word="addingWord"
                @speak="(text) => text ? speakText(text) : speakWord(currentWord)"
                @add-vocabulary="addWordToVocabulary"
                @seek-video="seekToWordInVideo"
              />
            </template>
            <template #annotation-popup>
              <SfDialog
                v-model="annotationPopupVisible"
                title="添加标注"
                width="420px"
              >
                <div class="sf-annotation-popup-content" v-if="annotationPopupVisible">
                  <div class="sf-annotation-preview">
                    <div class="sf-annotation-preview__label">选中文本</div>
                    <div class="sf-annotation-preview__text">"{{ selectedAnnotation.text }}"</div>
                  </div>
                  <div>
                    <div class="sf-annotation-type-label">标注类型</div>
                    <div class="sf-annotation-type-options">
                      <button
                        :class="['sf-annotation-type-btn', { selected: selectedAnnotation.type === 'vocabulary' }]"
                        @click="selectedAnnotation.type = 'vocabulary'; onAnnotationTypeChange('vocabulary')"
                      >
                        <span style="color: var(--color-danger); font-size: 12px;">●</span> 重点词汇
                      </button>
                      <button
                        :class="['sf-annotation-type-btn', { selected: selectedAnnotation.type === 'phrase' }]"
                        @click="selectedAnnotation.type = 'phrase'; onAnnotationTypeChange('phrase')"
                      >
                        <span style="color: var(--color-info); font-size: 12px;">●</span> 重点短语
                      </button>
                      <button
                        :class="['sf-annotation-type-btn', { selected: selectedAnnotation.type === 'important' }]"
                        @click="selectedAnnotation.type = 'important'; onAnnotationTypeChange('important')"
                      >
                        <span style="color: var(--color-warning); font-size: 12px;">●</span> 重点内容
                      </button>
                    </div>
                  </div>
                  <div>
                    <div class="sf-annotation-type-label" style="margin-bottom: 6px;">备注（可选）</div>
                    <SfInput
                      v-model="selectedAnnotation.note"
                      textarea
                      :rows="2"
                      placeholder="添加备注..."
                    />
                  </div>
                  <div class="sf-annotation-actions">
                    <button class="sf-btn sf-btn--ghost sf-btn--sm" @click="annotationPopupVisible = false">取消</button>
                    <button class="sf-btn sf-btn--primary sf-btn--sm" @click="saveAnnotation">
                      <Check :size="14" />
                      保存标注
                    </button>
                  </div>
                </div>
              </SfDialog>
            </template>
          </LearnSubtitleList>
          </div>
        </div>

        <!-- 右栏：解读面板 -->
        <!-- 解读面板已改为 Sheet 浮动抽屉，在页面底部 -->
      </div>
    </template>

    <!-- 快捷键帮助按钮 -->
    <button class="sf-shortcut-trigger" @click="showShortcutPanel = !showShortcutPanel" :class="{ active: showShortcutPanel }">
      <HelpCircle :size="18" />
    </button>

    <!-- 解读面板按钮 -->
    <button class="sf-interpretation-trigger" @click="interpretationSheetOpen = true" v-if="!loading">
      <BookOpen :size="18" />
      <span>词汇解读</span>
      <span class="sf-badge" v-if="interpretation.words?.length">{{ interpretation.words.length }}</span>
    </button>

    <!-- Phase 1B Task 2: 移动端底部 Tab Bar -->
    <nav class="sf-mobile-tabs" v-if="!loading">
      <button
        v-for="tab in mobileTabs"
        :key="tab.key"
        :class="['sf-mobile-tab', { active: mobileActiveTab === tab.key || (tab.key === 'interpretation' && interpretationSheetOpen) }]"
        @click="setMobileTab(tab.key)"
        :aria-label="tab.label"
      >
        <component :is="tab.icon" :size="20" />
        <span class="sf-mobile-tab-label">{{ tab.label }}</span>
      </button>
    </nav>

    <!-- 解读面板 Sheet — Phase 1B Task 5: mobile bottom / desktop right -->
    <Sheet v-if="isMobileView" v-model:open="interpretationSheetOpen">
      <SheetContent side="bottom" class="sf-interpretation-sheet sf-interpretation-sheet--mobile">
        <SheetHeader>
          <SheetTitle>词汇解读</SheetTitle>
        </SheetHeader>
        <InterpretationDrawer
          :data="interpretation"
          :tab="interpretationTab"
          :filter="interpretationFilter"
          :hide-cn="hideInterpretationCn"
          :learning-status="learningStatus"
          :loading="interpretationLoading"
          :is-generating="isGenerating"
          :generating-status="interpretationGeneratingStatus"
          @generate="generateInterpretation"
          @update:tab="interpretationTab = $event"
          @update:filter="interpretationFilter = $event"
          @update:hide-cn="hideInterpretationCn = $event"
          @set-status="setLearningStatus"
          @interpretation-click="handleInterpretationClick"
          @seek-subtitle="seekToSubtitle"
          @add-vocabulary="addToVocabulary"
        />
      </SheetContent>
    </Sheet>
    <Sheet v-else v-model:open="interpretationSheetOpen">
      <SheetContent side="right" class="sf-interpretation-sheet">
        <SheetHeader>
          <SheetTitle>词汇解读</SheetTitle>
        </SheetHeader>
        <InterpretationDrawer
          :data="interpretation"
          :tab="interpretationTab"
          :filter="interpretationFilter"
          :hide-cn="hideInterpretationCn"
          :learning-status="learningStatus"
          :loading="interpretationLoading"
          :is-generating="isGenerating"
          :generating-status="interpretationGeneratingStatus"
          @generate="generateInterpretation"
          @update:tab="interpretationTab = $event"
          @update:filter="interpretationFilter = $event"
          @update:hide-cn="hideInterpretationCn = $event"
          @set-status="setLearningStatus"
          @interpretation-click="handleInterpretationClick"
          @seek-subtitle="seekToSubtitle"
          @add-vocabulary="addToVocabulary"
        />
      </SheetContent>
    </Sheet>

    <!-- 快捷键帮助面板 -->
    <transition name="sf-slide">
      <div v-if="showShortcutPanel" class="sf-shortcut-panel">
        <div class="sf-shortcut-panel__header">
          <span>键盘快捷键</span>
          <button class="sf-shortcut-panel__close" @click="showShortcutPanel = false">
            <X />
          </button>
        </div>
        <div class="sf-shortcut-list">
          <div class="sf-shortcut-item"><kbd>Space</kbd><span>播放 / 暂停</span></div>
          <div class="sf-shortcut-item"><kbd>←</kbd><span>上一句字幕</span></div>
          <div class="sf-shortcut-item"><kbd>→</kbd><span>下一句字幕</span></div>
          <div class="sf-shortcut-item"><kbd>R</kbd><span>重播当前字幕</span></div>
          <div class="sf-shortcut-item"><kbd>T</kbd><span>显示/隐藏翻译</span></div>
          <div class="sf-shortcut-item"><kbd>I</kbd><span>打开/关闭解读面板</span></div>
          <div class="sf-shortcut-item"><kbd>G</kbd><span>生成解读</span></div>
          <div class="sf-shortcut-item"><kbd>?</kbd><span>打开快捷键帮助</span></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { useTTS } from '@/composables/useTTS'
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  Star,
  Mic,
  Edit3,
  Play,
  Pause,
  RefreshCw,
  MessageCircle,
  BookOpen,
  BarChart3,
  FileText,
  FileVideo,
  Headphones,
  Check,
  HelpCircle,
  Video,
  X,
  Bookmark,
  BookmarkCheck
} from 'lucide-vue-next'
import SfDialog from '@/components/ui/SfDialog.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfTooltip from '@/components/ui/SfTooltip.vue'
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { materialAPI, learningAPI, favoriteAPI, vocabularyAPI, pronunciationAPI, interpretationAPI, speechAPI, annotationAPI, subtitleBookmarkAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import DictationMode from './DictationMode.vue'
import FilterChip from '@/components/common/FilterChip.vue'
import InterpretationDrawer from '@/components/learn/LearnInterpretationDrawer.vue'
import LearnWordPopup from '@/components/learn/LearnWordPopup.vue'
import LearnVideoPlayer from '@/components/learn/LearnVideoPlayer.vue'
import LearnShadowingCard from '@/components/learn/LearnShadowingCard.vue'
import LearnSubtitleList from '@/components/learn/LearnSubtitleList.vue'
import LearnModeSwitcher from '@/components/learn/LearnModeSwitcher.vue'
import LearnHeader from '@/components/learn/LearnHeader.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { speakText, speakWord, preloadVoices } = useTTS()

const loading = ref(true)
const material = ref(null)
const subtitles = ref([])
const videoRef = ref(null)
const videoPlayerRef = ref(null)
const subtitleListRef = ref(null)
const currentIndex = ref(-1)
const autoScroll = ref(true)
const isSeeking = ref(false)

// 视频播放控制
const playbackRate = ref(1)
const loopCurrent = ref(false)
const learningProgress = ref(0)
const lastPosition = ref(0)  // 上次播放位置（秒）
const showResumeBanner = ref(false)  // 是否显示继续学习横幅
const showShortcutPanel = ref(false)  // 是否显示快捷键帮助面板
const interpretationSheetOpen = ref(false)  // 是否显示解读面板 Sheet

// 播放模式：single(单次) / single-loop(单集循环) / continuous(连续播放) / sentence-loop(单句循环)
const playMode = ref('single')

const playModeLabels = {
  single: '单次播放',
  'single-loop': '单集循环',
  continuous: '连续播放',
  'sentence-loop': '单句循环'
}

const playModeLabel = computed(() => playModeLabels[playMode.value] || '单次播放')

const setPlayMode = (mode) => {
  playMode.value = mode
  // 单句循环模式自动开启 loopCurrent
  if (mode === 'sentence-loop') {
    loopCurrent.value = true
  } else {
    loopCurrent.value = false
  }
}

// 学习模式：'shadowing' 跟读模式, 'dictation' 听写模式
const learningMode = ref('shadowing')
const dictationIndex = ref(0)  // 听写模式当前索引

// Phase 1B Task 2: 移动端 tab 切换 (video / shadowing / subtitles / interpretation)
const mobileActiveTab = ref('video')
const mobileTabs = [
  { key: 'video', label: '视频', icon: Video },
  { key: 'shadowing', label: '跟读', icon: Mic },
  { key: 'subtitles', label: '字幕', icon: FileText },
  { key: 'interpretation', label: '解读', icon: BookOpen }
]
const setMobileTab = (key) => {
  if (key === 'interpretation') {
    interpretationSheetOpen.value = true
    return
  }
  mobileActiveTab.value = key
}

// Phase 1B Task 5: 移动端宽度检测（用于解读面板 Sheet side 切换）
const isMobileView = ref(false)
const updateIsMobile = () => {
  isMobileView.value = typeof window !== 'undefined' && window.matchMedia('(max-width: 768px)').matches
}
onMounted(() => {
  updateIsMobile()
  const mql = window.matchMedia('(max-width: 768px)')
  if (mql.addEventListener) {
    mql.addEventListener('change', updateIsMobile)
  }
})
onUnmounted(() => {
  const mql = window.matchMedia('(max-width: 768px)')
  if (mql.removeEventListener) {
    mql.removeEventListener('change', updateIsMobile)
  }
})

// 字幕分页相关
const subtitlePageSize = 10 // 每页显示10条字幕
const subtitleCurrentPage = ref(1)
const subtitleTotalPages = computed(() => Math.ceil(subtitles.value.length / subtitlePageSize))

// 当前页的字幕列表
const paginatedSubtitles = computed(() => {
  const start = (subtitleCurrentPage.value - 1) * subtitlePageSize
  const end = start + subtitlePageSize
  return subtitles.value.slice(start, end)
})

// 当前字幕在当前页的索引
const currentSubtitleIndexInPage = computed(() => {
  if (currentIndex.value < 0) return -1
  const start = (subtitleCurrentPage.value - 1) * subtitlePageSize
  const end = start + subtitlePageSize
  if (currentIndex.value >= start && currentIndex.value < end) {
    return currentIndex.value - start
  }
  return -1
})

// 字幕翻译相关
const showTranslation = ref(true)  // 默认显示中英翻译
const showOnlyChinese = ref(false)  // 仅显示中文模式
const translationLoading = ref(false)

// 跟读相关
const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const audioUrl = ref(null)
const recordedBlob = ref(null)

// 收藏相关
const isFavorited = ref(false)
const favoriteLoading = ref(false)

// 视频解读相关
const interpretationTab = ref('words')
const interpretationFilter = ref('all')
const interpretationLoading = ref(false)
const isGenerating = ref(false)
const interpretationDrawerVisible = ref(false)  // 控制解读抽屉面板
const expandedItems = ref(new Set())

// 切换展开/折叠
const toggleItemExpand = (itemId) => {
  if (expandedItems.value.has(itemId)) {
    expandedItems.value.delete(itemId)
  } else {
    expandedItems.value.add(itemId)
  }
  // 触发响应式更新
  expandedItems.value = new Set(expandedItems.value)
}

// 检查是否展开
const isItemExpanded = (itemId) => {
  return expandedItems.value.has(itemId)
}

// 筛选后的解读列表
const filteredInterpretationItems = computed(() => {
  const items = interpretation.value[interpretationTab.value] || []
  if (interpretationFilter.value === 'all') {
    return items
  }
  return items.filter(item => {
    const status = learningStatus.value[item.id] || 'unmarked'
    if (interpretationFilter.value === 'unmarked') {
      return !learningStatus.value[item.id] // 没有设置过状态
    }
    return status === interpretationFilter.value
  })
})

// 发音评测相关
const pronunciationResult = ref(null)
const evaluationLoading = ref(false)

// 单词弹出框相关
const wordPopupVisible = ref(false)
const currentWord = ref('')
const wordLoading = ref(false)
const wordInfo = ref({
  phonetic: '',
  translation: '',
  example: ''
})
const addingWord = ref(false)

// 标注相关
const annotations = ref({})  // { subtitleId: [annotation, ...] }
const annotationPopupVisible = ref(false)

// 字幕收藏相关
const bookmarkedSubtitleIds = ref(new Set())  // 已收藏的字幕ID集合
const bookmarkedSubtitleMap = ref({})  // subtitle_id -> bookmark 对象的映射（含 id、practice_count 等）
const selectedAnnotation = ref({
  subtitleId: null,
  startOffset: 0,
  endOffset: 0,
  text: '',
  type: 'vocabulary',
  color: 'var(--color-annotation-vocabulary)',
  note: ''
})
const annotationColors = {
  vocabulary: 'var(--color-annotation-vocabulary)',
  phrase: 'var(--color-annotation-phrase)',
  important: 'var(--color-annotation-important)'
}

const interpretation = ref({
  words: [],
  phrases: [],
  grammar: [],
  idioms: []
})

// 解读项学习状态
const learningStatus = ref({}) // { interpretationId: 'known' | 'unknown' | 'vague' }

// 计算是否有解读数据
const hasInterpretation = computed(() => {
  return interpretation.value.words.length > 0 ||
         interpretation.value.phrases.length > 0 ||
         interpretation.value.grammar.length > 0 ||
         interpretation.value.idioms.length > 0
})

// 隐藏解读中文翻译
const hideInterpretationCn = ref(false)

// 解读筛选计数
const interpretationFilterCounts = computed(() => {
  const items = interpretation.value[interpretationTab.value] || []
  const counts = { all: items.length, unmarked: 0, known: 0, unknown: 0 }
  items.forEach(item => {
    const status = learningStatus.value[item.id]
    if (!status) counts.unmarked++
    else if (status === 'known') counts.known++
    else if (status === 'unknown') counts.unknown++
  })
  return counts
})

const categoryLabels = {
  travel: '旅行',
  shopping: '购物',
  social: '社交',
  work: '工作',
  daily: '日常',
  food: '餐饮'
}

const getCategoryLabel = (name) => categoryLabels[name] || name || '未分类'

const getDifficultyLabel = (level) => {
  const labels = { 1: 'A1 入门', 2: 'A2 基础', 3: 'B1 中级', 4: 'B2 中高', 5: 'C1 高级' }
  return labels[level] || 'A1 入门'
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const formatTime = (ms) => {
  const seconds = Math.floor(ms / 1000)
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 当前字幕
const currentSubtitle = computed(() => {
  if (currentIndex.value >= 0 && subtitles.value[currentIndex.value]) {
    return subtitles.value[currentIndex.value]
  }
  return null
})

const onVideoLoaded = () => {
  console.log('视频加载完成')
  // 自动恢复上次播放位置
  if (learningProgress.value > 0 && learningProgress.value < 95) {
    // 从后端加载的进度数据中获取 last_position
    if (lastPosition.value > 0 && videoRef.value) {
      videoRef.value.currentTime = lastPosition.value
      showResumeBanner.value = true
      toast.info(`上次看到 ${formatTime(lastPosition.value * 1000)}（${learningProgress.value}%），已自动跳转`, { duration: 4000 })
    }
  }
}

const onSeeked = () => {
  console.log('视频跳转完成, currentTime:', videoRef.value?.currentTime)
}

// 视频播放结束事件
const onVideoEnded = () => {
  if (playMode.value === 'single-loop') {
    // 单集循环：重新开始播放
    if (videoRef.value) {
      videoRef.value.currentTime = 0
      videoRef.value.play().catch(() => {})
    }
  }
  // 其他模式：默认停止
}

// 设置播放速度
const setPlaybackRate = () => {
  if (videoRef.value) {
    videoRef.value.playbackRate = playbackRate.value
  }
}

const onTimeUpdate = () => {
  if (!videoRef.value || isSeeking.value) return
  const currentTime = videoRef.value.currentTime * 1000

  // 循环当前句功能
  if (loopCurrent.value && currentSubtitle.value) {
    if (currentTime >= currentSubtitle.value.end_time) {
      seekTo(currentSubtitle.value.start_time)
      return
    }
  }

  // 找到当前字幕
  for (let i = 0; i < subtitles.value.length; i++) {
    const sub = subtitles.value[i]
    if (currentTime >= sub.start_time && currentTime <= sub.end_time) {
      if (currentIndex.value !== i) {
        currentIndex.value = i

        // 检查是否需要切换页面
        const targetPage = Math.floor(i / subtitlePageSize) + 1
        if (subtitleCurrentPage.value !== targetPage) {
          subtitleCurrentPage.value = targetPage
        }

        if (autoScroll.value) {
          scrollToSubtitle(i)
        }
      }
      break
    }
  }

  // 更新学习进度
  updateProgress()
}

const scrollToSubtitle = (index) => {
  nextTick(() => {
    if (subtitleListRef.value) {
      // 计算当前页内的索引
      const start = (subtitleCurrentPage.value - 1) * subtitlePageSize
      const pageLocalIndex = index - start
      const element = document.getElementById('subtitle-page-' + pageLocalIndex)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  })
}

// 根据页面索引获取全局索引
const getGlobalIndex = (pageIndex) => {
  return (subtitleCurrentPage.value - 1) * subtitlePageSize + pageIndex
}

const seekTo = (ms) => {
  const video = videoRef.value
  if (!video) {
    console.error('Video element not found!')
    return
  }

  const seconds = ms / 1000
  console.log('seekTo:', ms, 'ms =', seconds, 's')

  // 设置跳转标志
  isSeeking.value = true

  // 先暂停视频
  const wasPlaying = !video.paused
  video.pause()

  // 使用 requestAnimationFrame 确保 DOM 更新
  requestAnimationFrame(() => {
    video.currentTime = seconds

    // 监听 seeked 事件
    const handleSeeked = () => {
      video.removeEventListener('seeked', handleSeeked)
      isSeeking.value = false
      if (wasPlaying) {
        video.play().catch(() => {})
      }
    }

    video.addEventListener('seeked', handleSeeked)

    // 超时保护
    setTimeout(() => {
      video.removeEventListener('seeked', handleSeeked)
      isSeeking.value = false
    }, 2000)
  })
}

// 点击字幕跳转
const handleSubtitleClick = (sub, index) => {
  if (!sub || sub.start_time === undefined) {
    console.error('Invalid subtitle data!')
    return
  }

  currentIndex.value = index
  seekTo(sub.start_time)
}

const prevSubtitle = () => {
  if (currentIndex.value > 0) {
    seekTo(subtitles.value[currentIndex.value - 1].start_time)
  }
}

const replaySubtitle = () => {
  if (currentIndex.value >= 0) {
    const sub = subtitles.value[currentIndex.value]
    seekTo(sub.start_time)
    // 同时播放 TTS 发音
    if (sub.text_en) {
      speakText(sub.text_en)
    }
  }
}

// 仅 TTS 发音（不 seek 视频）
const speakCurrentSubtitle = () => {
  if (currentIndex.value >= 0) {
    const sub = subtitles.value[currentIndex.value]
    if (sub.text_en) {
      speakText(sub.text_en)
    }
  }
}

// 播放指定字幕句
const replaySpecificSubtitle = (sub) => {
  const idx = subtitles.value.findIndex(s => s.id === sub.id)
  if (idx >= 0) {
    currentIndex.value = idx
    seekTo(sub.start_time)
    if (sub.text_en) {
      speakText(sub.text_en)
    }
  }
}

// 跟读指定字幕句
const startRecordingForSubtitle = (sub) => {
  const idx = subtitles.value.findIndex(s => s.id === sub.id)
  if (idx >= 0) {
    currentIndex.value = idx
    seekTo(sub.start_time)
    nextTick(() => {
      toggleRecording()
    })
  }
}

const nextSubtitle = () => {
  if (currentIndex.value < subtitles.value.length - 1) {
    seekTo(subtitles.value[currentIndex.value + 1].start_time)
  }
}

// ==================== 跟读录音功能 ====================

const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    await startRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []

    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }

    mediaRecorder.value.onstop = () => {
      const blob = new Blob(audioChunks.value, { type: 'audio/webm' })
      recordedBlob.value = blob
      audioUrl.value = URL.createObjectURL(blob)
      // 停止所有音轨
      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.value.start()
    isRecording.value = true
    toast.success('开始录音，请跟读当前字幕')

    // 自动暂停视频
    if (videoRef.value && !videoRef.value.paused) {
      videoRef.value.pause()
    }
  } catch (error) {
    console.error('无法访问麦克风:', error)
    toast.error('无法访问麦克风，请检查浏览器权限')
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    toast.success('录音完成，可以播放试听')
    // 更新收藏字幕的练习次数
    incrementBookmarkPracticeCount()
  }
}

const incrementBookmarkPracticeCount = async () => {
  if (!userStore.isLoggedIn || currentIndex.value < 0) return
  const sub = subtitles.value[currentIndex.value]
  if (!sub) return

  try {
    // 检查该字幕是否已收藏
    if (bookmarkedSubtitleIds.value.has(sub.id)) {
      const bookmark = bookmarkedSubtitleMap.value[sub.id]
      if (bookmark) {
        await subtitleBookmarkAPI.incrementPractice(bookmark.id)
      }
    }
  } catch (e) {
    // 静默失败，不影响用户体验
    console.debug('更新练习次数失败', e)
  }
}

const clearRecording = () => {
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  audioUrl.value = null
  recordedBlob.value = null
  audioChunks.value = []
  pronunciationResult.value = null
  toast.success('已清除录音')
}

// ==================== 学习进度 ====================

let progressTimer = null
let watchDurationTimer = null
let isVideoPlaying = ref(false)

const updateProgress = () => {
  if (!userStore.isLoggedIn || !material.value) return

  if (progressTimer) clearTimeout(progressTimer)
  progressTimer = setTimeout(async () => {
    if (!videoRef.value) return
    const progress = Math.floor((videoRef.value.currentTime / videoRef.value.duration) * 100)
    learningProgress.value = progress
    try {
      await learningAPI.updateProgress({
        material_id: material.value.id,
        progress,
        last_position: Math.floor(videoRef.value.currentTime),
        completed: progress >= 95
      })
    } catch (e) {
      console.error('更新进度失败', e)
    }
  }, 2000)
}

// ==================== 观看时长上报 ====================

const startWatchDurationTimer = () => {
  stopWatchDurationTimer()
  watchDurationTimer = setInterval(async () => {
    if (!videoRef.value || videoRef.value.paused || !material.value) return
    try {
      await learningAPI.updateProgress({
        material_id: material.value.id,
        progress: learningProgress.value,
        last_position: Math.floor(videoRef.value.currentTime),
        completed: learningProgress.value >= 95,
        watch_duration: 10
      })
    } catch (e) {
      console.error('上报观看时长失败', e)
    }
  }, 10000)
}

const stopWatchDurationTimer = () => {
  if (watchDurationTimer) {
    clearInterval(watchDurationTimer)
    watchDurationTimer = null
  }
}

// ==================== 数据加载 ====================

const loadMaterial = async () => {
  const id = route.params.id
  loading.value = true

  try {
    const [matRes, subRes] = await Promise.all([
      materialAPI.getDetail(id),
      materialAPI.getSubtitles(id)
    ])
    material.value = matRes
    subtitles.value = subRes

    // 检查收藏状态
    if (userStore.isLoggedIn) {
      await checkFavoriteStatus()
      // 获取学习进度
      try {
        const record = await learningAPI.getProgress(id)
        if (record && record.progress) {
          learningProgress.value = record.progress
          lastPosition.value = record.last_position || 0
        }
      } catch (e) {
        console.log('暂无学习记录')
      }
      // 加载标注数据
      await loadAnnotations()
      // 加载字幕收藏数据
      await loadBookmarks()
    }
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
  }
}

// ==================== 收藏功能 ====================

const checkFavoriteStatus = async () => {
  if (!material.value) return
  try {
    const res = await favoriteAPI.check(material.value.id)
    isFavorited.value = res.is_favorited
  } catch (e) {
    console.error('检查收藏状态失败', e)
  }
}

const toggleFavorite = async () => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }

  if (!material.value) return

  favoriteLoading.value = true
  try {
    if (isFavorited.value) {
      await favoriteAPI.remove(material.value.id)
      isFavorited.value = false
      toast.success('已取消收藏')
    } else {
      await favoriteAPI.add(material.value.id)
      isFavorited.value = true
      toast.success('收藏成功')
    }
  } catch (e) {
    console.error('收藏操作失败', e)
  } finally {
    favoriteLoading.value = false
  }
}

// ==================== 视频解读功能 ====================

const interpretationGeneratingStatus = ref('') // pending / generating / done / failed
let _pollTimer = null

const loadInterpretation = async () => {
  if (!material.value) return

  interpretationLoading.value = true
  try {
    const res = await materialAPI.getInterpretation(material.value.id)
    interpretation.value = {
      words: res.words || [],
      phrases: res.phrases || [],
      grammar: res.grammar || [],
      idioms: res.idioms || []
    }

    // 如果没有数据，检查生成状态
    if (!interpretation.value.words.length && !interpretation.value.phrases.length && !interpretation.value.grammar.length && !interpretation.value.idioms.length) {
      await checkInterpretationStatus()
    } else {
      interpretationGeneratingStatus.value = 'done'
    }

    // 加载学习状态
    await loadLearningStatus()
  } catch (e) {
    console.error('加载解读失败', e)
    toast.error('加载解读失败')
  } finally {
    interpretationLoading.value = false
  }
}

// 切换解读抽屉面板
const toggleInterpretationDrawer = () => {
  interpretationDrawerVisible.value = !interpretationDrawerVisible.value
  // 如果打开且还没有数据，触发加载
  if (interpretationDrawerVisible.value && !hasInterpretation.value && !interpretationLoading.value) {
    loadInterpretation()
  }
}

const checkInterpretationStatus = async () => {
  if (!material.value) return
  try {
    const res = await materialAPI.getInterpretationStatus(material.value.id)
    interpretationGeneratingStatus.value = res.status

    if (res.status === 'generating') {
      isGenerating.value = true
      startPolling()
    } else if (res.status === 'pending') {
      // 自动触发生成
      await triggerGeneration()
    } else if (res.status === 'failed') {
      isGenerating.value = false
    }
  } catch (e) {
    console.error('检查解读状态失败', e)
  }
}

const triggerGeneration = async () => {
  if (!material.value) return
  isGenerating.value = true
  interpretationGeneratingStatus.value = 'generating'
  try {
    await materialAPI.generateInterpretation(material.value.id)
    startPolling()
  } catch (e) {
    console.error('触发生成失败', e)
    toast.error(e.response?.data?.detail || '触发生成失败')
    isGenerating.value = false
    interpretationGeneratingStatus.value = 'failed'
  }
}

const startPolling = () => {
  stopPolling()
  _pollTimer = setInterval(async () => {
    try {
      const res = await materialAPI.getInterpretationStatus(material.value.id)
      if (res.status === 'done') {
        stopPolling()
        isGenerating.value = false
        interpretationGeneratingStatus.value = 'done'
        // 重新加载解读数据
        const interpRes = await materialAPI.getInterpretation(material.value.id)
        interpretation.value = {
          words: interpRes.words || [],
          phrases: interpRes.phrases || [],
          grammar: interpRes.grammar || [],
          idioms: interpRes.idioms || []
        }
        await loadLearningStatus()
        toast.success('解读生成完成!')
      } else if (res.status === 'failed') {
        stopPolling()
        isGenerating.value = false
        interpretationGeneratingStatus.value = 'failed'
        toast.error('解读生成失败，请重试')
      }
    } catch (e) {
      console.error('轮询状态失败', e)
    }
  }, 3000)
}

const stopPolling = () => {
  if (_pollTimer) {
    clearInterval(_pollTimer)
    _pollTimer = null
  }
}

// 跳转到字幕对应时间点
const seekToSubtitle = (item) => {
  if (item.first_appearance_time != null && videoRef.value) {
    videoRef.value.currentTime = item.first_appearance_time / 1000
  }
}

const generateInterpretation = async () => {
  if (!material.value) return
  // 使用新的触发生成逻辑
  await triggerGeneration()
}

// 添加到生词本
const addToVocabulary = async (item) => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    await vocabularyAPI.add({
      word: item.content_en,
      context: item.context_sentence || item.example_sentence || item.content_cn,
      material_id: material.value.id,
      subtitle_id: item.subtitle_id || null
    })
    toast.success('已添加到生词本')
  } catch (e) {
    console.error('添加生词失败', e)
    toast.error('添加失败')
  }
}

// ==================== 解读项学习状态 ====================

const loadLearningStatus = async () => {
  if (!userStore.isLoggedIn || !material.value) return

  try {
    const result = await interpretationAPI.getStatus(material.value.id)
    const statusMap = {}
    result.forEach(item => {
      statusMap[item.interpretation_id] = item.status
    })
    learningStatus.value = statusMap
  } catch (e) {
    console.error('加载学习状态失败', e)
  }
}

const setLearningStatus = async (interpretationId, status) => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }
  if (!material.value) return

  try {
    await interpretationAPI.setStatus({
      interpretation_id: interpretationId,
      material_id: material.value.id,
      status: status
    })
    learningStatus.value[interpretationId] = status
    toast.success(status === 'known' ? '已标记为认识' : status === 'unknown' ? '已标记为不认识' : '已标记为模糊')
  } catch (e) {
    console.error('设置学习状态失败', e)
    toast.error('设置失败')
  }
}

const getStatusLabel = (interpretationId) => {
  return learningStatus.value[interpretationId] || 'unknown'
}

const getStatusClass = (interpretationId) => {
  const status = learningStatus.value[interpretationId]
  if (status === 'known') return 'status-known'
  if (status === 'unknown') return 'status-unknown'
  return ''
}

const getStatusType = (interpretationId) => {
  const status = learningStatus.value[interpretationId] || 'unknown'
  const typeMap = {
    'known': 'success',
    'unknown': 'danger',
    'vague': 'warning'
  }
  return typeMap[status] || 'info'
}

// ==================== 单词点击功能 ====================

// 将字幕文本分割成单词数组（保留空格和标点）
const getSubtitleWords = (text) => {
  if (!text) return []
  // 使用正则表达式匹配单词和非单词字符
  return text.match(/\S+/g) || []
}

// 判断一个单词是否可点击（纯字母组成）
const isWordClickable = (word) => {
  // 移除标点符号后检查是否为纯字母
  const cleanWord = word.replace(/[.,!?;:'"()\[\]{}""''—–-]/g, '')
  return /^[a-zA-Z]+(['-][a-zA-Z]+)*$/.test(cleanWord) && cleanWord.length > 1
}

// 显示单词弹出框
const showWordPopup = async (word, event) => {
  // 清理单词（移除标点）
  const cleanWord = word.replace(/[.,!?;:'"()\[\]{}""''—–-]/g, '').toLowerCase()

  if (!cleanWord) return

  currentWord.value = cleanWord
  wordPopupVisible.value = true
  wordLoading.value = true
  wordInfo.value = { phonetic: '', translation: '', example: '' }

  try {
    // 调用单词查询 API
    const result = await vocabularyAPI.lookup(cleanWord)
    wordInfo.value = {
      phonetic: result.phonetic || '',
      translation: result.translation || result.meaning || '',
      example: result.example || ''
    }
  } catch (e) {
    console.error('查询单词失败', e)
    // 如果查询失败，尝试使用翻译 API
    try {
      const translateResult = await materialAPI.translateText(cleanWord)
      wordInfo.value = {
        phonetic: '',
        translation: translateResult.translation || cleanWord,
        example: ''
      }
    } catch (e2) {
      console.error('翻译也失败', e2)
      wordInfo.value = {
        phonetic: '',
        translation: '暂无释义',
        example: ''
      }
    }
  } finally {
    wordLoading.value = false
  }
}

// ==================== 生命周期 ====================

onMounted(() => {
  preloadVoices() // 预先加载 voices，避免 iOS 首次发音延迟
})

// 将当前单词添加到生词本
const addWordToVocabulary = async () => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }

  if (!currentWord.value) return

  addingWord.value = true
  try {
    await vocabularyAPI.add({
      word: currentWord.value,
      context: wordInfo.value.example || wordInfo.value.translation,
      material_id: material.value?.id
    })
    toast.success('已添加到生词本')
  } catch (e) {
    console.error('添加生词失败', e)
    if (e.response?.data?.detail?.includes('已存在')) {
      toast.info('该单词已在生词本中')
    } else {
      toast.error('添加失败')
    }
  } finally {
    addingWord.value = false
  }
}

// 从单词弹窗跳转到视频对应时间点
const seekToWordInVideo = () => {
  if (!wordInfo.value) return

  // 优先使用 first_appearance_time（来自 interpretation）
  const seekTime = wordInfo.value.first_appearance_time
    || wordInfo.value.context_start_time
    || wordInfo.value.example_start_time

  if (seekTime && videoRef.value) {
    videoRef.value.currentTime = seekTime
    if (videoRef.value.paused) {
      videoRef.value.play().catch(() => {})
    }
    wordPopupVisible.value = false
    toast.success(`已跳转到 ${formatTime(seekTime * 1000)}`)
  } else {
    // 尝试从 interpretation 中查找
    handleInterpretationClick(currentWord.value)
    wordPopupVisible.value = false
  }
}

// 添加当前字幕到生词本
const addSubtitleToVocabulary = async () => {
  if (!currentSubtitle.value) {
    toast.warning('没有当前字幕')
    return
  }

  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    await vocabularyAPI.add({
      word: currentSubtitle.value.text_en,
      context: currentSubtitle.value.text_en,
      material_id: material.value.id,
      subtitle_id: currentSubtitle.value.id
    })
    toast.success('已添加到生词本')
  } catch (e) {
    console.error('添加生词失败', e)
    toast.error('添加失败')
  }
}

// ==================== 字幕标注功能 ====================

// 加载标注数据
const loadAnnotations = async () => {
  if (!userStore.isLoggedIn || !material.value) return

  try {
    const result = await annotationAPI.getByMaterial(material.value.id)
    const annotationMap = {}
    result.forEach(ann => {
      if (!annotationMap[ann.subtitle_id]) {
        annotationMap[ann.subtitle_id] = []
      }
      annotationMap[ann.subtitle_id].push(ann)
    })
    annotations.value = annotationMap
  } catch (e) {
    console.error('加载标注失败', e)
  }
}

// ==================== 字幕收藏功能 ====================

// 加载收藏数据
const loadBookmarks = async () => {
  if (!userStore.isLoggedIn || !material.value) return

  try {
    const result = await subtitleBookmarkAPI.check(material.value.id)
    bookmarkedSubtitleIds.value = new Set(result.bookmarked_ids || [])

    // 同时加载完整收藏列表用于获取 bookmark id 和 practice_count
    const bookmarks = await subtitleBookmarkAPI.getList(material.value.id)
    const map = {}
    bookmarks.forEach(b => {
      map[b.subtitle_id] = b
    })
    bookmarkedSubtitleMap.value = map
  } catch (e) {
    console.error('加载收藏失败', e)
  }
}

// 切换字幕收藏
const toggleBookmark = async (subtitle) => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }

  const subId = subtitle.id
  const isBookmarked = bookmarkedSubtitleIds.value.has(subId)

  if (isBookmarked) {
    // 需要通过 material 的 bookmark list 获取 bookmark id
    // 简化：先获取列表再删除
    try {
      const bookmarks = await subtitleBookmarkAPI.getList(material.value.id)
      const target = bookmarks.find(b => b.subtitle_id === subId)
      if (target) {
        await subtitleBookmarkAPI.remove(target.id)
        bookmarkedSubtitleIds.value.delete(subId)
        bookmarkedSubtitleIds.value = new Set(bookmarkedSubtitleIds.value)
        toast.success('已取消收藏')
      }
    } catch (e) {
      console.error('取消收藏失败', e)
      toast.error('操作失败')
    }
  } else {
    try {
      await subtitleBookmarkAPI.add({
        material_id: material.value.id,
        subtitle_id: subId
      })
      bookmarkedSubtitleIds.value.add(subId)
      bookmarkedSubtitleIds.value = new Set(bookmarkedSubtitleIds.value)
      toast.success('已收藏该字幕')
    } catch (e) {
      console.error('收藏失败', e)
      if (e.response?.data?.detail?.includes('已收藏')) {
        bookmarkedSubtitleIds.value.add(subId)
        bookmarkedSubtitleIds.value = new Set(bookmarkedSubtitleIds.value)
      } else {
        toast.error('收藏失败')
      }
    }
  }
}

// 处理文本选择
// ==================== 点读跳转功能 ====================

// 点击标注高亮词，跳转到视频对应时间
const handleAnnotationClick = (event) => {
  // 检查点击的是否是高亮词
  const target = event.target
  if (!target.classList.contains('annotation-highlight')) return

  // 获取时间戳
  const startTime = target.dataset.startTime
  if (startTime !== undefined) {
    // 跳转到视频对应时间
    seekTo(parseFloat(startTime))

    // 视觉反馈：短暂高亮效果
    target.classList.add('jump-flash')
    setTimeout(() => {
      target.classList.remove('jump-flash')
    }, 500)
  }
}

// 点击解读项（单词/短语/语法），跳转到视频对应时间
const handleInterpretationClick = (contentEn) => {
  if (!contentEn || !subtitles.value.length) return

  // 先播放发音
  speakText(contentEn)

  // 在字幕中查找包含该词/短语的字幕
  const searchText = contentEn.toLowerCase().trim()
  const foundSubtitle = subtitles.value.find(sub => {
    const subtitleText = (sub.text_en || '').toLowerCase()
    // 检查是否包含完整词/短语
    return subtitleText.includes(searchText)
  })

  if (foundSubtitle) {
    // 跳转到该字幕的时间
    seekTo(foundSubtitle.start_time)

    // 更新当前字幕索引
    const index = subtitles.value.findIndex(s => s.id === foundSubtitle.id)
    if (index !== -1) {
      currentIndex.value = index
    }

    // 如果当前页不包含该字幕，跳转到对应页
    const targetPage = Math.ceil((index + 1) / subtitlePageSize)
    if (targetPage !== subtitleCurrentPage.value) {
      subtitleCurrentPage.value = targetPage
    }

    // 滚动到对应字幕
    scrollToSubtitle(index)

    toast.success(`跳转到: ${formatTime(foundSubtitle.start_time)}`)
  }
}

const handleTextSelection = (subtitle, event) => {
  const selection = window.getSelection()
  const selectedText = selection.toString().trim()

  if (!selectedText || selectedText.length < 2) return

  // 获取选择范围
  const range = selection.getRangeAt(0)
  const subtitleText = subtitle.text_en

  // 计算选中文本在字幕中的位置
  let startOffset = 0
  let endOffset = 0

  // 创建一个临时范围来计算偏移
  const tempRange = document.createRange()
  const subtitleElement = event.target.closest('.sub-text')

  if (subtitleElement) {
    tempRange.selectNodeContents(subtitleElement)
    tempRange.setEnd(range.startContainer, range.startOffset)
    startOffset = tempRange.toString().length
    endOffset = startOffset + selectedText.length
  }

  // 设置选中的标注信息
  selectedAnnotation.value = {
    subtitleId: subtitle.id,
    startOffset,
    endOffset,
    text: selectedText,
    type: 'vocabulary',
    color: annotationColors.vocabulary,
    note: ''
  }

  // 显示标注弹窗
  annotationPopupVisible.value = true

  // 清除选择
  selection.removeAllRanges()
}

// 保存标注
const saveAnnotation = async () => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }

  if (!selectedAnnotation.value.text) return

  try {
    const result = await annotationAPI.add({
      material_id: material.value.id,
      subtitle_id: selectedAnnotation.value.subtitleId,
      start_offset: selectedAnnotation.value.startOffset,
      end_offset: selectedAnnotation.value.endOffset,
      annotated_text: selectedAnnotation.value.text,
      annotation_type: selectedAnnotation.value.type,
      color: selectedAnnotation.value.color,
      note: selectedAnnotation.value.note
    })

    // 更新本地标注数据
    if (!annotations.value[selectedAnnotation.value.subtitleId]) {
      annotations.value[selectedAnnotation.value.subtitleId] = []
    }
    annotations.value[selectedAnnotation.value.subtitleId].push(result)

    toast.success('标注已保存')
    annotationPopupVisible.value = false
  } catch (e) {
    console.error('保存标注失败', e)
    toast.error('保存失败')
  }
}

// 删除标注
const deleteAnnotation = async (annotationId, subtitleId) => {
  try {
    await annotationAPI.delete(annotationId)

    // 更新本地数据
    if (annotations.value[subtitleId]) {
      annotations.value[subtitleId] = annotations.value[subtitleId].filter(a => a.id !== annotationId)
    }

    toast.success('标注已删除')
  } catch (e) {
    console.error('删除标注失败', e)
    toast.error('删除失败')
  }
}

// 获取字幕的标注文本（带高亮）
const getAnnotatedText = (subtitle) => {
  const text = subtitle.text_en
  const subtitleAnnotations = annotations.value[subtitle.id] || []

  // 收集解读词汇用于自动高亮
  const interpWords = []
  if (hasInterpretation.value) {
    const allItems = [
      ...(interpretation.value.words || []),
      ...(interpretation.value.phrases || []),
      ...(interpretation.value.grammar || []),
      ...(interpretation.value.idioms || [])
    ]
    allItems.forEach(item => {
      if (item.content_en) {
        const cleanWord = item.content_en.trim()
        if (cleanWord.length > 1) {
          interpWords.push(cleanWord)
        }
      }
    })
    // 按长度降序排列，优先匹配长词/短语
    interpWords.sort((a, b) => b.length - a.length)
  }

  // 如果没有标注也没有解读词汇，直接返回
  if (subtitleAnnotations.length === 0 && interpWords.length === 0) {
    return text
  }

  // 构建高亮区间列表
  const highlightRanges = []

  // 1. 用户标注（优先级最高）
  subtitleAnnotations.forEach(ann => {
    highlightRanges.push({
      start: ann.start_offset,
      end: ann.end_offset,
      type: 'annotation',
      data: ann
    })
  })

  // 2. 解读词汇高亮（不与用户标注重叠）
  if (interpWords.length > 0) {
    const lowerText = text.toLowerCase()
    interpWords.forEach(word => {
      const lowerWord = word.toLowerCase()
      let searchFrom = 0
      while (searchFrom < lowerText.length) {
        const idx = lowerText.indexOf(lowerWord, searchFrom)
        if (idx === -1) break

        // 检查是否与已有区间重叠
        const wordEnd = idx + word.length
        const overlaps = highlightRanges.some(r =>
          (idx >= r.start && idx < r.end) || (wordEnd > r.start && wordEnd <= r.end) ||
          (idx <= r.start && wordEnd >= r.end)
        )
        if (!overlaps) {
          highlightRanges.push({
            start: idx,
            end: wordEnd,
            type: 'interp',
            word: word
          })
        }
        searchFrom = wordEnd
      }
    })
  }

  if (highlightRanges.length === 0) {
    return text
  }

  // 排序区间
  highlightRanges.sort((a, b) => a.start - b.start)

  let result = ''
  let lastIndex = 0

  highlightRanges.forEach(range => {
    // 添加区间前的文本
    if (range.start > lastIndex) {
      result += escapeHtml(text.substring(lastIndex, range.start))
    }

    const rangeText = escapeHtml(text.substring(range.start, range.end))

    if (range.type === 'annotation') {
      const ann = range.data
      result += `<span class="annotation-highlight clickable-word" style="background-color: ${ann.color}20; border-bottom: 2px solid ${ann.color};" data-subtitle-id="${subtitle.id}" data-start-time="${subtitle.start_time}" data-annotation-id="${ann.id}" title="${getAnnotationTypeLabel(ann.annotation_type)} - 点击跳转">${rangeText}</span>`
    } else {
      result += `<span class="interp-word-highlight" data-start-time="${subtitle.start_time}" title="点击跳转">${rangeText}</span>`
    }

    lastIndex = range.end
  })

  // 添加剩余文本
  if (lastIndex < text.length) {
    result += escapeHtml(text.substring(lastIndex))
  }

  return result
}

// HTML 转义工具
const escapeHtml = (str) => {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

// 获取标注类型标签
const getAnnotationTypeLabel = (type) => {
  const labels = {
    vocabulary: '重点词汇',
    phrase: '重点短语',
    important: '重点内容'
  }
  return labels[type] || '标注'
}

// 标注类型变更
const onAnnotationTypeChange = (type) => {
  selectedAnnotation.value.color = annotationColors[type] || '#ff0000'
}

// ==================== 中英字幕切换 ====================

const setSubtitleMode = async (mode) => {
  if (mode === 'bilingual') {
    showOnlyChinese.value = false
    showTranslation.value = true
  } else if (mode === 'en-only') {
    showOnlyChinese.value = false
    showTranslation.value = false
  } else if (mode === 'cn-only') {
    showTranslation.value = false
    showOnlyChinese.value = true
  }
  // 确保有中文翻译
  if ((showTranslation.value || showOnlyChinese.value) && subtitles.value.length > 0) {
    const hasChinese = subtitles.value.some(sub => sub.text_cn)
    if (!hasChinese) {
      await translateSubtitles()
    }
  }
}

const toggleTranslation = async () => {
  showTranslation.value = !showTranslation.value
  // 如果开启仅中文模式，则关闭它
  if (showTranslation.value && showOnlyChinese.value) {
    showOnlyChinese.value = false
  }

  // 如果开启翻译且字幕没有中文，则自动翻译
  if (showTranslation.value && subtitles.value.length > 0) {
    const hasChinese = subtitles.value.some(sub => sub.text_cn)
    if (!hasChinese) {
      await translateSubtitles()
    }
  }
}

// 切换仅显示中文模式
const toggleOnlyChinese = async () => {
  showOnlyChinese.value = !showOnlyChinese.value

  // 如果开启仅中文模式，需要先确保有中文翻译
  if (showOnlyChinese.value && subtitles.value.length > 0) {
    // 关闭普通翻译模式
    if (showTranslation.value) {
      showTranslation.value = false
    }
    // 确保有中文翻译
    const hasChinese = subtitles.value.some(sub => sub.text_cn)
    if (!hasChinese) {
      await translateSubtitles()
    }
  }
}

const translateSubtitles = async () => {
  if (!material.value) return

  translationLoading.value = true
  try {
    const subList = subtitles.value.map(sub => ({
      text_en: sub.text_en,
      text_cn: sub.text_cn
    }))
    const result = await materialAPI.translateSubtitles(material.value.id, subList)
    // 更新字幕列表
    if (result && result.subtitles) {
      for (let i = 0; i < subtitles.value.length; i++) {
        if (result.subtitles[i] && result.subtitles[i].text_cn) {
          subtitles.value[i].text_cn = result.subtitles[i].text_cn
        }
      }
    }
    toast.success('翻译完成')
  } catch (e) {
    console.error('翻译失败', e)
    toast.error('翻译失败')
  } finally {
    translationLoading.value = false
  }
}

// ==================== 发音评测 ====================

const recognizedText = ref('')  // 语音识别结果

const evaluatePronunciation = async () => {
  if (!recordedBlob.value) {
    toast.warning('请先录音')
    return
  }
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    return
  }
  if (!currentSubtitle.value) {
    toast.warning('没有当前字幕')
    return
  }

  evaluationLoading.value = true
  pronunciationResult.value = null
  recognizedText.value = ''

  try {
    // 使用语音识别 + 发音评测一体化接口
    const result = await speechAPI.recognizeAndEvaluate(
      recordedBlob.value,
      currentSubtitle.value.text_en
    )

    if (!result.success) {
      toast.error(result.error || '语音识别失败')
      // 如果语音识别失败，降级使用旧的评测方式
      const fallbackResult = await pronunciationAPI.evaluate(
        currentSubtitle.value.text_en,
        currentSubtitle.value.text_en
      )
      pronunciationResult.value = fallbackResult
      evaluationLoading.value = false
      return
    }

    recognizedText.value = result.recognized_text
    pronunciationResult.value = result.pronunciation_result

    if (pronunciationResult.value.score >= 80) {
      toast.success(`发音评测：${pronunciationResult.value.score}分，表现不错！`)
    } else if (pronunciationResult.value.score >= 60) {
      toast.warning(`发音评测：${pronunciationResult.value.score}分，继续加油！`)
    } else {
      toast.error(`发音评测：${pronunciationResult.value.score}分，需要多练习`)
    }
  } catch (e) {
    console.error('发音评测失败', e)
    toast.error('发音评测失败')
  } finally {
    evaluationLoading.value = false
  }
}

// ==================== 听写模式相关 ====================

const onDictationUpdateProgress = (newIndex) => {
  dictationIndex.value = newIndex
}

const onDictationComplete = (stats) => {
  toast.success(`听写练习完成！完成 ${stats.completedCount} 句，平均得分 ${stats.averageScore} 分`)
}

// ==================== 键盘快捷键 ====================

const handleKeyboard = (e) => {
  // 如果正在输入则不响应
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return

  switch (e.key) {
    case ' ':
      e.preventDefault()
      if (videoRef.value) {
        if (videoRef.value.paused) {
          videoRef.value.play()
        } else {
          videoRef.value.pause()
        }
      }
      break
    case 'ArrowLeft':
      e.preventDefault()
      prevSubtitle()
      break
    case 'ArrowRight':
      e.preventDefault()
      nextSubtitle()
      break
    case 'r':
    case 'R':
      e.preventDefault()
      replaySubtitle()
      break
    case '?':
      e.preventDefault()
      showShortcutPanel.value = !showShortcutPanel.value
      break
  }
}

// ==================== 生命周期 ====================

// 同步子组件的 video 元素引用
watch(() => videoPlayerRef.value?.playerRef, (el) => {
  if (el) videoRef.value = el
}, { immediate: true })

onMounted(() => {
  loadMaterial()
  // 确保获取最新用户信息
  if (userStore.token) {
    userStore.fetchProfile()
  }
  // 添加键盘事件
  window.addEventListener('keydown', handleKeyboard)
})

onUnmounted(() => {
  // 清理录音资源
  clearRecording()
  // 移除键盘事件
  window.removeEventListener('keydown', handleKeyboard)
  // 清理轮询
  stopPolling()
  // 清理观看时长定时器
  stopWatchDurationTimer()
})
</script>

<style scoped>
/* ==================== 页面容器 ==================== */
.sf-learn-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 20px 24px;
}

/* 模式切换淡入动画 */
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.sf-mode-content {
  animation: fadeSlideIn 0.3s var(--sf-easing-standard);
}

/* ==================== Annotation Popup 按钮 ==================== */
.sf-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--sf-radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--sf-duration-fast);
  border: 1px solid transparent;
}
.sf-btn--sm { padding: 6px 12px; font-size: 13px; }
.sf-btn--ghost {
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}
.sf-btn--ghost:hover {
  color: var(--color-brand-bright);
  border-color: var(--color-border-brand);
}
.sf-btn--primary {
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(63, 138, 91, 0.3);
}
.sf-btn--primary:hover {
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  filter: brightness(1.08);
  box-shadow: 0 6px 20px rgba(63, 138, 91, 0.4);
}
.sf-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ==================== 主内容区 ==================== */
.sf-main-content {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
  gap: 16px;
  align-items: start;
  animation: fadeSlideIn 0.3s var(--sf-easing-standard);
}

/* 两栏卡片化 */
.sf-left-column,
.sf-middle-column {
  background: var(--sf-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-lg);
  overflow: hidden;
}

/* 卡片内边距 */
.sf-card-inner {
  padding: 16px;
}

.sf-card-inner--secondary {
  padding: 0 16px 16px;
}

/* 听写模式全宽卡片 */
.sf-dictation-wrapper {
  grid-column: 1 / -1;
  background: var(--sf-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-lg);
  overflow: hidden;
  min-height: 400px;
}

/* 左栏：视频 + 跟读卡片 */
.sf-left-column {
  display: grid;
  grid-template-rows: auto auto;
  gap: 0;
}

.sf-left-column .sf-card-inner:first-child {
  padding: 20px 20px 14px;
}

.sf-left-column .sf-card-inner--secondary {
  padding: 14px 20px 20px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-pale, var(--sf-bg-card));
}

/* 中栏 */
.sf-middle-column {
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 110px);
  overflow: hidden;
  position: sticky;
  top: 70px;
}

.sf-middle-column .sf-card-inner {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 滚动条 */
.sf-main-content ::-webkit-scrollbar,
.sf-card-inner::-webkit-scrollbar {
  width: 5px;
}
.sf-main-content ::-webkit-scrollbar-track,
.sf-card-inner::-webkit-scrollbar-track {
  background: transparent;
}
.sf-main-content ::-webkit-scrollbar-thumb,
.sf-card-inner::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}
.dark .sf-main-content ::-webkit-scrollbar-thumb,
.dark .sf-card-inner::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
}

/* ==================== 快捷键帮助面板 ==================== */
.sf-shortcut-trigger {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
  border-radius: var(--sf-radius-full);
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(63, 138, 91, 0.4);
  z-index: 100;
  transition: all var(--sf-duration-fast) var(--sf-ease-bounce);
  border: none;
}
.sf-shortcut-trigger:hover {
  transform: scale(1.08) translateY(-1px);
  box-shadow: var(--sf-shadow-lg);
  background: var(--sf-brand-hover);
}
.sf-shortcut-trigger.active {
  background: var(--color-text-primary);
}

/* ==================== 解读面板触发器 ==================== */
.sf-interpretation-trigger {
  position: fixed;
  bottom: 24px;
  right: 76px;
  height: 40px;
  padding: 0 16px;
  border-radius: var(--sf-radius-full);
  background: var(--yt-cta-gradient, linear-gradient(#4DA06C 0%, #3F8A5B 100%));
  color: #fff;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(63, 138, 91, 0.4);
  z-index: 100;
  transition: all var(--sf-duration-fast) var(--sf-ease-bounce);
  border: none;
  font-size: 14px;
  font-weight: 500;
}

.sf-interpretation-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(63, 138, 91, 0.5);
  filter: brightness(1.05);
}

.sf-interpretation-trigger .sf-badge {
  background: rgba(255, 255, 255, 0.25);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.sf-interpretation-sheet {
  width: 400px !important;
  max-width: 90vw;
}

.sf-interpretation-sheet :deep(.sheet-content) {
  height: 100%;
  max-height: 100vh;
}

.sf-interpretation-sheet :deep(.sheet-header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.sf-interpretation-sheet :deep(.sheet-body) {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* ==================== 快捷键面板 ==================== */
.sf-shortcut-panel {
  z-index: 101;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.sf-shortcut-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  font-weight: 700;
  font-size: 14px;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
}

.sf-shortcut-panel__close {
  cursor: pointer;
  color: var(--color-text-muted);
  background: none;
  border: none;
  font-size: 16px;
  padding: 2px;
  border-radius: var(--sf-radius-sm);
  transition: color var(--sf-duration-fast);
}
.sf-shortcut-panel__close:hover { color: var(--color-text-primary); }

.sf-shortcut-list {
  padding: 8px 0;
}

.sf-shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.sf-shortcut-item kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 24px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 600;
  font-family: var(--sf-font-mono);
  text-align: center;
  background: var(--sf-bg-card);
  border: 1px solid var(--sf-border-strong);
  border-bottom-width: 2px;
  border-radius: var(--sf-radius-sm);
  color: var(--color-text-primary);
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}

/* ==================== 标注弹窗 ==================== */

.sf-annotation-popup-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sf-annotation-preview {
  padding: 12px 14px;
  background: var(--sf-bg-elevated);
  border-radius: var(--sf-radius-md);
}
.sf-annotation-preview__label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.sf-annotation-preview__text {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-brand-bright);
}

.sf-annotation-type-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.sf-annotation-type-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sf-annotation-type-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--sf-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-md);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: all var(--sf-duration-fast);
  font-family: inherit;
}
.sf-annotation-type-btn:hover {
  border-color: var(--sf-border-strong);
  color: var(--color-text-primary);
}
.sf-annotation-type-btn.selected {
  border-color: var(--color-brand-bright);
  background: var(--color-bg-mint);
  color: var(--color-brand-bright);
}
.sf-annotation-type-dot {
  font-size: 10px;
}

.sf-annotation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 6px;
}

/* ==================== 响应式适配 ==================== */
/* Phase 1B Task 1: 删掉 1280px / 1100px 的 3 列布局（解读面板已改 Sheet，右栏幽灵 div 浪费 340px 空白） */
@media (max-width: 1024px) {
  .sf-main-content {
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
  }
  .sf-left-column {
    grid-template-rows: auto auto;
  }
}

@media (max-width: 768px) {
  .sf-learn-page {
    padding: 0 12px 20px;
    padding-bottom: 80px; /* 给底部 tab bar 留空间 */
  }
  .sf-page-header {
    margin-bottom: 10px;
  }
  .sf-title {
    font-size: 16px;
  }
  .sf-segment {
    margin: 0 0 12px;
  }
  .sf-segment__item {
    padding: 8px 14px;
    font-size: 13px;
  }
  .sf-main-content {
    grid-template-columns: 1fr;
  }
  .sf-left-column,
  .sf-middle-column,
  .sf-right-column {
    margin-right: 0;
    margin-bottom: 12px;
  }
  .sf-shadowing-card__en {
    font-size: 20px;
  }
  .sf-dictation-mode .sf-dictation-sentence {
    font-size: 16px;
  }
  .sf-dictation-score {
    font-size: 32px;
    height: 64px;
    min-width: 64px;
  }

  /* ========== Phase 1B Task 2: 移动端 Tab 切换 ========== */
  /* 默认隐藏跟读卡和中栏，由 data-mobile-tab 控制显示 */
  .sf-left-column .sf-card-inner--secondary,
  .sf-main-content[data-mobile-tab="video"] .sf-middle-column {
    display: none;
  }
  /* shadowing tab: 显示跟读卡 + 字幕（紧凑） */
  .sf-main-content[data-mobile-tab="shadowing"] .sf-left-column .sf-card-inner:first-child {
    display: none;
  }
  .sf-main-content[data-mobile-tab="shadowing"] .sf-middle-column {
    display: none;
  }
  /* subtitles tab: 显示中栏 + 隐藏视频 */
  .sf-main-content[data-mobile-tab="subtitles"] .sf-left-column {
    display: none;
  }

  /* 视频贴顶（mobile-only 视频 tab） */
  .sf-main-content[data-mobile-tab="video"] {
    margin-top: -12px;
  }
  .sf-main-content[data-mobile-tab="video"] .sf-card-inner:first-child {
    border-radius: 0 0 var(--sf-radius-lg) var(--sf-radius-lg);
    margin: 0 -12px;
    padding: 0;
  }

  /* 解读按钮 mobile 隐藏（tab bar 接管） */
  .sf-interpretation-trigger {
    display: none !important;
  }
}

/* ========== Phase 1B Task 2: 移动端底部 Tab Bar ========== */
.sf-mobile-tabs {
  display: none;
}
@media (max-width: 768px) {
  .sf-mobile-tabs {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 64px;
    background: var(--color-bg-card);
    border-top: 1px solid var(--color-border);
    z-index: 200;
    box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.08);
    padding-bottom: env(safe-area-inset-bottom, 0);
  }
  .sf-mobile-tab {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    font-size: 11px;
    cursor: pointer;
    min-height: 48px;
    transition: color var(--sf-duration-fast);
    -webkit-tap-highlight-color: transparent;
  }
  .sf-mobile-tab:active {
    transform: scale(0.96);
  }
  .sf-mobile-tab.active {
    color: var(--color-brand-bright);
    font-weight: 600;
  }
  .sf-mobile-tab-label {
    line-height: 1;
  }
}

@media (max-width: 480px) {
  .sf-page-header {
    padding-bottom: 10px;
  }
  .sf-header-left {
    gap: 8px;
  }
  .sf-title {
    font-size: 15px;
  }
  .sf-segment {
    margin: 0 0 10px;
  }
  .sf-segment__item {
    padding: 8px 12px;
    font-size: 12px;
  }
  .sf-stat-badge {
    font-size: 10px;
    padding: 2px 8px;
  }
}

/* ==================== 骨架屏加载态 ==================== */
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.sf-skeleton-page { /* placeholder */ }

.sf-skeleton-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.sf-skeleton-segment {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.sf-skeleton-line {
  background: linear-gradient(90deg,
    var(--sf-bg-elevated) 25%,
    var(--sf-bg-card) 50%,
    var(--sf-bg-elevated) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease infinite;
}

.sf-skeleton-block {
  background: linear-gradient(90deg,
    var(--sf-bg-elevated) 25%,
    var(--sf-bg-card) 50%,
    var(--sf-bg-elevated) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease infinite;
}

.dark .sf-skeleton-line,
.dark .sf-skeleton-block {
  background: linear-gradient(90deg,
    rgba(255,255,255,0.04) 25%,
    rgba(255,255,255,0.08) 50%,
    rgba(255,255,255,0.04) 75%
  );
  background-size: 200% 100%;
}

/* ==================== 解读词汇高亮（跨组件生效） ==================== */
:deep(.interp-word-highlight) {
  border-bottom: 2px solid var(--color-brand-bright);
  background: var(--sf-brand-subtle);
  border-radius: 2px;
  cursor: pointer;
  transition: all var(--sf-duration-fast);
  padding: 0 1px;
}
:deep(.interp-word-highlight:hover) {
  background: var(--sf-brand-light);
  color: var(--color-brand-bright);
}

/* ==================== 标注高亮 ==================== */
:deep(.annotation-highlight) {
  cursor: pointer;
  border-radius: 2px;
  padding: 1px 2px;
  transition: all var(--sf-duration-fast);
}
:deep(.annotation-highlight:hover) {
  filter: brightness(0.95);
}

@keyframes sf-jump-flash {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
:deep(.annotation-highlight.jump-flash) {
  animation: sf-jump-flash 0.3s ease;
}
</style>
