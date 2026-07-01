import axios from 'axios'
import { toast } from '@/composables/useToast'

// baseURL: 生产环境用绝对 URL（api 子域）, 开发环境用相对路径（同源 vite proxy）
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 5-P1-4 fix: blob 下载需要保留 headers (Content-Disposition 拿文件名),
    // 不能像 JSON 那样只返回 response.data (Blob 对象没 .data 属性, 会炸)
    if (response.config.responseType === 'blob') {
      return response
    }
    return response.data
  },
  (error) => {
    // 401 未授权，清除无效 token
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // 如果不在登录页，跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    const message = error.response?.data?.detail || '请求失败'
    toast.error(message)
    return Promise.reject(error)
  }
)

// ==================== 认证 API ====================
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (phone, password) => api.post('/auth/login', { phone, password }),
  getProfile: () => api.get('/auth/profile'),
  // P0 商业化: 忘记密码重置 (用激活码当凭证)
  forgotPassword: (phone, invite_code, new_password) =>
    api.post('/auth/forgot-password', { phone, invite_code, new_password })
}

// ==================== 语料 API ====================
export const materialAPI = {
  getList: (params) => api.get('/materials', { params }),
  getDetail: (id) => api.get(`/materials/${id}`),
  getSubtitles: (id) => api.get(`/materials/${id}/subtitles`),
  getCategories: () => api.get('/materials/categories'),
  getInterpretation: (id) => api.get(`/materials/${id}/interpretation`),
  getInterpretationStatus: (id) => api.get(`/materials/${id}/interpretation/status`),
  // 后台任务实时进度 (替换字幕 / 重新解读时返回)
  getProgress: (id) => api.get(`/materials/${id}/progress`),
  generateInterpretation: (id) => api.post(`/materials/${id}/interpretation/generate`, {}),
  // 长字幕分批翻译 (后端 BATCH=40, 每批单独 commit), 405 条字幕约 5-10 分钟
  translateSubtitles: (id, subtitles) => api.post(`/materials/${id}/translate`, { subtitles }, { timeout: 600000 }),
  translateText: (text) => api.post('/materials/translate-text', { text }, { timeout: 30000 }),
  // 创建语料（管理员）- Plan B: 浏览器直传 OSS
  // 1. 先调 presignUpload 拿 3 个 presigned URL
  // 2. PUT 3 个文件直接到 OSS (带 onUploadProgress 真实进度)
  // 3. 调 finalizeUpload 创建 Material 记录
  presignUpload: (fileNames) => api.post('/materials/presign-upload', fileNames),
  finalizeUpload: (data) => api.post('/materials/finalize-upload', data),

  // 旧接口保留兼容 (走 backend 中转,慢)
  create: (formData) => api.post('/materials', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  })
}

// ==================== 学习记录 API ====================
export const learningAPI = {
  updateProgress: (data) => api.post('/learning/progress', data),
  getHistory: (limit = 20) => api.get(`/learning/history?limit=${limit}`),
  getProgress: (materialId) => api.get(`/learning/progress/${materialId}`)
}

// ==================== 发音评测 API ====================
export const pronunciationAPI = {
  evaluate: (spokenText, expectedText) => api.post('/learning/pronunciation/evaluate', {
    spoken_text: spokenText,
    expected_text: expectedText
  })
}

// ==================== 收藏 API ====================
export const favoriteAPI = {
  add: (materialId) => api.post(`/favorites/${materialId}`),
  remove: (materialId) => api.delete(`/favorites/${materialId}`),
  check: (materialId) => api.get(`/favorites/check/${materialId}`),
  getList: (params) => api.get('/favorites', { params })
}

// ==================== 生词本 API ====================
export const vocabularyAPI = {
  add: (data) => api.post('/learning/vocabulary', data),
  getList: (params) => api.get('/learning/vocabulary', { params }),
  markMastered: (id) => api.put(`/learning/vocabulary/${id}/master`),
  unmarkMastered: (id) => api.put(`/learning/vocabulary/${id}/unmaster`), // 5-P0-1
  // 5-P2-5: 星标
  star: (id) => api.put(`/learning/vocabulary/${id}/star`),
  unstar: (id) => api.put(`/learning/vocabulary/${id}/unstar`),
  delete: (id) => api.delete(`/learning/vocabulary/${id}`),
  // 5-P0-4: 批量操作 (3 个端点共用 BatchIdsRequest)
  batchMaster: (ids) => api.post('/learning/vocabulary/batch-master', { ids }),
  batchUnmaster: (ids) => api.post('/learning/vocabulary/batch-unmaster', { ids }),
  batchStar: (ids) => api.post('/learning/vocabulary/batch-star', { ids }),     // 5-P2-5
  batchUnstar: (ids) => api.post('/learning/vocabulary/batch-unstar', { ids }), // 5-P2-5
  batchDelete: (ids) => api.post('/learning/vocabulary/batch-delete', { ids }),
  // 5-P1-4: 导出 (后端返回文件流, 前端用 blob 下载)
  export: (params) => api.get('/learning/vocabulary/export', { params, responseType: 'blob' }),
  // 5-P2-10: 单词查重
  check: (word) => api.get(`/learning/vocabulary/check?word=${encodeURIComponent(word)}`),
  lookup: (word) => api.get(`/learning/vocabulary/lookup?word=${encodeURIComponent(word)}`, { timeout: 30000 }),
  // 复习相关
  getReviewQueue: (limit = 20) => api.get(`/learning/vocabulary/review-queue?limit=${limit}`),
  submitReview: (data) => api.post('/learning/vocabulary/review', data),
  getReviewStats: () => api.get('/learning/vocabulary/review-stats')
}

// ==================== 解读项学习状态 API ====================
export const interpretationAPI = {
  setStatus: (data) => api.post('/learning/interpretation/status', data),
  getStatus: (materialId) => api.get(`/learning/interpretation/status/${materialId}`)
}

// ==================== 学习统计 API ====================
export const learningStatsAPI = {
  getStatistics: () => api.get('/learning/statistics'),
  getRecent: (limit = 10) => api.get(`/learning/recent?limit=${limit}`),
  getCompleted: (limit = 10) => api.get(`/learning/completed?limit=${limit}`),
  getRecords: (params) => api.get('/learning/records', { params }),
  getCalendar: (year, month) => api.get('/learning/calendar', { params: { year, month } }),
  getTrend: (days = 7) => api.get(`/learning/trend?days=${days}`),
  // 3.1 合并端点: 一次拿 5 个视图数据 (stats + trend + recent + completed + records-首页)
  getDashboard: () => api.get('/learning/dashboard'),
}

// ==================== 语音识别 API ====================
export const speechAPI = {
  // 语音识别 + 发音评测（上传音频文件）
  recognizeAndEvaluate: (audioBlob, expectedText) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    formData.append('expected_text', expectedText)
    return api.post('/learning/speech/recognize', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000  // 语音识别可能需要更长时间
    })
  }
}

// ==================== 听写练习 API ====================
export const dictationAPI = {
  submit: (data) => api.post('/learning/dictation/submit', data),
  getRecords: (materialId) => api.get(`/learning/dictation/records/${materialId}`),
  getStatistics: () => api.get('/learning/dictation/statistics')
}

// ==================== 字幕标注 API ====================
export const annotationAPI = {
  add: (data) => api.post('/learning/annotations', data),
  getByMaterial: (materialId) => api.get(`/learning/annotations/${materialId}`),
  getBySubtitle: (subtitleId) => api.get(`/learning/annotations/subtitle/${subtitleId}`),
  delete: (id) => api.delete(`/learning/annotations/${id}`),
  update: (id, data) => api.put(`/learning/annotations/${id}`, data)
}

// ==================== 字幕收藏 API ====================
export const subtitleBookmarkAPI = {
  add: (data) => api.post('/learning/bookmarks', data),
  remove: (id) => api.delete(`/learning/bookmarks/${id}`),
  check: (materialId) => api.get(`/learning/bookmarks/check/${materialId}`),
  getList: (materialId) => api.get(`/learning/bookmarks/${materialId}`),
  /** 单次获取所有字幕收藏（join Subtitle），替代循环 N+1
 *  4-P1-4: 支持 search + material_id 参数 */
  getAll: (params) => api.get('/learning/bookmarks/all', { params }),
  incrementPractice: (bookmarkId) => api.post(`/learning/bookmarks/${bookmarkId}/practice`),
  // 4-P1-5: 批量删除
  batchDelete: (ids) => api.post('/learning/bookmarks/batch-delete', { ids }),
  // 5-P1-2: 更新笔记
  update: (id, data) => api.patch(`/learning/bookmarks/${id}`, data),
  // 5-P1-2: 设置标签 (replace-all, 按 name)
  setTags: (id, tagNames) => api.put(`/learning/bookmarks/${id}/tags`, { tag_names: tagNames })
}

// ==================== 5-P1-2: 用户收藏标签 API ====================
export const bookmarkTagAPI = {
  list: () => api.get('/learning/bookmark-tags'),
  create: (data) => api.post('/learning/bookmark-tags', data),
  delete: (id) => api.delete(`/learning/bookmark-tags/${id}`)
}

// ==================== 5-P1-2 (后缀): 收藏文件夹 API ====================
export const bookmarkFolderAPI = {
  list: () => api.get('/learning/bookmark-folders'),
  create: (data) => api.post('/learning/bookmark-folders', data),
  update: (id, data) => api.patch(`/learning/bookmark-folders/${id}`, data),
  delete: (id) => api.delete(`/learning/bookmark-folders/${id}`),
  moveBookmark: (bookmarkId, folderId) => api.put(`/learning/bookmarks/${bookmarkId}/folder`, { folder_id: folderId }),
  batchMove: (ids, folderId) => api.post('/learning/bookmarks/batch-move-folder', { ids, folder_id: folderId })
}

// ==================== 5-P2 (后缀): 收藏导出 API ====================
// 返回 Blob (csv/json), 浏览器自动下载
export const bookmarkExportAPI = {
  download: (params) => api.get('/learning/bookmarks/export', {
    params,
    responseType: 'blob'
  })
}

// ==================== 标签 API ====================
// 后端路由: GET/POST /api/tags, PUT/DELETE /api/tags/{id} (tags.py router prefix=/api/tags)
// create/update/delete 内部有 admin role 校验 (current_user.role != 1 → 403)
export const tagsAPI = {
  getList: (params) => api.get('/tags', { params }),
  create: (data) => api.post('/tags', data),
  update: (id, data) => api.put(`/tags/${id}`, data),
  delete: (id) => api.delete(`/tags/${id}`),
  assignTags: (materialId, tagIds) => api.post(`/admin/materials/${materialId}/tags`, { tag_ids: tagIds })
}

// ==================== 管理员 API ====================
export const adminAPI = {
  // 语料管理
  getMaterials: (params) => api.get('/admin/materials', { params }),
  toggleMaterialStatus: (id, isActive) => api.put(`/admin/materials/${id}/status`, null, { params: { is_active: isActive } }),
  deleteMaterial: (id, deleteFiles = false) => api.delete(`/admin/materials/${id}`, { params: { delete_files: deleteFiles } }),
  batchUpload: (formData) => api.post('/admin/materials/batch-upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  }),

  // 编辑
  updateMaterial: (id, data) => api.put(`/admin/materials/${id}`, data),

  // 批量操作
  batchDelete: (ids, deleteFiles = false) => api.post('/admin/materials/batch-delete',
    { ids }, { params: { delete_files: deleteFiles } }),
  batchUpdateStatus: (ids, isActive) => api.post('/admin/materials/batch-status', { ids, is_active: isActive }),

  // 重新生成字幕 / 重新解读
  retranscribe: (id, params = {}) => api.post(`/admin/materials/${id}/retranscribe`, null, { params, timeout: 30000 }),
  reinterpret: (id) => api.post(`/admin/materials/${id}/reinterpret`, null, { timeout: 30000 }),
  replaceSubtitle: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/admin/materials/${id}/replace-subtitle`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    })
  },
  probeDuration: (videoPath) => api.post('/admin/materials/probe-duration', { video_path: videoPath }),
  backfillDurations: () => api.post('/admin/materials/backfill-durations'),

  // CSV 导出 (blob 下载, 跟词汇导出用同套路)
  exportMaterials: (params) => api.get('/admin/materials/export', {
    params,
    responseType: 'blob'
  }),

  // 通过 URL 抓取语料 (B站自动,YouTube手动)
  fetchFromUrl: (data) => api.post('/admin/materials/fetch-url', data, { timeout: 30000 }),
  getFetchStatus: (taskId) => api.get(`/admin/materials/fetch-status/${taskId}`),
  listFetchTasks: () => api.get('/admin/materials/fetch-tasks'),

  // 统计信息
  getStats: () => api.get('/admin/stats'),

  // 存储管理
  getStorageInfo: () => api.get('/admin/storage/info'),
  testStorage: () => api.post('/admin/storage/test'),

  // 激活码管理
  generateActivationCodes: (data) => api.post('/admin/activation-codes', data),
  getActivationCodes: (params) => api.get('/admin/activation-codes', { params }),
  deleteActivationCode: (id) => api.delete(`/admin/activation-codes/${id}`),
  batchDeleteActivationCodes: (ids) => api.post('/admin/activation-codes/batch-delete', { ids }),
  deleteAllUnusedActivationCodes: (confirm = true) => api.delete('/admin/activation-codes-all', { params: { confirm } }),

  // 公告管理
  createAnnouncement: (data) => api.post('/admin/announcements', data),
  getAnnouncements: (params) => api.get('/admin/announcements', { params }),
  updateAnnouncement: (id, data) => api.put(`/admin/announcements/${id}`, data),
  deleteAnnouncement: (id) => api.delete(`/admin/announcements/${id}`),

  // 视频转字幕 (faster-whisper)
  transcribe: (formData) => api.post('/admin/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000  // 10 分钟
  }),
  getTranscribeStatus: (taskId) => api.get(`/admin/transcribe-status/${taskId}`),
  listTranscribeTasks: () => api.get('/admin/transcribe-tasks')
}

// ==================== 公告 API ====================
export const announcementAPI = {
  getList: (params) => api.get('/announcements', { params })
}

export default api
