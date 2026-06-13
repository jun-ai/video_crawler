import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { vocabularyAPI } from '@/api'

export const useVocabularyStore = defineStore('vocabulary', () => {
  const vocabularies = ref([])
  const total = ref(0)
  const loading = ref(false)
  const filters = ref({
    page: 1,
    page_size: 20,
    sort_by: 'newest'
  })
  const wordInfoCache = ref({})

  const masteredCount = computed(() => vocabularies.value.filter(v => v.mastered).length)
  const unmasteredCount = computed(() => vocabularies.value.filter(v => !v.mastered).length)

  const loadVocabularies = async (params = {}) => {
    loading.value = true
    try {
      const res = await vocabularyAPI.getList({ ...filters.value, ...params })
      vocabularies.value = res.items || res
      total.value = res.total || vocabularies.value.length
    } catch (e) {
      console.error('加载词汇失败', e)
    } finally {
      loading.value = false
    }
  }

  const addWord = async (data) => {
    const res = await vocabularyAPI.add(data)
    return res
  }

  const markMastered = async (id) => {
    await vocabularyAPI.markMastered(id)
  }

  const deleteWord = async (id) => {
    await vocabularyAPI.delete(id)
  }

  const lookupWord = async (word) => {
    if (wordInfoCache.value[word]) return wordInfoCache.value[word]
    const result = await vocabularyAPI.lookup(word)
    wordInfoCache.value[word] = result
    return result
  }

  return {
    vocabularies, total, loading, filters, wordInfoCache,
    masteredCount, unmasteredCount,
    loadVocabularies, addWord, markMastered, deleteWord, lookupWord
  }
})
