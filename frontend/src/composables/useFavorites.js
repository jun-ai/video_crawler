import { ref } from 'vue'
import { favoriteAPI } from '@/api'

export function useFavorites() {
  const favoriteMap = ref({})  // materialId -> boolean

  const checkFavorite = async (materialId) => {
    try {
      const res = await favoriteAPI.check(materialId)
      favoriteMap.value[materialId] = res.is_favorited
      return res.is_favorited
    } catch (e) {
      return false
    }
  }

  const toggleFavorite = async (materialId) => {
    const isFav = favoriteMap.value[materialId]
    try {
      if (isFav) {
        await favoriteAPI.remove(materialId)
        favoriteMap.value[materialId] = false
        return false
      } else {
        await favoriteAPI.add(materialId)
        favoriteMap.value[materialId] = true
        return true
      }
    } catch (e) {
      throw e
    }
  }

  const isFavorited = (materialId) => !!favoriteMap.value[materialId]

  return { favoriteMap, checkFavorite, toggleFavorite, isFavorited }
}
