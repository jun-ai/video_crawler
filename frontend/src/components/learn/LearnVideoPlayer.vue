<template>
  <div class="video-section">
    <div class="video-player-wrapper">
      <video
        ref="playerRef"
        :src="material?.video_path"
        key="video-player"
        class="video-player"
        controls
        @timeupdate="$emit('timeupdate')"
        @loadedmetadata="$emit('loadedmetadata')"
        @seeked="$emit('seeked')"
        @ended="$emit('ended')"
        @play="onPlay"
        @pause="onPause"
      ></video>

      <!-- 视频封面图（未播放时显示） -->
      <div
        v-if="cover && !playing && material?.video_path"
        class="video-cover"
        @click="startPlayback"
      >
        <img :src="cover" :alt="material?.title || '视频封面'" class="cover-image" />
        <div class="cover-overlay">
          <div class="cover-play-btn">
            <svg viewBox="0 0 24 24" width="36" height="36" fill="white">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
          <span class="cover-title" v-if="material?.title">{{ material.title }}</span>
        </div>
      </div>
    </div>

    <!-- 视频控制栏 -->
    <div class="video-controls">
      <div class="speed-control">
        <div class="speed-selector">
          <button
            v-for="rate in [0.5, 0.75, 1, 1.25, 1.5]"
            :key="rate"
            :class="['speed-selector__btn', { active: playbackRate === rate }]"
            @click="$emit('update:playbackRate', rate)"
          >{{ rate }}x</button>
        </div>
      </div>
      <div class="loop-control">
        <SfSwitch :model-value="loopCurrent" size="small" active-text="循环当前句" @update:model-value="$emit('update:loopCurrent', $event)" />
      </div>
    </div>

    <!-- 视频简介 -->
    <div class="video-info-card" v-if="material">
      <div class="video-info-desc" v-if="material.description">
        {{ material.description }}
      </div>
      <div class="start-learning-hint" v-if="!currentSubtitle">
        <Play class="hint-icon" :size="16" />
        <span>播放视频开始学习 · 按空格键暂停/播放</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SfSwitch from '@/components/ui/SfSwitch.vue'
import { Play } from 'lucide-vue-next'

const props = defineProps({
  material: { type: Object, default: null },
  playbackRate: { type: Number, default: 1 },
  loopCurrent: { type: Boolean, default: false },
  currentSubtitle: { type: Object, default: null }
})

const emit = defineEmits([
  'timeupdate', 'loadedmetadata', 'seeked', 'ended', 'play', 'pause',
  'update:playbackRate', 'update:loopCurrent'
])

const playerRef = ref(null)
const playing = ref(false)

const onPlay = () => {
  playing.value = true
  emit('play')
}

const onPause = () => {
  playing.value = false
  emit('pause')
}

const startPlayback = () => {
  if (playerRef.value) {
    playerRef.value.play()
  }
}

const togglePlay = () => {
  if (!playerRef.value) return
  if (playerRef.value.paused) {
    playerRef.value.play()
  } else {
    playerRef.value.pause()
  }
}

const seekRelative = (deltaSec) => {
  if (!playerRef.value) return
  const cur = playerRef.value.currentTime || 0
  playerRef.value.currentTime = Math.max(0, cur + deltaSec)
}

defineExpose({ playerRef, playing, togglePlay, seekRelative })
</script>

<style scoped>
.video-section {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.video-player-wrapper {
  position: relative;
  border-radius: var(--sf-radius-lg);
  overflow: hidden;
  background: #000;
  box-shadow: var(--sf-shadow-md);
}

.video-player {
  width: 100%;
  aspect-ratio: 16 / 9;
  display: block;
  border-radius: var(--sf-radius-lg);
  object-fit: contain;
  background: #000;
}

/* 视频封面图 */
.video-cover {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  cursor: pointer;
  border-radius: var(--sf-radius-lg);
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  transition: background var(--sf-duration-normal);
}

.video-cover:hover .cover-overlay {
  background: rgba(0, 0, 0, 0.5);
}

.video-cover:hover .cover-play-btn {
  transform: scale(1.08);
}

.cover-play-btn {
  width: 80px;
  height: 80px;
  background: rgba(37, 99, 235, 0.92);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--sf-duration-fast) var(--sf-ease-bounce),
              background var(--sf-duration-fast);
  box-shadow: var(--sf-shadow-lg);
}

.cover-play-btn svg {
  width: 40px;
  height: 40px;
  margin-left: 4px;
}

.cover-title {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  max-width: 80%;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 视频控制栏 */
.video-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-top: none;
  border-radius: 0 0 var(--sf-radius-lg) var(--sf-radius-lg);
}

/* 倍速按钮组 */
.speed-selector {
  display: flex;
  gap: 2px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--sf-radius-full);
  padding: 2px;
}

.speed-selector__btn {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: var(--sf-radius-full);
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--sf-duration-fast);
  font-family: inherit;
  white-space: nowrap;
}

.speed-selector__btn:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
}

.speed-selector__btn.active {
  background: var(--sf-cta-gradient, linear-gradient(#60A5FA 0%, #3B82F6 100%));
  color: #fff;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

/* 保留 el-select 样式兼容 */
.speed-control .el-select {
  --el-select-input-focus-border-color: var(--color-brand) !important;
}

.loop-control :deep(.el-switch__label) {
  color: var(--sf-text-secondary) !important;
}

.loop-control :deep(.el-switch__label.is-active) {
  color: var(--color-brand) !important;
}

/* 视频信息卡片 */
.video-info-card {
  background: var(--color-bg-card);
  border-radius: var(--sf-radius-lg);
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  box-shadow: var(--sf-shadow-sm);
  margin-top: 12px;
}

.video-info-desc {
  font-size: 13px;
  color: var(--sf-text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.start-learning-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 10px;
  margin-top: 8px;
  background: var(--sf-brand-subtle);
  border-radius: var(--sf-radius-md);
  border: 1px solid rgba(37, 99, 235, 0.2);
  text-align: center;
}

.start-learning-hint .hint-icon {
  font-size: 16px;
  color: var(--color-brand-bright);
}

.start-learning-hint span {
  font-size: 12px;
  color: var(--color-text-primary);
  font-weight: 500;
}
</style>
