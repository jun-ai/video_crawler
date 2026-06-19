<template>
  <div :class="['video-card', { 'list-mode': layout === 'list' }]" @click="handleClick">
    <!-- 缩略图 16:9 -->
    <div class="thumbnail">
      <img :src="cover" :alt="title" @error="handleImageError" />

      <!-- 收藏红心 -->
      <div
        class="fav-heart"
        @click.stop="emit('toggle-favorite', id)"
      >
        <svg
          viewBox="0 0 24 24"
          width="18"
          height="18"
          :fill="favorited ? 'var(--color-danger)' : 'none'"
          :stroke="favorited ? 'none' : '#fff'"
          stroke-width="2"
        >
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
        </svg>
      </div>

      <!-- 时长标签 -->
      <div class="duration" v-if="duration">{{ formatDuration(duration) }}</div>

      <!-- 已完成徽章 -->
      <div class="completed-badge" v-if="completed">
        <CheckCircle2 :size="12" />
        <span>已完成</span>
      </div>

      <!-- 进度条 overlay on cover -->
      <div class="progress-bar" v-if="progress > 0 && !completed">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>

      <!-- 难度色块 -->
      <div class="difficulty-badge" v-if="difficulty">
        {{ difficultyLabel }}
      </div>

      <!-- 播放图标 -->
      <div class="play-overlay" v-if="showPlayIcon">
        <PlayCircle :size="48" />
      </div>
    </div>

    <!-- 视频信息 -->
    <div class="video-info">
      <h3 class="video-title">{{ title }}</h3>
      <p class="video-description" v-if="description">{{ description }}</p>
      <!-- 标签 Chips -->
      <div class="tag-chips-row" v-if="tags.length > 0">
        <span
          v-for="tag in tags.slice(0, 3)"
          :key="tag.id"
          class="tag-chip-small"
          :style="{ '--chip-color': tag.color || 'var(--color-brand)' }"
        >{{ tag.name }}</span>
      </div>
      <!-- meta -->
      <div class="video-meta" v-if="showMeta">
        <span class="meta-item" v-if="viewCount">{{ formatViewCount(viewCount) }} 次观看</span>
      </div>
      <div class="progress-text" v-if="progressText">{{ progressText }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CheckCircle2, PlayCircle } from 'lucide-vue-next'

const props = defineProps({
  id: { type: [Number, String], required: true },
  title: { type: String, default: '' },
  cover: { type: String, default: '' },
  duration: { type: Number, default: 0 },
  progress: { type: Number, default: 0 },
  difficulty: { type: Number, default: 0 },
  viewCount: { type: Number, default: 0 },
  category: { type: String, default: '' },
  showAvatar: { type: Boolean, default: true },
  showMeta: { type: Boolean, default: true },
  layout: { type: String, default: 'grid' },
  showPlayIcon: { type: Boolean, default: false },
  completed: { type: Boolean, default: false },
  progressText: { type: String, default: '' },
  description: { type: String, default: '' },
  favorited: { type: Boolean, default: false },
  tags: { type: Array, default: () => [] }
})

const emit = defineEmits(['click', 'toggle-favorite'])

// 墨绿系难度色
const difficultyColors = {
  1: '#93C5FD', // 入门 - brand-light
  2: '#8BBFA5', // 基础
  3: '#5DA882', // 中级
  4: '#16A34A', // 进阶
  5: '#2563EB'  // 高级 - brand
}

const difficultyLabel = computed(() => {
  const labels = ['', '入门', '基础', '中级', '进阶', '高级']
  return labels[props.difficulty] || ''
})

const formatDuration = (seconds) => {
  if (!seconds) return ''
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatViewCount = (count) => {
  if (count >= 10000) return `${(count / 10000).toFixed(1)}w`
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k`
  return count
}

const handleImageError = (e) => {
  e.target.style.display = 'none'
  e.target.parentElement.style.background = 'linear-gradient(135deg, var(--color-bg-elevated) 0%, var(--color-brand) 100%)'
}

const handleClick = () => {
  emit('click', props.id)
}
</script>

<style scoped>
.video-card {
  cursor: pointer;
  background: var(--color-bg-card);
  border-radius: 16px;
  overflow: hidden;
  transition: transform var(--sf-duration-slow) cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow var(--sf-duration-slow) ease, border-color var(--sf-duration-slow) ease;
  border: 1.5px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  position: relative;
}

.video-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, var(--color-brand) 0%, var(--color-accent) 100%);
  opacity: 0;
  transition: opacity var(--sf-duration-slow) ease;
  border-radius: 3px 0 0 3px;
  z-index: 4;
}

.video-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(37, 99, 235, 0.15), 0 4px 12px rgba(0, 0, 0, 0.06);
  border-color: var(--color-brand);
}

.video-card:hover::before {
  opacity: 1;
}

/* ====== 缩略图 ====== */
.thumbnail {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  background: var(--color-bg-elevated);
  overflow: hidden;
}

.thumbnail::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0);
  transition: background var(--sf-duration-slow) ease;
  pointer-events: none;
  z-index: 1;
}

.video-card:hover .thumbnail::after {
  background: rgba(0, 0, 0, 0.08);
}

.thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--sf-duration-slower) cubic-bezier(0.34, 1.56, 0.64, 1);
}

.video-card:hover .thumbnail img {
  transform: scale(1.05);
}

/* 播放图标遮罩 */
.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  opacity: 0;
  transition: opacity var(--sf-duration-normal);
  z-index: 2;
  color: white;
}

.video-card:hover .play-overlay {
  opacity: 1;
}

/* 时长标签 */
.duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.78);
  color: #fff;
  padding: 3px 7px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  z-index: 3;
}

/* 收藏红心 */
.fav-heart {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 3;
  width: 30px;
  height: 30px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background var(--sf-duration-fast), transform var(--sf-duration-normal) cubic-bezier(0.34, 1.56, 0.64, 1);
  color: white;
}

.fav-heart:hover {
  background: rgba(0, 0, 0, 0.6);
  transform: scale(1.15);
}

/* 已完成徽章 */
.completed-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: var(--color-success);
  color: #fff;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 3px;
  line-height: 1;
  z-index: 3;
}

/* 难度色块 */
.difficulty-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  line-height: 1;
  z-index: 3;
  letter-spacing: 0.3px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--color-brand);
  backdrop-filter: blur(4px);
}

/* 进度条 */
.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(0, 0, 0, 0.12);
  z-index: 3;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand) 0%, var(--color-accent) 100%);
  transition: width var(--sf-duration-slow) ease;
}

/* ====== 视频信息 ====== */
.video-info {
  padding: 14px 14px 16px;
}

.video-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.35;
  margin: 0 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-description {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.meta-item {
  font-size: 12px;
  color: var(--color-text-muted);
}

.progress-text {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-top: 6px;
}

/* 标签 Chips */
.tag-chips-row {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.tag-chip-small {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 500;
  background: color-mix(in srgb, var(--chip-color) 8%, transparent);
  color: var(--chip-color);
  border: 1px solid color-mix(in srgb, var(--chip-color) 15%, transparent);
  line-height: 1.4;
}

/* ====== 列表模式 ====== */
.video-card.list-mode {
  display: flex;
  border-radius: 12px;
}

.video-card.list-mode .thumbnail {
  width: 160px;
  min-width: 160px;
  padding-bottom: 0;
  height: 90px;
  border-radius: 12px 0 0 12px;
}

.video-card.list-mode .video-info {
  flex: 1;
  padding: 10px 14px;
}

.video-card.list-mode .video-title {
  font-size: 15px;
  -webkit-line-clamp: 1;
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .video-card:hover {
    transform: translateY(-1px);
  }

  .video-title {
    font-size: 15px;
  }

  .video-info {
    padding: 10px 12px 12px;
  }

  .video-card.list-mode .thumbnail {
    width: 120px;
    min-width: 120px;
    height: 68px;
  }
}

@media (max-width: 480px) {
  .video-title {
    font-size: 14px;
  }

  .video-info {
    padding: 8px 10px 10px;
  }

  .video-card.list-mode .thumbnail {
    width: 100px;
    min-width: 100px;
    height: 56px;
  }
}
</style>
