<template>
  <div class="material-upload">
    <div class="page-header">
      <h1>上传语料</h1>
      <SfButton @click="goBack">返回列表</SfButton>
    </div>

    <div class="card-container">
      <SfForm>
        <SfFormItem label="标题" required>
          <SfInput v-model="form.title" placeholder="请输入语料标题" />
        </SfFormItem>

        <SfFormItem label="描述">
          <SfInput v-model="form.description" placeholder="请输入语料描述" textarea />
        </SfFormItem>

        <SfFormItem label="分类" required>
          <SfSelect v-model="form.category" :options="categoryOptions" placeholder="请选择分类" />
        </SfFormItem>

        <SfFormItem label="难度">
          <div class="star-rating">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              class="star-btn"
              :class="{ active: star <= form.difficulty }"
              @click="form.difficulty = star"
            >
              <Star :size="20" :fill="star <= form.difficulty ? 'currentColor' : 'none'" />
            </button>
            <span class="star-label">{{ form.difficulty }} / 5</span>
          </div>
        </SfFormItem>

        <SfFormItem label="视频文件" required>
          <div class="upload-area">
            <input type="file" ref="videoInput" accept=".mp4,.webm,.mov" @change="handleVideoChange" class="file-input" />
            <SfButton type="primary" size="sm" @click="$refs.videoInput.click()">选择视频</SfButton>
            <span v-if="files.video" class="file-name">{{ files.video.name }}</span>
            <span v-else class="file-tip">支持 MP4, WebM, MOV 格式</span>
          </div>
        </SfFormItem>

        <SfFormItem label="字幕文件" required>
          <div class="upload-area">
            <input type="file" ref="subtitleInput" accept=".srt,.vtt" @change="handleSubtitleChange" class="file-input" />
            <SfButton type="primary" size="sm" @click="$refs.subtitleInput.click()">选择字幕</SfButton>
            <span v-if="files.subtitle" class="file-name">{{ files.subtitle.name }}</span>
            <span v-else class="file-tip">支持 SRT, VTT 格式</span>
          </div>
        </SfFormItem>

        <SfFormItem label="封面图片" required>
          <div class="upload-area">
            <input type="file" ref="coverInput" accept=".jpg,.jpeg,.png" @change="handleCoverChange" class="file-input" />
            <SfButton type="primary" size="sm" @click="$refs.coverInput.click()">选择封面</SfButton>
            <span v-if="files.cover" class="file-name">{{ files.cover.name }}</span>
            <span v-else class="file-tip">支持 JPG, PNG 格式</span>
          </div>
        </SfFormItem>

        <SfFormItem>
          <div class="form-actions">
            <SfButton type="primary" @click="submitForm" :loading="uploading">
              {{ uploading ? '上传中...' : '提交' }}
            </SfButton>
            <SfButton @click="resetForm">重置</SfButton>
          </div>
        </SfFormItem>
      </SfForm>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="card-container progress-card">
      <div class="progress-title">上传进度</div>
      <SfProgress :percentage="uploadProgress" :type="uploadStatus === 'success' ? 'success' : uploadStatus === 'exception' ? 'danger' : 'brand'" />
      <div class="progress-text">{{ uploadText }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from '@/composables/useToast'
import { Star } from 'lucide-vue-next'
import { materialAPI } from '@/api'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfForm from '@/components/ui/SfForm.vue'
import SfFormItem from '@/components/ui/SfFormItem.vue'
import SfProgress from '@/components/ui/SfProgress.vue'

const router = useRouter()
const videoInput = ref(null)
const subtitleInput = ref(null)
const coverInput = ref(null)

const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const uploadText = ref('')

const form = reactive({
  title: '',
  description: '',
  category: '',
  difficulty: 2
})

const categoryOptions = [
  { label: '旅行', value: 'travel' },
  { label: '购物', value: 'shopping' },
  { label: '社交', value: 'social' },
  { label: '工作', value: 'work' },
  { label: '日常', value: 'daily' },
  { label: '餐饮', value: 'food' }
]

const files = reactive({
  video: null,
  subtitle: null,
  cover: null
})

const handleVideoChange = (e) => {
  files.video = e.target.files[0] || null
}

const handleSubtitleChange = (e) => {
  files.subtitle = e.target.files[0] || null
}

const handleCoverChange = (e) => {
  files.cover = e.target.files[0] || null
}

const submitForm = async () => {
  if (!form.title) {
    toast.error('请输入标题')
    return
  }
  if (!form.category) {
    toast.error('请选择分类')
    return
  }
  if (!files.video) {
    toast.error('请选择视频文件')
    return
  }
  if (!files.subtitle) {
    toast.error('请选择字幕文件')
    return
  }
  if (!files.cover) {
    toast.error('请选择封面图片')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = ''
  uploadText.value = '准备上传...'

  try {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('description', form.description || '')
    formData.append('category', form.category)
    formData.append('difficulty', form.difficulty)
    formData.append('video', files.video)
    formData.append('subtitle', files.subtitle)
    formData.append('cover', files.cover)

    uploadProgress.value = 30
    uploadText.value = '正在上传文件到云存储...'

    await materialAPI.create(formData)

    uploadProgress.value = 100
    uploadStatus.value = 'success'
    uploadText.value = '上传成功！'

    toast.success('语料上传成功')
    setTimeout(() => {
      router.push('/admin/materials')
    }, 1500)
  } catch (e) {
    uploadStatus.value = 'exception'
    uploadText.value = '上传失败: ' + (e.response?.data?.detail || e.message)
    toast.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const resetForm = () => {
  form.title = ''
  form.description = ''
  form.category = ''
  form.difficulty = 2
  files.video = null
  files.subtitle = null
  files.cover = null
  if (videoInput.value) videoInput.value.value = ''
  if (subtitleInput.value) subtitleInput.value.value = ''
  if (coverInput.value) coverInput.value.value = ''
}

const goBack = () => {
  router.push('/admin/materials')
}
</script>

<style scoped>
.material-upload {
  max-width: 800px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.progress-card {
  margin-top: 24px;
}

.progress-title {
  font-weight: 500;
  margin-bottom: 16px;
}

.progress-text {
  margin-top: 8px;
  color: #909399;
  font-size: 14px;
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
  color: var(--color-text-muted);
  padding: 2px;
  transition: color 0.15s;
}

.star-btn.active {
  color: var(--color-warning);
}

.star-label {
  margin-left: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-input {
  display: none;
}

.file-name {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.file-tip {
  font-size: 13px;
  color: var(--color-text-muted);
}

.form-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 20px;
  }

  .upload-area {
    flex-wrap: wrap;
  }
}
</style>
