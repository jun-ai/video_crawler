<template>
  <SfDialog
    :model-value="visible"
    :title="word"
    width="360px"
    class="word-dialog"
    :modal-append-to-body="true"
    destroy-on-close
    @update:model-value="$emit('update:visible', $event)"
  >
    <div class="word-popup-content" v-if="visible">
      <!-- Loading -->
      <div v-if="loading" class="word-loading">
        <Loader2 class="is-loading" :size="16" />
        <span>正在查询单词...</span>
      </div>
      <!-- Word info -->
      <div v-else class="word-info">
        <div class="word-pronunciation">
          <span class="phonetic" v-if="wordInfo.phonetic">/{{ wordInfo.phonetic }}/</span>
          <SfButton type="primary" size="sm" round @click="$emit('speak', word)" title="播放发音">
            <Headphones :size="14" />
          </SfButton>
        </div>
        <div class="word-translation" v-if="wordInfo.translation">
          <div class="translation-label">释义</div>
          <div class="translation-content">{{ wordInfo.translation }}</div>
        </div>
        <div class="word-example" v-if="wordInfo.example">
          <div class="example-label">例句</div>
          <div class="example-content" @click="$emit('speak', wordInfo.example)">
            {{ wordInfo.example }}
            <Headphones class="speak-icon-small" :size="12" />
          </div>
        </div>
        <div class="word-actions">
          <SfButton type="success" @click="$emit('add-vocabulary')" :loading="addingWord">
            <BookOpen :size="14" /> 加入生词本
          </SfButton>
          <SfButton
            v-if="wordInfo.context_sentence || wordInfo.first_appearance_time"
            size="sm"
            @click="$emit('seek-video')"
            title="跳转到视频中出现位置"
          >
            <Play :size="14" />
            跳转到视频
          </SfButton>
        </div>
      </div>
    </div>
  </SfDialog>
</template>

<script setup>
import SfDialog from '@/components/ui/SfDialog.vue'
import SfButton from '@/components/ui/SfButton.vue'
import { Loader2, Headphones, BookOpen, Play } from 'lucide-vue-next'

defineProps({
  visible: Boolean,
  word: { type: String, default: '' },
  loading: Boolean,
  wordInfo: { type: Object, default: () => ({ phonetic: '', translation: '', example: '' }) },
  addingWord: Boolean
})

defineEmits(['update:visible', 'speak', 'add-vocabulary', 'seek-video'])
</script>
