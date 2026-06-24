<template>
  <div class="fetch-url-page">
    <div class="page-header">
      <div class="header-left">
        <h1>通过 URL 抓取语料</h1>
        <span class="header-desc">粘贴 YouTube / B站 视频链接,自动下载视频+字幕+封面入库</span>
      </div>
      <SfButton @click="goBack" class="back-btn">返回列表</SfButton>
    </div>

    <div class="form-card">
      <SfForm>
        <!-- URL 输入 -->
        <SfFormItem label="视频 URL" required>
          <SfInput
            v-model="form.url"
            placeholder="https://www.bilibili.com/video/BV... 或 https://www.youtube.com/watch?v=..."
            :rows="1"
            :class="{ 'sf-input-error': form.url && !isValidUrl }"
          />
          <div v-if="form.url && !isValidUrl" class="field-error">URL 格式不正确,请粘贴完整的 https:// 链接</div>
        </SfFormItem>

        <!-- 分类 + 难度 -->
        <div class="form-row">
          <SfFormItem label="分类" required class="form-row-item">
            <SfSelect
              v-model="form.category"
              :options="categoryOptions"
              placeholder="选择分类"
              :class="{ 'sf-select-error': form.url && isValidUrl && !form.category }"
            />
            <div v-if="form.url && isValidUrl && !form.category" class="field-error">请选择分类</div>
            <div v-else-if="categoryOptions.length === 0" class="field-error">
              暂无分类,请先去
              <a href="/admin/tags" target="_blank" class="link-inline">标签管理</a>
              创建
            </div>
          </SfFormItem>
          <SfFormItem label="难度" class="form-row-item">
            <div class="star-rating">
              <button
                v-for="star in 5"
                :key="star"
                type="button"
                class="star-btn"
                :class="{ active: star <= form.difficulty }"
                @click="form.difficulty = star"
              >
                <Star :size="18" :fill="star <= form.difficulty ? 'currentColor' : 'none'" />
              </button>
              <span class="star-label">{{ form.difficulty }} / 5</span>
            </div>
          </SfFormItem>
        </div>

        <!-- 字幕语言选择 -->
        <SfFormItem label="字幕语言" v-if="form.url">
          <div class="lang-chips">
            <div
              v-for="lang in availableLangs"
              :key="lang.value"
              :class="['lang-chip', { active: form.subtitle_langs.includes(lang.value) }]"
              @click="toggleLang(lang.value)"
            >
              {{ lang.label }}
            </div>
          </div>
          <div class="hint">点击切换;自动去重(中英双语字幕)</div>
        </SfFormItem>

        <!-- 提交 -->
        <div class="submit-bar">
          <div class="submit-hint" v-if="!canSubmit">
            <AlertCircle :size="14" />
            <span>{{ disabledReason }}</span>
          </div>
          <SfButton
            type="primary"
            @click="startFetch"
            :loading="fetching"
            :disabled="!canSubmit"
            class="submit-btn"
          >
            <Download v-if="!fetching" :size="16" style="margin-right: 6px;" />
            {{ fetching ? '抓取中...' : '开始抓取' }}
          </SfButton>
        </div>
      </SfForm>
    </div>

    <!-- 当前任务进度 -->
    <div v-if="currentTask" class="status-card">
      <div class="status-header">
        <span class="status-title">
          <Loader2 v-if="currentTask.status !== 'done' && currentTask.status !== 'failed'" :size="16" class="spin" />
          <CheckCircle2 v-else-if="currentTask.status === 'done'" :size="16" class="ok" />
          <XCircle v-else :size="16" class="fail" />
          任务 {{ currentTask.task_id }}
        </span>
        <SfTag :type="statusType(currentTask.status)" size="sm">{{ statusLabel(currentTask.status) }}</SfTag>
      </div>
      <div class="status-progress">
        <SfProgress :percent="currentTask.progress || 0" :status="currentTask.status === 'failed' ? 'exception' : 'normal'" />
      </div>
      <div class="status-message">{{ currentTask.message || '等待开始...' }}</div>
      <div v-if="currentTask.status === 'done' && currentTask.material_id" class="status-actions">
        <SfButton type="primary" size="sm" @click="goMaterial(currentTask.material_id)">
          <Eye :size="14" style="margin-right: 4px;" />查看语料
        </SfButton>
        <SfButton size="sm" @click="goEditMaterial(currentTask.material_id)">
          <Pencil :size="14" style="margin-right: 4px;" />编辑
        </SfButton>
      </div>
      <div v-if="currentTask.status === 'failed' && currentTask.error" class="status-error">
        <strong>错误:</strong> {{ currentTask.error }}
      </div>
    </div>

    <!-- 历史任务 -->
    <div v-if="recentTasks.length > 0" class="history-card">
      <div class="history-header">
        <h3>最近任务</h3>
        <SfButton type="ghost" size="sm" @click="loadRecentTasks">
          <RefreshCw :size="14" />
        </SfButton>
      </div>
      <div class="history-list">
        <div
          v-for="t in recentTasks"
          :key="t.task_id"
          class="history-item"
          @click="viewTask(t)"
        >
          <div class="history-item-left">
            <SfTag :type="statusType(t.status)" size="sm">{{ statusLabel(t.status) }}</SfTag>
            <span class="history-url">{{ truncate(t.url, 50) }}</span>
          </div>
          <div class="history-item-right">
            <span class="history-platform">{{ t.platform }}</span>
            <span class="history-time">{{ formatTime(t.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { adminAPI, materialAPI } from '@/api'
import {
  Star, Download, Loader2, CheckCircle2, XCircle,
  RefreshCw, Eye, Pencil, AlertCircle
} from 'lucide-vue-next'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfProgress from '@/components/ui/SfProgress.vue'

const router = useRouter()

// 状态
const fetching = ref(false)
const currentTask = ref(null)
const recentTasks = ref([])
const categories = ref([])
let pollTimer = null

// 表单
const form = reactive({
  url: '',
  category: '',
  difficulty: 2,
  subtitle_langs: ['en', 'zh-Hans']
})

// 计算属性
const availableLangs = [
  { label: '英语 (en)', value: 'en' },
  { label: '中英双语 (zh-Hans)', value: 'zh-Hans' }
]

const categoryOptions = computed(() => {
  return categories.value.map(c => ({ label: c.name, value: c.name }))
})

const isValidUrl = computed(() => {
  if (!form.url) return false
  try {
    const u = new URL(form.url)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
})

const canSubmit = computed(() => {
  return isValidUrl.value && !!form.category
})

const disabledReason = computed(() => {
  if (!form.url) return '请填写视频 URL'
  if (!isValidUrl.value) return 'URL 格式不正确'
  if (!form.category) return '请选择分类'
  if (categoryOptions.value.length === 0) return '请先在标签管理中创建分类'
  return ''
})

// 方法
const toggleLang = (value) => {
  const idx = form.subtitle_langs.indexOf(value)
  if (idx >= 0) form.subtitle_langs.splice(idx, 1)
  else form.subtitle_langs.push(value)
}

const detectPlatform = (url) => {
  if (!url) return 'unknown'
  if (/bilibili\.com|b23\.tv/i.test(url)) return 'bilibili'
  if (/youtube\.com|youtu\.be/i.test(url)) return 'youtube'
  return 'other'
}

const startFetch = async () => {
  if (!canSubmit.value) {
    toast.error('请填写完整:URL + 分类')
    return
  }
  fetching.value = true
  try {
    const res = await adminAPI.fetchFromUrl({
      url: form.url,
      category: form.category,
      difficulty: form.difficulty,
      subtitle_langs: form.subtitle_langs
    })
    toast.success('已加入抓取队列')
    currentTask.value = {
      task_id: res.task_id,
      status: 'pending',
      progress: 0,
      message: '已加入队列,等待执行...',
      url: form.url,
      platform: detectPlatform(form.url)
    }
    startPolling(res.task_id)
    loadRecentTasks()
  } catch (e) {
    toast.error(e?.response?.data?.detail || '启动失败')
  } finally {
    fetching.value = false
  }
}

const startPolling = (taskId) => {
  stopPolling()
  pollTimer = setInterval(async () => {
    try {
      const t = await adminAPI.getFetchStatus(taskId)
      currentTask.value = t
      if (t.status === 'done' || t.status === 'failed') {
        stopPolling()
        loadRecentTasks()
        if (t.status === 'done') {
          toast.success(`抓取完成!语料 ID = ${t.material_id}`)
        }
      }
    } catch (e) {
      // 任务可能过期 (重启后清空),停止轮询
      stopPolling()
      currentTask.value = { ...currentTask.value, status: 'failed', error: '任务已过期,请刷新历史' }
    }
  }, 1500)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const loadRecentTasks = async () => {
  try {
    const tasks = await adminAPI.listFetchTasks()
    recentTasks.value = Array.isArray(tasks) ? tasks : []
  } catch (e) {
    console.error('加载历史任务失败', e)
  }
}

const loadCategories = async () => {
  try {
    categories.value = await materialAPI.getCategories() || []
    // UX 优化: 只有一个分类时自动选上(免去一次点击)
    if (categories.value.length === 1 && !form.category) {
      form.category = categories.value[0].name
    }
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

const viewTask = (task) => {
  if (task.status === 'done' && task.material_id) {
    goMaterial(task.material_id)
  } else if (task.status === 'pending' || task.status === 'fetching' || task.status === 'parsing') {
    // 继续轮询这个任务
    startPolling(task.task_id)
    currentTask.value = task
    toast.info('继续跟踪此任务')
  }
}

const goMaterial = (id) => {
  if (!id) return
  // 在前台打开,管理员可以预览
  window.open(`/learn/${id}`, '_blank')
}

const goEditMaterial = (id) => {
  if (!id) return
  router.push(`/admin/materials`)
  // 进列表后用户需要找 — 这里不直接打开编辑 modal,简化
  toast.info('请在语料列表中找到 ID=' + id + ' 并点击编辑')
}

const goBack = () => {
  router.push('/admin/materials')
}

// UI helpers
const statusType = (s) => {
  const m = { pending: 'warning', fetching: 'info', parsing: 'info', done: 'success', failed: 'danger' }
  return m[s] || 'default'
}

const statusLabel = (s) => {
  const m = { pending: '排队中', fetching: '下载中', parsing: '解析中', done: '已完成', failed: '失败' }
  return m[s] || s
}

const truncate = (s, n) => {
  if (!s) return ''
  return s.length > n ? s.slice(0, n) + '...' : s
}

const formatTime = (iso) => {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch { return iso }
}

onMounted(() => {
  loadCategories()
  loadRecentTasks()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.fetch-url-page {
  max-width: 880px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 16px;
}
.header-left h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--sf-admin-text-primary, #f5f5f5);
}
.header-desc {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: var(--sf-admin-text-muted, #888);
}
.back-btn {
  border-radius: 10px;
}

.form-card {
  background: var(--sf-admin-bg-card);
  border: 1px solid var(--sf-admin-border);
  border-radius: 12px;
  padding: 28px;
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.form-row-item {
  min-width: 0;
}

.star-rating {
  display: flex;
  align-items: center;
  gap: 4px;
}
.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(255,255,255,0.15);
  padding: 2px;
  transition: color 0.15s, transform 0.15s;
}
.star-btn:hover { transform: scale(1.15); }
.star-btn.active { color: #fbbf24; }
.star-label {
  margin-left: 8px;
  font-size: 12px;
  color: var(--sf-admin-text-muted, #888);
}

.lang-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.lang-chip {
  padding: 6px 14px;
  border: 1px solid var(--sf-admin-border, rgba(255,255,255,0.12));
  border-radius: 16px;
  font-size: 13px;
  color: var(--sf-admin-text-secondary);
  cursor: pointer;
  user-select: none;
  transition: all 0.15s;
}
.lang-chip:hover {
  border-color: var(--sf-admin-accent, #60a5fa);
}
.lang-chip.active {
  background: var(--sf-admin-accent, #60a5fa);
  color: #fff;
  border-color: var(--sf-admin-accent, #60a5fa);
}
.hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--sf-admin-text-muted, #888);
}

.submit-bar {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 14px;
}
.submit-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #f59e0b;
}
.submit-btn {
  min-width: 160px;
  height: 44px;
  border-radius: 10px;
  font-weight: 600;
}

/* ── Field Validation Errors ── */
.field-error {
  margin-top: 6px;
  font-size: 12px;
  color: #ef4444;
  font-weight: 500;
}
.field-error .link-inline {
  color: var(--sf-admin-accent, #60a5fa);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px solid currentColor;
}
:deep(.sf-input-error) {
  border-color: #ef4444 !important;
}
:deep(.sf-input-error:focus) {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15) !important;
}
:deep(.sf-select-error .sf-select-trigger) {
  border-color: #ef4444 !important;
}

/* ── Status Card ── */
.status-card {
  background: var(--sf-admin-bg-card);
  border: 1px solid var(--sf-admin-border);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
}
.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.status-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--sf-admin-text-primary);
}
.spin {
  animation: spin 1s linear infinite;
  color: var(--sf-admin-accent, #60a5fa);
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.ok { color: #10b981; }
.fail { color: #ef4444; }
.status-progress {
  margin-bottom: 10px;
}
.status-message {
  font-size: 13px;
  color: var(--sf-admin-text-secondary);
  word-break: break-word;
}
.status-error {
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: #fca5a5;
  word-break: break-all;
}
.status-actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

/* ── History Card ── */
.history-card {
  background: var(--sf-admin-bg-card);
  border: 1px solid var(--sf-admin-border);
  border-radius: 12px;
  padding: 20px 24px;
}
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.history-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--sf-admin-text-primary);
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.12s;
}
.history-item:hover {
  background: rgba(96,165,250,0.06);
}
.history-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1;
}
.history-url {
  font-size: 12px;
  color: var(--sf-admin-text-secondary);
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.history-item-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.history-platform {
  font-size: 11px;
  color: var(--sf-admin-text-muted);
  text-transform: uppercase;
  font-weight: 600;
}
.history-time {
  font-size: 12px;
  color: var(--sf-admin-text-muted);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}
</style>
