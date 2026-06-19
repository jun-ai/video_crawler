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
      <SfTable :columns="columns" :data="codes">
        <template #id="{ row }">{{ row.id }}</template>
        <template #code="{ row }">
          <code class="code-cell">{{ row.code }}</code>
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
import { ref, reactive, onMounted } from 'vue'
import { toast } from '@/composables/useToast'
import { Plus, Copy } from 'lucide-vue-next'
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
const codes = ref([])
const generatedCodes = ref([])
const showGenerateDialog = ref(false)
const showResultDialog = ref(false)

const columns = [
  { key: 'id', label: 'ID', width: '70px' },
  { key: 'code', label: '激活码', width: '140px' },
  { key: 'usage', label: '使用情况', width: '160px' },
  { key: 'status', label: '状态', width: '100px' },
  { key: 'expires_at', label: '有效期', width: '180px' },
  { key: 'created_at', label: '创建时间', width: '180px' },
  { key: 'actions', label: '操作', width: '100px' }
]

const generateForm = reactive({
  count: 5,
  max_uses: 1,
  expires_days: 30
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadCodes = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getActivationCodes({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    codes.value = res.items || []
    pagination.total = res.total || 0
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
    loadCodes()
  } catch (e) {
    toast.error('删除失败')
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
  max-width: 1200px;
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
  background: #F8FAF8;
  border: 1px solid var(--sf-admin-border);
  border-radius: 16px;
  padding: 4px;
  overflow: hidden;
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
  color: #2563EB;
  letter-spacing: 0.5px;
  border: 1px solid rgba(96, 165, 250, 0.15);
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
  color: #2563EB;
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
  color: #2563EB;
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
