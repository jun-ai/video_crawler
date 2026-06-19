import axios from 'axios'
import { toast } from '@/composables/useToast'

const api = axios.create({
  baseURL: '/api',
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
  getProfile: () => api.get('/auth/profile')
}

// ==================== 语料 API ====================
export const materialAPI = {
  getList: (params) => api.get('/materials', { params }),
  getDetail: (id) => api.get(`/materials/${id}`),
  getSubtitles: (id) => api.get(`/materials/${id}/subtitles`),
  getCategories: () => api.get('/materials/categories'),
  getInterpretation: (id) => api.get(`/materials/${id}/interpretation`),
  getInterpretationStatus: (id) => api.get(`/materials/${id}/interpretation/status`),
  generateInterpretation: (id) => api.post(`/materials/${id}/interpretation/generate`, {}),
  translateSubtitles: (id, subtitles) => api.post(`/materials/${id}/translate`, { subtitles }, { timeout: 120000 }),
  translateText: (text) => api.post('/materials/translate-text', { text }, { timeout: 30000 }),
  // 创建语料（管理员）
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
  delete: (id) => api.delete(`/learning/vocabulary/${id}`),
  // 5-P0-4: 批量操作 (3 个端点共用 BatchIdsRequest)
  batchMaster: (ids) => api.post('/learning/vocabulary/batch-master', { ids }),
  batchUnmaster: (ids) => api.post('/learning/vocabulary/batch-unmaster', { ids }),
  batchDelete: (ids) => api.post('/learning/vocabulary/batch-delete', { ids }),
  // 5-P1-4: 导出 (后端返回文件流, 前端用 blob 下载)
  export: (params) => api.get('/learning/vocabulary/export', { params, responseType: 'blob' }),
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
  update: (id, data) => api.patch(`/learning/bookmarks/${id}`, data)
}

// ==================== 标签 API ====================
export const tagsAPI = {
  getList: (params) => api.get('/tags', { params }),
  create: (data) => api.post('/admin/tags', data),
  update: (id, data) => api.put(`/admin/tags/${id}`, data),
  delete: (id) => api.delete(`/admin/tags/${id}`),
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

  // 统计信息
  getStats: () => api.get('/admin/stats'),

  // 存储管理
  getStorageInfo: () => api.get('/admin/storage/info'),
  testStorage: () => api.post('/admin/storage/test'),

  // 激活码管理
  generateActivationCodes: (data) => api.post('/admin/activation-codes', data),
  getActivationCodes: (params) => api.get('/admin/activation-codes', { params }),
  deleteActivationCode: (id) => api.delete(`/admin/activation-codes/${id}`),

  // 公告管理
  createAnnouncement: (data) => api.post('/admin/announcements', data),
  getAnnouncements: (params) => api.get('/admin/announcements', { params }),
  updateAnnouncement: (id, data) => api.put(`/admin/announcements/${id}`, data),
  deleteAnnouncement: (id) => api.delete(`/admin/announcements/${id}`)
}

// ==================== 公告 API ====================
export const announcementAPI = {
  getList: (params) => api.get('/announcements', { params })
}

export default api
