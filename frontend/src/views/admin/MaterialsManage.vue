<template>
  <div class="materials-manage">
    <div class="page-header">
      <h1>语料管理</h1>
      <SfButton type="primary" @click="goToUpload">
        <Plus :size="16" style="margin-right: 4px;" />
        上传语料
      </SfButton>
    </div>

    <!-- 筛选条件 -->
    <div class="card-container filter-card">
      <SfForm>
        <div class="filter-row">
          <SfFormItem label="关键词">
            <SfInput v-model="filters.keyword" placeholder="搜索标题" @keyup.enter="loadMaterials" />
          </SfFormItem>
          <SfFormItem label="分类">
            <SfSelect v-model="filters.category" :options="categoryOptions" placeholder="全部分类" />
          </SfFormItem>
          <SfFormItem label="状态">
            <SfSelect v-model="filters.is_active" :options="statusOptions" placeholder="全部状态" />
          </SfFormItem>
          <SfFormItem>
            <div class="filter-actions">
              <SfButton type="primary" @click="loadMaterials">搜索</SfButton>
              <SfButton @click="resetFilters">重置</SfButton>
            </div>
          </SfFormItem>
        </div>
      </SfForm>
    </div>

    <!-- 语料列表 -->
    <div class="card-container">
      <SfTable :columns="columns" :data="materials">
        <template #id="{ row }">{{ row.id }}</template>
        <template #title="{ row }">{{ row.title }}</template>
        <template #category="{ row }">{{ row.category }}</template>
        <template #difficulty="{ row }">
          <SfTag :type="getDifficultyType(row.difficulty)" size="sm">
            {{ getDifficultyLabel(row.difficulty) }}
          </SfTag>
        </template>
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
            <SfButton type="ghost" size="sm" @click="viewMaterial(row)">
              查看
            </SfButton>
            <SfPopconfirm
              title="确定要删除这个语料吗？"
              @confirm="deleteMaterial(row)"
            >
              <SfButton type="danger" size="sm">删除</SfButton>
            </SfPopconfirm>
          </div>
        </template>
      </SfTable>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <SfPagination
          :current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          @update:current-page="(p) => { pagination.page = p; loadMaterials() }"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { Plus } from 'lucide-vue-next'
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
import SfPagination from '@/components/ui/SfPagination.vue'

const router = useRouter()

const loading = ref(false)
const materials = ref([])
const categories = ref([])

const columns = [
  { key: 'id', label: 'ID', width: '80px' },
  { key: 'title', label: '标题' },
  { key: 'category', label: '分类', width: '100px' },
  { key: 'difficulty', label: '难度', width: '80px' },
  { key: 'view_count', label: '观看次数', width: '100px' },
  { key: 'is_active', label: '状态', width: '120px' },
  { key: 'created_at', label: '创建时间', width: '180px' },
  { key: 'actions', label: '操作', width: '150px' }
]

const categoryOptions = computed(() => {
  const opts = categories.value.map(cat => ({ label: cat.name, value: cat.name }))
  return opts
})

const statusOptions = [
  { label: '已激活', value: true },
  { label: '未激活', value: false }
]

const filters = reactive({
  keyword: '',
  category: '',
  is_active: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadMaterials = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getMaterials({
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    })
    materials.value = res.items.map(m => ({ ...m, statusLoading: false }))
    pagination.total = res.total
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
    await adminAPI.deleteMaterial(row.id, true)
    toast.success('删除成功')
    loadMaterials()
  } catch (e) {
    toast.error('删除失败')
  }
}

const viewMaterial = (row) => {
  router.push(`/learn/${row.id}`)
}

const goToUpload = () => {
  router.push('/admin/upload')
}

const resetFilters = () => {
  filters.keyword = ''
  filters.category = ''
  filters.is_active = null
  pagination.page = 1
  loadMaterials()
}

const getDifficultyLabel = (level) => {
  const labels = { 1: '初级', 2: '基础', 3: '中级', 4: '中高级', 5: '高级' }
  return labels[level] || '未知'
}

const getDifficultyType = (level) => {
  const types = { 1: 'success', 2: 'default', 3: 'warning', 4: 'danger', 5: 'danger' }
  return types[level] || 'default'
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
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
  max-width: 1400px;
}

/* ── Page Header ── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #E2E8E2;
  letter-spacing: -0.3px;
}

/* ── Filter Card ── */
.filter-card {
  margin-bottom: 24px;
  background: #0F1A14;
  border-color: rgba(255, 255, 255, 0.06);
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
  background: #0F1A14;
  border-color: rgba(255, 255, 255, 0.06);
}

/* ── Table Overrides (dark admin) ── */
.card-container :deep(.sf-table-wrap) {
  border-color: rgba(255, 255, 255, 0.06);
}

.card-container :deep(.sf-table th) {
  color: #94A398;
  background: rgba(255, 255, 255, 0.03);
  border-bottom-color: rgba(255, 255, 255, 0.06);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.card-container :deep(.sf-table td) {
  color: #C8D6CC;
  border-bottom-color: rgba(255, 255, 255, 0.04);
  padding: 14px 16px;
}

/* Zebra stripe rows */
.card-container :deep(.sf-table tbody tr:nth-child(even) td) {
  background: rgba(255, 255, 255, 0.02);
}

.card-container :deep(.sf-table tbody tr:hover td) {
  background: rgba(111, 163, 134, 0.08);
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
  background: #C73E3A;
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
    background: #0F1A14;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
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
    color: #6FA386;
    font-size: 12px;
    opacity: 0.7;
  }

  .card-container :deep(.sf-table tbody tr td:nth-child(2)) {
    flex: 1 1 100%;
    font-weight: 600;
    color: #E2E8E2;
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
</style>
