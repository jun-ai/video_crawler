<template>
  <div class="activation-codes-manage">
    <div class="page-header">
      <h2>激活码管理</h2>
      <SfButton type="primary" @click="showGenerateDialog = true">
        <Plus :size="16" style="margin-right: 4px;" /> 生成激活码
      </SfButton>
    </div>

    <!-- 生成对话框 -->
    <SfDialog v-model="showGenerateDialog" title="批量生成激活码" width="440px">
      <SfForm>
        <SfFormItem label="生成数量">
          <SfInput v-model="generateForm.count" type="number" placeholder="1-50" />
        </SfFormItem>
        <SfFormItem label="最大使用次数">
          <SfInput v-model="generateForm.max_uses" type="number" placeholder="1-100" />
        </SfFormItem>
        <SfFormItem label="有效天数">
          <SfInput v-model="generateForm.expires_days" type="number" placeholder="0=永久" />
          <div class="form-tip">设为 0 表示永久有效</div>
        </SfFormItem>
      </SfForm>
      <template #footer>
        <SfButton @click="showGenerateDialog = false">取消</SfButton>
        <SfButton type="primary" @click="handleGenerate" :loading="generating">生成</SfButton>
      </template>
    </SfDialog>

    <!-- 生成结果对话框 -->
    <SfDialog v-model="showResultDialog" title="激活码已生成" width="520px">
      <div class="result-codes">
        <div v-for="code in generatedCodes" :key="code" class="code-item">
          <code class="code-text">{{ code }}</code>
          <SfButton type="ghost" size="sm" @click="copyCode(code)">
            <Copy :size="14" style="margin-right: 4px;" /> 复制
          </SfButton>
        </div>
      </div>
      <template #footer>
        <SfButton @click="copyAllCodes">复制全部</SfButton>
        <SfButton type="primary" @click="showResultDialog = false">完成</SfButton>
      </template>
    </SfDialog>

    <!-- 列表 -->
    <div class="card-container list-card">
      <!-- 7-20: 筛选/搜索条 (放表格上方, 跟工具栏分开) -->
      <div class="filter-bar">
        <div class="status-group">
          <SfButton
            :type="filters.status === 'all' ? 'primary' : 'ghost'"
            size="sm"
            @click="filters.status = 'all'; onFilterChange('status')"
          >全部</SfButton>
          <SfButton
            :type="filters.status === 'unused' ? 'primary' : 'ghost'"
            size="sm"
            @click="filters.status = 'unused'; onFilterChange('status')"
          >未使用</SfButton>
          <SfButton
            :type="filters.status === 'used' ? 'primary' : 'ghost'"
            size="sm"
            @click="filters.status = 'used'; onFilterChange('status')"
          >已使用</SfButton>
        </div>

        <div class="filter-search">
          <SfInput
            v-model="filters.code"
            placeholder="激活码 (模糊搜索)"
            clearable
            :maxlength="32"
            @input="onFilterChange('code')"
          >
            <template #prefix>
              <Search :size="14" />
            </template>
          </SfInput>
          <SfInput
            v-model="filters.phone"
            placeholder="绑定手机号 (模糊搜索)"
            clearable
            :maxlength="11"
            @input="onFilterChange('phone')"
          >
            <template #prefix>
              <Phone :size="14" />
            </template>
          </SfInput>
          <SfButton type="ghost" size="sm" @click="resetFilters">重置</SfButton>
        </div>
      </div>

      <!-- 顶部操作栏: 批量删除 (v-if 有选) + 全部删除未使用 (一直显示) -->
      <div class="list-toolbar">
        <div class="list-toolbar__left">
          <span class="list-toolbar__count">共 {{ pagination.total }} 个激活码</span>
          <span v-if="selectedIds.length > 0" class="list-toolbar__selected">
            已选 <strong>{{ selectedIds.length }}</strong> 个
          </span>
        </div>
        <div class="list-toolbar__right">
          <!-- 全选 checkbox (header) — 在 toolbar 跟表头都能切换 -->
          <label class="select-all-label">
            <input
              type="checkbox"
              :checked="isAllSelected"
              :indeterminate.prop="selectAllState === 1"
              @change="toggleSelectAll"
            />
            <span>全选当前页</span>
          </label>
          <SfButton
            v-if="selectedIds.length > 0"
            type="ghost"
            size="sm"
            @click="clearSelection"
          >
            取消选择
          </SfButton>
          <SfPopconfirm
            v-if="selectedIds.length > 0"
            :title="`确定删除选中的 ${selectedIds.length} 个激活码？`"
            @confirm="batchDeleteSelected"
          >
            <SfButton type="danger" size="sm" :loading="bulkDeleting">
              <Trash2 :size="14" style="margin-right: 4px;" />
              批量删除
            </SfButton>
          </SfPopconfirm>
          <SfPopconfirm
            title="确定删除所有未使用的激活码？已使用的会保留。"
            @confirm="deleteAllUnused"
          >
            <SfButton type="danger" size="sm" :loading="deletingAll">
              <Trash2 :size="14" style="margin-right: 4px;" />
              全部删除未使用
            </SfButton>
          </SfPopconfirm>
        </div>
      </div>
      <SfTable :columns="columns" :data="codes">
        <template #select="{ row }">
          <input
            type="checkbox"
            class="row-checkbox"
            :checked="selectedIds.includes(row.id)"
            @change="toggleSelect(row.id)"
          />
        </template>
        <template #id="{ row }">{{ row.id }}</template>
        <template #code="{ row }">
          <code class="code-cell">{{ row.code }}</code>
        </template>
        <template #used_by_phone="{ row }">
          <span v-if="row.used_by_phone" class="user-binding">
            <span class="user-phone">{{ row.used_by_phone }}</span>
            <span class="user-name">({{ row.used_by_username }})</span>
          </span>
          <span v-else class="user-empty">—</span>
        </template>
        <template #usage="{ row }">
          <div class="usage-info">
            <SfProgress
              :percentage="row.max_uses > 0 ? Math.round(row.use_count / row.max_uses * 100) : 0"
              :stroke-width="6"
              :type="row.use_count >= row.max_uses ? 'danger' : 'brand'"
              :show-text="false"
              style="width: 80px"
            />
            <span class="usage-text">{{ row.use_count }}/{{ row.max_uses }}</span>
          </div>
        </template>
        <template #status="{ row }">
          <SfTag :type="row.is_used ? 'default' : 'success'" size="sm">
            {{ row.is_used ? '已用完' : '可用' }}
          </SfTag>
        </template>
        <template #expires_at="{ row }">
          <span v-if="row.expires_at" class="expire-text">
            {{ formatDate(row.expires_at) }}
          </span>
          <span v-else class="expire-text permanent">永久有效</span>
        </template>
        <template #created_at="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
        <template #actions="{ row }">
          <SfPopconfirm
            title="确定删除此激活码？"
            @confirm="handleDelete(row)"
          >
            <SfButton type="danger" size="sm">删除</SfButton>
          </SfPopconfirm>
        </template>
      </SfTable>

      <div class="pagination-wrap">
        <SfPagination
          :current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          @update:current-page="(p) => { pagination.page = p; loadCodes() }"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { toast } from '@/composables/useToast'
import { Plus, Copy, Trash2, Search, Phone } from 'lucide-vue-next'
import { adminAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfDialog from '@/components/ui/SfDialog.vue'
import SfTable from '@/components/ui/SfTable.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfProgress from '@/components/ui/SfProgress.vue'
import SfPopconfirm from '@/components/ui/SfPopconfirm.vue'
import SfPagination from '@/components/ui/SfPagination.vue'

const loading = ref(false)
const generating = ref(false)
const bulkDeleting = ref(false)
const deletingAll = ref(false)
const codes = ref([])
const generatedCodes = ref([])
const showGenerateDialog = ref(false)
const showResultDialog = ref(false)
const selectedIds = ref([])  // 多选 ids

// 全选 checkbox 状态: 0=未选, 1=部分, 2=全选
const selectAllState = computed(() => {
  if (selectedIds.value.length === 0) return 0
  if (selectedIds.value.length === codes.value.length) return 2
  return 1
})
const isAllSelected = computed(() => selectAllState.value === 2)

function toggleSelect(id) {
  const i = selectedIds.value.indexOf(id)
  if (i >= 0) selectedIds.value.splice(i, 1)
  else selectedIds.value.push(id)
}
function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = codes.value.map(c => c.id)
  }
}
function clearSelection() {
  selectedIds.value = []
}

const columns = [
  { key: 'select', label: '', width: '50px' },
  { key: 'id', label: 'ID', width: '70px' },
  { key: 'code', label: '激活码', width: '140px' },
  { key: 'usage', label: '使用情况', width: '160px' },
  { key: 'used_by_phone', label: '绑定用户', width: '160px' },
  { key: 'status', label: '状态', width: '100px' },
  { key: 'expires_at', label: '有效期', width: '180px' },
  { key: 'created_at', label: '创建时间', width: '180px' },
  { key: 'actions', label: '操作', width: '100px' }
]

const generateForm = reactive({
  count: 5,
  max_uses: 1,
  expires_days: 365  // 默认 1 年 (365 天); 用户填 0 = 永久, 留空 = 后端按 None 处理
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 7-20: 筛选/搜索状态
const filters = reactive({
  status: 'all',    // all | unused | used
  code: '',
  phone: ''
})

let searchTimer = null
const onFilterChange = (key) => {
  // 输入框用 debounce 避免每按一键打一次
  if (key === 'code' || key === 'phone') {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      pagination.page = 1
      loadCodes()
    }, 300)
  } else {
    pagination.page = 1
    loadCodes()
  }
}

const resetFilters = () => {
  filters.status = 'all'
  filters.code = ''
  filters.phone = ''
  pagination.page = 1
  loadCodes()
}

const loadCodes = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getActivationCodes({
      page: pagination.page,
      page_size: pagination.pageSize,
      status: filters.status === 'all' ? undefined : filters.status,
      code: filters.code.trim() || undefined,
      phone: filters.phone.trim() || undefined
    })
    codes.value = res.items || []
    pagination.total = res.total || 0
    clearSelection()  // 翻页/刷新清空选择 (避免跨页选错)
  } catch (e) {
    toast.error('加载激活码列表失败')
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  generating.value = true
  try {
    const res = await adminAPI.generateActivationCodes(generateForm)
    generatedCodes.value = res.codes || []
    showGenerateDialog.value = false
    showResultDialog.value = true
    toast.success(`成功生成 ${res.count} 个激活码`)
    loadCodes()
  } catch (e) {
    toast.error('生成激活码失败')
  } finally {
    generating.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await adminAPI.deleteActivationCode(row.id)
    toast.success('激活码已删除')
    // 删完从 selectedIds 移除
    selectedIds.value = selectedIds.value.filter(id => id !== row.id)
    loadCodes()
  } catch (e) {
    toast.error('删除失败')
  }
}

// 批量删除选中的激活码
const batchDeleteSelected = async () => {
  if (!selectedIds.value.length) return
  bulkDeleting.value = true
  try {
    const res = await adminAPI.batchDeleteActivationCodes([...selectedIds.value])
    toast.success(res.message || `已删除 ${res.deleted_count} 个激活码`)
    clearSelection()
    loadCodes()
  } catch (e) {
    toast.error('批量删除失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    bulkDeleting.value = false
  }
}

// 全部删除"未使用"的激活码 (后端 confirm=true 二次确认, 已用的保留)
const deleteAllUnused = async () => {
  deletingAll.value = true
  try {
    const res = await adminAPI.deleteAllUnusedActivationCodes(true)
    toast.success(res.message || `已删除 ${res.deleted_count} 个未使用的激活码`)
    clearSelection()
    loadCodes()
  } catch (e) {
    toast.error('全部删除失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    deletingAll.value = false
  }
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    toast.success('已复制到剪贴板')
  })
}

const copyAllCodes = () => {
  const text = generatedCodes.value.join('\n')
  navigator.clipboard.writeText(text).then(() => {
    toast.success('已复制全部激活码')
  })
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadCodes()
})
</script>

<style scoped>
/* ====== Phase 3 Admin — ActivationCodesManage (CSS-only dark) ====== */

.activation-codes-manage {
  padding: 0;
  max-width: 100%;
}

/* -- Page Header -- */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--sf-admin-border);
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--sf-admin-text-primary);
  letter-spacing: -0.3px;
}

/* -- Table Card -- */
.list-card {
  background: var(--sf-admin-bg);
  border: 1px solid var(--sf-admin-border);
  border-radius: 16px;
  padding: 4px;
  overflow: hidden;
}

/* 7-20: 筛选条 (放列表卡片顶部, 跟 toolbar 区分) */
.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}
.filter-bar .status-group {
  display: inline-flex;
  gap: 6px;
}
.filter-bar .status-group :deep(.sf-btn) {
  border-radius: 999px;
  padding: 0 14px;
}
.filter-bar .filter-search {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 280px;
  justify-content: flex-end;
}
.filter-bar .filter-search :deep(.sf-input) {
  width: 200px;
}

/* -- Form tip -- */
.form-tip {
  font-size: 12px;
  color: var(--sf-admin-text-muted);
  margin-top: 4px;
}

/* -- Code cell -- */
.code-cell {
  background: rgba(96, 165, 250, 0.12);
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  color: var(--sf-brand);
  letter-spacing: 0.5px;
  border: 1px solid rgba(96, 165, 250, 0.15);
}

/* 7-20: 绑定用户展示 (激活码管理) */
.user-binding {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
}
.user-phone {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: var(--color-text-primary);
}
.user-name {
  font-size: 11px;
  color: var(--color-text-muted, #999);
}
.user-empty {
  color: var(--color-text-muted, #999);
}

/* -- Usage info -- */
.usage-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.usage-text {
  font-size: 13px;
  color: var(--sf-admin-text-secondary);
  font-variant-numeric: tabular-nums;
}

/* -- Expire text -- */
.expire-text {
  font-size: 13px;
  color: var(--sf-admin-text-secondary);
}

.expire-text.permanent {
  color: var(--sf-brand);
  font-weight: 600;
}

/* -- Result dialog codes -- */
.result-codes {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 4px;
}

.result-codes::-webkit-scrollbar {
  width: 4px;
}

.result-codes::-webkit-scrollbar-track {
  background: transparent;
}

.result-codes::-webkit-scrollbar-thumb {
  background: rgba(96, 165, 250, 0.25);
  border-radius: 2px;
}

.code-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--sf-admin-bg-hover);
  border-radius: 10px;
  border: 1px solid #EDF0ED;
  transition: background var(--sf-duration-fast), border-color var(--sf-duration-fast);
}

.code-item:hover {
  background: rgba(96, 165, 250, 0.08);
  border-color: rgba(96, 165, 250, 0.2);
}

.code-text {
  font-size: 15px;
  font-weight: 600;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  color: var(--sf-brand);
  letter-spacing: 1px;
}

/* -- Pagination -- */
.pagination-wrap {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  padding: 0 16px 12px;
}

/* ====== Mobile ====== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  .list-card {
    border-radius: 12px;
    padding: 2px;
  }

  .pagination-wrap {
    justify-content: center;
    padding: 0 8px 8px;
  }
}
</style>
