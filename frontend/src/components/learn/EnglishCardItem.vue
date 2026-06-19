<template>
  <div
    :class="[
      'ec-vocab-card',
      type === 'grammar' && 'ec-grammar-card',
      {
        'ec-card-selected': selected,
        'ec-card-known': status === 'known',
        'ec-card-unknown': status === 'unknown'
      }
    ]"
    @click="selected ? $emit('toggle-select', null) : $emit('toggle-select', item.id)"
  >
    <!-- 卡片头部: 词/短语/表达 + 音标 + POS + 喇叭 -->
    <div class="ec-card-header">
      <div class="ec-card-word-row">
        <span class="ec-card-word" @click.stop="$emit('speak', item.content_en)">{{ item.content_en }}</span>
        <span v-if="type === 'word' && item.phonetic" class="ec-card-phonetic" @click.stop="$emit('speak', item.content_en)">{{ item.phonetic }}</span>
        <span class="ec-card-pos">{{ posLabel }}</span>
        <button class="ec-speak-btn" @click.stop="$emit('speak', item.content_en)" title="播放发音" :aria-label="`播放 ${item.content_en} 的发音`">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
        </button>
      </div>

      <!-- 评分按钮 (右对齐) -->
      <div class="ec-card-actions" v-if="type !== 'grammar' || true">
        <SfTooltip content="认识" placement="top">
          <button
            class="ec-circle-btn ec-btn-known"
            :class="{ active: status === 'known' }"
            :aria-label="`标记 ${item.content_en} 为认识`"
            :aria-pressed="status === 'known'"
            @click.stop="$emit('set-status', { id: item.id, status: 'known' })"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
          </button>
        </SfTooltip>
        <SfTooltip content="不认识" placement="top">
          <button
            class="ec-circle-btn ec-btn-unknown"
            :class="{ active: status === 'unknown' }"
            :aria-label="`标记 ${item.content_en} 为不认识`"
            :aria-pressed="status === 'unknown'"
            @click.stop="$emit('set-status', { id: item.id, status: 'unknown' })"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
        </SfTooltip>
      </div>
    </div>

    <!-- 释义区 (word/phrase 显示) -->
    <div class="ec-card-meanings" v-if="type !== 'grammar'">
      <div class="ec-card-cn" v-if="!hideChinese && item.content_cn">{{ item.content_cn }}</div>
      <div class="ec-card-en-def" v-if="item.english_definition">{{ item.english_definition }}</div>
    </div>

    <!-- 例句 (word/phrase 始终显示) -->
    <div class="ec-card-example" v-if="type !== 'grammar' && item.example_sentence">
      <div class="ec-example-label">例句</div>
      <div
        class="ec-example-text"
        :class="{ 'cursor-pointer': type === 'phrase' }"
        @click.stop="type === 'phrase' && $emit('speak', item.example_sentence)"
      >{{ item.example_sentence }}</div>
    </div>

    <!-- Grammar: 字幕原句 + 翻译 (默认显示, 详细分析折叠) -->
    <template v-if="type === 'grammar'">
      <div class="ec-card-meanings" v-if="item.context_sentence">
        <div class="ec-expand-label">字幕原句</div>
        <div class="ec-expand-text">{{ item.context_sentence }}</div>
      </div>
      <div class="ec-card-meanings" v-if="!hideChinese && item.context_translation">
        <div class="ec-expand-label">中文翻译</div>
        <div class="ec-expand-text">{{ item.context_translation }}</div>
      </div>

      <!-- 折叠按钮: 2.10 grammar 默认折叠 -->
      <button
        v-if="hasAnalysis"
        class="ec-grammar-toggle"
        :aria-expanded="grammarExpanded"
        :aria-label="grammarExpanded ? '收起表达分析' : '展开表达分析'"
        @click.stop="$emit('toggle-grammar', item.id)"
      >
        <Lightbulb :size="14" />
        <span>{{ grammarExpanded ? '收起分析' : '看分析' }}</span>
        <svg :class="['ec-chevron', { rotated: grammarExpanded }]" viewBox="0 0 24 24" width="12" height="12" fill="currentColor">
          <path d="M7 10l5 5 5-5z" />
        </svg>
      </button>

      <transition name="ec-expand">
        <div class="ec-card-meanings ec-analysis-area" v-if="grammarExpanded && hasAnalysis">
          <div class="ec-analysis-item" v-if="item.explanation">{{ item.explanation }}</div>
          <div class="ec-analysis-item" v-if="item.structure_analysis">
            <span class="ec-analysis-label">结构解析：</span>{{ item.structure_analysis }}
          </div>
          <div class="ec-analysis-item" v-if="parseList(item.similar_expressions).length > 0">
            <span class="ec-analysis-label">举一反三：</span>
            <div class="ec-expand-tags">
              <span class="ec-expand-tag" v-for="(expr, idx) in parseList(item.similar_expressions)" :key="idx">{{ expr }}</span>
            </div>
          </div>
          <div class="ec-analysis-item" v-if="item.usage_scenario">
            <span class="ec-analysis-label">使用场景：</span>{{ item.usage_scenario }}
          </div>
          <div class="ec-analysis-item" v-if="parseList(item.alternative_phrasings).length > 0">
            <span class="ec-analysis-label">相似表达：</span>
            <div class="ec-expand-tags">
              <span class="ec-expand-tag" v-for="(phrase, idx) in parseList(item.alternative_phrasings)" :key="idx">{{ phrase }}</span>
            </div>
          </div>
        </div>
      </transition>

      <!-- 例句 (grammar 总是显示, 折叠不影响) -->
      <div class="ec-card-example" v-if="item.example_sentence">
        <div class="ec-example-label">例句</div>
        <div class="ec-example-text">{{ item.example_sentence }}</div>
      </div>

      <!-- 点读跳转 -->
      <div class="ec-jump-row">
        <button class="ec-jump-btn" @click.stop="$emit('jump-learn', item)">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          点读跳转
        </button>
      </div>
    </template>

    <!-- word/phrase 展开区 (selected 控制) -->
    <transition name="ec-expand" v-if="type !== 'grammar'">
      <div class="ec-card-expand" v-if="selected">
        <!-- 通用: 语境 + 译文 -->
        <div class="ec-expand-section" v-if="item.context_sentence">
          <div class="ec-expand-label">语境</div>
          <div class="ec-expand-text">{{ item.context_sentence }}</div>
        </div>
        <div class="ec-expand-section" v-if="!hideChinese && item.context_translation">
          <div class="ec-expand-label">译文</div>
          <div class="ec-expand-text">{{ item.context_translation }}</div>
        </div>
        <!-- word 特有: 其他释义 -->
        <div class="ec-expand-section" v-if="type === 'word' && parseList(item.other_pos_definitions).length > 0">
          <div class="ec-expand-label">其他释义</div>
          <div class="ec-expand-text" v-for="(def, idx) in parseList(item.other_pos_definitions)" :key="idx">{{ def }}</div>
        </div>
        <!-- phrase 特有: 近义词 -->
        <div class="ec-expand-section" v-if="type === 'phrase' && parseList(item.synonyms).length > 0">
          <div class="ec-expand-label">近义词</div>
          <div class="ec-expand-tags">
            <span class="ec-expand-tag" v-for="(syn, idx) in parseList(item.synonyms)" :key="idx">{{ syn }}</span>
          </div>
        </div>
      </div>
    </transition>

    <!-- 展开指示器 (word/phrase 才有) -->
    <div class="ec-card-expand-indicator" v-if="type !== 'grammar' && hasExpandContent">
      <ArrowRight :size="14" :class="{ rotated: selected }" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowRight, Lightbulb } from 'lucide-vue-next'
import SfTooltip from '@/components/ui/SfTooltip.vue'

const props = defineProps({
  item: { type: Object, required: true },
  type: { type: String, required: true, validator: v => ['word', 'phrase', 'grammar'].includes(v) },
  status: { type: String, default: '' },  // 'known' / 'unknown' / ''
  selected: { type: Boolean, default: false },
  hideChinese: { type: Boolean, default: false },
  grammarExpanded: { type: Boolean, default: false },
})

defineEmits([
  'toggle-select',     // (id or null) 父组件管理 selectedCardId
  'set-status',        // ({ id, status }) 父组件管理 learningStatus
  'speak',             // (text) 调 TTS
  'toggle-grammar',    // (id) 父组件管理 expandedGrammarIds
  'jump-learn',        // (item) 跳到学习页
])

// POS 标签: word 取 part_of_speech, phrase='短语', grammar='表达'
const posLabel = computed(() => {
  if (props.type === 'phrase') return '短语'
  if (props.type === 'grammar') return '表达'
  return props.item.part_of_speech || ''
})

// grammar 是否有分析内容 (决定是否显示折叠按钮)
const hasAnalysis = computed(() => {
  const i = props.item
  return i.explanation || i.structure_analysis
    || parseList(i.similar_expressions).length > 0
    || i.usage_scenario
    || parseList(i.alternative_phrasings).length > 0
})

// word/phrase 是否有可展开内容 (决定是否显示展开箭头)
const hasExpandContent = computed(() => {
  const i = props.item
  if (i.context_sentence) return true
  if (!props.hideChinese && i.context_translation) return true
  if (props.type === 'word' && parseList(i.other_pos_definitions).length > 0) return true
  if (props.type === 'phrase' && parseList(i.synonyms).length > 0) return true
  return false
})

// 解析 JSON 数组字段 (后端存的是 JSON string)
const parseList = (val) => {
  if (!val) return []
  if (Array.isArray(val)) return val
  try {
    const parsed = JSON.parse(val)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}
</script>
