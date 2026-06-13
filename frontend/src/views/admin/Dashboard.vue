<template>
  <div class="dashboard">
    <h1 class="page-title">数据统计</h1>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" style="--accent: var(--sf-admin-accent);">
        <div class="stat-icon-wrap">
          <Video :size="28" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.materials?.total || 0 }}</div>
          <div class="stat-label">语料总数</div>
        </div>
        <div class="stat-bg-icon">
          <Video :size="64" />
        </div>
      </div>
      <div class="stat-card" style="--accent: var(--color-success);">
        <div class="stat-icon-wrap">
          <Check :size="28" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.materials?.active || 0 }}</div>
          <div class="stat-label">已激活</div>
        </div>
        <div class="stat-bg-icon">
          <Check :size="64" />
        </div>
      </div>
      <div class="stat-card" style="--accent: var(--color-info);">
        <div class="stat-icon-wrap">
          <Eye :size="28" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total_views || 0 }}</div>
          <div class="stat-label">总观看次数</div>
        </div>
        <div class="stat-bg-icon">
          <Eye :size="64" />
        </div>
      </div>
      <div class="stat-card" style="--accent: var(--color-warning);">
        <div class="stat-icon-wrap">
          <Folder :size="28" />
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.categories?.length || 0 }}</div>
          <div class="stat-label">分类数量</div>
        </div>
        <div class="stat-bg-icon">
          <Folder :size="64" />
        </div>
      </div>
    </div>

    <div class="info-grid">
      <!-- 存储信息 -->
      <div class="info-card">
        <div class="card-header">
          <h3 class="card-title">存储配置</h3>
          <SfButton size="sm" @click="testStorage" :loading="testing" class="test-btn">
            测试连接
          </SfButton>
        </div>
        <div class="storage-grid">
          <div class="storage-item">
            <span class="storage-label">存储类型</span>
            <span class="storage-value">{{ storageInfo.storage_type || '-' }}</span>
          </div>
          <div class="storage-item">
            <span class="storage-label">云端存储</span>
            <SfTag :type="storageInfo.is_cloud ? 'success' : 'default'" size="sm">
              {{ storageInfo.is_cloud ? '是' : '否' }}
            </SfTag>
          </div>
          <div class="storage-item">
            <span class="storage-label">CDN 加速</span>
            <SfTag :type="storageInfo.cdn_enabled ? 'success' : 'default'" size="sm">
              {{ storageInfo.cdn_enabled ? '已启用' : '未启用' }}
            </SfTag>
          </div>
        </div>
      </div>

      <!-- 分类统计 -->
      <div class="info-card">
        <div class="card-header">
          <h3 class="card-title">分类统计</h3>
        </div>
        <div class="category-list">
          <div v-for="cat in stats.categories || []" :key="cat.name" class="category-item">
            <span class="cat-name">{{ cat.name }}</span>
            <div class="cat-bar-wrap">
              <div
                class="cat-bar"
                :style="{ width: getBarWidth(cat.count) + '%' }"
              />
            </div>
            <span class="cat-count">{{ cat.count }}</span>
          </div>
          <div v-if="!stats.categories?.length" class="empty-text">暂无分类数据</div>
        </div>
      </div>

      <!-- 存储分布 -->
      <div class="info-card" v-if="stats.storage && Object.keys(stats.storage).length">
        <div class="card-header">
          <h3 class="card-title">存储分布</h3>
        </div>
        <div class="storage-dist">
          <div v-for="(count, type) in stats.storage" :key="type" class="dist-item">
            <span class="dist-type">{{ type }}</span>
            <span class="dist-count">{{ count }} 个文件</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { toast } from '@/composables/useToast'
import { Video, Check, Eye, Folder } from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfTag from '@/components/ui/SfTag.vue'
import { adminAPI } from '@/api'

const stats = ref({})
const storageInfo = ref({})
const testing = ref(false)

const loadStats = async () => {
  try {
    stats.value = await adminAPI.getStats()
  } catch (e) {
    toast.error('加载统计失败')
  }
}

const loadStorageInfo = async () => {
  try {
    storageInfo.value = await adminAPI.getStorageInfo()
  } catch (e) {
    console.error('加载存储信息失败', e)
  }
}

const testStorage = async () => {
  testing.value = true
  try {
    const result = await adminAPI.testStorage()
    if (result.success) {
      toast.success('存储连接正常')
    } else {
      toast.error(result.message)
    }
  } catch (e) {
    toast.error('测试失败')
  } finally {
    testing.value = false
  }
}

const getBarWidth = (count) => {
  const cats = stats.value.categories || []
  const max = Math.max(...cats.map(c => c.count), 1)
  return Math.max(8, (count / max) * 100)
}

onMounted(() => {
  loadStats()
  loadStorageInfo()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.page-title {
  margin: 0 0 24px;
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  background: var(--sf-admin-sidebar-bg);
  border-radius: 16px;
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-card);
  transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.28s ease;
  border: 1px solid var(--sf-admin-sidebar-border);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-card-hover);
}

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  flex-shrink: 0;
}

.stat-body {
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 2px;
}

.stat-bg-icon {
  position: absolute;
  right: -8px;
  bottom: -12px;
  color: color-mix(in srgb, var(--accent) 6%, transparent);
  z-index: 0;
}

/* 信息区域网格 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-card {
  background: var(--sf-admin-sidebar-bg);
  border-radius: 16px;
  padding: 22px;
  border: 1px solid var(--sf-admin-sidebar-border);
  box-shadow: var(--shadow-card);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.test-btn {
  border-radius: 10px;
}

/* 存储信息 */
.storage-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.storage-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--sf-admin-sidebar-active);
  border-radius: 10px;
}

.storage-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.storage-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

/* 分类统计 */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cat-name {
  font-size: 13px;
  color: var(--color-text-secondary);
  width: 60px;
  flex-shrink: 0;
}

.cat-bar-wrap {
  flex: 1;
  height: 8px;
  background: var(--sf-admin-sidebar-active);
  border-radius: 4px;
  overflow: hidden;
}

.cat-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-brand), #60a5fa);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.cat-count {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  width: 30px;
  text-align: right;
}

.empty-text {
  font-size: 13px;
  color: var(--color-text-muted);
  text-align: center;
  padding: 16px;
}

/* 存储分布 */
.storage-dist {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--sf-admin-sidebar-active);
  border-radius: 8px;
}

.dist-type {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.dist-count {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
}

/* 响应式 */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
