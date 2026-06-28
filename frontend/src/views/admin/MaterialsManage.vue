<template>
  <div class="materials-manage">
    <div class="page-header">
      <div class="header-left">
        <h1>语料管理</h1>
        <span class="header-sub">{{ pagination.total }} 个语料 · 已选 {{ selectedIds.length }} 个</span>
      </div>
      <div class="header-actions">
        <!-- 列设置按钮: 控制每列显隐 + 重置列宽 -->
        <SfDropdown placement="bottom" :menu-style="{ right: 0, left: 'auto', minWidth: '220px', padding: '8px' }">
          <template #trigger>
            <SfButton type="ghost">
              <Settings :size="16" style="margin-right: 4px;" />
              列设置
            </SfButton>
          </template>
          <div class="col-picker" @click.stop>
            <div class="col-picker-header">
              <span>显示列</span>
              <button class="col-picker-reset" @click="resetColumnPrefs">重置默认</button>
            </div>
            <label
              v-for="col in allColumns"
              :key="col.key"
              class="col-picker-row"
              :class="{ 'col-picker-row-disabled': col.required }"
            >
              <input
                type="checkbox"
                :checked="!hiddenKeys.includes(col.key)"
                :disabled="col.required"
                @change="toggleColumn(col.key)"
              />
              <span class="col-picker-label">{{ col.label || '(无标题)' }}</span>
            </label>
            <div class="col-picker-hint">
              列宽也可直接拖拽表头右边调节
            </div>
          </div>
        </SfDropdown>
        <SfButton @click="exportCsv" :loading="exporting" type="ghost">
          <Download :size="16" style="margin-right: 4px;" />
          导出CSV
        </SfButton>
        <SfButton type="primary" @click="goToUpload">
          <Plus :size="16" style="margin-right: 4px;" />
          上传语料
        </SfButton>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="card-container filter-card">
      <SfForm>
        <div class="filter-row">
          <SfFormItem label="关键词">
            <SfInput v-model="filters.keyword" placeholder="搜索标题" @keyup.enter="loadMaterials(1)" />
          </SfFormItem>
          <SfFormItem label="分类">
            <SfSelect v-model="filters.category" :options="categoryOptions" placeholder="全部分类" />
          </SfFormItem>
          <SfFormItem label="状态">
            <SfSelect v-model="filters.is_active" :options="statusOptions" placeholder="全部状态" />
          </SfFormItem>
          <SfFormItem label="时长">
            <SfSelect v-model="filters.duration" :options="durationOptions" placeholder="全部时长" @change="loadMaterials(1)" />
          </SfFormItem>
          <SfFormItem>
            <div class="filter-actions">
              <SfButton type="primary" @click="loadMaterials(1)">搜索</SfButton>
              <SfButton @click="resetFilters">重置</SfButton>
            </div>
          </SfFormItem>
        </div>
      </SfForm>
    </div>

    <!-- 批量操作工具条 (选中时显示) -->
    <div class="bulk-toolbar" v-if="selectedIds.length > 0">
      <div class="bulk-left">
        <span class="bulk-count">已选 <strong>{{ selectedIds.length }}</strong> 个</span>
        <SfButton type="ghost" size="sm" @click="clearSelection">取消选择</SfButton>
      </div>
      <div class="bulk-actions">
        <SfButton size="sm" @click="batchPublish" :loading="bulkLoading">
          <Eye :size="14" style="margin-right: 4px;" />批量发布
        </SfButton>
        <SfButton size="sm" @click="batchUnpublish" :loading="bulkLoading">
          <EyeOff :size="14" style="margin-right: 4px;" />取消发布
        </SfButton>
        <SfPopconfirm
          title="确定要删除选中的语料吗？"
          @confirm="batchDelete(false)"
        >
          <SfButton type="danger" size="sm" :loading="bulkLoading">批量删除</SfButton>
        </SfPopconfirm>
      </div>
    </div>

    <!-- 语料列表 -->
    <div class="card-container">
      <SfTable
        :columns="columns"
        :data="materials"
        :width-overrides="colWidths"
        :hidden-keys="hiddenKeys"
        @column-resize="onColumnResize"
      >
        <template #select="{ row }">
          <input
            type="checkbox"
            class="row-checkbox"
            :checked="selectedIds.includes(row.id)"
            @change="toggleSelect(row.id)"
          />
        </template>
        <template #id="{ row }">{{ row.id }}</template>
        <template #title="{ row }">
          <div class="title-cell">
            <span class="title-text">{{ row.title }}</span>
            <span v-if="row.storage_type" class="storage-badge">{{ row.storage_type }}</span>
          </div>
        </template>
        <template #category="{ row }">
          <SfTag v-if="row.category" type="default" size="sm">{{ getCategoryLabel(row.category) }}</SfTag>
          <span v-else class="muted">—</span>
        </template>
        <template #difficulty="{ row }">
          <SfTag :type="getDifficultyType(row.difficulty)" size="sm">
            {{ getDifficultyLabel(row.difficulty) }}
          </SfTag>
        </template>
        <template #duration="{ row }">{{ row.duration ? formatDuration(row.duration) : '—' }}</template>
        <template #view_count="{ row }">{{ row.view_count }}</template>
        <template #is_active="{ row }">
          <div class="status-cell">
            <SfTag :type="row.is_active ? 'success' : 'warning'" size="sm">
              {{ row.is_active ? '已发布' : '待审核' }}
            </SfTag>
            <SfSwitch
              v-model="row.is_active"
              @change="toggleStatus(row)"
              style="margin-left: 8px;"
            />
          </div>
        </template>
        <template #created_at="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
        <template #actions="{ row }">
          <div class="action-cell">
            <SfButton type="ghost" size="sm" @click="openEdit(row)">
              <Pencil :size="13" style="margin-right: 2px;" />编辑
            </SfButton>
            <SfPopconfirm
              title="确定要删除这个语料吗？"
              @confirm="deleteMaterial(row)"
            >
              <SfButton type="danger" size="sm">删除</SfButton>
            </SfPopconfirm>
            <SfDropdown trigger="click" placement="bottom-end">
              <template #trigger>
                <SfButton type="ghost" size="sm" class="more-btn">
                  <MoreHorizontal :size="14" />
                </SfButton>
              </template>
              <div class="sf-menu">
                <div class="menu-item" @click="viewMaterial(row)">
                  <Eye :size="14" /><span>查看</span>
                </div>
                <div class="menu-item" @click="openOssInfo(row)">
                  <Server :size="14" /><span>OSS 信息</span>
                </div>
                <div class="menu-divider"></div>
                <div class="menu-item" @click="doRetranscribe(row)">
                  <FileText :size="14" /><span>重新转字幕</span>
                </div>
                <div class="menu-item" @click="doReinterpret(row)">
                  <Sparkles :size="14" /><span>重新 AI 解读</span>
                </div>
              </div>
            </SfDropdown>
          </div>
        </template>
      </SfTable>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <SfPagination
          :current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          @update:current-page="(p) => loadMaterials(p)"
        />
      </div>
    </div>

    <!-- 编辑 modal -->
    <SfDialog v-model="editModal.show" :title="editModal.title" width="640px">
      <SfForm>
        <SfFormItem label="标题" required>
          <SfInput v-model="editModal.form.title" placeholder="语料标题" />
        </SfFormItem>
        <SfFormItem label="描述">
          <SfInput v-model="editModal.form.description" placeholder="语料描述 (可选)" textarea :rows="3" />
        </SfFormItem>
        <div class="edit-row">
          <SfFormItem label="分类" class="edit-col">
            <SfSelect v-model="editModal.form.category" :options="categoryOptions" placeholder="选择分类" />
          </SfFormItem>
          <SfFormItem label="难度" class="edit-col">
            <SfSelect
              v-model="editModal.form.difficulty"
              :options="difficultyOptions"
              placeholder="难度"
            />
          </SfFormItem>
          <SfFormItem label="时长(秒)" class="edit-col">
            <div class="duration-input-group">
              <SfInput v-model.number="editModal.form.duration" type="number" placeholder="秒" />
              <SfButton
                type="ghost"
                size="sm"
                :loading="probingDuration"
                :disabled="!editModal.form.video_path || probingDuration"
                @click="probeMaterialDuration"
                title="从 OSS 下载视频并用 ffprobe 自动提取时长"
              >
                <RefreshCw :size="14" style="margin-right: 4px;" />
                自动检测
              </SfButton>
            </div>
          </SfFormItem>
        </div>
        <SfFormItem label="状态">
          <div class="edit-status">
            <SfSwitch v-model="editModal.form.is_active" />
            <span class="status-label">{{ editModal.form.is_active ? '已发布' : '待审核' }}</span>
          </div>
        </SfFormItem>
      </SfForm>
      <template #footer>
        <div class="dialog-footer">
          <SfButton @click="editModal.show = false">取消</SfButton>
          <SfButton type="primary" @click="saveEdit" :loading="editModal.saving">保存</SfButton>
        </div>
      </template>
    </SfDialog>

    <!-- OSS 信息 modal -->
    <SfDialog v-model="ossModal.show" title="OSS / 存储信息" width="560px">
      <div class="oss-info" v-if="ossModal.row">
        <div class="oss-row">
          <span class="oss-label">存储类型</span>
          <SfTag :type="ossModal.row.storage_type === 'local' ? 'default' : 'success'" size="sm">
            {{ ossModal.row.storage_type || 'local' }}
          </SfTag>
        </div>
        <div class="oss-row">
          <span class="oss-label">语料 ID</span>
          <code>{{ ossModal.row.id }}</code>
        </div>
        <div class="oss-row">
          <span class="oss-label">视频路径</span>
          <code class="oss-path">{{ ossModal.row.video_path || '—' }}</code>
        </div>
        <div class="oss-row">
          <span class="oss-label">字幕路径</span>
          <code class="oss-path">{{ ossModal.row.subtitle_path || '—' }}</code>
        </div>
        <div class="oss-row">
          <span class="oss-label">封面路径</span>
          <code class="oss-path">{{ ossModal.row.cover_path || '—' }}</code>
        </div>
        <div class="oss-row">
          <span class="oss-label">视频大小</span>
          <span>{{ formatBytes(ossModal.row.video_size) }}</span>
        </div>
        <div class="oss-row">
          <span class="oss-label">时长</span>
          <span>{{ ossModal.row.duration ? formatDuration(ossModal.row.duration) : '—' }}</span>
        </div>
        <div class="oss-row">
          <span class="oss-label">观看次数</span>
          <span>{{ ossModal.row.view_count }}</span>
        </div>
        <div class="oss-row">
          <span class="oss-label">AI 解读</span>
          <SfTag :type="interpretationStatusType(ossModal.row.interpretation_status)" size="sm">
            {{ ossModal.row.interpretation_status || 'pending' }}
          </SfTag>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <SfButton @click="ossModal.show = false">关闭</SfButton>
        </div>
      </template>
    </SfDialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import {
  Download, Plus, Pencil, Eye, EyeOff, MoreHorizontal, Settings, RefreshCw
} from 'lucide-vue-next'
import { adminAPI, materialAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfTable from '@/components/ui/SfTable.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfSwitch from '@/components/ui/SfSwitch.vue'
import SfPopconfirm from '@/components/ui/SfPopconfirm.vue'
import SfDropdown from '@/components/ui/SfDropdown.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import SfDialog from '@/components/ui/SfDialog.vue'

const router = useRouter()

const loading = ref(false)
const exporting = ref(false)
const bulkLoading = ref(false)
const materials = ref([])
const categories = ref([])
const selectedIds = ref([])

// 编辑 modal 状态
const editModal = reactive({
  show: false,
  saving: false,
  probingDuration: false,
  title: '编辑语料',
  form: { id: null, title: '', description: '', category: '', difficulty: 2, duration: null, is_active: true, video_path: null }
})

// OSS 信息 modal 状态
const ossModal = reactive({
  show: false,
  row: null
})

// 表格列定义 — title 列给默认 280px,避免默认被挤窄看不清
// 字段 order 决定列设置 popover 里的顺序
const allColumns = [
  { key: 'select', label: '', width: 40, required: true },
  { key: 'id', label: 'ID', width: 70 },
  { key: 'title', label: '标题', width: 280, minWidth: 160 },
  { key: 'category', label: '分类', width: 100, minWidth: 70 },
  { key: 'difficulty', label: '难度', width: 80, minWidth: 60 },
  { key: 'duration', label: '时长', width: 90, minWidth: 60 },
  { key: 'view_count', label: '观看', width: 80, minWidth: 60 },
  { key: 'is_active', label: '状态', width: 150, minWidth: 110 },
  { key: 'created_at', label: '创建时间', width: 180, minWidth: 120 },
  { key: 'actions', label: '操作', width: 200, minWidth: 160, required: true }
]
// SfTable 用的 columns (px 数字)
const columns = allColumns.map(c => ({ key: c.key, label: c.label, width: c.width + 'px', minWidth: c.minWidth }))

// ==================== 列设置 (用户偏好, localStorage 持久化) ====================
const PREFS_KEY = 'fluenty.admin.materials.tablePrefs.v1'
const columnPickerOpen = ref(false)

const loadPrefs = () => {
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    if (!raw) return { hidden: [], widths: {} }
    const p = JSON.parse(raw)
    return {
      hidden: Array.isArray(p.hidden) ? p.hidden : [],
      widths: p.widths && typeof p.widths === 'object' ? p.widths : {}
    }
  } catch { return { hidden: [], widths: {} } }
}

const initialPrefs = loadPrefs()
const hiddenKeys = ref(initialPrefs.hidden)        // 隐藏的列 key
const colWidths = ref(initialPrefs.widths)         // 用户拖拽后的列宽 (px)

watch([hiddenKeys, colWidths], () => {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify({
      hidden: hiddenKeys.value,
      widths: colWidths.value
    }))
  } catch {}
}, { deep: true })

const toggleColumn = (key) => {
  const i = hiddenKeys.value.indexOf(key)
  if (i >= 0) hiddenKeys.value.splice(i, 1)
  else hiddenKeys.value.push(key)
}

const resetColumnPrefs = () => {
  hiddenKeys.value = []
  colWidths.value = {}
}

const onColumnResize = ({ key, width }) => {
  colWidths.value = { ...colWidths.value, [key]: width }
}

const categoryOptions = computed(() => {
  const opts = categories.value.map(cat => ({ label: cat.name, value: cat.name }))
  return [{ label: '全部分类', value: '' }, ...opts]
})

const difficultyOptions = [
  { label: '1 - 初级', value: 1 },
  { label: '2 - 基础', value: 2 },
  { label: '3 - 中级', value: 3 },
  { label: '4 - 中高级', value: 4 },
  { label: '5 - 高级', value: 5 }
]

const statusOptions = [
  { label: '全部状态', value: null },
  { label: '已发布', value: true },
  { label: '待审核', value: false }
]

// 时长筛选 (秒) — 跟"分类/状态"同样的预设档位
const durationOptions = [
  { label: '全部时长', value: '' },
  { label: '短视频 (< 60s)', value: 'short' },
  { label: '中等 (60-180s)', value: 'medium' },
  { label: '中长 (180-600s)', value: 'long' },
  { label: '长视频 (> 600s)', value: 'extra' }
]

// duration enum → 后端 min_duration / max_duration query params
// 注: max_duration=null 表示无上限 (用于 "长视频 >600s" 档)
function durationToRange(value) {
  switch (value) {
    case 'short':  return { min_duration: 0,   max_duration: 60 }
    case 'medium': return { min_duration: 60,  max_duration: 180 }
    case 'long':   return { min_duration: 180, max_duration: 600 }
    case 'extra':  return { min_duration: 600, max_duration: null }
    default:       return {}
  }
}

const filters = reactive({
  keyword: '',
  category: '',
  is_active: null,
  duration: ''  // 全部时长 / short / medium / long / extra (映射 min/max_duration)
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadMaterials = async (page = null) => {
  if (page) pagination.page = page
  loading.value = true
  try {
    const res = await adminAPI.getMaterials({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters,
      ...durationToRange(filters.duration)  // duration enum → min/max query params
    })
    materials.value = res.items.map(m => ({ ...m, statusLoading: false }))
    pagination.total = res.total
    selectedIds.value = []  // 翻页清空选择
  } catch (e) {
    toast.error('加载语料列表失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    categories.value = await materialAPI.getCategories()
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

const toggleStatus = async (row) => {
  row.statusLoading = true
  try {
    await adminAPI.toggleMaterialStatus(row.id, row.is_active)
    toast.success('状态已更新')
  } catch (e) {
    row.is_active = !row.is_active
    toast.error('更新状态失败')
  } finally {
    row.statusLoading = false
  }
}

const deleteMaterial = async (row) => {
  try {
    await adminAPI.deleteMaterial(row.id, false)
    toast.success('已删除')
    selectedIds.value = selectedIds.value.filter(id => id !== row.id)
    loadMaterials()
  } catch (e) {
    toast.error('删除失败')
  }
}

const viewMaterial = (row) => {
  window.open(`/learn/${row.id}`, '_blank')
}

const goToUpload = () => {
  router.push('/admin/upload')
}

const resetFilters = () => {
  filters.keyword = ''
  filters.category = ''
  filters.is_active = null
  filters.duration = ''
  pagination.page = 1
  loadMaterials()
}

// ============ 选择 / 批量操作 ============

const toggleSelect = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

const clearSelection = () => {
  selectedIds.value = []
}

const batchPublish = () => batchUpdateStatusAction(true)
const batchUnpublish = () => batchUpdateStatusAction(false)

const batchUpdateStatusAction = async (isActive) => {
  if (!selectedIds.value.length) return
  bulkLoading.value = true
  try {
    const res = await adminAPI.batchUpdateStatus(selectedIds.value, isActive)
    toast.success(res.message || '操作完成')
    clearSelection()
    loadMaterials()
  } catch (e) {
    toast.error('操作失败')
  } finally {
    bulkLoading.value = false
  }
}

const batchDelete = async (deleteFiles) => {
  if (!selectedIds.value.length) return
  bulkLoading.value = true
  try {
    const res = await adminAPI.batchDelete(selectedIds.value, deleteFiles)
    toast.success(res.message || '已删除')
    clearSelection()
    loadMaterials()
  } catch (e) {
    toast.error('删除失败')
  } finally {
    bulkLoading.value = false
  }
}

// ============ 编辑 modal ============

const openEdit = (row) => {
  editModal.form = {
    id: row.id,
    title: row.title || '',
    description: row.description || '',
    category: row.category || '',
    difficulty: row.difficulty || 2,
    duration: row.duration || null,
    is_active: !!row.is_active,
    video_path: row.video_path || null   // 给"自动检测时长"按钮用
  }
  editModal.title = `编辑语料 #${row.id}`
  editModal.show = true
}

// 自动检测时长: 从 OSS 下载视频 → 后端 ffprobe → 填 input
const probeMaterialDuration = async () => {
  const vp = editModal.form.video_path
  if (!vp) {
    toast.error('该语料没有视频文件路径,无法探测')
    return
  }
  editModal.probingDuration = true
  try {
    const res = await adminAPI.probeDuration(vp)
    editModal.form.duration = res.duration
    toast.success(`自动检测完成: ${res.duration} 秒`)
  } catch (e) {
    toast.error('自动检测失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    editModal.probingDuration = false
  }
}

const saveEdit = async () => {
  if (!editModal.form.title?.trim()) {
    toast.error('标题必填')
    return
  }
  editModal.saving = true
  try {
    await adminAPI.updateMaterial(editModal.form.id, editModal.form)
    toast.success('已更新')
    editModal.show = false
    loadMaterials()
  } catch (e) {
    toast.error(e?.response?.data?.detail || '更新失败')
  } finally {
    editModal.saving = false
  }
}

// ============ OSS 信息 modal ============

const openOssInfo = (row) => {
  ossModal.row = row
  ossModal.show = true
}

// ============ 重新生成字幕 / 解读 ============

const doRetranscribe = async (row) => {
  if (!confirm(`确定要重新为「${row.title}」生成字幕吗?\n这会从 OSS 下载视频 → whisper 转录 → 替换字幕,过程较慢(几分钟到几十分钟)。`)) return
  try {
    const res = await adminAPI.retranscribe(row.id)
    toast.success(`已启动, task_id: ${res.task_id}`)
  } catch (e) {
    toast.error('启动失败')
  }
}

const doReinterpret = async (row) => {
  if (!confirm(`确定要重新生成「${row.title}」的 AI 解读?\n会清空现有解读并重新生成,过程约 1-2 分钟。`)) return
  try {
    await adminAPI.reinterpret(row.id)
    toast.success('已重新触发 AI 解读')
  } catch (e) {
    toast.error('启动失败')
  }
}

// ============ CSV 导出 ============

const exportCsv = async () => {
  exporting.value = true
  try {
    const params = { ...filters }
    // 过滤掉空值
    Object.keys(params).forEach(k => {
      if (params[k] === '' || params[k] === null || params[k] === undefined) delete params[k]
    })
    const blob = await adminAPI.exportMaterials(params)
    // 从 Content-Disposition 拿文件名
    const disposition = blob.headers?.['content-disposition'] || ''
    const match = disposition.match(/filename="?([^";]+)"?/)
    const filename = match?.[1] || `materials-${Date.now()}.csv`

    const url = URL.createObjectURL(blob.data)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.success(`已导出 ${pagination.total} 个语料`)
  } catch (e) {
    console.error('Export failed:', e)
    toast.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// ============ 工具函数 ============

const getDifficultyLabel = (level) => {
  const labels = { 1: '初级', 2: '基础', 3: '中级', 4: '中高级', 5: '高级' }
  return labels[level] || '未知'
}

const getDifficultyType = (level) => {
  const types = { 1: 'success', 2: 'default', 3: 'warning', 4: 'danger', 5: 'danger' }
  return types[level] || 'default'
}

const getCategoryLabel = (name) => {
  const m = categories.value.find(c => c.name === name)
  return m?.name || name
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

const formatDuration = (sec) => {
  if (!sec) return ''
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}h${m}m`
  if (m > 0) return `${m}m${s}s`
  return `${s}s`
}

const formatBytes = (bytes) => {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  return `${(bytes / 1024 / 1024 / 1024).toFixed(2)} GB`
}

const interpretationStatusType = (s) => {
  const m = { pending: 'warning', generating: 'info', done: 'success', failed: 'danger' }
  return m[s] || 'default'
}

onMounted(() => {
  loadMaterials()
  loadCategories()
})
</script>

<style scoped>
/* ========================================
   MaterialsManage — Phase 3 CSS-only dark admin
   ======================================== */

.materials-manage {
  max-width: 100%;
}

/* ── Page Header ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}
.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.header-sub {
  font-size: 12px;
  color: var(--sf-admin-text-muted, rgba(255,255,255,0.5));
}
.header-actions {
  display: flex;
  gap: 8px;
}

/* ── Duration input + 自动检测按钮 (同一行) ── */
.duration-input-group {
  display: flex;
  gap: 8px;
  align-items: center;
}
.duration-input-group .sf-input {
  flex: 1;
  min-width: 100px;
}

.page-header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--sf-admin-text-primary);
  letter-spacing: -0.3px;
}

/* ── Bulk Toolbar ── */
.bulk-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(96,165,250,0.10), rgba(96,165,250,0.04));
  border: 1px solid rgba(96,165,250,0.25);
  border-radius: 10px;
  padding: 10px 16px;
  margin-bottom: 16px;
  animation: slideDown 0.18s ease;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.bulk-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bulk-count {
  font-size: 13px;
  color: var(--sf-admin-text-secondary);
}
.bulk-count strong {
  color: var(--sf-brand, #60a5fa);
  font-size: 14px;
  margin: 0 2px;
}
.bulk-actions {
  display: flex;
  gap: 8px;
}

/* ── Row Checkbox ── */
.row-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--sf-brand, #60a5fa);
}

/* ── Title Cell ── */
.title-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
  max-width: 380px;
}
.title-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}
.storage-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  background: rgba(96,165,250,0.12);
  color: #60a5fa;
  border-radius: 4px;
  text-transform: uppercase;
  width: fit-content;
}
.muted {
  color: rgba(255,255,255,0.3);
}

/* ── Action Cell (multi buttons) ── */
.action-cell {
  display: flex;
  gap: 6px;
  align-items: center;
}
.more-btn {
  padding: 0 6px !important;
  min-width: 28px;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 13px;
  color: var(--sf-admin-text-primary);
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.12s;
}
.menu-item:hover {
  background: rgba(255,255,255,0.06);
}
.menu-divider {
  height: 1px;
  background: var(--sf-admin-border, rgba(255,255,255,0.08));
  margin: 4px 0;
}

/* ── Dropdown menu (深色底 + 浅色文字) ── */
/* SfDropdown 内部用 var(--color-bg-card) (浅色主题=白),在 admin 跟页面融为一体看不到。
   强制深色底 + 浅色文字 + 浅色 hover,跟 admin 卡片区分。 */
.card-container :deep(.sf-dropdown-menu) {
  background: #1E293B !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
  padding: 4px !important;
}
.card-container :deep(.sf-dropdown-menu .menu-item) {
  color: #F1F5F9 !important;
}
.card-container :deep(.sf-dropdown-menu .menu-item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
}
.card-container :deep(.sf-dropdown-menu .menu-divider) {
  background: rgba(255, 255, 255, 0.08) !important;
}

/* ── Edit Modal ── */
.edit-row {
  display: flex;
  gap: 12px;
}
.edit-col {
  flex: 1;
}
.edit-status {
  display: flex;
  align-items: center;
  gap: 10px;
}
.status-label {
  font-size: 13px;
  color: var(--sf-admin-text-secondary);
}

/* ── Dialog Footer ── */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* ── OSS Info ── */
.oss-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px 4px;
}
.oss-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.oss-row:last-child {
  border-bottom: none;
}
.oss-label {
  font-size: 12px;
  color: var(--sf-admin-text-muted, rgba(255,255,255,0.5));
  font-weight: 500;
}
.oss-path {
  display: block;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 11px;
  color: var(--sf-admin-text-secondary);
  background: rgba(0,0,0,0.2);
  padding: 4px 8px;
  border-radius: 4px;
  word-break: break-all;
  line-height: 1.5;
}

/* ── Filter Card ── */
.filter-card {
  margin-bottom: 24px;
  background: var(--sf-admin-bg-card);
  border-color: var(--sf-admin-border);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

/* ── Table Card ── */
.card-container {
  background: var(--sf-admin-bg-card);
  border-color: var(--sf-admin-border);
}

/* ── Table Overrides (dark admin) ── */
.card-container :deep(.sf-table-wrap) {
  border-color: var(--sf-admin-border);
}

.card-container :deep(.sf-table th) {
  color: var(--sf-admin-text-secondary);
  background: rgba(255, 255, 255, 0.03);
  border-bottom-color: var(--sf-admin-border);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.card-container :deep(.sf-table td) {
  color: var(--sf-admin-text-primary);
  border-bottom-color: rgba(255, 255, 255, 0.04);
  padding: 14px 16px;
}

/* Zebra stripe rows */
.card-container :deep(.sf-table tbody tr:nth-child(even) td) {
  background: rgba(255, 255, 255, 0.02);
}

.card-container :deep(.sf-table tbody tr:hover td) {
  background: rgba(96, 165, 250, 0.08);
}

/* ── Status & Action Cells ── */
.status-cell {
  display: flex;
  align-items: center;
}

.action-cell {
  display: flex;
  gap: 8px;
}

.action-cell :deep(.sf-btn--danger):hover {
  background: var(--sf-danger);
}

/* ── Pagination ── */
.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-header h1 {
    font-size: 19px;
  }

  .filter-card :deep(.sf-form-item) {
    margin-right: 0;
    margin-bottom: 8px;
    width: 100%;
  }

  .filter-card :deep(.sf-input),
  .filter-card :deep(.sf-select) {
    width: 100% !important;
  }

  .filter-row {
    display: block;
  }

  .pagination-wrap {
    justify-content: center;
  }

  /* ── Mobile: table → card list ── */
  .card-container :deep(.sf-table-wrap) {
    border: none;
    background: transparent;
  }

  .card-container :deep(.sf-table) {
    display: block;
  }

  .card-container :deep(.sf-table thead) {
    display: none;
  }

  .card-container :deep(.sf-table tbody) {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .card-container :deep(.sf-table tbody tr) {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 16px;
    background: var(--sf-admin-bg-card);
    border-radius: 12px;
    border: 1px solid var(--sf-admin-border);
    align-items: center;
  }

  .card-container :deep(.sf-table tbody tr:hover td) {
    background: transparent;
  }

  .card-container :deep(.sf-table tbody tr td) {
    border-bottom: none;
    padding: 4px 8px;
    font-size: 13px;
  }

  .card-container :deep(.sf-table tbody tr td:first-child) {
    font-weight: 600;
    color: var(--sf-brand);
    font-size: 12px;
    opacity: 0.7;
  }

  .card-container :deep(.sf-table tbody tr td:nth-child(2)) {
    flex: 1 1 100%;
    font-weight: 600;
    color: var(--sf-admin-text-primary);
    font-size: 15px;
    padding-top: 0;
    padding-left: 8px;
    margin-top: -4px;
  }

  .card-container :deep(.sf-table tbody tr td:last-child) {
    flex: 1 1 100%;
    padding-top: 8px;
    margin-top: 4px;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
  }
}

@media (max-width: 480px) {
  .filter-card {
    padding: 16px;
  }

  .card-container {
    padding: 12px;
  }
}

/* ── 列设置 Popover ── */
.col-picker {
  display: flex;
  flex-direction: column;
  gap: 4px;
  user-select: none;
}
.col-picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 4px 6px 8px;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 4px;
}
.col-picker-reset {
  background: transparent;
  border: none;
  color: var(--color-brand);
  font-size: 12px;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
}
.col-picker-reset:hover {
  background: var(--color-bg-elevated);
}
.col-picker-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 6px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-primary);
}
.col-picker-row:hover {
  background: var(--color-bg-elevated);
}
.col-picker-row-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.col-picker-row input[type="checkbox"] {
  cursor: pointer;
}
.col-picker-row-disabled input[type="checkbox"] {
  cursor: not-allowed;
}
.col-picker-label {
  flex: 1;
}
.col-picker-hint {
  font-size: 11px;
  color: var(--color-text-muted);
  padding: 6px 6px 0;
  border-top: 1px solid var(--color-border);
  margin-top: 4px;
  line-height: 1.4;
}
</style>
