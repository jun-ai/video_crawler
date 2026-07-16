<template>
  <div class="practice-page">
    <!-- Phase 6 (H5): 极简 header + 返回按钮 -->
    <header v-if="isMobileView" class="sf-h5-header">
      <button class="sf-h5-back" type="button" @click="$router.back()" aria-label="返回学习页面">
        <ArrowLeft :size="22" />
      </button>
      <h1 class="sf-h5-title">练习 · {{ materialTitle || '加载中' }}</h1>
    </header>
    <!-- 桌面端 header -->
    <div v-else class="page-header">
      <SfButton type="ghost" size="sm" @click="$router.back()" aria-label="返回学习页面">
        <ArrowLeft :size="20" />
      </SfButton>
      <h1 class="page-title">练习 · {{ materialTitle || '加载中' }}</h1>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <Loader2 :size="32" class="is-loading" />
      <span>加载练习材料...</span>
    </div>

    <!-- 未传 material_id (从 4-tab 直接点练习) -->
    <div v-else-if="!materialId" class="empty-state">
      <PartyPopper :size="48" class="empty-emoji-icon" />
      <h2>选择视频开始练习</h2>
      <p>从学习列表选一个视频，跟读模仿训练口语</p>
      <SfButton type="primary" @click="$router.push('/learn')">去学习列表</SfButton>
    </div>

    <!-- 3 种练习模式选择 -->
    <div v-else class="practice-modes">
      <p class="practice-intro">选择一种练习模式开始</p>
      <div class="mode-card" @click="startPractice('shadowing')">
        <div class="mode-icon">
          <Mic :size="28" />
        </div>
        <div class="mode-info">
          <h3>跟读</h3>
          <p>看字幕跟读模仿，智能评分发音</p>
        </div>
        <ChevronRight :size="20" class="mode-arrow" />
      </div>
      <div class="mode-card" @click="startPractice('dictation')">
        <div class="mode-icon">
          <Headphones :size="28" />
        </div>
        <div class="mode-info">
          <h3>听写</h3>
          <p>听音频默写句子，训练耳朵+拼写</p>
        </div>
        <ChevronRight :size="20" class="mode-arrow" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Loader2, PartyPopper, Mic, Headphones, ChevronRight } from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import { materialAPI } from '@/api'
import { toast } from '@/composables/useToast'

// 移动端检测
const isMobileView = ref(typeof window !== 'undefined' && window.matchMedia('(max-width: 768px)').matches)
const updateIsMobile = () => {
  isMobileView.value = window.matchMedia('(max-width: 768px)').matches
}
onMounted(() => window.addEventListener('resize', updateIsMobile))
onUnmounted(() => window.removeEventListener('resize', updateIsMobile))

const route = useRoute()
const router = useRouter()

const materialId = computed(() => route.query.material_id ? Number(route.query.material_id) : null)
const materialTitle = ref('')
const loading = ref(false)

// 加载视频标题
onMounted(async () => {
  if (!materialId.value) return
  loading.value = true
  try {
    const res = await materialAPI.getDetail(materialId.value)
    materialTitle.value = res.data?.title || res.title || ''
  } catch (e) {
    console.error('加载视频失败', e)
    toast.error('加载视频失败')
  } finally {
    loading.value = false
  }
})

const startPractice = (mode) => {
  // shadowing: 跳回 learn/42 (在 learn 内做跟读)
  // dictation: 跳回 learn/42?mode=dictation
  router.push(`/learn/${materialId.value}?mode=${mode}`)
}
</script>

<style scoped>
.practice-page {
  min-height: 100vh;
  background: var(--color-bg-base, #FAFAF7);
  padding-bottom: 40px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  background: var(--color-bg-card, #fff);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 24px;
}
.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 24px;
  text-align: center;
  color: var(--color-text-secondary);
}
.is-loading {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.empty-state h2 {
  margin: 8px 0 4px;
  color: var(--color-text-primary);
}
.empty-state p {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.5;
}
.empty-emoji-icon {
  color: var(--color-brand);
}

.practice-modes {
  max-width: 480px;
  margin: 24px auto;
  padding: 0 16px;
}
.practice-intro {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0 4px 16px;
  text-align: center;
}
.mode-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  margin-bottom: 12px;
  background: var(--color-bg-card, #fff);
  border: 1.5px solid var(--color-border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.18s ease;
  -webkit-tap-highlight-color: transparent;
}
.mode-card:hover {
  border-color: var(--color-brand);
  background: var(--color-brand);
  transform: translateY(-1px);
}
.mode-card:active {
  transform: scale(0.98);
}
.mode-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  background: var(--color-brand);
  color: var(--color-brand);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.mode-info {
  flex: 1;
  min-width: 0;
}
.mode-info h3 {
  margin: 0 0 4px;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.mode-info p {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}
.mode-arrow {
  flex-shrink: 0;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .practice-modes {
    margin-top: 16px;
  }
  .mode-card {
    padding: 16px 18px;
  }
  .mode-icon {
    width: 44px;
    height: 44px;
  }
}
</style>
