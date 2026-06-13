<template>
  <div class="announcements-manage">
    <div class="page-header">
      <h2>公告管理</h2>
      <SfButton type="primary" @click="openCreateDialog">
        <Plus :size="16" style="margin-right: 4px;" /> 发布公告
      </SfButton>
    </div>

    <!-- 公告列表 -->
    <div class="announcement-list">
      <div v-for="item in announcements" :key="item.id" class="announcement-card">
        <div class="announcement-header">
          <div class="announcement-meta">
            <SfTag :type="getTypeTagColor(item.type)" size="sm">
              {{ getTypeLabel(item.type) }}
            </SfTag>
            <span v-if="item.priority >= 2" class="priority-badge urgent">紧急</span>
            <span v-else-if="item.priority >= 1" class="priority-badge important">重要</span>
            <span class="announcement-title">{{ item.title }}</span>
          </div>
          <div class="announcement-actions">
            <SfSwitch
              :model-value="item.is_active"
              @change="toggleActive(item)"
              style="margin-right: 8px;"
            />
            <SfButton type="ghost" size="sm" @click="openEditDialog(item)">
              <Pencil :size="14" />
            </SfButton>
            <SfPopconfirm
              title="确定删除此公告？"
              @confirm="handleDelete(item)"
            >
              <SfButton type="danger" size="sm">
                <Trash2 :size="14" />
              </SfButton>
            </SfPopconfirm>
          </div>
        </div>
        <div class="announcement-content">{{ item.content }}</div>
        <div class="announcement-footer">
          <span class="announcement-time">{{ formatDate(item.created_at) }}</span>
        </div>
      </div>

      <SfEmpty v-if="!loading && announcements.length === 0" description="暂无公告" />
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="pagination.total > pagination.pageSize">
      <SfPagination
        :current-page="pagination.page"
        :page-size="pagination.pageSize"
        :total="pagination.total"
        @update:current-page="(p) => { pagination.page = p; loadAnnouncements() }"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <SfDialog
      v-model="showDialog"
      :title="editingItem ? '编辑公告' : '发布公告'"
      width="560px"
    >
      <SfForm>
        <SfFormItem label="标题" required>
          <SfInput v-model="form.title" placeholder="请输入公告标题" />
        </SfFormItem>
        <SfFormItem label="内容" required>
          <SfInput v-model="form.content" placeholder="请输入公告内容" textarea />
        </SfFormItem>
        <SfFormItem label="类型">
          <div class="radio-group">
            <button
              v-for="opt in typeOptions"
              :key="opt.value"
              type="button"
              :class="['radio-btn', { active: form.type === opt.value }]"
              @click="form.type = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </SfFormItem>
        <SfFormItem label="优先级">
          <div class="priority-selector">
            <div class="priority-slider">
              <input
                type="range"
                :min="0"
                :max="2"
                :step="1"
                v-model.number="form.priority"
                class="slider-input"
              />
              <div class="priority-labels">
                <span :class="{ active: form.priority === 0 }">普通</span>
                <span :class="{ active: form.priority === 1 }">重要</span>
                <span :class="{ active: form.priority === 2 }">紧急</span>
              </div>
            </div>
          </div>
        </SfFormItem>
        <SfFormItem label="发布状态">
          <SfSwitch v-model="form.is_active" />
        </SfFormItem>
      </SfForm>
      <template #footer>
        <SfButton @click="showDialog = false">取消</SfButton>
        <SfButton type="primary" @click="handleSave" :loading="saving">保存</SfButton>
      </template>
    </SfDialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { toast } from '@/composables/useToast'
import { Plus, Pencil, Trash2 } from 'lucide-vue-next'
import { adminAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfDialog from '@/components/ui/SfDialog.vue'
import SfSwitch from '@/components/ui/SfSwitch.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfPopconfirm from '@/components/ui/SfPopconfirm.vue'
import SfPagination from '@/components/ui/SfPagination.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'

const loading = ref(false)
const saving = ref(false)
const announcements = ref([])
const showDialog = ref(false)
const editingItem = ref(null)

const form = reactive({
  title: '',
  content: '',
  type: 'info',
  priority: 0,
  is_active: true
})

const typeOptions = [
  { label: '通知', value: 'info' },
  { label: '更新', value: 'update' },
  { label: '提醒', value: 'warning' },
  { label: '活动', value: 'success' }
]

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadAnnouncements = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getAnnouncements({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    announcements.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    toast.error('加载公告失败')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  editingItem.value = null
  Object.assign(form, {
    title: '',
    content: '',
    type: 'info',
    priority: 0,
    is_active: true
  })
  showDialog.value = true
}

const openEditDialog = (item) => {
  editingItem.value = item
  Object.assign(form, {
    title: item.title,
    content: item.content,
    type: item.type,
    priority: item.priority,
    is_active: item.is_active
  })
  showDialog.value = true
}

const handleSave = async () => {
  if (!form.title) {
    toast.error('请输入标题')
    return
  }
  if (!form.content) {
    toast.error('请输入内容')
    return
  }
  saving.value = true
  try {
    if (editingItem.value) {
      await adminAPI.updateAnnouncement(editingItem.value.id, form)
      toast.success('公告已更新')
    } else {
      await adminAPI.createAnnouncement(form)
      toast.success('公告已发布')
    }
    showDialog.value = false
    loadAnnouncements()
  } catch (e) {
    toast.error('保存失败')
  } finally {
    saving.value = false
  }
}

const toggleActive = async (item) => {
  try {
    await adminAPI.updateAnnouncement(item.id, { is_active: !item.is_active })
    item.is_active = !item.is_active
    toast.success(item.is_active ? '公告已显示' : '公告已隐藏')
  } catch (e) {
    toast.error('操作失败')
  }
}

const handleDelete = async (item) => {
  try {
    await adminAPI.deleteAnnouncement(item.id)
    toast.success('公告已删除')
    loadAnnouncements()
  } catch (e) {
    toast.error('删除失败')
  }
}

const getTypeLabel = (type) => {
  const map = { info: '通知', update: '更新', warning: '提醒', success: '活动' }
  return map[type] || '通知'
}

const getTypeTagColor = (type) => {
  const map = { info: 'default', update: 'brand', warning: 'warning', success: 'success' }
  return map[type] || 'default'
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadAnnouncements()
})
</script>

<style scoped>
/* ====== Phase 3 Admin — AnnouncementsManage (CSS-only dark) ====== */

.announcements-manage {
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
  border-bottom: 1px solid #E5E9E5;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1A2820;
  letter-spacing: -0.3px;
}

/* -- Announcement List -- */
.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* -- Card -- */
.announcement-card {
  background: #F8FAF8;
  border-radius: 14px;
  padding: 18px 22px;
  border: 1px solid #E5E9E5;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.announcement-card:hover {
  background: #F0F4F1;
  border-color: rgba(111, 163, 134, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* -- Card Header -- */
.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.announcement-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.announcement-title {
  font-weight: 600;
  font-size: 15px;
  color: #1A2820;
}

/* -- Priority Badge -- */
.priority-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.priority-badge.urgent {
  background: rgba(199, 62, 58, 0.15);
  color: #E8827A;
  border: 1px solid rgba(199, 62, 58, 0.25);
}

.priority-badge.important {
  background: rgba(226, 114, 91, 0.15);
  color: #F08A72;
  border: 1px solid rgba(226, 114, 91, 0.25);
}

/* -- Actions -- */
.announcement-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

/* -- Content -- */
.announcement-content {
  font-size: 14px;
  color: #5A6B62;
  line-height: 1.65;
  margin-bottom: 12px;
  white-space: pre-wrap;
}

/* -- Footer -- */
.announcement-footer {
  display: flex;
  justify-content: flex-end;
}

.announcement-time {
  font-size: 12px;
  color: #8A9A90;
  font-variant-numeric: tabular-nums;
}

/* -- Pagination -- */
.pagination-wrap {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* -- Radio Group (type selector in dialog) -- */
.radio-group {
  display: flex;
  gap: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  background: #F8FAF8;
}

.radio-btn {
  padding: 8px 18px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: #5A6B62;
  transition: all 0.15s;
  border-right: 1px solid #E5E9E5;
  font-weight: 500;
}

.radio-btn:last-child {
  border-right: none;
}

.radio-btn:hover {
  background: rgba(111, 163, 134, 0.08);
  color: #C5D9CC;
}

.radio-btn.active {
  background: #0F4C3A;
  color: #fff;
}

/* -- Priority Slider -- */
.priority-selector {
  max-width: 300px;
}

.slider-input {
  width: 100%;
  appearance: none;
  height: 6px;
  background: #F5F7F5;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.slider-input::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #0F4C3A;
  cursor: pointer;
  border: 2px solid #0F4C3A;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.3);
}

.slider-input::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #0F4C3A;
  cursor: pointer;
  border: 2px solid #0F4C3A;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.3);
}

.priority-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 12px;
  color: #8A9A90;
}

.priority-labels span.active {
  color: #0F4C3A;
  font-weight: 600;
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

  .pagination-wrap {
    justify-content: center;
  }

  .announcement-list {
    gap: 10px;
  }

  .announcement-card {
    padding: 14px 16px;
    border-radius: 12px;
  }

  .announcement-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .announcement-title {
    font-size: 15px;
  }

  .announcement-content {
    font-size: 13px;
  }

  .radio-group {
    flex-wrap: wrap;
  }

  .radio-btn {
    padding: 7px 14px;
    font-size: 12px;
  }
}
</style>
