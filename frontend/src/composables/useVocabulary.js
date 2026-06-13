import { ref } from 'vue'
import { vocabularyAPI, materialAPI } from '@/api'

export function useVocabulary() {
  const wordInfoCache = ref({})
  const addingWord = ref(false)

  const lookupWord = async (word) => {
    if (wordInfoCache.value[word]) return wordInfoCache.value[word]

    try {
      const result = await vocabularyAPI.lookup(word)
      wordInfoCache.value[word] = result
      return result
    } catch (e) {
      // 降级到翻译 API
      try {
        const translateResult = await materialAPI.translateText(word)
        const result = {
          phonetic: '',
          translation: translateResult.translation || word,
          example: ''
        }
        wordInfoCache.value[word] = result
        return result
      } catch (e2) {
        return { phonetic: '', translation: '暂无释义', example: '' }
      }
    }
  }

  const addToVocabulary = async (word, context, materialId, subtitleId) => {
    addingWord.value = true
    try {
      await vocabularyAPI.add({ word, context, material_id: materialId, subtitle_id: subtitleId })
      return true
    } catch (e) {
      throw e
    } finally {
      addingWord.value = false
    }
  }

  return { wordInfoCache, addingWord, lookupWord, addToVocabulary }
}
