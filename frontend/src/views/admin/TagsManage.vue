<template>
  <div class="tags-manage">
    <div class="page-header">
      <div class="header-left">
        <h2>标签管理</h2>
        <span class="header-count">共 {{ filteredTags.length }} 个标签</span>
      </div>
      <SfButton type="primary" @click="showCreateDialog = true" class="create-btn">
        <Plus :size="16" style="margin-right: 4px;" /> 新建标签
      </SfButton>
    </div>

    <!-- 标签分类 Tabs -->
    <div class="tabs-bar">
      <SfTabs v-model="activeTab" :tabs="tabOptions" @update:model-value="loadTags" />
    </div>

    <!-- 标签网格 -->
    <div class="tag-grid">
      <div v-for="tag in filteredTags" :key="tag.id" class="tag-card">
        <div class="tag-card-top">
          <div class="tag-color-dot" :style="{ background: tag.color }"></div>
          <div class="tag-card-name">{{ tag.name }}</div>
          <SfTag :type="tag.type === 'creator' ? 'brand' : 'success'" size="sm">
            {{ tag.type === 'creator' ? '博主' : '话题' }}
          </SfTag>
        </div>
        <div class="tag-card-bottom">
          <span class="tag-order-label">排序: {{ tag.display_order }}</span>
          <div class="tag-card-actions">
            <button class="action-btn edit-btn" @click="editTag(tag)" title="编辑">
              <Pencil :size="14" />
            </button>
            <button class="action-btn delete-btn" @click="handleDelete(tag)" title="删除">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
      </div>

      <SfEmpty v-if="!loading && filteredTags.length === 0" description="暂无标签" />
    </div>

    <!-- 创建/编辑对话框 -->
    <SfDialog
      v-model="showCreateDialog"
      :title="editingTag ? '编辑标签' : '新建标签'"
      width="440px"
    >
      <SfForm>
        <SfFormItem label="标签名称">
          <SfInput v-model="tagForm.name" placeholder="输入标签名称" />
        </SfFormItem>
        <SfFormItem label="标签类型">
          <SfSelect v-model="tagForm.type" :options="tagTypeOptions" />
        </SfFormItem>
        <SfFormItem label="标签颜色">
          <div class="color-row">
            <input type="color" v-model="tagForm.color" class="color-picker" />
            <span class="color-preview">{{ tagForm.color }}</span>
          </div>
        </SfFormItem>
        <SfFormItem label="排序权重">
          <SfInput v-model="tagForm.display_order" type="number" placeholder="0-999" />
        </SfFormItem>
      </SfForm>
      <template #footer>
        <SfButton @click="showCreateDialog = false">取消</SfButton>
        <SfButton type="primary" @click="handleSave" :loading="saving">保存</SfButton>
      </template>
    </SfDialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { toast } from '@/composables/useToast'
import { showConfirm } from '@/composables/useConfirm'
import { Plus, Pencil, Trash2 } from 'lucide-vue-next'
import { tagsAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfDialog from '@/components/ui/SfDialog.vue'
import SfTag from '@/components/ui/SfTag.vue'
import SfTabs from '@/components/ui/SfTabs.vue'
import SfEmpty from '@/components/ui/SfEmpty.vue'

const loading = ref(false)
const saving = ref(false)
const tags = ref([])
const activeTab = ref('creator')
const showCreateDialog = ref(false)
const editingTag = ref(null)

const tabOptions = [
  { key: 'creator', label: '博主标签' },
  { key: 'topic', label: '话题标签' }
]

const tagTypeOptions = [
  { label: '博主', value: 'creator' },
  { label: '话题', value: 'topic' }
]

const tagForm = ref({
  name: '',
  type: 'creator',
  color: '#3F8A5B',       /* Phase 0+ 默认品牌色 (替原紫 #5c6ef5) */
  display_order: 0
})

const filteredTags = computed(() =>
  tags.value.filter(t => t.type === activeTab.value)
)

const resetForm = () => {
  tagForm.value = {
    name: '',
    type: activeTab.value,
    color: '#3F8A5B',       /* Phase 0+ 默认品牌色 (替原紫) */
    display_order: 0
  }
  editingTag.value = null
}

const loadTags = async () => {
  loading.value = true
  try {
    const res = await tagsAPI.getList()
    tags.value = res || []
  } catch (e) {
    console.error('加载标签失败', e)
  } finally {
    loading.value = false
  }
}

const editTag = (tag) => {
  editingTag.value = tag
  tagForm.value = {
    name: tag.name,
    type: tag.type,
    color: tag.color,
    display_order: tag.display_order
  }
  showCreateDialog.value = true
}

const handleSave = async () => {
  if (!tagForm.value.name.trim()) {
    toast.warning('请输入标签名称')
    return
  }
  saving.value = true
  try {
    if (editingTag.value) {
      await tagsAPI.update(editingTag.value.id, tagForm.value)
      toast.success('标签已更新')
    } else {
      await tagsAPI.create(tagForm.value)
      toast.success('标签已创建')
    }
    showCreateDialog.value = false
    resetForm()
    await loadTags()
  } catch (e) {
    console.error('保存标签失败', e)
  } finally {
    saving.value = false
  }
}

const handleDelete = async (tag) => {
  const confirmed = await showConfirm({ title: '提示', message: `确定删除标签「${tag.name}」？` })
  if (confirmed) {
    try {
      await tagsAPI.delete(tag.id)
      toast.success('标签已删除')
      await loadTags()
    } catch (e) {
      console.error('删除标签失败', e)
    }
  }
}

// Watch dialog open to reset form
watch(showCreateDialog, (val) => {
  if (val && !editingTag.value) {
    resetForm()
  }
})

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
/* ====== 页面容器 ====== */
.tags-manage {
  padding: 0;
}

/* ====== 页头 ====== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.header-count {
  font-size: 12px;
  color: var(--color-text-muted);
}

.create-btn {
  border-radius: 10px;
}

/* ====== Tabs ====== */
.tabs-bar {
  margin-bottom: 20px;
}

/* ====== 标签网格 ====== */
.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

/* ====== 标签卡片 ====== */
.tag-card {
  background: var(--sf-admin-sidebar-bg);
  border: 1px solid var(--sf-admin-sidebar-border);
  border-radius: var(--radius-md, 12px);
  padding: 16px 18px;
  transition: all 0.2s;
  position: relative;
}

.tag-card:hover {
  border-color: var(--sf-admin-accent);
  background: var(--sf-admin-sidebar-active);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.tag-card-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.tag-color-dot {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  flex-shrink: 0;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.06);
}

.tag-card-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text-primary);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-order-label {
  font-size: 11px;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

/* ====== 操作按钮（hover 显现） ====== */
.tag-card-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}

.tag-card:hover .tag-card-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid var(--sf-admin-sidebar-border);
  background: var(--sf-admin-sidebar-active);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.edit-btn:hover {
  color: var(--sf-admin-accent);
  border-color: var(--sf-admin-accent);
  background: var(--sf-admin-accent-light);
}

.delete-btn:hover {
  color: #E07870;
  border-color: rgba(199, 62, 58, 0.4);
  background: rgba(199, 62, 58, 0.12);
}

/* ====== 对话框内颜色选择 ====== */
.color-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-picker {
  width: 40px;
  height: 40px;
  border: 2px solid var(--sf-admin-sidebar-border);
  border-radius: 10px;
  cursor: pointer;
  padding: 0;
  background: none;
}

.color-preview {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .page-header h2 {
    font-size: 18px;
  }

  .tag-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 10px;
  }

  .tag-card {
    padding: 14px;
  }

  /* 移动端始终显示操作按钮 */
  .tag-card-actions {
    opacity: 1;
  }

  .action-btn {
    min-width: 36px;
    min-height: 36px;
  }
}

@media (max-width: 480px) {
  .tag-grid {
    grid-template-columns: 1fr;
  }

  .tag-card-name {
    font-size: 13px;
  }
}
</style>
