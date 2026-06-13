/**
 * Text-to-Speech composable - 统一的语音合成功能
 *
 * 特性：
 * - iOS Safari 兼容（voices 异步加载）
 * - Android/PC 全支持
 * - 自动选择英文语音
 * - 错误处理和用户提示
 */
import { toast } from './useToast'

export function useTTS() {
  // ============================================
  // 核心：统一的 speak 函数
  // ============================================
  const speak = (text, options = {}) => {
    if (!text) return

    // 调试：打印环境信息
    console.log('[TTS Debug] window.speechSynthesis:', !!window.speechSynthesis)
    console.log('[TTS Debug] userAgent:', navigator.userAgent)

    // 检查浏览器是否支持语音合成
    if (!('speechSynthesis' in window) || !window.speechSynthesis) {
      console.error('[TTS Debug] speechSynthesis 不可用')
      // 提供更具体的错误信息
      const ua = navigator.userAgent.toLowerCase()
      if (ua.includes('micromessenger')) {
        toast.warning('微信浏览器暂不支持语音播放，建议使用 Safari 或 Chrome')
      } else if (ua.includes('qqbrowser')) {
        toast.warning('QQ 浏览器暂不支持语音播放，建议使用系统浏览器')
      } else if (ua.includes('ucbrowser')) {
        toast.warning('UC 浏览器暂不支持语音播放，建议使用 Chrome')
      } else {
        toast.warning('您的浏览器不支持语音合成功能，建议使用 Safari 或 Chrome')
      }
      return
    }

    const utterance = new SpeechSynthesisUtterance(text)
    const lang = options.lang || 'en-US'
    utterance.lang = lang
    utterance.rate = options.rate !== undefined ? options.rate : 0.9
    utterance.pitch = options.pitch !== undefined ? options.pitch : 1

    // 错误处理
    utterance.onerror = (e) => {
      // 忽略中断错误（用户主动取消）
      if (e.error === 'interrupted' || e.error === 'canceled') return
      console.warn('TTS error:', e.error)
      toast.warning('语音播放失败，请刷新页面重试')
    }

    // ============================================
    // 语音选择：兼容 iOS（voices 异步加载）+ Android/PC
    // ============================================
    const selectVoice = () => {
      const voices = window.speechSynthesis.getVoices()
      if (!voices || voices.length === 0) return

      const langPrefix = lang.split('-')[0]

      // 优先级：精确匹配 > 语言前缀匹配
      let voice = voices.find(v => v.lang === lang)
      if (!voice) {
        voice = voices.find(v => v.lang.startsWith(langPrefix))
      }
      // iOS 上 fallback：任意英语语音
      if (!voice && langPrefix === 'en') {
        voice = voices.find(v => v.lang.startsWith('en'))
      }
      if (voice) {
        utterance.voice = voice
      }
    }

    // 取消之前的发音
    window.speechSynthesis.cancel()

    // 尝试立即获取 voices（PC/Android 通常已缓存）
    selectVoice()

    const voicesCount = window.speechSynthesis.getVoices().length

    if (voicesCount === 0) {
      // iOS Safari：voices 尚未加载，需要等待 voiceschanged 事件
      const onVoicesChanged = () => {
        selectVoice()
        window.speechSynthesis.speak(utterance)
      }
      window.speechSynthesis.addEventListener('voiceschanged', onVoicesChanged, { once: true })
      return
    }

    window.speechSynthesis.speak(utterance)
  }

  // ============================================
  // 便捷方法
  // ============================================
  const speakText = (text, rate = 0.9) => {
    speak(text, { lang: 'en-US', rate })
  }

  const speakWord = (word) => {
    speak(word, { lang: 'en-US', rate: 0.8 })
  }

  const speakSentence = (sentence) => {
    speak(sentence, { lang: 'en-US', rate: 0.9 })
  }

  // ============================================
  // 初始化（可选）：在页面加载时预先触发 voices 加载
  // 对 iOS 特别有帮助，可以在组件 mounted 时调用一次
  // ============================================
  const preloadVoices = () => {
    if (!('speechSynthesis' in window)) return

    // 立即获取（如果有）
    window.speechSynthesis.getVoices()

    // 触发 voiceschanged（iOS 需要）
    window.speechSynthesis.dispatchEvent(new Event('voiceschanged'))
  }

  // 停止当前发音
  const stop = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }

  return {
    speak,
    speakText,
    speakWord,
    speakSentence,
    preloadVoices,
    stop
  }
}