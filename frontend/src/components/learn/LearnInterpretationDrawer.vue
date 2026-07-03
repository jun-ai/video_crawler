<template>
  <div class="sf-interp-panel">
    <!-- Phase 11 (H5): iOS 风格顶部 drag handle, 视觉提示可下滑关闭 -->
    <div class="sf-interp-drag-handle" aria-hidden="true">
      <span class="sf-interp-drag-handle__bar"></span>
    </div>

    <!-- 面板头部 -->
    <div class="sf-interp-panel__header">
      <h3 class="sf-interp-panel__title">视频解读</h3>
      <div class="sf-interp-panel__header-actions">
        <button
          v-if="hasData"
          class="sf-btn sf-btn--ghost sf-btn--sm"
          :disabled="isGenerating"
          @click="$emit('generate')"
        >
          <Loader2 class="is-loading" :size="16" v-if="isGenerating" /><RefreshCw v-else :size="16" />
          {{ isGenerating ? '生成中...' : '重新生成' }}
        </button>
        <!-- Phase 11: 显式大 X 关闭按钮, 替代 shadcn 默认看不见的 16px X -->
        <button
          class="sf-interp-panel__close"
          @click="$emit('close')"
          aria-label="关闭"
        >
          <X :size="18" />
        </button>
      </div>
    </div>

    <!-- Tab 导航: H5 横向滚动 + 桌面平铺 -->
    <div class="sf-tabs sf-tabs--scrollable">
      <button class="sf-tabs__item" :class="{ active: tab === 'words' }" @click="$emit('update:tab', 'words')">
        单词 <span class="sf-tabs__count">{{ data.words.length }}</span>
      </button>
      <button class="sf-tabs__item" :class="{ active: tab === 'phrases' }" @click="$emit('update:tab', 'phrases')">
        短语 <span class="sf-tabs__count">{{ data.phrases.length }}</span>
      </button>
      <button class="sf-tabs__item" :class="{ active: tab === 'grammar' }" @click="$emit('update:tab', 'grammar')">
        地道表达 <span class="sf-tabs__count">{{ data.grammar.length }}</span>
      </button>
      <button class="sf-tabs__item" :class="{ active: tab === 'idioms' }" @click="$emit('update:tab', 'idioms')">
        习语 <span class="sf-tabs__count">{{ data.idioms.length }}</span>
      </button>
    </div>

    <!-- 筛选栏 + 操作按钮 -->
    <div class="sf-filter-bar sf-filter-bar--scrollable" v-if="hasData">
      <button
        v-for="f in filterOptions"
        :key="f.value"
        :class="['sf-chip', { active: filter === f.value }]"
        @click="$emit('update:filter', f.value)"
      >
        {{ f.label }} <span class="sf-chip__count">{{ filterCounts[f.value] }}</span>
      </button>
      <div class="sf-spacer"></div>
      <button class="sf-btn sf-btn--ghost sf-btn--sm sf-btn--hide-on-mobile" @click="$emit('update:hideCn', !hideCn)">
        <Eye :size="14" />
        {{ hideCn ? '显示中文' : '隐藏中文' }}
      </button>
    </div>

    <!-- 内容区 -->
    <div class="sf-interp-panel__content">

      <!-- 加载中 -->
      <div v-if="loading" class="sf-interp-panel__state">
        <Loader2 class="is-loading sf-interp-panel__spinner" :size="28" />
        <span>加载中...</span>
      </div>

      <!-- 生成中状态 -->
      <div v-else-if="isGenerating" class="sf-interp-panel__generating">
        <div class="sf-generating-card">
          <Loader2 class="sf-generating-card__icon is-loading" :size="24" />
          <div class="sf-generating-card__info">
            <span class="sf-generating-card__title">正在分析视频内容</span>
            <div class="sf-generating-steps">
              <div
                v-for="(step, idx) in generatingSteps"
                :key="step.key"
                :class="['sf-generating-step', { active: isStepActive(step.key), done: isStepDone(step.key) }]"
              >
                <span class="sf-generating-step__dot"></span>
                <span>{{ step.label }}</span>
              </div>
            </div>
          </div>
        </div>
        <span class="sf-interp-panel__hint">后台生成中，你可以继续观看视频</span>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!hasData" class="sf-interp-panel__state">
        <div class="sf-empty-state">
          <MessageCircle class="sf-empty-state__icon" :size="40" />
          <template v-if="generatingStatus === 'failed'">
            <p class="sf-empty-state__text">解读生成失败</p>
            <button class="sf-btn sf-btn--primary sf-btn--sm" @click="$emit('generate')">重新生成</button>
          </template>
          <template v-else>
            <p class="sf-empty-state__text">暂无解读数据</p>
            <button class="sf-btn sf-btn--primary sf-btn--sm" @click="$emit('generate')">
              <Wand2 :size="14" /> 生成解读
            </button>
          </template>
        </div>
      </div>

      <!-- 卡片列表 -->
      <template v-else>
        <div v-if="filteredItems.length === 0" class="sf-interp-panel__state">
          <span class="sf-interp-panel__hint">{{ filter === 'all' ? '暂无数据' : '没有符合条件的项目' }}</span>
        </div>
        <div v-else class="sf-interp-list">
          <!-- 单词卡片 -->
          <template v-if="tab === 'words'">
            <div v-for="item in filteredItems" :key="item.id" :class="['sf-interp-card', getStatusClass(item.id)]">
              <div class="sf-interp-card__main" @click="toggleExpand(item.id)">
                <div :class="['sf-interp-card__status-bar', getStatusBarClass(item.id)]"></div>
                <div class="sf-interp-card__body">
                  <div class="sf-interp-card__row sf-interp-card__row--primary">
                    <div class="sf-interp-card__word" @click.stop="$emit('interpretation-click', item)">
                      <span class="sf-interp-card__word-text">{{ item.content_en }}</span>
                      <Headphones class="sf-interp-card__speak" :size="13" />
                    </div>
                    <span :class="['sf-badge', 'sf-badge--' + getStatusType(item.id)]">
                      {{ getStatusText(item.id) }}
                    </span>
                  </div>
                  <div class="sf-interp-card__row sf-interp-card__row--meta">
                    <span v-if="item.phonetic" class="sf-interp-card__phonetic">{{ item.phonetic }}</span>
                    <span v-if="item.part_of_speech" class="sf-interp-card__pos">{{ item.part_of_speech }}</span>
                    <span :class="['sf-difficulty-tag', 'sf-difficulty-tag--' + (item.difficulty || 1)]">
                      {{ getDifficultyLabel(item.difficulty) }}
                    </span>
                    <span v-if="item.frequency_rank" class="sf-interp-card__freq">Top {{ item.frequency_rank }}</span>
                  </div>
                  <div v-if="!hideCn && item.content_cn" class="sf-interp-card__row sf-interp-card__row--cn">
                    <span class="sf-interp-card__cn">{{ item.content_cn }}</span>
                  </div>
                  <div v-if="!hideCn && item.english_definition" class="sf-interp-card__row">
                    <span class="sf-interp-card__en-def">{{ item.english_definition }}</span>
                  </div>
                </div>
                <div class="sf-interp-card__chevron">
                  <ChevronDown :size="16" :class="{ rotated: isExpanded(item.id) }" />
                </div>
              </div>

              <div v-if="isExpanded(item.id)" class="sf-interp-card__details">
                <div v-if="item.other_pos_definitions" class="sf-detail-item">
                  <div class="sf-detail-item__label">其他词性</div>
                  <div class="sf-detail-item__text">{{ item.other_pos_definitions }}</div>
                </div>
                <div v-if="item.example_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('interpretation-click', item)">
                  <div class="sf-detail-item__label">例句</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.example_sentence }}</div>
                </div>
                <div v-if="item.context_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('seek-subtitle', item)">
                  <div class="sf-detail-item__label">字幕出处</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.context_sentence }}</div>
                  <div v-if="!hideCn && item.context_translation" class="sf-detail-item__sub">{{ item.context_translation }}</div>
                </div>
                <div class="sf-detail-item sf-detail-item--actions">
                  <button class="sf-btn sf-btn--primary sf-btn--sm" @click.stop="$emit('add-vocabulary', item)">
                    <Plus :size="14" /> 加入生词本
                  </button>
                  <div class="sf-status-toggle">
                    <button
                      :class="['sf-status-btn', { active: getStatus(item.id) === 'known' }]"
                      @click.stop="$emit('set-status', item.id, 'known')"
                    >认识</button>
                    <button
                      :class="['sf-status-btn', 'sf-status-btn--danger', { active: getStatus(item.id) === 'unknown' }]"
                      @click.stop="$emit('set-status', item.id, 'unknown')"
                    >不认识</button>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 短语卡片 -->
          <template v-if="tab === 'phrases'">
            <div v-for="item in filteredItems" :key="item.id" :class="['sf-interp-card', getStatusClass(item.id)]">
              <div class="sf-interp-card__main" @click="toggleExpand(item.id)">
                <div :class="['sf-interp-card__status-bar', getStatusBarClass(item.id)]"></div>
                <div class="sf-interp-card__body">
                  <div class="sf-interp-card__row sf-interp-card__row--primary">
                    <div class="sf-interp-card__word" @click.stop="$emit('interpretation-click', item)">
                      <span class="sf-interp-card__word-text">{{ item.content_en }}</span>
                      <Headphones class="sf-interp-card__speak" :size="13" />
                    </div>
                    <span :class="['sf-badge', 'sf-badge--' + getStatusType(item.id)]">
                      {{ getStatusText(item.id) }}
                    </span>
                  </div>
                  <div class="sf-interp-card__row sf-interp-card__row--meta">
                    <span v-if="item.phonetic" class="sf-interp-card__phonetic">{{ item.phonetic }}</span>
                    <span :class="['sf-difficulty-tag', 'sf-difficulty-tag--' + (item.difficulty || 1)]">
                      {{ getDifficultyLabel(item.difficulty) }}
                    </span>
                    <span v-if="item.frequency_rank" class="sf-interp-card__freq">Top {{ item.frequency_rank }}</span>
                  </div>
                  <div v-if="!hideCn && item.content_cn" class="sf-interp-card__row sf-interp-card__row--cn">
                    <span class="sf-interp-card__cn">{{ item.content_cn }}</span>
                  </div>
                  <div v-if="!hideCn && item.english_definition" class="sf-interp-card__row">
                    <span class="sf-interp-card__en-def">{{ item.english_definition }}</span>
                  </div>
                </div>
                <div class="sf-interp-card__chevron">
                  <ChevronDown :size="16" :class="{ rotated: isExpanded(item.id) }" />
                </div>
              </div>

              <div v-if="isExpanded(item.id)" class="sf-interp-card__details">
                <div v-if="item.synonyms" class="sf-detail-item">
                  <div class="sf-detail-item__label">近义词</div>
                  <div class="sf-synonym-tags">
                    <span v-for="s in (item.synonyms || '').split(',')" :key="s" class="sf-tag">{{ s.trim() }}</span>
                  </div>
                </div>
                <div v-if="item.example_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('interpretation-click', item)">
                  <div class="sf-detail-item__label">例句</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.example_sentence }}</div>
                </div>
                <div v-if="item.context_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('seek-subtitle', item)">
                  <div class="sf-detail-item__label">字幕出处</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.context_sentence }}</div>
                  <div v-if="!hideCn && item.context_translation" class="sf-detail-item__sub">{{ item.context_translation }}</div>
                </div>
                <div class="sf-detail-item sf-detail-item--actions">
                  <button class="sf-btn sf-btn--primary sf-btn--sm" @click.stop="$emit('add-vocabulary', item)">
                    <Plus :size="14" /> 加入生词本
                  </button>
                  <div class="sf-status-toggle">
                    <button :class="['sf-status-btn', { active: getStatus(item.id) === 'known' }]" @click.stop="$emit('set-status', item.id, 'known')">认识</button>
                    <button :class="['sf-status-btn', 'sf-status-btn--danger', { active: getStatus(item.id) === 'unknown' }]" @click.stop="$emit('set-status', item.id, 'unknown')">不认识</button>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 地道表达卡片 -->
          <template v-if="tab === 'grammar'">
            <div v-for="item in filteredItems" :key="item.id" :class="['sf-interp-card', getStatusClass(item.id)]">
              <div class="sf-interp-card__main" @click="toggleExpand(item.id)">
                <div :class="['sf-interp-card__status-bar', getStatusBarClass(item.id)]"></div>
                <div class="sf-interp-card__body">
                  <div class="sf-interp-card__row sf-interp-card__row--primary">
                    <div class="sf-interp-card__word" @click.stop="$emit('interpretation-click', item)">
                      <span class="sf-interp-card__word-text">{{ item.content_en }}</span>
                      <Headphones class="sf-interp-card__speak" :size="13" />
                    </div>
                    <span :class="['sf-badge', 'sf-badge--' + getStatusType(item.id)]">
                      {{ getStatusText(item.id) }}
                    </span>
                  </div>
                  <div class="sf-interp-card__row sf-interp-card__row--meta">
                    <span v-if="item.phonetic" class="sf-interp-card__phonetic">{{ item.phonetic }}</span>
                    <span :class="['sf-difficulty-tag', 'sf-difficulty-tag--' + (item.difficulty || 1)]">
                      {{ getDifficultyLabel(item.difficulty) }}
                    </span>
                  </div>
                  <div v-if="!hideCn && item.content_cn" class="sf-interp-card__row sf-interp-card__row--cn">
                    <span class="sf-interp-card__cn">{{ item.content_cn }}</span>
                  </div>
                </div>
                <div class="sf-interp-card__chevron">
                  <ChevronDown :size="16" :class="{ rotated: isExpanded(item.id) }" />
                </div>
              </div>

              <div v-if="isExpanded(item.id)" class="sf-interp-card__details">
                <div v-if="item.context_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('interpretation-click', item)">
                  <div class="sf-detail-item__label">字幕原文</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.context_sentence }}</div>
                </div>
                <div v-if="!hideCn && item.context_translation" class="sf-detail-item">
                  <div class="sf-detail-item__label">中文翻译</div>
                  <div class="sf-detail-item__text">{{ item.context_translation }}</div>
                </div>
                <div v-if="item.explanation || item.structure_analysis || item.similar_expressions || item.usage_scenario || item.alternative_phrasings" class="sf-detail-item">
                  <div class="sf-detail-item__label">表达分析</div>
                  <div v-if="item.explanation" class="sf-detail-item__text">{{ item.explanation }}</div>
                  <div v-if="item.structure_analysis" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">结构：</span>{{ item.structure_analysis }}
                  </div>
                  <div v-if="item.similar_expressions" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">举一反三：</span>{{ item.similar_expressions }}
                  </div>
                  <div v-if="item.usage_scenario" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">场景：</span>{{ item.usage_scenario }}
                  </div>
                  <div v-if="item.alternative_phrasings" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">相似表达：</span>{{ item.alternative_phrasings }}
                  </div>
                </div>
                <div v-if="item.example_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('interpretation-click', item)">
                  <div class="sf-detail-item__label">例句</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.example_sentence }}</div>
                </div>
                <div class="sf-detail-item sf-detail-item--actions">
                  <button class="sf-btn sf-btn--primary sf-btn--sm" @click.stop="$emit('add-vocabulary', item)">
                    <Plus :size="14" /> 加入生词本
                  </button>
                  <div class="sf-status-toggle">
                    <button :class="['sf-status-btn', { active: getStatus(item.id) === 'known' }]" @click.stop="$emit('set-status', item.id, 'known')">认识</button>
                    <button :class="['sf-status-btn', 'sf-status-btn--danger', { active: getStatus(item.id) === 'unknown' }]" @click.stop="$emit('set-status', item.id, 'unknown')">不认识</button>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 习语卡片 -->
          <template v-if="tab === 'idioms'">
            <div v-for="item in filteredItems" :key="item.id" :class="['sf-interp-card', getStatusClass(item.id)]">
              <div class="sf-interp-card__main" @click="toggleExpand(item.id)">
                <div :class="['sf-interp-card__status-bar', getStatusBarClass(item.id)]"></div>
                <div class="sf-interp-card__body">
                  <div class="sf-interp-card__row sf-interp-card__row--primary">
                    <div class="sf-interp-card__word" @click.stop="$emit('interpretation-click', item)">
                      <span class="sf-interp-card__word-text">{{ item.content_en }}</span>
                      <Headphones class="sf-interp-card__speak" :size="13" />
                    </div>
                    <span :class="['sf-badge', 'sf-badge--' + getStatusType(item.id)]">
                      {{ getStatusText(item.id) }}
                    </span>
                  </div>
                  <div class="sf-interp-card__row sf-interp-card__row--meta">
                    <span v-if="item.phonetic" class="sf-interp-card__phonetic">{{ item.phonetic }}</span>
                    <span :class="['sf-difficulty-tag', 'sf-difficulty-tag--' + (item.difficulty || 1)]">
                      {{ getDifficultyLabel(item.difficulty) }}
                    </span>
                  </div>
                  <div v-if="!hideCn && item.content_cn" class="sf-interp-card__row sf-interp-card__row--cn">
                    <span class="sf-interp-card__cn">{{ item.content_cn }}</span>
                  </div>
                </div>
                <div class="sf-interp-card__chevron">
                  <ChevronDown :size="16" :class="{ rotated: isExpanded(item.id) }" />
                </div>
              </div>

              <div v-if="isExpanded(item.id)" class="sf-interp-card__details">
                <div v-if="item.explanation" class="sf-detail-item">
                  <div class="sf-detail-item__label">含义</div>
                  <div class="sf-detail-item__text">{{ item.explanation }}</div>
                </div>
                <div v-if="!hideCn && item.cultural_background" class="sf-detail-item">
                  <div class="sf-detail-item__label">文化背景</div>
                  <div class="sf-detail-item__text">{{ item.cultural_background }}</div>
                </div>
                <div v-if="item.context_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('interpretation-click', item)">
                  <div class="sf-detail-item__label">字幕原文</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.context_sentence }}</div>
                </div>
                <div v-if="!hideCn && item.context_translation" class="sf-detail-item">
                  <div class="sf-detail-item__label">中文翻译</div>
                  <div class="sf-detail-item__text">{{ item.context_translation }}</div>
                </div>
                <div v-if="item.structure_analysis || item.similar_expressions || item.usage_scenario || item.alternative_phrasings" class="sf-detail-item">
                  <div class="sf-detail-item__label">表达分析</div>
                  <div v-if="item.structure_analysis" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">结构：</span>{{ item.structure_analysis }}
                  </div>
                  <div v-if="item.similar_expressions" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">举一反三：</span>{{ item.similar_expressions }}
                  </div>
                  <div v-if="item.usage_scenario" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">场景：</span>{{ item.usage_scenario }}
                  </div>
                  <div v-if="item.alternative_phrasings" class="sf-detail-item__text">
                    <span class="sf-detail-item__tag">相似表达：</span>{{ item.alternative_phrasings }}
                  </div>
                </div>
                <div v-if="item.example_sentence" class="sf-detail-item sf-detail-item--clickable" @click="$emit('interpretation-click', item)">
                  <div class="sf-detail-item__label">例句</div>
                  <div class="sf-detail-item__text sf-detail-item__text--clickable">{{ item.example_sentence }}</div>
                </div>
                <div class="sf-detail-item sf-detail-item--actions">
                  <button class="sf-btn sf-btn--primary sf-btn--sm" @click.stop="$emit('add-vocabulary', item)">
                    <Plus :size="14" /> 加入生词本
                  </button>
                  <div class="sf-status-toggle">
                    <button :class="['sf-status-btn', { active: getStatus(item.id) === 'known' }]" @click.stop="$emit('set-status', item.id, 'known')">认识</button>
                    <button :class="['sf-status-btn', 'sf-status-btn--danger', { active: getStatus(item.id) === 'unknown' }]" @click.stop="$emit('set-status', item.id, 'unknown')">不认识</button>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  Loader2, ArrowRight, RefreshCw, Headphones,
  Eye, MessageCircle, Wand2, Plus, ChevronDown, X
} from 'lucide-vue-next'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({ words: [], phrases: [], grammar: [], idioms: [] })
  },
  tab: { type: String, default: 'words' },
  filter: { type: String, default: 'all' },
  hideCn: Boolean,
  learningStatus: { type: Object, default: () => ({}) },
  loading: Boolean,
  isGenerating: Boolean,
  generatingStatus: { type: String, default: '' }
})

const emit = defineEmits([
  'generate', 'update:tab', 'update:filter',
  'update:hideCn', 'set-status', 'interpretation-click',
  'seek-subtitle', 'add-vocabulary', 'close'
])

// 展开状态
const expandedItems = ref(new Set())

const toggleExpand = (itemId) => {
  const newSet = new Set(expandedItems.value)
  if (newSet.has(itemId)) {
    newSet.delete(itemId)
  } else {
    newSet.add(itemId)
  }
  expandedItems.value = newSet
}
const isExpanded = (itemId) => expandedItems.value.has(itemId)

// 计算属性
const hasData = computed(() =>
  props.data.words.length > 0 || props.data.phrases.length > 0 ||
  props.data.grammar.length > 0 || props.data.idioms.length > 0
)

const filterCounts = computed(() => {
  const items = props.data[props.tab] || []
  const counts = { all: items.length, unmarked: 0, known: 0, unknown: 0 }
  items.forEach(item => {
    const status = props.learningStatus[item.id]
    if (!status) counts.unmarked++
    else if (status === 'known') counts.known++
    else if (status === 'unknown') counts.unknown++
  })
  return counts
})

const filterOptions = [
  { value: 'all', label: '全部' },
  { value: 'unmarked', label: '未标记' },
  { value: 'known', label: '认识' },
  { value: 'unknown', label: '不认识' }
]

const filteredItems = computed(() => {
  const items = props.data[props.tab] || []
  if (props.filter === 'all') return items
  return items.filter(item => {
    if (props.filter === 'unmarked') return !props.learningStatus[item.id]
    return (props.learningStatus[item.id] || 'unmarked') === props.filter
  })
})

// 生成步骤（用于状态显示）
const generatingSteps = [
  { key: 'words', label: '分析单词' },
  { key: 'phrases', label: '提取短语' },
  { key: 'grammar', label: '地道表达' },
  { key: 'idioms', label: '习语分析' }
]

const stepOrder = ['words', 'phrases', 'grammar', 'idioms']
const isStepActive = (stepKey) => {
  if (props.generatingStatus === 'done') return false
  const currentIdx = stepOrder.indexOf(props.tab)
  const stepIdx = stepOrder.indexOf(stepKey)
  return stepIdx === currentIdx
}
const isStepDone = (stepKey) => {
  if (props.generatingStatus === 'done') return true
  const currentIdx = stepOrder.indexOf(props.tab)
  const stepIdx = stepOrder.indexOf(stepKey)
  return stepIdx < currentIdx
}

// 辅助函数
const getDifficultyLabel = (level) => {
  const labels = { 1: 'A1', 2: 'A2', 3: 'B1', 4: 'B2', 5: 'C1' }
  return labels[level] || 'A1'
}

const getStatus = (id) => props.learningStatus[id] || null
const getStatusText = (id) => {
  const s = props.learningStatus[id]
  if (s === 'known') return '认识'
  if (s === 'unknown') return '不认识'
  return '未标记'
}
const getStatusType = (id) => {
  const s = props.learningStatus[id]
  if (s === 'known') return 'success'
  if (s === 'unknown') return 'danger'
  return 'muted'
}
const getStatusClass = (id) => {
  const s = props.learningStatus[id]
  if (s === 'known') return 'sf-interp-card--known'
  if (s === 'unknown') return 'sf-interp-card--unknown'
  return ''
}
const getStatusBarClass = (id) => {
  const s = props.learningStatus[id]
  if (s === 'known') return 'sf-interp-card__status-bar--known'
  if (s === 'unknown') return 'sf-interp-card__status-bar--danger'
  return ''
}
</script>

<style scoped>
/* ==================== 面板整体 ==================== */
.sf-interp-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg-card);
  overflow: hidden;
}

/* 面板头部 */
.sf-interp-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 14px 18px 12px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-card);
  flex-shrink: 0;
}

/* Phase 11: header 右侧 action 容器 (重新生成 + 大 X) */
.sf-interp-panel__header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Phase 11: 显式大 X 关闭按钮, 替代 shadcn 默认看不见的 16px X */
.sf-interp-panel__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
  flex-shrink: 0;
}
.sf-interp-panel__close:hover {
  background: var(--color-bg-base);
  color: var(--color-text-primary);
}
.sf-interp-panel__close:active {
  transform: scale(0.92);
}

/* Phase 11: iOS 风格顶部 drag handle, 视觉提示可下滑关闭 */
.sf-interp-drag-handle {
  display: none; /* 默认桌面隐藏 */
  justify-content: center;
  padding: 8px 0 4px;
  flex-shrink: 0;
}
.sf-interp-drag-handle__bar {
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background: var(--color-border);
  opacity: 0.6;
}
@media (max-width: 768px) {
  .sf-interp-drag-handle { display: flex; }
  .sf-interp-panel__header { padding: 4px 18px 10px; } /* drag handle 已占空间, 头部少一截 */
  /* Phase 11: H5 隐藏 "隐藏中文" 按钮 (H5 用 更多 sheet 切字幕模式) */
  .sf-btn--hide-on-mobile { display: none; }
}
.sf-interp-panel__title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.2px;
}

/* ==================== Tab 导航 ==================== */
.sf-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  overflow-x: auto;
  scrollbar-width: none;
  flex-shrink: 0;
  background: var(--color-bg-elevated);
  /* Phase 11: 平滑横向滚动 + scroll-snap */
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x proximity;
}
.sf-tabs::-webkit-scrollbar { display: none; }

.sf-tabs__item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 14px;
  flex-shrink: 0; /* Phase 11: 不缩小, 触发横向滚动 */
  scroll-snap-align: start;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  border: none;
  background: transparent;
  position: relative;
  transition: color var(--sf-duration-fast);
  white-space: nowrap;
  flex-shrink: 0;
  font-family: inherit;
}
.sf-tabs__item:hover { color: var(--color-text-primary); }
.sf-tabs__item.active {
  color: var(--color-brand);
  font-weight: 600;
}
.sf-tabs__item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-brand);
  border-radius: 2px 2px 0 0;
}
.sf-tabs__count {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: var(--sf-radius-full);
  background: rgba(37, 99, 235, 0.1);
  color: var(--color-brand);
  font-weight: 500;
}
.sf-tabs__item:not(.active) .sf-tabs__count {
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
}

/* ==================== 筛选栏 ==================== */
.sf-filter-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-base);
  flex-wrap: wrap;
  flex-shrink: 0;
}
/* Phase 11: H5 改横向滚动, 不换行, 隐藏中文按钮用 hide-on-mobile 隐藏 */
.sf-filter-bar--scrollable {
  flex-wrap: nowrap;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  padding-right: 14px;
}
.sf-filter-bar--scrollable::-webkit-scrollbar { display: none; }
.sf-filter-bar--scrollable .sf-chip { flex-shrink: 0; }

.sf-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  border: 1px solid transparent;
  border-radius: var(--sf-radius-full);
  cursor: pointer;
  transition: all var(--sf-duration-fast) var(--sf-ease-bounce);
  font-family: inherit;
  line-height: 1.4;
}
.sf-chip:hover {
  border-color: var(--sf-border-strong);
  color: var(--color-text-primary);
}
.sf-chip.active {
  background: var(--color-brand);
  color: #fff;
  box-shadow: var(--sf-shadow-xs);
}
.sf-chip__count {
  font-size: 10px;
  opacity: 0.75;
}
.sf-spacer { flex: 1; }

/* ==================== 内容区 ==================== */
.sf-interp-panel__content {
  flex: 1;
  overflow-y: auto;
}

.sf-interp-panel__content::-webkit-scrollbar {
  width: 5px;
}
.sf-interp-panel__content::-webkit-scrollbar-track {
  background: transparent;
}
.sf-interp-panel__content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}
.dark .sf-interp-panel__content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
}

/* 状态占位 */
.sf-interp-panel__state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 20px;
  color: var(--color-text-muted);
  font-size: 13px;
  text-align: center;
}
.sf-interp-panel__spinner {
  font-size: 28px;
  color: var(--color-brand);
}
.sf-interp-panel__hint {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* 生成中 */
.sf-interp-panel__generating {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px 20px;
}
.sf-generating-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-lg);
  width: 100%;
}
.sf-generating-card__icon {
  font-size: 24px;
  color: var(--color-brand);
  flex-shrink: 0;
  margin-top: 2px;
}
.sf-generating-card__info { flex: 1; }
.sf-generating-card__title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 10px;
}
.sf-generating-steps {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.sf-generating-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-muted);
}
.sf-generating-step.active { color: var(--color-brand); font-weight: 500; }
.sf-generating-step.done { color: var(--color-brand); }
.sf-generating-step__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-text-muted);
  flex-shrink: 0;
}
.sf-generating-step.active .sf-generating-step__dot { background: var(--color-brand); }
.sf-generating-step.done .sf-generating-step__dot { background: var(--color-brand); }

/* 空状态 */
.sf-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.sf-empty-state__icon {
  font-size: 40px;
  color: var(--sf-border-strong);
}
.sf-empty-state__text {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-muted);
}

/* 卡片列表 */
.sf-interp-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}

/* ==================== 解读卡片 ==================== */
.sf-interp-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-lg);
  overflow: hidden;
  transition: box-shadow var(--sf-duration-fast) var(--sf-ease-standard),
              border-color var(--sf-duration-fast),
              transform var(--sf-duration-fast) var(--sf-ease-bounce);
}
.sf-interp-card:hover {
  box-shadow: var(--sf-shadow-md);
  border-color: var(--color-brand);
  transform: translateY(-1px);
}
.sf-interp-card--known {
  border-left: 3px solid var(--color-success);
}
.sf-interp-card--unknown {
  border-left: 3px solid var(--color-danger);
}

/* 卡片主体（可点击） */
.sf-interp-card__main {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 13px 13px 13px 0;
  cursor: pointer;
  user-select: none;
}
.sf-interp-card__main:hover .sf-interp-card__speak {
  opacity: 1;
}

/* 状态颜色条 */
.sf-interp-card__status-bar {
  width: 3px;
  align-self: stretch;
  background: transparent;
  border-radius: 3px 0 0 3px;
  flex-shrink: 0;
}
.sf-interp-card__status-bar--known { background: var(--color-success); }
.sf-interp-card__status-bar--danger { background: var(--color-danger); }

/* 卡片内容 */
.sf-interp-card__body { flex: 1; min-width: 0; }

.sf-interp-card__row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}
.sf-interp-card__row:last-child { margin-bottom: 0; }
.sf-interp-card__row--primary { margin-bottom: 6px; }
.sf-interp-card__row--meta { margin-bottom: 3px; }

/* 词汇 + 发音按钮 */
.sf-interp-card__word {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 2px 5px;
  margin: -2px -5px;
  border-radius: var(--sf-radius-sm);
  transition: background var(--sf-duration-fast);
}
.sf-interp-card__word:hover { background: var(--sf-brand-subtle); }
.sf-interp-card__word-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.3px;
  line-height: 1.3;
}
.sf-interp-card__speak {
  font-size: 13px;
  color: var(--color-brand);
  opacity: 0;
  transition: opacity var(--sf-duration-fast);
}

/* 状态徽章 */
.sf-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 9px;
  font-size: 10px;
  font-weight: 600;
  border-radius: var(--sf-radius-full);
  letter-spacing: 0.2px;
  cursor: pointer;
  transition: all var(--sf-duration-fast);
  flex-shrink: 0;
}
.sf-badge--success {
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-success);
}
.sf-badge--danger {
  background: rgba(239, 68, 68, 0.12);
  color: #dc2626;
}
.sf-badge--muted {
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
}
.sf-badge:hover { filter: brightness(0.92); }

/* 元数据 */
.sf-interp-card__phonetic {
  font-size: 12px;
  color: var(--color-text-muted);
  font-style: italic;
  font-family: var(--sf-font-mono);
}
.sf-interp-card__pos {
  font-size: 10px;
  padding: 2px 7px;
  border-radius: var(--sf-radius-full);
  background: rgba(37, 99, 235, 0.1);
  color: #2563EB;
  font-weight: 600;
}
.sf-difficulty-tag {
  font-size: 10px;
  padding: 2px 7px;
  border-radius: var(--sf-radius-full);
  font-weight: 600;
}
.sf-difficulty-tag--1 { background: var(--sf-difficulty-1-bg); color: var(--sf-difficulty-1-text); }
.sf-difficulty-tag--2 { background: var(--sf-difficulty-2-bg); color: var(--sf-difficulty-2-text); }
.sf-difficulty-tag--3 { background: var(--sf-difficulty-3-bg); color: var(--sf-difficulty-3-text); }
.sf-difficulty-tag--4 { background: var(--sf-difficulty-4-bg); color: var(--sf-difficulty-4-text); }
.sf-difficulty-tag--5 { background: var(--sf-difficulty-5-bg); color: var(--sf-difficulty-5-text); }
.sf-interp-card__freq {
  font-size: 10px;
  color: var(--color-text-muted);
  font-weight: 500;
}
.sf-interp-card__cn {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.sf-interp-card__en-def {
  font-size: 11px;
  color: var(--color-text-muted);
  font-style: italic;
  line-height: 1.4;
}

/* 展开图标 */
.sf-interp-card__chevron {
  padding: 4px;
  color: var(--color-text-muted);
  flex-shrink: 0;
  margin-top: 2px;
}
.sf-interp-card__chevron svg {
  transition: transform var(--sf-duration-normal) var(--sf-ease-standard);
  display: block;
}
.sf-interp-card__chevron .rotated { transform: rotate(180deg); }

/* ==================== 展开详情 ==================== */
.sf-interp-card__details {
  padding: 12px 14px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  animation: sf-fade-in var(--sf-duration-normal) var(--sf-ease-standard);
}

@keyframes sf-fade-in {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.sf-detail-item {
  margin-bottom: 12px;
}
.sf-detail-item:last-child { margin-bottom: 0; }
.sf-detail-item__label {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 5px;
}
.sf-detail-item__text {
  font-size: 13px;
  color: var(--color-text-primary);
  line-height: 1.6;
}
.sf-detail-item__text--clickable {
  cursor: pointer;
  padding: 7px 10px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-sm);
  transition: all var(--sf-duration-fast);
}
.sf-detail-item__text--clickable:hover {
  border-color: var(--color-brand);
  color: var(--color-brand);
}
.sf-detail-item__sub {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-top: 3px;
  padding-left: 10px;
}
.sf-detail-item__tag {
  font-weight: 600;
  color: var(--color-brand);
  font-size: 12px;
}

/* 近义词标签 */
.sf-synonym-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.sf-tag {
  font-size: 11px;
  padding: 3px 10px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-full);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--sf-duration-fast);
}
.sf-tag:hover {
  border-color: var(--color-brand);
  color: var(--color-brand);
}

/* 操作区 */
.sf-detail-item--actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
  margin-top: 4px;
}

/* 状态切换按钮 */
.sf-status-toggle {
  display: flex;
  gap: 6px;
}
.sf-status-btn {
  font-size: 11px;
  padding: 4px 12px;
  border-radius: var(--sf-radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--sf-duration-fast);
  font-weight: 500;
  font-family: inherit;
}
.sf-status-btn:hover {
  border-color: var(--color-text-secondary);
  color: var(--color-text-secondary);
}
.sf-status-btn.active {
  background: var(--color-brand);
  border-color: var(--color-brand);
  color: #fff;
}
.sf-status-btn--danger.active {
  background: var(--color-danger);
  border-color: var(--color-danger);
  color: #fff;
}
</style>
