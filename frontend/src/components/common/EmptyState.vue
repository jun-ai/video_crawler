<template>
  <div class="empty-state" :class="[typeClass]">
    <div class="empty-illustration">
      <!-- 根据场景类型显示不同图标/插图 -->
      <div v-if="type === 'no-materials'" class="illustration-icon">
        <svg viewBox="0 0 120 90" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="10" y="10" width="42" height="30" rx="4" fill="var(--color-bg-elevated)" stroke="var(--color-border)" stroke-width="1.5"/>
          <polygon points="25,18 25,32 37,25" fill="var(--color-text-muted)"/>
          <rect x="58" y="10" width="42" height="30" rx="4" fill="var(--color-bg-elevated)" stroke="var(--color-border)" stroke-width="1.5"/>
          <polygon points="73,18 73,32 85,25" fill="var(--color-text-muted)"/>
          <rect x="34" y="48" width="42" height="30" rx="4" fill="var(--color-bg-elevated)" stroke="var(--color-border)" stroke-width="1.5"/>
          <polygon points="49,56 49,70 61,63" fill="var(--color-text-muted)"/>
        </svg>
      </div>
      <div v-else-if="type === 'no-vocabulary'" class="illustration-icon">
        <svg viewBox="0 0 100 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="15" y="5" width="55" height="70" rx="6" fill="var(--color-bg-elevated)" stroke="var(--color-border)" stroke-width="1.5"/>
          <line x1="25" y1="22" x2="60" y2="22" stroke="var(--color-text-muted)" stroke-width="2" stroke-linecap="round"/>
          <line x1="25" y1="34" x2="55" y2="34" stroke="var(--color-border)" stroke-width="2" stroke-linecap="round"/>
          <line x1="25" y1="46" x2="58" y2="46" stroke="var(--color-border)" stroke-width="2" stroke-linecap="round"/>
          <line x1="25" y1="58" x2="48" y2="58" stroke="var(--color-border)" stroke-width="2" stroke-linecap="round"/>
          <circle cx="70" cy="55" r="18" fill="var(--color-brand)" fill-opacity="0.1" stroke="var(--color-brand)" stroke-width="1.5"/>
          <text x="70" y="61" text-anchor="middle" fill="var(--color-brand)" font-size="18" font-weight="bold">+</text>
        </svg>
      </div>
      <div v-else-if="type === 'no-favorites'" class="illustration-icon">
        <svg viewBox="0 0 100 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M50 70 L15 38 C8 30 8 18 18 12 C28 6 40 10 50 22 C60 10 72 6 82 12 C92 18 92 30 85 38 Z" fill="var(--color-bg-elevated)" stroke="var(--color-text-muted)" stroke-width="1.5" stroke-dasharray="4 2"/>
        </svg>
      </div>
      <div v-else-if="type === 'all-completed'" class="illustration-icon">
        <svg viewBox="0 0 100 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="50" cy="40" r="30" fill="var(--color-brand)" fill-opacity="0.1" stroke="var(--color-brand)" stroke-width="1.5"/>
          <path d="M36 40 L46 50 L66 30" stroke="var(--color-brand)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div v-else-if="type === 'welcome'" class="illustration-icon">
        <svg viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="60" cy="32" r="24" fill="var(--color-brand)" fill-opacity="0.1" stroke="var(--color-brand)" stroke-width="1.5"/>
          <circle cx="52" cy="28" r="3" fill="var(--color-brand)"/>
          <circle cx="68" cy="28" r="3" fill="var(--color-brand)"/>
          <path d="M48 36 Q60 48 72 36" stroke="var(--color-brand)" stroke-width="2" fill="none" stroke-linecap="round"/>
          <path d="M30 55 L36 48 L42 55" stroke="var(--color-brand)" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <path d="M78 55 L84 48 L90 55" stroke="var(--color-brand)" stroke-width="1.5" fill="none" stroke-linecap="round"/>
          <circle cx="20" cy="20" r="3" fill="var(--color-brand)" fill-opacity="0.3"/>
          <circle cx="100" cy="15" r="2" fill="var(--color-brand)" fill-opacity="0.3"/>
          <circle cx="105" cy="60" r="4" fill="var(--color-brand)" fill-opacity="0.2"/>
          <circle cx="15" cy="55" r="2.5" fill="var(--color-brand)" fill-opacity="0.2"/>
        </svg>
      </div>
      <div v-else-if="type === 'no-results'" class="illustration-icon">
        <svg viewBox="0 0 100 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="42" cy="35" r="20" fill="var(--color-bg-elevated)" stroke="var(--color-text-muted)" stroke-width="1.5"/>
          <line x1="56" y1="49" x2="75" y2="68" stroke="var(--color-text-muted)" stroke-width="3" stroke-linecap="round"/>
          <line x1="35" y1="28" x2="49" y2="42" stroke="var(--color-text-muted)" stroke-width="2" stroke-linecap="round"/>
          <line x1="49" y1="28" x2="35" y2="42" stroke="var(--color-text-muted)" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <!-- 默认图标 -->
      <div v-else class="empty-icon-default">
        <svg viewBox="0 0 64 41" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="32" cy="20.5" rx="32" ry="20.5" fill="currentColor" fill-opacity="0.25"/>
          <path d="M22 18h20v2H22v-2zm0 6h14v2H22v-2z" fill="currentColor" fill-opacity="0.5"/>
        </svg>
      </div>
    </div>

    <div class="empty-content">
      <h3 class="empty-title">{{ displayTitle }}</h3>
      <p class="empty-description" v-if="displayDescription">{{ displayDescription }}</p>
    </div>

    <div class="empty-actions" v-if="$slots.actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  // 场景类型：控制预设的图标和文案
  type: {
    type: String,
    default: 'default' // default | no-materials | no-vocabulary | no-favorites | all-completed | welcome | no-results
  }
})

const typeClass = computed(() => `empty-type-${props.type}`)

// 预设文案
const presetTexts = {
  'default': { title: '暂无数据', description: '' },
  'no-materials': { title: '暂无语料', description: '还没有学习材料，请稍后再来查看' },
  'no-vocabulary': { title: '生词本是空的', description: '在学习视频时，遇到不认识的单词可以添加到这里' },
  'no-favorites': { title: '还没有收藏', description: '浏览语料库时，点击收藏按钮可以保存感兴趣的内容' },
  'all-completed': { title: '全部完成！', description: '太棒了！你已经学完了所有内容，继续保持吧' },
  'welcome': { title: '开始你的学习之旅', description: '浏览语料库，选择感兴趣的视频开始学习吧' },
  'no-results': { title: '没有找到结果', description: '换个关键词或筛选条件试试' }
}

const displayTitle = computed(() => {
  return props.title || presetTexts[props.type]?.title || '暂无数据'
})

const displayDescription = computed(() => {
  return props.description || presetTexts[props.type]?.description || ''
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 56px 16px;
  text-align: center;
}

.empty-illustration {
  margin-bottom: 20px;
  color: var(--color-text-muted);
}

.illustration-icon {
  width: 140px;
  height: 100px;
  opacity: 0.7;
  transition: opacity var(--sf-duration-slow);
}

.illustration-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state:hover .illustration-icon {
  opacity: 0.9;
}

.empty-icon-default {
  width: 120px;
  height: 80px;
}

.empty-icon-default svg {
  width: 100%;
  height: 100%;
}

.empty-content {
  max-width: 320px;
}

.empty-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 6px;
}

.empty-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

.empty-actions {
  margin-top: 24px;
  display: flex;
  gap: 8px;
}

/* 不同场景的细微色调差异 */
.empty-type-all-completed .empty-title {
  color: var(--color-brand);
}

.empty-type-welcome .illustration-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* 响应式 */
@media (max-width: 768px) {
  .empty-state {
    padding: 36px 8px;
  }

  .illustration-icon {
    width: 100px;
    height: 72px;
  }

  .empty-title {
    font-size: 15px;
  }

  .empty-description {
    font-size: 13px;
  }
}
</style>
