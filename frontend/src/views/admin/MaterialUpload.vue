<template>
  <div class="material-upload">
    <div class="page-header">
      <div class="header-left">
        <h1>上传语料</h1>
        <span class="header-desc">添加新的学习视频素材 · 也可以 <a href="/admin/upload/fetch-url" class="link">通过 URL 抓取</a></span>
      </div>
      <SfButton @click="goBack" class="back-btn">返回列表</SfButton>
    </div>

    <!-- 表单区域 -->
    <div class="form-card">
      <div class="form-grid">
        <!-- 左列：基本信息 -->
        <div class="form-col">
          <div class="section-label">基本信息</div>
          <SfForm>
            <SfFormItem label="标题" required>
              <SfInput v-model="form.title" placeholder="请输入语料标题" />
            </SfFormItem>

            <SfFormItem label="描述">
              <SfInput v-model="form.description" placeholder="请输入语料描述" textarea />
            </SfFormItem>

            <div class="form-row">
              <SfFormItem label="分类" required class="form-row-item">
                <SfSelect v-model="form.category" :options="categoryOptions" placeholder="请选择分类" />
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
          </SfForm>
        </div>

        <!-- 右列：文件上传 -->
        <div class="form-col">
          <div class="section-label">文件上传</div>

          <!-- 视频文件 -->
          <div
            class="drop-zone"
            :class="{ 'has-file': files.video, 'is-dragging': dragging.video }"
            @click="$refs.videoInput.click()"
            @dragover.prevent="dragging.video = true"
            @dragenter.prevent="dragging.video = true"
            @dragleave.prevent="dragging.video = false"
            @drop.prevent="handleDrop($event, 'video')"
          >
            <input type="file" ref="videoInput" accept=".mp4,.webm,.mov,.mkv,.m4v" @change="handleVideoChange" class="file-input" />
            <div class="drop-zone-content">
              <svg class="drop-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              <div v-if="files.video" class="drop-file-name">{{ files.video.name }}</div>
              <template v-else>
                <div class="drop-title">拖拽或点击上传视频</div>
                <div class="drop-hint">MP4, WebM, MOV, MKV, M4V</div>
              </template>
            </div>
            <div class="drop-zone-tag">视频文件 *</div>
          </div>

          <!-- 字幕 + 封面 -->
          <div class="upload-row">
            <div
              class="drop-zone drop-zone-sm"
              :class="{ 'has-file': files.subtitle, 'is-dragging': dragging.subtitle }"
              @click="$refs.subtitleInput.click()"
              @dragover.prevent="dragging.subtitle = true"
              @dragenter.prevent="dragging.subtitle = true"
              @dragleave.prevent="dragging.subtitle = false"
              @drop.prevent="handleDrop($event, 'subtitle')"
            >
              <input type="file" ref="subtitleInput" accept=".srt,.vtt" @change="handleSubtitleChange" class="file-input" />
              <div class="drop-zone-content">
                <svg class="drop-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                <div v-if="files.subtitle" class="drop-file-name-sm">{{ files.subtitle.name }}</div>
                <template v-else>
                  <div class="drop-title-sm">拖拽字幕</div>
                  <div class="drop-hint-sm">SRT / VTT</div>
                </template>
              </div>
            </div>
            <div
              class="drop-zone drop-zone-sm"
              :class="{ 'has-file': files.cover, 'is-dragging': dragging.cover }"
              @click="$refs.coverInput.click()"
              @dragover.prevent="dragging.cover = true"
              @dragenter.prevent="dragging.cover = true"
              @dragleave.prevent="dragging.cover = false"
              @drop.prevent="handleDrop($event, 'cover')"
            >
              <input type="file" ref="coverInput" accept=".jpg,.jpeg,.png,.webp" @change="handleCoverChange" class="file-input" />
              <div class="drop-zone-content">
                <svg class="drop-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                <div v-if="files.cover" class="drop-file-name-sm">{{ files.cover.name }}</div>
                <template v-else>
                  <div class="drop-title-sm">拖拽封面</div>
                  <div class="drop-hint-sm">JPG / PNG / WebP</div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交区 -->
    <div class="submit-bar">
      <SfButton @click="resetForm" class="reset-btn">重置</SfButton>
      <SfButton type="primary" @click="submitForm" :loading="uploading" class="submit-btn">
        {{ uploading ? '上传中...' : '提交上传' }}
      </SfButton>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="progress-card">
      <div class="progress-header">
        <div class="progress-title">上传进度</div>
        <div class="progress-text">{{ uploadText }}</div>
      </div>
      <SfProgress :percentage="uploadProgress" :type="uploadStatus === 'success' ? 'success' : uploadStatus === 'exception' ? 'danger' : 'brand'" />
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

// 拖拽上传支持
const dragging = reactive({
  video: false,
  subtitle: false,
  cover: false
})

const VIDEO_EXTS = ['.mp4', '.webm', '.mov', '.mkv', '.m4v', '.avi', '.flv']
const SUBTITLE_EXTS = ['.srt', '.vtt']
const IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']

const getExt = (name) => {
  const idx = name.lastIndexOf('.')
  return idx >= 0 ? name.slice(idx).toLowerCase() : ''
}

const handleDrop = (e, target) => {
  // 关闭 drag 视觉
  dragging[target] = false
  const droppedFiles = Array.from(e.dataTransfer?.files || [])
  if (!droppedFiles.length) return

  // 根据目标类型过滤
  let matched = null
  for (const f of droppedFiles) {
    const ext = getExt(f.name)
    if (target === 'video' && VIDEO_EXTS.includes(ext)) { matched = f; break }
    if (target === 'subtitle' && SUBTITLE_EXTS.includes(ext)) { matched = f; break }
    if (target === 'cover' && IMAGE_EXTS.includes(ext)) { matched = f; break }
  }

  if (!matched) {
    const expected = target === 'video' ? VIDEO_EXTS : target === 'subtitle' ? SUBTITLE_EXTS : IMAGE_EXTS
    toast.error(`不支持的文件类型,请上传 ${expected.join('/')} 格式`)
    return
  }

  files[target] = matched
  toast.success(`已选择: ${matched.name}`)
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
    // ==================== Plan B: 浏览器直传 OSS ====================
    // 1) 拿 presigned URL (3 个文件)
    uploadText.value = '获取上传凭证...'
    uploadProgress.value = 2
    const presign = await materialAPI.presignUpload({
      video_name: files.video.name,
      subtitle_name: files.subtitle.name,
      cover_name: files.cover.name
    })
    // 2) 直接 PUT 到 OSS,带真实进度
    // 总权重: video 85% + subtitle 10% + cover 5%
    const totalBytes = files.video.size + files.subtitle.size + files.cover.size
    let uploadedBytes = 0

    const putToOSS = async (file, info, label) => {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        xhr.open('PUT', info.url)
        xhr.setRequestHeader('Content-Type', info.content_type)
        xhr.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const fileLoaded = e.loaded
            const fileTotal = e.total
            const filePercent = fileLoaded / fileTotal
            // 整个上传进度: (之前完成 + 当前文件已上传) / 总字节
            const overallLoaded = uploadedBytes + fileLoaded
            const overallPercent = Math.floor((overallLoaded / totalBytes) * 95)  // 0-95%
            uploadProgress.value = Math.min(95, overallPercent)
            uploadText.value = `${label} ${Math.floor(filePercent * 100)}% (${(fileLoaded/1024/1024).toFixed(1)}MB / ${(fileTotal/1024/1024).toFixed(1)}MB)`
          }
        }
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            uploadedBytes += file.size
            resolve()
          } else {
            reject(new Error(`${label} 上传失败: HTTP ${xhr.status} ${xhr.responseText?.slice(0,200)}`))
          }
        }
        xhr.onerror = () => reject(new Error(`${label} 网络错误`))
        xhr.send(file)
      })
    }

    // 视频最大先传 (失败成本最高)
    uploadText.value = '上传视频到云存储...'
    await putToOSS(files.video, presign.video, '视频')

    uploadText.value = '上传字幕...'
    await putToOSS(files.subtitle, presign.subtitle, '字幕')

    uploadText.value = '上传封面...'
    await putToOSS(files.cover, presign.cover, '封面')

    // 3) finalize: 创建 Material 记录
    uploadProgress.value = 96
    uploadText.value = '正在保存...'
    await materialAPI.finalizeUpload({
      title: form.title,
      description: form.description || '',
      category: form.category,
      difficulty: form.difficulty,
      video_key: presign.video.key,
      subtitle_key: presign.subtitle.key,
      cover_key: presign.cover.key
    })

    uploadProgress.value = 100
    uploadStatus.value = 'success'
    uploadText.value = '上传成功！智能解读正在后台生成...'

    toast.success('语料上传成功')
    setTimeout(() => {
      router.push('/admin/materials')
    }, 1500)
  } catch (e) {
    uploadStatus.value = 'exception'
    const errMsg = e.response?.data?.detail || e.message
    uploadText.value = '上传失败: ' + errMsg
    toast.error('上传失败: ' + errMsg)
    console.error('Upload error:', e)
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
/* ====== 页面容器 ====== */
.material-upload {
  max-width: 960px;
}

/* ====== 页头 ====== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.header-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 4px;
  display: block;
}
.header-desc .link {
  color: var(--sf-admin-accent, #60a5fa);
  text-decoration: none;
  font-weight: 500;
  border-bottom: 1px dashed currentColor;
}
.header-desc .link:hover {
  border-bottom-style: solid;
}

.back-btn {
  border-radius: 10px;
}

/* ====== 表单卡片 ====== */
.form-card {
  background: var(--sf-admin-sidebar-bg);
  border: 1px solid var(--sf-admin-sidebar-border);
  border-radius: var(--radius-lg, 12px);
  padding: 28px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.form-col {
  min-width: 0;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--sf-admin-accent);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--sf-admin-sidebar-border);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-row-item {
  min-width: 0;
}

/* ====== 星级评分 ====== */
.star-rating {
  display: flex;
  align-items: center;
  gap: 4px;
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.15);
  padding: 2px;
  transition: color var(--sf-duration-fast), transform var(--sf-duration-fast);
}

.star-btn:hover {
  transform: scale(1.15);
}

.star-btn.active {
  color: var(--sf-warning);
}

.star-label {
  margin-left: 8px;
  font-size: 12px;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

/* ====== 拖拽上传区 ====== */
.file-input {
  display: none;
}

.drop-zone {
  position: relative;
  border: 2px dashed var(--sf-admin-border-hover);
  border-radius: var(--radius-lg, 12px);
  padding: 32px 20px;
  cursor: pointer;
  transition: all var(--sf-duration-normal);
  background: rgba(255, 255, 255, 0.02);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 160px;
}

.drop-zone:hover {
  border-color: var(--sf-admin-accent);
  background: var(--sf-admin-accent-light);
}

.drop-zone.is-dragging {
  border-color: var(--sf-admin-accent);
  border-style: solid;
  background: var(--sf-admin-accent-light);
  transform: scale(1.01);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15);
}

.drop-zone.has-file {
  border-color: var(--sf-admin-accent);
  border-style: solid;
  background: var(--sf-admin-accent-light);
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.drop-icon {
  width: 36px;
  height: 36px;
  color: var(--color-text-muted);
  transition: color var(--sf-duration-normal);
}

.drop-zone:hover .drop-icon {
  color: var(--sf-admin-accent);
}

.drop-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.drop-hint {
  font-size: 12px;
  color: var(--color-text-muted);
}

.drop-file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--sf-admin-accent);
  word-break: break-all;
}

.drop-zone-tag {
  position: absolute;
  top: 10px;
  right: 12px;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 小尺寸上传区（字幕 + 封面） */
.upload-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.drop-zone-sm {
  min-height: 120px;
  padding: 20px 14px;
}

.drop-icon-sm {
  width: 28px;
  height: 28px;
  color: var(--color-text-muted);
  transition: color var(--sf-duration-normal);
}

.drop-zone:hover .drop-icon-sm {
  color: var(--sf-admin-accent);
}

.drop-title-sm {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.drop-hint-sm {
  font-size: 11px;
  color: var(--color-text-muted);
}

.drop-file-name-sm {
  font-size: 12px;
  font-weight: 500;
  color: var(--sf-admin-accent);
  word-break: break-all;
}

/* ====== 提交栏 ====== */
.submit-bar {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.submit-btn {
  min-width: 140px;
  height: 44px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
}

.reset-btn {
  border-radius: 10px;
}

/* ====== 上传进度 ====== */
.progress-card {
  margin-top: 20px;
  background: var(--sf-admin-sidebar-bg);
  border: 1px solid var(--sf-admin-sidebar-border);
  border-radius: var(--radius-lg, 12px);
  padding: 20px 24px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.progress-title {
  font-weight: 600;
  font-size: 15px;
  color: var(--color-text-primary);
}

.progress-text {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* ====== 响应式 ====== */
@media (max-width: 768px) {
  .form-card {
    padding: 20px 16px;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .header-left h1 {
    font-size: 20px;
  }

  .drop-zone {
    min-height: 120px;
    padding: 24px 16px;
  }

  .drop-zone-sm {
    min-height: 100px;
    padding: 16px 12px;
  }

  .upload-row {
    grid-template-columns: 1fr;
  }

  .submit-bar {
    flex-direction: column;
  }

  .submit-btn {
    width: 100%;
  }
}
</style>
