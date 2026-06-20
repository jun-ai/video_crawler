<template>
  <div class="transcribe-manage">
    <div class="page-header">
      <div class="header-left">
        <h2>视频转字幕</h2>
        <span class="header-desc">faster-whisper 本地转录 · 上传视频自动生成 SRT</span>
      </div>
    </div>

    <!-- 配置区 -->
    <div class="config-card">
      <div class="form-grid">
        <div class="form-item">
          <label class="form-label">模型</label>
          <SfSelect
            v-model="form.model_size"
            :options="modelOptions"
            placeholder="选择模型"
          />
          <div class="form-hint">base 平衡 · tiny 最快 · small 最准（耗内存）</div>
        </div>
        <div class="form-item">
          <label class="form-label">语言</label>
          <SfSelect
            v-model="form.language"
            :options="languageOptions"
            placeholder="选择语言"
          />
          <div class="form-hint">留空自动检测 · 已知语言可指定提速</div>
        </div>
      </div>
    </div>

    <!-- 上传区 -->
    <div class="upload-card">
      <div
        class="drop-zone"
        :class="{ 'is-dragover': isDragover, 'is-disabled': uploading }"
        @click="triggerFileInput"
        @dragover.prevent="isDragover = true"
        @dragleave.prevent="isDragover = false"
        @drop.prevent="onFileDrop"
      >
        <input
          ref="fileInput"
          type="file"
          accept="video/*,.mp4,.mov,.mkv,.webm,.avi,.flv,.m4v"
          style="display: none"
          @change="onFileChange"
        />
        <div v-if="!selectedFile" class="drop-placeholder">
          <div class="drop-icon">🎬</div>
          <div class="drop-title">点击或拖拽视频到此处</div>
          <div class="drop-desc">支持 mp4 / mov / mkv / webm / avi / flv / m4v · 上限 500MB</div>
        </div>
        <div v-else class="file-info">
          <div class="file-icon">📁</div>
          <div class="file-details">
            <div class="file-name">{{ selectedFile.name }}</div>
            <div class="file-size">{{ formatSize(selectedFile.size) }}</div>
          </div>
          <SfButton type="ghost" size="sm" @click.stop="clearFile">移除</SfButton>
        </div>
      </div>

      <div class="action-row">
        <SfButton
          type="primary"
          :loading="uploading"
          :disabled="!selectedFile || uploading"
          @click="startTranscribe"
        >
          {{ uploading ? '处理中...' : '开始转录' }}
        </SfButton>
      </div>
    </div>

    <!-- 进度区 -->
    <div v-if="currentTask" class="progress-card">
      <div class="progress-header">
        <span class="progress-title">{{ currentTask.filename }}</span>
        <span class="progress-status" :class="`status-${currentTask.status}`">
          {{ statusText(currentTask.status) }}
        </span>
      </div>
      <SfProgress :percentage="currentTask.progress" :type="progressType" />
      <div class="progress-message">{{ currentTask.message || currentTask.error }}</div>

      <!-- 结果区 -->
      <div v-if="currentTask.status === 'done'" class="result-section">
        <div class="result-meta">
          <span v-if="currentTask.language_detected">语言: {{ currentTask.language_detected }}</span>
          <span v-if="currentTask.duration">时长: {{ currentTask.duration.toFixed(1) }}s</span>
          <span v-if="currentTask.segment_count">字幕条数: {{ currentTask.segment_count }}</span>
        </div>
        <SfInput
          v-model="currentTask.srt"
          type="textarea"
          :rows="14"
          readonly
          class="srt-textarea"
        />
        <div class="result-actions">
          <SfButton type="primary" @click="downloadSrt">💾 下载 SRT</SfButton>
          <SfButton type="ghost" @click="copySrt">📋 复制</SfButton>
        </div>
      </div>
    </div>

    <!-- 历史任务 -->
    <div v-if="recentTasks.length" class="history-card">
      <div class="history-header">最近任务</div>
      <div
        v-for="task in recentTasks.slice(0, 10)"
        :key="task.task_id"
        class="history-item"
      >
        <div class="history-info">
          <div class="history-filename">{{ task.filename }}</div>
          <div class="history-meta">
            {{ task.model_size }} · {{ task.segment_count || 0 }} 条字幕
            <span v-if="task.duration"> · {{ task.duration.toFixed(1) }}s</span>
          </div>
        </div>
        <div class="history-status" :class="`status-${task.status}`">
          {{ statusText(task.status) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Mic, FileAudio, AlertCircle } from 'lucide-vue-next'
import { adminAPI } from '@/api'
import { toast } from '@/composables/useToast'
import SfButton from '@/components/ui/SfButton.vue'
import SfInput from '@/components/ui/SfInput.vue'
import SfSelect from '@/components/ui/SfSelect.vue'
import SfProgress from '@/components/ui/SfProgress.vue'

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragover = ref(false)
const uploading = ref(false)
const currentTask = ref(null)
const recentTasks = ref([])
let pollTimer = null

const form = ref({
  model_size: 'base',
  language: ''
})

const modelOptions = [
  { label: 'base (推荐，~140MB)', value: 'base' },
  { label: 'tiny (最快，~75MB)', value: 'tiny' },
  { label: 'small (最准，~460MB)', value: 'small' }
]

const languageOptions = [
  { label: '自动检测', value: '' },
  { label: '英语 en', value: 'en' },
  { label: '中文 zh', value: 'zh' }
]

const progressType = computed(() => {
  if (!currentTask.value) return 'primary'
  if (currentTask.value.status === 'failed') return 'danger'
  if (currentTask.value.status === 'done') return 'success'
  return 'primary'
})

function statusText(status) {
  const map = {
    pending: '等待',
    transcribing: '转录中',
    done: '完成',
    failed: '失败'
  }
  return map[status] || status
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB'
}

function triggerFileInput() {
  if (!uploading.value) fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (file) setFile(file)
}

function onFileDrop(e) {
  isDragover.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) setFile(file)
}

function setFile(file) {
  if (file.size > 500 * 1024 * 1024) {
    toast.error('文件超过 500MB 上限')
    return
  }
  const ext = '.' + (file.name.split('.').pop() || '').toLowerCase()
  const allowed = ['.mp4', '.mov', '.mkv', '.webm', '.avi', '.flv', '.m4v']
  if (!allowed.includes(ext)) {
    toast.error(`不支持的格式: ${ext}`)
    return
  }
  selectedFile.value = file
  currentTask.value = null
}

function clearFile() {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

async function startTranscribe() {
  if (!selectedFile.value) return
  uploading.value = true
  const fd = new FormData()
  fd.append('file', selectedFile.value)
  fd.append('model_size', form.value.model_size)
  if (form.value.language) fd.append('language', form.value.language)

  try {
    const data = await adminAPI.transcribe(fd)
    currentTask.value = {
      task_id: data.task_id,
      filename: data.filename || selectedFile.value.name,
      model_size: data.model_size,
      status: 'pending',
      progress: 0,
      message: data.message || '已加入队列...'
    }
    pollStatus()
  } catch (e) {
    toast.error('上传失败: ' + (e?.response?.data?.detail || e.message))
    uploading.value = false
  }
}

async function pollStatus() {
  if (!currentTask.value) return
  try {
    const data = await adminAPI.getTranscribeStatus(currentTask.value.task_id)
    currentTask.value = { ...currentTask.value, ...data }
    if (data.status === 'done' || data.status === 'failed') {
      uploading.value = false
      clearFile()
      loadRecentTasks()
      return
    }
    pollTimer = setTimeout(pollStatus, 2000)
  } catch (e) {
    uploading.value = false
    toast.error('查询失败: ' + e.message)
  }
}

function downloadSrt() {
  if (!currentTask.value?.srt) return
  const baseName = (currentTask.value.filename || 'subtitle').replace(/\.[^.]+$/, '')
  const blob = new Blob([currentTask.value.srt], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = baseName + '.srt'
  a.click()
  URL.revokeObjectURL(url)
  toast.success('已下载')
}

async function copySrt() {
  if (!currentTask.value?.srt) return
  try {
    await navigator.clipboard.writeText(currentTask.value.srt)
    toast.success('已复制到剪贴板')
  } catch {
    toast.error('复制失败')
  }
}

async function loadRecentTasks() {
  try {
    const data = await adminAPI.listTranscribeTasks()
    recentTasks.value = data || []
  } catch (e) {
    // 静默
  }
}

onMounted(() => {
  loadRecentTasks()
})

onUnmounted(() => {
  if (pollTimer) clearTimeout(pollTimer)
})
</script>

<style scoped>
.transcribe-manage {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}

.header-left h2 {
  font-size: 22px;
  font-weight: 600;
  color: var(--sf-admin-text);
  margin: 0 0 4px;
}

.header-desc {
  color: var(--sf-admin-text-secondary);
  font-size: 13px;
}

/* === 配置区 === */
.config-card {
  background: var(--sf-admin-bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--sf-admin-border);
  margin-bottom: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 13px;
  color: var(--sf-admin-text);
  margin-bottom: 6px;
  font-weight: 500;
}

.form-hint {
  font-size: 12px;
  color: var(--sf-admin-text-secondary);
  margin-top: 4px;
}

/* === 上传区 === */
.upload-card {
  background: var(--sf-admin-bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--sf-admin-border);
  margin-bottom: 16px;
}

.drop-zone {
  border: 2px dashed var(--sf-admin-border);
  border-radius: 10px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--sf-admin-bg);
}

.drop-zone:hover {
  border-color: var(--sf-primary, #409eff);
  background: var(--sf-admin-bg-hover, rgba(64, 158, 255, 0.04));
}

.drop-zone.is-dragover {
  border-color: var(--sf-primary, #409eff);
  background: rgba(64, 158, 255, 0.08);
}

.drop-zone.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.drop-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.drop-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.drop-title {
  font-size: 15px;
  color: var(--sf-admin-text);
  font-weight: 500;
}

.drop-desc {
  font-size: 12px;
  color: var(--sf-admin-text-secondary);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
}

.file-icon {
  font-size: 36px;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 14px;
  color: var(--sf-admin-text);
  font-weight: 500;
  word-break: break-all;
}

.file-size {
  font-size: 12px;
  color: var(--sf-admin-text-secondary);
  margin-top: 2px;
}

.action-row {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* === 进度区 === */
.progress-card {
  background: var(--sf-admin-bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--sf-admin-border);
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--sf-admin-text);
  word-break: break-all;
}

.progress-status {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
  margin-left: 12px;
}

.status-pending { background: #ecf5ff; color: #409eff; }
.status-transcribing { background: #fdf6ec; color: #e6a23c; }
.status-done { background: #f0f9eb; color: #67c23a; }
.status-failed { background: #fef0f0; color: #f56c6c; }

.progress-message {
  font-size: 13px;
  color: var(--sf-admin-text-secondary);
  margin-top: 8px;
  min-height: 18px;
}

.result-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--sf-admin-border);
}

.result-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--sf-admin-text-secondary);
  margin-bottom: 12px;
}

.srt-textarea :deep(textarea) {
  font-family: 'SF Mono', Consolas, 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.result-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

/* === 历史 === */
.history-card {
  background: var(--sf-admin-bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--sf-admin-border);
}

.history-header {
  font-size: 14px;
  font-weight: 500;
  color: var(--sf-admin-text);
  margin-bottom: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--sf-admin-border);
}

.history-item:last-child {
  border-bottom: none;
}

.history-filename {
  font-size: 13px;
  color: var(--sf-admin-text);
  word-break: break-all;
}

.history-meta {
  font-size: 12px;
  color: var(--sf-admin-text-secondary);
  margin-top: 2px;
}

.history-status {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
  white-space: nowrap;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .transcribe-manage {
    padding: 16px;
  }
}
</style>
