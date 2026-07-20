<template>
  <div class="profile-page">
    <!-- 用户信息卡片 -->
    <div class="profile-hero">
      <div class="profile-hero-inner">
        <div class="profile-avatar">
          <SfAvatar :name="userStore.user?.username?.charAt(0) || 'U'" size="lg" />
        </div>
        <div class="profile-user-info">
          <h1 class="profile-name">{{ userStore.user?.username || '未登录' }}</h1>
          <p class="profile-meta">
            <span v-if="userStore.user?.created_at">加入于 {{ formatDate(userStore.user.created_at) }}</span>
          </p>
        </div>
        <!-- 编辑入口:文字链接,取代 SfButton (更轻,不抢 hero 视觉) -->
        <button v-if="userStore.isLoggedIn" class="profile-edit-link" @click="showEditDialog = true">
          <Pencil :size="14" />
          <span>编辑</span>
        </button>
      </div>
    </div>

    <!-- 7-20: 会员信息永远显示. 注册已强制激活码, 正常用户都是已激活状态, 此处仅展示 -->
    <div class="profile-section" v-if="userStore.user?.activation_code_id">
      <PageHeader title="会员信息" />
      <div class="membership-card">
        <div class="membership-row" v-if="userStore.user?.activation_code">
          <span class="membership-label">激活码</span>
          <span class="membership-value membership-code">{{ userStore.user.activation_code.code }}</span>
        </div>
        <div class="membership-row" v-if="userStore.user?.activated_at">
          <span class="membership-label">激活时间</span>
          <span class="membership-value">{{ formatDate(userStore.user.activated_at) }}</span>
        </div>
        <div class="membership-row">
          <span class="membership-label">到期时间</span>
          <span class="membership-value" :class="membershipExpiryClass">
            <template v-if="userStore.user?.activation_code?.expires_at">
              {{ formatDate(userStore.user.activation_code.expires_at) }}
              <span v-if="membershipStatusLabel" class="membership-badge">{{ membershipStatusLabel }}</span>
            </template>
            <template v-else>
              <span class="permanent-text">永久有效</span>
            </template>
          </span>
        </div>
      </div>
    </div>

    <!-- 学习统计 (Phase 23b: 保留,加图标增强视觉权重) -->
    <div class="profile-section">
      <PageHeader title="学习统计" />
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><BookOpen :size="18" /></div>
          <div class="stat-value">{{ stats.total_materials || '—' }}</div>
          <div class="stat-label">学习语料</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><CalendarDays :size="18" /></div>
          <div class="stat-value">{{ stats.total_learning_days || '—' }}</div>
          <div class="stat-label">学习天数</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon stat-icon--accent"><Flame :size="18" /></div>
          <div class="stat-value stat-value--accent">{{ stats.streak_days || '—' }}</div>
          <div class="stat-label">连续学习</div>
        </div>
      </div>
    </div>

    <!-- 最近学习 -->
    <div class="profile-section" v-if="recentLearning.length > 0">
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

    <!-- Phase 26+6: 学习中心/卡片 菜单入口已删 (用户反馈 7-16: "我的里面的学习中心卡片都不要这2个") -->

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
      <SfForm @submit="saveProfile">
        <SfFormItem label="用户名" required>
          <SfInput v-model="editForm.username" placeholder="请输入用户名" />
        </SfFormItem>
      </SfForm>
      <template #footer>
        <SfButton type="ghost" @click="showEditDialog = false">取消</SfButton>
        <SfButton type="primary" @click="saveProfile" :loading="saving">保存</SfButton>
      </template>
    </SfDialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { showConfirm } from '@/composables/useConfirm'
import {
  BookOpen,
  CalendarDays,
  Flame,
  Pencil
} from 'lucide-vue-next'
import SfDialog from '@/components/ui/SfDialog.vue'
import SfButton from '@/components/ui/SfButton.vue'
import SfAvatar from '@/components/ui/SfAvatar.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfInput from '@/components/ui/SfInput.vue'
import { useUserStore } from '@/stores/user'
import { learningStatsAPI } from '@/api'
import PageHeader from '@/components/common/PageHeader.vue'
import VideoCard from '@/components/common/VideoCard.vue'

const router = useRouter()
const userStore = useUserStore()

const stats = reactive({
  total_materials: 0,
  total_learning_days: 0,
  streak_days: 0
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

// P0-8: 会员到期状态计算 (用于 Profile 会员信息区块)
const membershipStatusLabel = computed(() => {
  const ac = userStore.user?.activation_code
  if (!ac?.expires_at) return '永久有效'
  const expiresAt = new Date(ac.expires_at)
  const now = new Date()
  if (expiresAt < now) return '已过期'
  const daysLeft = Math.ceil((expiresAt - now) / (1000 * 60 * 60 * 24))
  return `剩余 ${daysLeft} 天`
})

const membershipExpiryClass = computed(() => {
  const ac = userStore.user?.activation_code
  if (!ac?.expires_at) return ''
  const expiresAt = new Date(ac.expires_at)
  const now = new Date()
  if (expiresAt < now) return 'membership-value--expired'
  const daysLeft = Math.ceil((expiresAt - now) / (1000 * 60 * 60 * 24))
  if (daysLeft <= 30) return 'membership-value--warning'
  return ''
})

// Phase 23b: 砍 statusLabel/formatDateTime (激活信息整块已删,这两个 helper 只它用)

const goLearn = (id) => {
  router.push(`/learn/${id}`)
}

const loadStats = async () => {
  try {
    const res = await learningStatsAPI.getStatistics()
    stats.total_materials = res.total_materials || 0
    stats.total_learning_days = res.total_learning_days || 0
    stats.streak_days = res.streak_days || 0
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

// 7-20: 兑换激活码逻辑已删 (注册必填激活码, 登录后默认已激活, Profile 仅展示)

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
.profile-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 0 32px 0;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Hero 用户信息 ── */
.profile-hero {
  margin-bottom: 24px;
  /* Phase 23b: 显式墨绿渐变 (原 var(--sf-cta-gradient) fallback 到蓝色,跟墨绿色调不一致) */
  background: linear-gradient(135deg, #4DA06C 0%, var(--color-brand) 100%);
  border-radius: var(--radius-lg);
  padding: 28px 32px;
  color: #fff;
  position: relative;
  overflow: hidden;
}

.profile-hero-inner {
  display: flex;
  align-items: center;
  gap: 20px;
}

.profile-avatar :deep(.el-avatar),
.profile-avatar :deep(.sf-avatar) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  border: 3px solid rgba(255, 255, 255, 0.4);
}

.profile-user-info {
  flex: 1;
  min-width: 0;
}

.profile-name {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #fff;
}

.profile-meta {
  font-size: 13px;
  opacity: 0.85;
  margin: 0;
}

.profile-edit-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.92);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 120ms ease;
  -webkit-tap-highlight-color: transparent;
  align-self: flex-start;
}
.profile-edit-link:hover {
  background: rgba(255, 255, 255, 0.12);
}
.profile-edit-link:active {
  background: rgba(255, 255, 255, 0.2);
}

/* ── 统计区域 ── */
.profile-section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}

/* P0-8: 会员信息卡片 */
.membership-card {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.membership-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  padding: 8px 12px;
  background: var(--color-bg-secondary, rgba(0, 0, 0, 0.02));
  border-radius: var(--radius-md);
}
.membership-label {
  color: var(--color-text-secondary, #666);
  font-weight: 500;
}
.membership-value {
  color: var(--color-text-primary, #222);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.membership-code {
  font-family: ui-monospace, "SF Mono", Menlo, monospace;
  letter-spacing: 0.5px;
}
.membership-value--warning {
  color: #d97706;
}
.membership-value--expired {
  color: #dc2626;
}
.membership-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #fef3c7;
  color: #92400e;
  font-weight: 600;
}
.membership-value--expired + .membership-badge,
.membership-value:has(.membership-badge) .membership-badge {
  /* keep badge style */
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.stat-card {
  text-align: center;
  padding: 20px 12px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: border-color var(--sf-duration-normal) cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  border-color: var(--color-border);
  transform: translateY(-1px);
}

.stat-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin: 0 auto 6px;
  border-radius: 8px;
  background: var(--color-brand-subtle);              /* Phase 24: 草绿半透底(跟 brand 同色相, 不是墨绿) */
  color: var(--color-brand);                          /* 草绿 icon */
}
.stat-icon--accent {
  background: rgba(245, 158, 11, 0.12);   /* 橙色淡底(连续学习用) */
  color: #D97706;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  color: var(--color-brand-bright);
  margin-bottom: 4px;
  letter-spacing: -0.01em;
}

.stat-value--accent {
  color: var(--color-accent);
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

/* ── 视频网格 ── */
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

/* ── 菜单 ── */
.profile-menu {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background var(--sf-duration-normal) cubic-bezier(0.4, 0, 0.2, 1),
              padding-left 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border-bottom: 1px solid var(--color-border);
  gap: 16px;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: var(--color-bg-elevated);
  padding-left: 24px;
}

.menu-item svg:first-child {
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.menu-item span {
  flex: 1;
  font-size: 15px;
  color: var(--color-text-primary);
}

.menu-arrow {
  color: var(--color-text-muted);
  flex-shrink: 0;
}

/* ── 退出登录 ── */
.logout-section {
  text-align: center;
  padding: 16px 0;
}

.logout-btn {
  width: 100%;
  max-width: 320px;
  height: 48px !important;
  font-size: 15px;
  font-weight: 600;
  background: var(--color-accent) !important;
  border: none;
  border-radius: var(--radius-md);
  transition: background var(--sf-duration-normal) cubic-bezier(0.4, 0, 0.2, 1);
}

.logout-btn:hover {
  background: var(--color-accent-hover) !important;
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .profile-hero {
    padding: 20px;
    border-radius: var(--radius-md);
  }

  .profile-hero-inner {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .profile-name {
    font-size: 20px;
  }

  .profile-section {
    padding: 20px 16px;
    border-radius: var(--radius-md);
    margin-bottom: 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .stat-card {
    padding: 16px 8px;
  }

  .stat-value {
    font-size: 22px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }

  .profile-menu {
    border-radius: var(--radius-md);
  }

  .logout-btn {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .profile-hero {
    padding: 16px;
  }

  .profile-name {
    font-size: 18px;
  }

  .stat-card {
    padding: 12px 6px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-label {
    font-size: 12px;
  }

  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .menu-item {
    padding: 14px 16px;
  }

  .menu-item span {
    font-size: 14px;
  }
}
</style>
