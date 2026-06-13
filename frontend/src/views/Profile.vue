<template>
  <div class="yt-profile">
    <!-- 用户信息卡片 -->
    <div class="channel-header">
      <div class="channel-banner">
        <div class="channel-info">
          <div class="channel-avatar">
            <SfAvatar :name="userStore.user?.username?.charAt(0) || 'U'" size="lg" />
          </div>
          <div class="channel-details">
            <h1 class="channel-name">{{ userStore.user?.username || '未登录' }}</h1>
            <p class="channel-meta">
              <span v-if="userStore.user?.created_at">加入于 {{ formatDate(userStore.user.created_at) }}</span>
            </p>
          </div>
          <SfButton type="primary" class="edit-btn" @click="showEditDialog = true">
            编辑资料
          </SfButton>
        </div>
      </div>
    </div>

    <!-- 学习统计 -->
    <div class="stats-section">
      <PageHeader title="学习统计" />
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_materials }}</div>
          <div class="stat-label">学习语料</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_learning_days }}</div>
          <div class="stat-label">学习天数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value highlight">{{ stats.streak_days }}</div>
          <div class="stat-label">连续学习</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_vocabulary }}</div>
          <div class="stat-label">生词数量</div>
        </div>
      </div>
    </div>

    <!-- 最近学习 -->
    <div class="recent-section" v-if="recentLearning.length > 0">
      <PageHeader title="最近学习">
        <template #actions>
          <SfButton type="ghost" size="sm" @click="$router.push('/learning-center')">
            查看全部
          </SfButton>
        </template>
      </PageHeader>
      <div class="video-grid">
        <VideoCard
          v-for="item in recentLearning"
          :key="item.id"
          :id="item.material_id"
          :title="item.material_title"
          :cover="item.material_cover"
          :progress="item.progress"
          :show-avatar="false"
          @click="goLearn"
        />
      </div>
    </div>

    <!-- 功能菜单 -->
    <div class="menu-section">
      <div class="menu-item" @click="$router.push('/favorites')">
        <Star :size="22" />
        <span>我的收藏</span>
        <ArrowRight :size="16" class="menu-arrow" />
      </div>
      <div class="menu-item" @click="$router.push('/vocabulary')">
        <BookOpen :size="22" />
        <span>生词本</span>
        <ArrowRight :size="16" class="menu-arrow" />
      </div>
      <div class="menu-item" @click="$router.push('/learning-center')">
        <BarChart3 :size="22" />
        <span>学习中心</span>
        <ArrowRight :size="16" class="menu-arrow" />
      </div>
    </div>

    <!-- 退出登录 -->
    <div class="logout-section">
      <SfButton type="danger" size="lg" @click="handleLogout" class="logout-btn">
        退出登录
      </SfButton>
    </div>

    <!-- 编辑资料对话框 -->
    <SfDialog
      v-model="showEditDialog"
      title="编辑资料"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <SfButton type="ghost" @click="showEditDialog = false">取消</SfButton>
        <SfButton type="primary" @click="saveProfile" :loading="saving">保存</SfButton>
      </template>
    </SfDialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { showConfirm } from '@/composables/useConfirm'
import {
  Star,
  BookOpen,
  ArrowRight,
  BarChart3
} from 'lucide-vue-next'
import SfDialog from '@/components/ui/SfDialog.vue'
import SfButton from '@/components/ui/SfButton.vue'
import SfAvatar from '@/components/ui/SfAvatar.vue'
import { useUserStore } from '@/stores/user'
import { learningStatsAPI } from '@/api'
import PageHeader from '@/components/common/PageHeader.vue'
import VideoCard from '@/components/common/VideoCard.vue'

const router = useRouter()
const userStore = useUserStore()

const stats = reactive({
  total_materials: 0,
  completed_materials: 0,
  in_progress_materials: 0,
  total_vocabulary: 0,
  mastered_vocabulary: 0,
  total_learning_days: 0,
  this_week_learning_days: 0,
  streak_days: 0,
  total_favorites: 0
})

const recentLearning = ref([])
const showEditDialog = ref(false)
const saving = ref(false)

const editForm = reactive({
  username: ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const goLearn = (id) => {
  router.push(`/learn/${id}`)
}

const loadStats = async () => {
  try {
    const res = await learningStatsAPI.getStatistics()
    stats.total_materials = res.total_materials || 0
    stats.completed_materials = res.completed_materials || 0
    stats.in_progress_materials = res.in_progress_materials || 0
    stats.total_vocabulary = res.total_vocabulary || 0
    stats.mastered_vocabulary = res.mastered_vocabulary || 0
    stats.total_learning_days = res.total_learning_days || 0
    stats.this_week_learning_days = res.this_week_learning_days || 0
    stats.streak_days = res.streak_days || 0
    stats.total_favorites = res.total_favorites || 0
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

const loadRecentLearning = async () => {
  try {
    const res = await learningStatsAPI.getRecent(5)
    recentLearning.value = res || []
  } catch (e) {
    console.error('加载学习记录失败', e)
  }
}

const handleLogout = async () => {
  const confirmed = await showConfirm({ title: '提示', message: '确定要退出登录吗？' })
  if (confirmed) {
    userStore.logout()
    toast.success('已退出登录')
    router.push('/')
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    // 这里需要后端提供更新用户信息的API
    // 暂时只更新本地状态
    if (userStore.user) {
      userStore.user.username = editForm.username
    }
    toast.success('保存成功')
    showEditDialog.value = false
  } catch (e) {
    console.error('保存失败', e)
    toast.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  // 初始化编辑表单
  if (userStore.user) {
    editForm.username = userStore.user.username || ''
  }

  // 加载数据
  if (userStore.isLoggedIn) {
    loadStats()
    loadRecentLearning()
  }
})
</script>

<style scoped>
.yt-profile {
  max-width: 1000px;
  margin: 0 auto;
}

/* 频道头部 */
.channel-header {
  margin-bottom: var(--spacing-xl, 24px);
}

.channel-banner {
  background: var(--color-brand);
  border-radius: var(--radius-lg);
  padding: 28px;
  color: #fff;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg, 20px);
}

.channel-avatar .el-avatar {
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
  font-size: 32px;
  font-weight: bold;
  border: 3px solid rgba(255, 255, 255, 0.5);
}

.channel-details {
  flex: 1;
}

.channel-name {
  font-size: var(--font-size-2xl, 24px);
  font-weight: var(--font-weight-semibold, 600);
  margin: 0 0 4px 0;
}

.channel-meta {
  font-size: var(--font-size-base, 14px);
  opacity: 0.9;
  margin: 0;
}

.edit-btn {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
}

.edit-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.7);
}

/* 统计区域 */
.stats-section {
  background: var(--color-bg-base);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: 16px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: var(--color-bg-elevated);
  border-radius: 14px;
  border: 1px solid transparent;
  transition: border-color 0.2s, transform 0.2s;
}

.stat-card:hover {
  border-color: var(--color-border);
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-brand);
  margin-bottom: 4px;
}

.stat-value.highlight {
  color: var(--color-warning);
}

.stat-label {
  font-size: var(--font-size-sm, 13px);
  color: var(--color-text-secondary);
}

/* 最近学习 */
.recent-section {
  margin-bottom: var(--spacing-xl, 24px);
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
  margin-top: 16px;
}

/* 菜单 */
.menu-section {
  background: var(--color-bg-base);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.2s, padding-left 0.2s;
  border-bottom: 1px solid var(--color-border);
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: var(--color-bg-elevated);
  padding-left: 24px;
}

.menu-item .el-icon:first-child {
  margin-right: var(--spacing-md, 16px);
  font-size: 22px;
  color: var(--color-text-secondary);
}

.menu-item span {
  flex: 1;
  font-size: var(--font-size-base, 15px);
  color: var(--color-text-primary);
}

.menu-arrow {
  color: var(--color-text-muted);
}

/* 退出登录 */
.logout-section {
  text-align: center;
  padding: var(--spacing-2xl, 24px) 0;
}

.logout-btn {
  width: 100%;
  max-width: 300px;
}

/* 响应式 */
@media (max-width: 768px) {
  .channel-banner {
    padding: var(--spacing-lg, 20px);
    border-radius: var(--radius-md, 8px);
  }

  .channel-info {
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-sm, 12px);
  }

  .channel-name {
    font-size: var(--font-size-xl, 20px);
  }

  .channel-meta {
    font-size: var(--font-size-sm, 13px);
  }

  .stats-section {
    padding: var(--spacing-md, 16px);
    border-radius: var(--radius-md, 8px);
    margin-bottom: var(--spacing-md, 16px);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm, 12px);
  }

  .stat-card {
    padding: var(--spacing-md, 16px);
  }

  .stat-value {
    font-size: var(--font-size-2xl, 24px);
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: var(--spacing-sm, 12px);
  }

  .menu-section {
    border-radius: var(--radius-md, 8px);
  }

  .menu-item {
    padding: var(--spacing-sm, 14px) var(--spacing-md, 16px);
  }

  .menu-item span {
    font-size: var(--font-size-sm, 14px);
  }

  .logout-btn {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .channel-banner {
    padding: var(--spacing-md, 16px);
  }

  .channel-name {
    font-size: var(--font-size-lg, 18px);
  }

  .stat-card {
    padding: var(--spacing-sm, 12px);
  }

  .stat-value {
    font-size: var(--font-size-xl, 20px);
  }

  .stat-label {
    font-size: var(--font-size-xs, 12px);
  }

  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
