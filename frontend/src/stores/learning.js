import { defineStore } from 'pinia'
import { ref } from 'vue'
import { learningAPI } from '@/api'

export const useLearningStore = defineStore('learning', () => {
  const statistics = ref(null)
  const recentMaterials = ref([])
  const loading = ref(false)

  const getStatistics = async () => {
    try {
      statistics.value = await learningAPI.getStatistics()
    } catch (e) {
      console.error('加载统计失败', e)
    }
  }

  const loadProgress = async (materialId) => {
    try {
      return await learningAPI.getProgress(materialId)
    } catch (e) {
      return null
    }
  }

  const updateProgress = async (data) => {
    try {
      await learningAPI.updateProgress(data)
    } catch (e) {
      console.error('更新进度失败', e)
    }
  }

  return {
    statistics, recentMaterials, loading,
    getStatistics, loadProgress, updateProgress
  }
})
