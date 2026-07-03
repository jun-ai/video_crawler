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
        <div class="sf-right-column" :class="{ 'drawer-open': showToolboxDrawer }">
          <div class="sf-card-inner">
            <div class="sf-skeleton-block" style="height: 320px; border-radius: var(--sf-radius-lg);"></div>
          </div>
        </div>
      </div>
    </template>

    <!-- 主内容（加载完成后） -->
    <template v-else>
      <!-- 页面头部 — Phase 1B Task 4: 提取到独立组件 -->
      <template v-if="!isMobileView">
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
      </template>
      <!-- H5 端: 极简 header (只有返回 + 标题), 跟对标一样 -->
      <header v-else class="sf-h5-header">
        <button class="sf-h5-back" type="button" @click="$router.back()" aria-label="返回">
          <ArrowLeft :size="22" />
        </button>
        <h1 class="sf-h5-title">{{ material?.title }}</h1>
      </header>

      <!-- 学习模式切换 — Phase 1B Task 3: 提取到独立组件 -->
      <LearnModeSwitcher v-if="!isMobileView" v-model="learningMode" />

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
              :font-size="subtitleFontSize"
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

        <!-- Phase 9 (H5): AI 智能解读 + 开始跟读 sticky 操作条, 视频下方固定, 永远可见 1-tap 入口 -->
        <div class="sf-ai-action-bar">
          <button
            class="sf-ai-action-bar__btn sf-ai-action-bar__btn--ai"
            :class="{ 'sf-ai-action-bar__btn--done': hasInterpretation, 'sf-ai-action-bar__btn--loading': isGenerating }"
            :disabled="isGenerating"
            @click="handleAiAction"
            aria-label="AI 智能解读"
          >
            <Sparkles v-if="!hasInterpretation && !isGenerating" :size="18" />
            <span v-else-if="isGenerating" class="sf-ai-action-bar__spinner"></span>
            <Check v-else :size="18" />
            <span class="sf-ai-action-bar__label">
              {{ isGenerating ? 'AI 分析中' : (hasInterpretation ? '已解读' : 'AI 智能解读') }}
            </span>
          </button>
          <button
            class="sf-ai-action-bar__btn sf-ai-action-bar__btn--shadow"
            @click="openPracticePage"
            aria-label="开始跟读"
          >
            <Play :size="18" />
            <span class="sf-ai-action-bar__label">开始跟读</span>
          </button>
        </div>

        <!-- 中栏：字幕列表区域 -->
        <div class="sf-middle-column">
          <div class="sf-card-inner">
            <LearnSubtitleList
            ref="subtitleListRef"
            :subtitles="subtitles"
            :paginated-subtitles="paginatedSubtitles"
            :current-subtitle-index-in-page="currentSubtitleIndexInPage"
            :current-index="currentIndex"
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
            :font-size="subtitleFontSize"
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

        <!-- 右栏：学习工具箱 -->
        <div class="sf-right-column" :class="{ 'drawer-open': showToolboxDrawer }">
          <button class="sf-drawer-close" @click="showToolboxDrawer = false" aria-label="关闭">
            <X :size="18" />
          </button>
          <LearnToolbox
            :learning-progress="learningProgress"
            :vocab-count="interpretation.words.length + interpretation.phrases.length"
            :bookmark-count="bookmarkedSubtitleIds.size"
            :annotation-count="annotationCount"
            :has-interpretation="hasInterpretation"
            :is-generating="isGenerating"
            @open-interpretation="interpretationSheetOpen = true"
          />
        </div>
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

    <!-- 工具箱抽屉触发器（仅 < 1280px 显示） -->
    <button class="sf-toolbox-trigger" @click="showToolboxDrawer = true" v-if="!loading">
      <Wrench :size="18" />
      <span class="sf-badge" v-if="vocabCount + bookmarkedSubtitleIds.size > 0">{{ vocabCount + bookmarkedSubtitleIds.size }}</span>
    </button>

    <!-- 工具箱抽屉遮罩 -->
    <div class="sf-toolbox-overlay" v-if="showToolboxDrawer" @click="showToolboxDrawer = false"></div>

    <!-- Phase 1B Task 2 + Phase 2 (H5): 移动端 5-icon 工具栏 (SpeakVlog 规范: 字幕/倍速/闪卡/收藏/练习) -->
    <!-- Phase 8: 拆 2 行 — 次行 2-icon (循环+更多) + 主行 5-icon, 单次显示当前 play mode -->
    <div class="sf-mobile-tabs-wrap" v-if="!loading">
      <nav class="sf-mobile-tabs sf-mobile-tabs--secondary">
        <button
          v-for="tab in mobileTabsSecondary"
          :key="tab.key"
          :class="['sf-mobile-tab', 'sf-mobile-tab--compact', { active: isMobileTabActive(tab.key) }]"
          @click="setMobileTab(tab.key)"
          :aria-label="tab.label"
        >
          <component :is="tab.icon" :size="16" />
          <span class="sf-mobile-tab-label">{{ tab.label }}</span>
        </button>
      </nav>
      <nav class="sf-mobile-tabs sf-mobile-tabs--primary">
        <button
          v-for="tab in mobileTabs"
          :key="tab.key"
          :class="['sf-mobile-tab', { active: isMobileTabActive(tab.key) }]"
          @click="setMobileTab(tab.key)"
          :aria-label="tab.label"
        >
          <component :is="tab.icon" :size="20" />
          <span class="sf-mobile-tab-label">{{ tab.label }}</span>
        </button>
      </nav>
    </div>

    <!-- 解读面板 Sheet — desktop right side, H5 bottom 全屏 (phase 10: 不被 toolbar/AI bar 覆盖)
         phase 11: 移除重复 SheetHeader (Drawer 自带 "视频解读" h3) + shadcn 默认 X 隐藏 (Drawer 自带大 X) -->
    <Sheet v-model:open="interpretationSheetOpen">
      <SheetContent :side="isMobileView ? 'bottom' : 'right'" class="sf-interpretation-sheet">
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
          @close="interpretationSheetOpen = false"
        />
      </SheetContent>
    </Sheet>

    <!-- Phase 2 (H5): 移动端 字幕设置 Sheet (双语/英文/中文/字号) -->
    <Sheet v-model:open="showSubtitleSettings">
      <SheetContent side="bottom" class="sf-subtitle-settings-sheet">
        <SheetHeader>
          <SheetTitle>字幕设置</SheetTitle>
        </SheetHeader>
        <div class="sf-subtitle-settings">
          <!-- 字幕模式单选 -->
          <div class="sf-subtitle-row">
            <span class="sf-subtitle-label">字幕模式</span>
            <div class="sf-subtitle-options">
              <button
                v-for="opt in [
                  { key: 'bilingual', label: '双语' },
                  { key: 'en-only',   label: '仅英文' },
                  { key: 'cn-only',   label: '仅中文' }
                ]"
                :key="opt.key"
                :class="['sf-subtitle-opt', { active: subtitleMode === opt.key }]"
                @click="setSubtitleMode(opt.key)"
              >{{ opt.label }}</button>
            </div>
          </div>
          <!-- 字号滑块 -->
          <div class="sf-subtitle-row">
            <span class="sf-subtitle-label">字体大小</span>
            <div class="sf-subtitle-size-row">
              <button
                v-for="size in [14, 16, 18, 20]"
                :key="size"
                :class="['sf-subtitle-opt', { active: subtitleFontSize === size }]"
                @click="subtitleFontSize = size"
              >{{ size }}</button>
            </div>
          </div>
          <!-- 应用/关闭 -->
          <div class="sf-subtitle-actions">
            <button class="sf-subtitle-cancel" @click="showSubtitleSettings = false">关闭</button>
          </div>
        </div>
      </SheetContent>
    </Sheet>

    <!-- Phase 2 (H5): 移动端 倍速选择 Sheet -->
    <Sheet v-model:open="showPlaybackRateSheet">
      <SheetContent side="bottom" class="sf-playback-rate-sheet">
        <SheetHeader>
          <SheetTitle>播放倍速</SheetTitle>
        </SheetHeader>
        <div class="sf-playback-rate-list">
          <button
            v-for="rate in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]"
            :key="rate"
            :class="['sf-rate-opt', { active: playbackRate === rate }]"
            @click="selectPlaybackRate(rate)"
          >
            <span class="sf-rate-label">{{ rate }}x</span>
            <span v-if="playbackRate === rate" class="sf-rate-check">✓</span>
          </button>
        </div>
      </SheetContent>
    </Sheet>

    <!-- Phase 6 (H5): 移动端 练习模式 Sheet (跟读/听写/复述) -->
    <Sheet v-model:open="showPracticeSheet">
      <SheetContent side="bottom" class="sf-practice-sheet">
        <SheetHeader>
          <SheetTitle>选择练习模式</SheetTitle>
        </SheetHeader>
        <div class="sf-practice-list">
          <button
            :class="['sf-practice-opt', { active: learningMode === 'shadowing' }]"
            @click="selectPracticeMode('shadowing')"
          >
            <span class="sf-practice-label">跟读</span>
            <span class="sf-practice-desc">看字幕跟读模仿</span>
            <span v-if="learningMode === 'shadowing'" class="sf-practice-check">✓</span>
          </button>
          <button
            :class="['sf-practice-opt', { active: learningMode === 'dictation' }]"
            @click="selectPracticeMode('dictation')"
          >
            <span class="sf-practice-label">听写</span>
            <span class="sf-practice-desc">听音频默写句子</span>
            <span v-if="learningMode === 'dictation'" class="sf-practice-check">✓</span>
          </button>
          <button
            :class="['sf-practice-opt']"
            @click="selectPracticeMode('retelling')"
          >
            <span class="sf-practice-label">复述</span>
            <span class="sf-practice-desc">听后用自己的话复述 (开发中)</span>
          </button>
        </div>
      </SheetContent>
    </Sheet>

    <!-- Phase 8 (H5): 移动端 播放模式 Sheet (单次/循环/连续/单句) -->
    <Sheet v-model:open="showPlayModeSheet">
      <SheetContent side="bottom" class="sf-playmode-sheet">
        <SheetHeader>
          <SheetTitle>播放模式</SheetTitle>
        </SheetHeader>
        <div class="sf-playmode-list">
          <button
            v-for="opt in [
              { key: 'single',         label: '单次播放', desc: '播完当前视频就停' },
              { key: 'single-loop',    label: '单集循环', desc: '当前视频循环播放' },
              { key: 'continuous',     label: '连续播放', desc: '播完自动播下一个' },
              { key: 'sentence-loop',  label: '单句循环', desc: '当前字幕循环' }
            ]"
            :key="opt.key"
            :class="['sf-playmode-opt', { active: playMode === opt.key }]"
            @click="selectPlayMode(opt.key)"
          >
            <span class="sf-playmode-label">{{ opt.label }}</span>
            <span class="sf-playmode-desc">{{ opt.desc }}</span>
            <span v-if="playMode === opt.key" class="sf-playmode-check">✓</span>
          </button>
        </div>
      </SheetContent>
    </Sheet>

    <!-- Phase 8 (H5): 移动端 更多 Sheet (字幕模式 / 自动滚动 / 生成解读) -->
    <Sheet v-model:open="showMoreSheet">
      <SheetContent side="bottom" class="sf-more-sheet">
        <SheetHeader>
          <SheetTitle>更多</SheetTitle>
        </SheetHeader>
        <div class="sf-more-list">
          <button
            :class="['sf-more-opt', { active: subtitleMode === 'bilingual' }]"
            @click="setSubtitleMode('bilingual'); showMoreSheet = false"
          >
            <span class="sf-more-label">双语字幕</span>
            <span v-if="subtitleMode === 'bilingual'" class="sf-more-check">✓</span>
          </button>
          <button
            :class="['sf-more-opt', { active: subtitleMode === 'en-only' }]"
            @click="setSubtitleMode('en-only'); showMoreSheet = false"
          >
            <span class="sf-more-label">仅英文</span>
            <span v-if="subtitleMode === 'en-only'" class="sf-more-check">✓</span>
          </button>
          <button
            :class="['sf-more-opt', { active: subtitleMode === 'cn-only' }]"
            @click="setSubtitleMode('cn-only'); showMoreSheet = false"
          >
            <span class="sf-more-label">仅中文</span>
            <span v-if="subtitleMode === 'cn-only'" class="sf-more-check">✓</span>
          </button>
          <button
            class="sf-more-opt"
            @click="toggleAutoScroll()"
          >
            <span class="sf-more-label">{{ autoScroll ? '关闭自动滚动' : '开启自动滚动' }}</span>
            <span v-if="autoScroll" class="sf-more-check">✓</span>
          </button>
          <!-- Phase 9: AI 智能解读 移到视频下 sticky bar (1-tap), 此处只显示说明, 已生成时变 "查看解读" -->
          <button
            :class="['sf-more-opt']"
            @click="handleAiAction"
            v-if="hasInterpretation"
          >
            <span class="sf-more-label">查看 AI 解读</span>
            <span class="sf-more-check">✓</span>
          </button>
        </div>
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
  Wrench,
  Type,
  Gauge,
  Layers,
  PencilLine,
  Repeat,
  MoreHorizontal,
  Sparkles
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
import LearnToolbox from '@/components/learn/LearnToolbox.vue'

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
// Phase 2 (H5): 移动端工具栏抽屉状态
const showSubtitleSettings = ref(false)   // 字幕设置 sheet (双语/英文/中文/字号)
const showPlaybackRateSheet = ref(false)  // 倍速选择 sheet
const showPlayModeSheet = ref(false)      // Phase 8 (H5): 播放模式 sheet (单次/循环/连续/单句)
const showMoreSheet = ref(false)          // Phase 8 (H5): 更多 sheet (字幕模式/自动滚动/生成解读)
const showToolboxDrawer = ref(false)      // 兼容旧 API, 移动端工具抽屉

// 工具箱 badge 计数
const vocabCount = computed(() => (interpretation.value?.words?.length || 0) + (interpretation.value?.phrases?.length || 0))

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

// Phase 8 (H5): Sheet 用的 play mode 选择 (关 sheet + toast)
const selectPlayMode = (mode) => {
  setPlayMode(mode)
  showPlayModeSheet.value = false
  toast.success(`播放: ${playModeLabels[mode] || mode}`)
}

// Phase 8 (H5): 更多 sheet — 自动滚动开关
const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
  showMoreSheet.value = false
  toast.success(autoScroll.value ? '自动滚动已开启' : '自动滚动已关闭')
}

// Phase 9 (H5): AI 操作条按钮: 有解读 → 打开解读 sheet, 无 → 调 LLM 生成
const handleAiAction = () => {
  if (isGenerating.value) return
  if (hasInterpretation.value) {
    // 已有解读 → 打开 sheet (桌面右侧 / H5 弹右侧)
    interpretationSheetOpen.value = true
  } else {
    // 没解读 → 调 LLM 生成
    generateInterpretation()
  }
}

// 学习模式：'shadowing' 跟读模式, 'dictation' 听写模式
const learningMode = ref('shadowing')
const dictationIndex = ref(0)  // 听写模式当前索引

// Phase 1B Task 2 + Phase 2 (H5): 移动端 5-icon 工具栏 (SpeakVlog 规范 — 字幕/倍速/闪卡/收藏/练习)
// H5 不是"砍剩 1 个", 也不是"PC 平移" — 跟对标保持 5 入口, 各打开对应 sheet/动作
// Phase 8: 顶部 play mode + 更多 整合成次行 2-icon (循环/更多), 主行不变
const mobileActiveTab = ref(null)  // null = 默认视图

// Phase 8: 次行 (循环 + 更多) — 紧凑样式, 显示当前 play mode 在 label
const mobileTabsSecondary = computed(() => [
  { key: 'playMode', label: playModeShortLabel.value, icon: Repeat, action: 'openPlayMode' },
  { key: 'more',     label: '更多',                   icon: MoreHorizontal, action: 'openMore' }
])
const playModeShortLabel = computed(() => ({
  single: '单次', 'single-loop': '循环', continuous: '连续', 'sentence-loop': '单句'
}[playMode.value] || '单次'))

// Phase 15: 砍掉闪卡 (H5 砍掉生词本, 闪卡目标页 /vocabulary-review 屏蔽, 按钮失效)
const mobileTabs = [
  { key: 'subtitle',     label: '字幕', icon: Type,      action: 'openSubtitleSettings' },
  { key: 'playbackRate', label: '倍速', icon: Gauge,     action: 'openPlaybackRate' },
  { key: 'practice',     label: '练习', icon: PencilLine, action: 'openPracticePage' }
]

const setMobileTab = (key) => {
  // 先查次行
  const sec = mobileTabsSecondary.value.find(t => t.key === key)
  if (sec) { handleSecAction(sec.action); return }
  // 再查主行
  const tab = mobileTabs.find(t => t.key === key)
  if (!tab) return
  switch (tab.action) {
    case 'openSubtitleSettings': showSubtitleSettings.value = true; break
    case 'openPlaybackRate':     showPlaybackRateSheet.value = true; break
    case 'openPracticePage':     openPracticePage(); break
  }
}

const handleSecAction = (action) => {
  switch (action) {
    case 'openPlayMode':  showPlayModeSheet.value = true; break
    case 'openMore':      showMoreSheet.value = true; break
  }
}

// Phase 6 (H5): 练习 → 跳独立页 /practice?material_id=N (H5 极简 header + 返回箭头)
const openPracticePage = () => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }
  const mid = material.value?.id
  router.push(mid ? `/practice?material_id=${mid}` : '/practice')
}

// Phase 6 (H5): 练习 → 弹 practice sheet (跟读/听写/复述 3 选 1), 在 learn 内切模式, 不跳独立页
const openPracticeSheet = () => {
  showPracticeSheet.value = true
}

const showPracticeSheet = ref(false)
const selectPracticeMode = (mode) => {
  // mode: 'shadowing' (跟读) | 'dictation' (听写) | 'retelling' (复述)
  learningMode.value = mode
  showPracticeSheet.value = false
  if (mode === 'dictation') {
    toast.success('已切换到听写模式')
  } else if (mode === 'retelling') {
    toast.info('复述模式开发中, 当前用跟读')
    learningMode.value = 'shadowing'
  } else {
    toast.success('已切换到跟读模式')
  }
}

// 工具栏高亮: 各 icon 对应 sheet 打开时, 该 icon active
const isMobileTabActive = (key) => {
  if (key === 'subtitle' && showSubtitleSettings.value) return true
  if (key === 'playbackRate' && showPlaybackRateSheet.value) return true
  if (key === 'practice' && showPracticeSheet.value) return true
  if (key === 'playMode' && showPlayModeSheet.value) return true
  if (key === 'more' && showMoreSheet.value) return true
  return false
}

// Phase 1B Task 5: 移动端宽度检测（用于解读面板 Sheet side 切换）
const isMobileView = ref(false)
const updateIsMobile = () => {
  isMobileView.value = typeof window !== 'undefined' && window.matchMedia('(max-width: 768px)').matches
  // H5 端: 强制 learningMode 永远为 shadowing (听写模式 H5 砍掉)
  if (isMobileView.value && learningMode.value === 'dictation') {
    learningMode.value = 'shadowing'
  }
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
// Phase 2 (H5): 字幕设置 sheet 用的派生状态 — 从 localStorage 恢复, 刷新保持用户选择
const SUBTITLE_FONT_SIZE_KEY = 'sf_subtitle_font_size'
const VALID_FONT_SIZES = [14, 16, 18, 20]
const _savedFontSize = (() => {
  try {
    const v = parseInt(localStorage.getItem(SUBTITLE_FONT_SIZE_KEY) || '16', 10)
    return VALID_FONT_SIZES.includes(v) ? v : 16
  } catch { return 16 }
})()
const subtitleFontSize = ref(_savedFontSize)
watch(subtitleFontSize, (v) => {
  try { localStorage.setItem(SUBTITLE_FONT_SIZE_KEY, String(v)) } catch {}
})
const subtitleMode = computed(() => {
  if (showOnlyChinese.value) return 'cn-only'
  if (!showTranslation.value) return 'en-only'
  return 'bilingual'
})
// setSubtitleMode / setPlaybackRate 定义在下方 (L2033 / L812 附近)
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

// 标注总数（工具箱用）
const annotationCount = computed(() => {
  return Object.values(annotations.value).reduce((sum, arr) => sum + arr.length, 0)
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
    // 视频元数据未加载完时 duration = NaN, JSON.stringify(NaN) = "null" 会让后端 Pydantic 校验炸
    const dur = videoRef.value.duration
    if (!isFinite(dur) || dur <= 0) return
    const progress = Math.floor((videoRef.value.currentTime / dur) * 100)
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
    // 视频元数据未加载完时不要发,避免发送 0 进度噪音
    const dur = videoRef.value.duration
    if (!isFinite(dur) || dur <= 0) return
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

    // 3.8 处理 ?start_time=N query: 跳到指定时间, 定位字幕, 滚动高亮
    applyStartTimeQuery()
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
  }
}

// 3.8 时间戳跳转: 读 query.start_time, seek + 定位 + 滚动
const applyStartTimeQuery = () => {
  const startTime = Number(route.query.start_time)
  if (!Number.isFinite(startTime) || startTime < 0) return
  if (subtitles.value.length === 0) return

  // 找包含该时间点的字幕 (start_time <= t <= end_time)
  let idx = subtitles.value.findIndex(s =>
    s.start_time <= startTime && startTime <= s.end_time
  )
  // 没找到, 取最接近的下一条
  if (idx < 0) {
    idx = subtitles.value.findIndex(s => s.start_time > startTime)
    if (idx < 0) idx = subtitles.value.length - 1
  }

  currentIndex.value = idx
  // seekTo 调用 videoPlayerRef, 字幕已就绪
  nextTick(() => {
    seekTo(startTime)
    scrollToSubtitle(idx)
    // 高亮提示
    toast.info(`已跳到 ${formatDuration(startTime)}`)
  })
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
      // 不自动触发 LLM，只标记状态，等上传时的后台任务自己跑完
      interpretationGeneratingStatus.value = 'pending'
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
  // 先查状态：done 直接读数据库（秒开），不重复调 LLM
  try {
    const statusRes = await materialAPI.getInterpretationStatus(material.value.id)
    if (statusRes.status === 'done') {
      // 数据已有，直接加载
      interpretationGeneratingStatus.value = 'done'
      await loadInterpretation()
      return
    }
    if (statusRes.status === 'generating') {
      // 正在生成中，开始轮询
      isGenerating.value = true
      interpretationGeneratingStatus.value = 'generating'
      startPolling()
      return
    }
    // pending / failed：后台任务可能还没跑或失败了，不再让用户侧触发 LLM
    if (statusRes.status === 'pending') {
      toast.info('AI 解读正在准备中，请稍后刷新重试')
    } else if (statusRes.status === 'failed') {
      toast.error('AI 解读生成失败，请联系管理员重新上传')
    }
    interpretationGeneratingStatus.value = statusRes.status
  } catch (e) {
    console.error('加载解读失败', e)
    toast.error('加载解读失败')
  }
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
    // 尝试从 interpretation 中查找 (构造一个 minimal item 对象)
    handleInterpretationClick({ content_en: currentWord.value })
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
    // 只调一次 getList，从中提取 subtitle_id 集合（去掉冗余的 check 调用）
    const bookmarks = await subtitleBookmarkAPI.getList(material.value.id)
    const map = {}
    const idSet = new Set()
    bookmarks.forEach(b => {
      map[b.subtitle_id] = b
      idSet.add(b.subtitle_id)
    })
    bookmarkedSubtitleMap.value = map
    bookmarkedSubtitleIds.value = idSet
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
        // API 方法是 .remove 不是 .delete (旧代码 bug 修复)
        await subtitleBookmarkAPI.remove(target.id)
        bookmarkedSubtitleIds.value.delete(subId)
        toast.success('已取消收藏')
      }
    } catch (e) {
      console.error('取消收藏失败', e)
      toast.error('操作失败')
    }
  } else {
    try {
      await subtitleBookmarkAPI.add({ material_id: material.value.id, subtitle_id: subId, note: '' })
      bookmarkedSubtitleIds.value.add(subId)
      toast.success('已收藏')
    } catch (e) {
      console.error('收藏失败', e)
      toast.error('操作失败')
    }
  }
}

// Phase 2 (H5): 移动端"收藏"按钮 — 收藏当前字幕
const bookmarkCurrentSubtitle = () => {
  if (!userStore.isLoggedIn) {
    toast.warning('请先登录')
    router.push('/login')
    return
  }
  const sub = subtitles.value[currentIndex.value]
  if (!sub) {
    toast.warning('当前没有可收藏的字幕')
    return
  }
  toggleBookmark(sub)
}

// Phase 2 (H5): 倍速切换
const selectPlaybackRate = (rate) => {
  playbackRate.value = rate
  showPlaybackRateSheet.value = false
  toast.success(`已切换到 ${rate}x 倍速`)
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
// 5-P0 (1.1): 优先用 item.timestamp (后端已存), 找不到再 fallback 到 text 匹配
const handleInterpretationClick = (item) => {
  if (!item) return

  // 1. 播放发音
  const speakContent = item.content_en || item.example_sentence || item.context_sentence || ''
  if (speakContent) speakText(speakContent)

  // 2. 优先用 timestamp 字段 (后端 VideoInterpretation.timestamp, AI 生成时存)
  if (item.timestamp) {
    seekTo(item.timestamp)
    // 尝试找到对应的 subtitle, 高亮 + 翻页
    if (subtitles.value.length) {
      const foundSubtitle = subtitles.value.find(
        sub => Math.abs((sub.start_time || 0) - item.timestamp) < 1500  // 1.5s 误差
      )
      if (foundSubtitle) {
        const index = subtitles.value.findIndex(s => s.id === foundSubtitle.id)
        if (index !== -1) {
          currentIndex.value = index
          const targetPage = Math.ceil((index + 1) / subtitlePageSize)
          if (targetPage !== subtitleCurrentPage.value) {
            subtitleCurrentPage.value = targetPage
          }
        }
      }
    }
    return
  }

  // 3. Fallback: 在字幕中查找包含该词/短语的字幕 (老逻辑)
  if (!subtitles.value.length) return
  const searchText = (item.content_en || '').toLowerCase().trim()
  if (!searchText) return
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
  // 兼容两种 class: 实际是 .sf-subtitle-item__text, 老代码写 .sub-text (永远 null)
  const subtitleElement = event.target.closest('.sf-subtitle-item__text')
                              || event.target.closest('.sub-text')
                              || event.target.closest('.sf-subtitle-item')

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
  // Phase 2 (H5): 关闭字幕设置 sheet + toast 提示
  showSubtitleSettings.value = false
  toast.success(`字幕: ${mode === 'bilingual' ? '双语' : mode === 'en-only' ? '仅英文' : '仅中文'}`)
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
  // 长字幕(>40 条)分批翻译 5-10 分钟, 给用户一个持久提示避免重复点击
  const translatingToast = toast.info('翻译中,字幕较多请稍候…', { duration: 0 })
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
    toast.close(translatingToast)
    if (result && result.failed_batches && result.failed_batches.length > 0) {
      toast.warning(`部分翻译失败 (${result.translated_count}/${result.total}),失败批次 ${result.failed_batches.join(',')},稍后重试`)
    } else if (result && result.translated_count !== undefined) {
      toast.success(`翻译完成 ${result.translated_count}/${result.total}`)
    } else {
      toast.success('翻译完成')
    }
  } catch (e) {
    console.error('翻译失败', e)
    toast.close(translatingToast)
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

// Phase 11: 解读 sheet 打开时自动暂停视频 (关闭不自动恢复, 用户可手动)
watch(interpretationSheetOpen, (open) => {
  if (open && videoRef.value && !videoRef.value.paused) {
    videoRef.value.pause()
  }
})

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
  margin: 0 auto;
  padding: 0 20px 24px;
}

/* ==================== H5 极简 Header (对标) ==================== */
.sf-h5-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 50;
}
.sf-h5-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  flex-shrink: 0;
}
.sf-h5-back:active {
  background: var(--color-bg-elevated);
}
.sf-h5-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
}
.sf-btn--primary:hover {
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  filter: brightness(1.08);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}
.sf-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* ==================== 主内容区 ==================== */
.sf-main-content {
  display: grid;
  grid-template-columns: minmax(0, 2.6fr) minmax(0, 1fr) 200px;
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
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
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
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
  z-index: 100;
  transition: all var(--sf-duration-fast) var(--sf-ease-bounce);
  border: none;
  font-size: 14px;
  font-weight: 500;
}

.sf-interpretation-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(37, 99, 235, 0.4);
  filter: brightness(1.05);
}

/* 工具箱抽屉触发器 — 仅 < 1280px */
.sf-toolbox-trigger {
  position: fixed;
  bottom: 24px;
  right: 144px;
  width: 40px;
  height: 40px;
  border-radius: var(--sf-radius-full);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  display: none;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  z-index: 100;
  transition: all var(--sf-duration-fast) var(--sf-ease-bounce);
}
.sf-toolbox-trigger:hover {
  transform: translateY(-2px);
  color: var(--color-brand-bright);
  border-color: var(--color-brand-bright);
}
.sf-toolbox-trigger .sf-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--color-brand);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
@media (max-width: 1280px) {
  .sf-toolbox-trigger {
    display: flex;
  }
}
@media (max-width: 768px) {
  .sf-toolbox-trigger {
    bottom: 76px;
  }
}

/* 工具箱抽屉遮罩 */
.sf-toolbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 199;
  display: none;
}
@media (max-width: 1280px) {
  .sf-toolbox-overlay {
    display: block;
  }
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
/* Phase 10: Sheet 用 Teleport 渲染到 body, 不在 Learn.vue DOM 树内, scoped [data-v-hash] 不命中
   解: 把 z-index / H5 样式放非 scoped <style> 块 (文件末尾) */

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

/* ==================== Phase 2 (H5): 字幕设置 Sheet ==================== */
.sf-subtitle-settings-sheet :deep(.sheet-content) {
  max-height: 60vh;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
}
.sf-subtitle-settings {
  padding: 20px 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.sf-subtitle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.sf-subtitle-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
  flex-shrink: 0;
}
.sf-subtitle-options,
.sf-subtitle-size-row {
  display: flex;
  gap: 8px;
}
.sf-subtitle-opt {
  padding: 8px 16px;
  border-radius: 8px;
  background: var(--color-bg-elevated, #f5f5f5);
  color: var(--color-text-primary, #222);
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}
.sf-subtitle-opt.active {
  background: var(--color-brand, #10B981);
  color: #fff;
  border-color: var(--color-brand, #10B981);
}
.sf-subtitle-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}
.sf-subtitle-cancel {
  padding: 10px 20px;
  border-radius: 8px;
  background: var(--color-bg-elevated, #f5f5f5);
  color: var(--color-text-primary, #222);
  border: none;
  font-size: 14px;
  cursor: pointer;
}

/* ==================== Phase 2 (H5): 倍速选择 Sheet ==================== */
.sf-playback-rate-sheet :deep(.sheet-content) {
  max-height: 50vh;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
}
.sf-playback-rate-list {
  padding: 12px 16px 24px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.sf-rate-opt {
  position: relative;
  padding: 14px 8px;
  border-radius: 10px;
  background: var(--color-bg-elevated, #f5f5f5);
  color: var(--color-text-primary, #222);
  border: 1px solid transparent;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-tap-highlight-color: transparent;
}
.sf-rate-opt.active {
  background: var(--color-brand, #10B981);
  color: #fff;
  border-color: var(--color-brand, #10B981);
}
.sf-rate-check {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 10px;
  font-weight: 700;
}
.sf-rate-label {
  font-feature-settings: 'tnum';
}

/* ==================== 练习模式 Sheet (Phase 6 H5) ==================== */
.sf-practice-sheet :deep(.sheet-content) {
  max-width: 420px;
  margin: 0 auto;
  padding: 0 16px 24px;
  background: var(--color-bg-card);
}
.sf-practice-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}
.sf-practice-opt {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 16px 20px;
  background: var(--color-bg-base, #FAFAF7);
  border: 1.5px solid var(--color-border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.18s ease;
  -webkit-tap-highlight-color: transparent;
  text-align: left;
}
.sf-practice-opt:active {
  transform: scale(0.98);
}
.sf-practice-opt.active {
  background: var(--color-brand-subtle, #E8F0EB);
  border-color: var(--color-brand, #10B981);
}
.sf-practice-label {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.sf-practice-opt.active .sf-practice-label {
  color: var(--color-brand, #10B981);
}
.sf-practice-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}
.sf-practice-check {
  position: absolute;
  top: 16px;
  right: 16px;
  color: var(--color-brand, #10B981);
  font-size: 18px;
  font-weight: 700;
}

/* ==================== Phase 8 (H5): 播放模式 Sheet ==================== */
.sf-playmode-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}
.sf-playmode-opt {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 16px 20px;
  background: var(--color-bg-base, #FAFAF7);
  border: 1.5px solid var(--color-border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.18s ease;
  -webkit-tap-highlight-color: transparent;
  text-align: left;
}
.sf-playmode-opt:active { transform: scale(0.98); }
.sf-playmode-opt.active {
  background: var(--color-brand-subtle, #E8F0EB);
  border-color: var(--color-brand, #10B981);
}
.sf-playmode-label {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.sf-playmode-opt.active .sf-playmode-label {
  color: var(--color-brand, #10B981);
}
.sf-playmode-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}
.sf-playmode-check {
  position: absolute;
  top: 16px;
  right: 16px;
  color: var(--color-brand, #10B981);
  font-size: 18px;
  font-weight: 700;
}

/* ==================== Phase 8 (H5): 更多 Sheet ==================== */
.sf-more-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}
.sf-more-opt {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: var(--color-bg-base, #FAFAF7);
  border: 1.5px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.18s ease;
  -webkit-tap-highlight-color: transparent;
  text-align: left;
}
.sf-more-opt:active { transform: scale(0.98); }
.sf-more-opt.active {
  background: var(--color-brand-subtle, #E8F0EB);
  border-color: var(--color-brand, #10B981);
}
.sf-more-opt.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.sf-more-label {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-primary);
}
.sf-more-opt.active .sf-more-label {
  color: var(--color-brand, #10B981);
  font-weight: 600;
}
.sf-more-check {
  color: var(--color-brand, #10B981);
  font-size: 18px;
  font-weight: 700;
}

/* ==================== Phase 8 (H5): 次行 2-icon 紧凑样式 ==================== */
.sf-mobile-tab--compact {
  min-height: 36px;
  font-size: 10px;
  gap: 2px;
}
.sf-mobile-tab--compact .sf-mobile-tab-label {
  font-size: 10px;
}

/* ==================== 5-icon 工具栏 active 状态强化 (Phase 6 H5) ==================== */
.sf-mobile-tab.active {
  color: var(--color-brand, #10B981);
  background: var(--color-brand-subtle, #E8F0EB);
  font-weight: 600;
}
.sf-mobile-tab.active svg {
  stroke: var(--color-brand, #10B981);
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
/* 1024px 以下: 2 栏(隐藏右栏工具箱) */
@media (max-width: 1280px) {
  .sf-right-column {
    position: fixed;
    top: 64px;
    right: 0;
    bottom: 0;
    width: 280px;
    z-index: 200;
    background: var(--sf-bg-card);
    border-left: 1px solid var(--color-border);
    box-shadow: -8px 0 32px rgba(0, 0, 0, 0.08);
    transform: translateX(100%);
    transition: transform var(--sf-duration-slow) var(--sf-easing-standard);
    padding: 48px 16px 16px;
    overflow-y: auto;
    display: block !important;
  }
  .sf-right-column.drawer-open {
    transform: translateX(0);
  }
  .sf-drawer-close {
    display: flex;
  }
}

.sf-drawer-close {
  display: none;
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: var(--sf-radius-md);
  border: none;
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1;
  transition: all var(--sf-duration-fast);
}
.sf-drawer-close:hover {
  color: var(--color-text-primary);
  background: var(--color-border);
}
@media (max-width: 1280px) {
  .sf-main-content {
    grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
  }
}
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
    padding: 0;          /* H5 端视频通栏, 不要 12px 边距 */
    padding-bottom: calc(104px + env(safe-area-inset-bottom, 0px)); /* Phase 8: 给底 2 行 tab bar (40+64) 留空间 */
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

  /* ====== H5 (≤ 768px): 视频播放器固定不滚 (滑动字幕列表时) ====== */
  /* sticky 失效原因: .sf-left-column 高度 432 < viewport 844, sticky 触发条件不满足
     改 fixed + main-content padding-top 让出空间 */
  .sf-left-column .sf-card-inner:first-child {
    position: fixed;
    top: 50px;  /* h5 header 底 */
    left: 0;
    right: 0;
    max-height: 220px;
    z-index: 11;
    background: var(--color-bg-page);
    margin: 0;
    padding: 8px 12px;
    border-radius: 0;
  }
  .sf-left-column .sf-card-inner:first-child video {
    max-height: 200px;
    width: 100%;
    border-radius: var(--sf-radius-md);
    object-fit: contain;
  }
  /* 给 main-content 上移 240px 让出 fixed video 空间 */
  .sf-main-content {
    padding-top: 240px;
  }
  /* middle column 不要 sticky (之前是 desktop 配置, mobile 改成 normal flow) */
  .sf-middle-column {
    position: static !important;
    max-height: none !important;
    top: auto !important;
  }
  /* h5 header 高 z-index, 保证覆盖 fixed video */
  .sf-h5-header {
    z-index: 20;
  }

  /* H5 (≤ 768px): 隐藏 video 下面的桌面控件 (倍速按钮 + 循环开关) + 视频简介
     倍速已有 5-icon 工具栏的"倍速"sheet 接管, 简介在 H5 浪费空间
     用 :deep() 穿透子组件 LearnVideoPlayer scoped style */
  .sf-left-column :deep(.video-controls),
  .sf-left-column :deep(.video-info-card) {
    display: none !important;
  }

  /* ====== Phase 9 (H5): AI 智能解读 + 开始跟读 sticky 操作条 ======
     视频下方固定, 永远可见, 1-tap 入口
     高度 64px, top: 268 (= 50 header + 220 video 底), z-index 12 在 video 之上 */
  .sf-ai-action-bar {
    display: flex;
    position: fixed;
    top: 268px;
    left: 0;
    right: 0;
    height: 64px;
    z-index: 12;
    background: var(--color-bg-card);
    border-top: 1px solid var(--color-border);
    border-bottom: 1px solid var(--color-border);
    padding: 0 12px;
    gap: 10px;
    align-items: center;
  }
  .sf-ai-action-bar__btn {
    flex: 1;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border-radius: 12px;
    border: none;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    -webkit-tap-highlight-color: transparent;
  }
  .sf-ai-action-bar__btn:active {
    transform: scale(0.97);
  }
  .sf-ai-action-bar__btn:disabled {
    opacity: 0.7;
    cursor: wait;
  }
  .sf-ai-action-bar__btn--ai {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: #fff;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  }
  .sf-ai-action-bar__btn--ai.sf-ai-action-bar__btn--done {
    background: var(--color-brand-subtle, #E8F0EB);
    color: var(--color-brand, #10B981);
    box-shadow: none;
  }
  .sf-ai-action-bar__btn--shadow {
    background: var(--color-bg-elevated, #f8f8fa);
    color: var(--color-text-primary);
    border: 1.5px solid var(--color-border);
  }
  .sf-ai-action-bar__label {
    line-height: 1;
  }
  .sf-ai-action-bar__spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  /* main-content padding-top 给视频 + AI bar 让出空间: 240 + 64 + 8 = 312 */
  .sf-main-content {
    padding-top: 332px;
  }
}

/* ========== Phase 1B Task 2: 移动端底部 Tab Bar ========== */
.sf-mobile-tabs-wrap {
  display: none;
}
/* Phase 8: 桌面隐藏, H5 显示 2 行 (次行 2-icon + 主行 5-icon) */
.sf-mobile-tabs {
  display: flex;
}
@media (max-width: 768px) {
  .sf-mobile-tabs-wrap {
    display: flex;
    flex-direction: column;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--color-bg-card);
    border-top: 1px solid var(--color-border);
    z-index: 200;
    box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.08);
    padding-bottom: env(safe-area-inset-bottom, 0);
  }
  /* Phase 8: 次行 2-icon (循环+更多) — 紧凑, 浅色背景区分 */
  .sf-mobile-tabs--secondary {
    height: 40px;
    background: var(--color-bg-elevated, #f8f8fa);
    border-bottom: 1px solid var(--color-border);
  }
  .sf-mobile-tabs--primary {
    height: 64px;
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
    font-size: 11px;
    margin-top: 3px;
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

<!-- Phase 10: Sheet 用 Teleport 渲染到 body, 不在 Learn.vue DOM 树内, scoped [data-v-hash] 不命中
     放非 scoped <style> 块: 直接匹配 .sf-interpretation-sheet -->
<style>
.sf-interpretation-sheet {
  z-index: 250; /* 提到 toolbar (200) 之上, 避免被遮 */
}
.sf-interpretation-sheet [data-dismissable-layer] > button[class*="absolute"][class*="right-4"][class*="top-4"] {
  /* Phase 11: 隐藏 shadcn 默认的 16px X (opacity 0.7 看不见), Drawer 自带大 X */
  display: none !important;
}

@media (max-width: 768px) {
  .sf-interpretation-sheet {
    width: 100% !important;
    max-width: 100% !important;
    height: 90dvh !important;
    max-height: 90dvh !important;
    border-radius: 16px 16px 0 0 !important;
    /* z-index 250 继承, 在 toolbar 200 + AI bar 12 之上 */
  }
}
</style>
