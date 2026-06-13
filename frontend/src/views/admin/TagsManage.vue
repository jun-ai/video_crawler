<template>
  <div class="tags-manage">
    <div class="page-header">
      <h2>标签管理</h2>
      <SfButton type="primary" @click="showCreateDialog = true">
        <Plus :size="16" style="margin-right: 4px;" /> 新建标签
      </SfButton>
    </div>

    <!-- 标签分类 Tabs -->
    <SfTabs v-model="activeTab" :tabs="tabOptions" @update:model-value="loadTags" />

    <!-- 标签列表 -->
    <div class="tag-list">
      <div v-for="tag in filteredTags" :key="tag.id" class="tag-item">
        <div class="tag-info">
          <span class="tag-color" :style="{ background: tag.color }"></span>
          <span class="tag-name">{{ tag.name }}</span>
          <SfTag :type="tag.type === 'creator' ? 'brand' : 'success'" size="sm">
            {{ tag.type === 'creator' ? '博主' : '话题' }}
          </SfTag>
          <span class="tag-order">排序: {{ tag.display_order }}</span>
        </div>
        <div class="tag-actions">
          <SfButton type="ghost" size="sm" @click="editTag(tag)">
            <Pencil :size="14" />
          </SfButton>
          <SfButton type="danger" size="sm" @click="handleDelete(tag)">
            <Trash2 :size="14" />
          </SfButton>
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
  color: '#5c6ef5',
  display_order: 0
})

const filteredTags = computed(() =>
  tags.value.filter(t => t.type === activeTab.value)
)

const resetForm = () => {
  tagForm.value = {
    name: '',
    type: activeTab.value,
    color: '#5c6ef5',
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
.tags-manage {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  color: var(--color-text-primary);
}

.tag-list {
  margin-top: 16px;
}

.tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid var(--sf-admin-sidebar-border);
  border-radius: 8px;
  margin-bottom: 8px;
  background: var(--sf-admin-sidebar-bg);
  transition: box-shadow 0.2s;
}

.tag-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.tag-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tag-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  flex-shrink: 0;
}

.tag-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text-primary);
}

.tag-order {
  font-size: 12px;
  color: var(--color-text-muted);
}

.tag-actions {
  display: flex;
  gap: 4px;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-picker {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  background: none;
}

.color-preview {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-family: monospace;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .tag-item {
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 12px;
  }

  .tag-info {
    flex-wrap: wrap;
    gap: 6px;
  }

  .tag-order {
    display: none;
  }

  .tag-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .tag-actions .sf-button {
    min-width: 36px;
    min-height: 36px;
  }
}

@media (max-width: 480px) {
  .tags-manage {
    padding: 0;
  }

  .tag-name {
    font-size: 13px;
  }
}
</style>
