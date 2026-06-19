/**
 * useDictationExtractor - DictationMode 听写挖空逻辑
 *
 * 三个核心函数:
 * - extractKeyWords(text): 关键词提取(扩展停用词 + 长度过滤)
 * - pickBlankPositions(text, seed, count): 挖空位置稳定(seed 决定 → 同句同位置)
 * - buildDistractors(correctWord, contextWords, count): 干扰项(优先上下文相似词)
 *
 * 解决:
 * - 2.6 关键词 = 真正"难"的词, 不是 is/of/to 这种没意义的虚词
 * - 2.7 挖空位置稳定 = 用户重看同一句, 挖空处不变 (避免每次刷新位置全乱)
 * - 2.8 干扰项语义相关 = 不要"make" 当 "ubiquitous" 的干扰项
 */

import { computed } from 'vue'

// 扩展停用词表 (常见 200+ 词, 涵盖虚词/代词/助词/介词/连词/常用 be 动词)
// 解决: 之前简单词表只 60 词, 漏了 "really" / "actually" / "almost" 等副词
export const STOP_WORDS = new Set([
  // 冠词
  'a', 'an', 'the',
  // be 动词 / 助动词
  'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
  'do', 'does', 'did', 'done', 'doing',
  'have', 'has', 'had', 'having',
  'will', 'would', 'shall', 'should',
  'can', 'could', 'may', 'might', 'must',
  // 代词
  'i', 'you', 'he', 'she', 'it', 'we', 'they',
  'me', 'him', 'her', 'us', 'them',
  'my', 'your', 'his', 'its', 'our', 'their',
  'mine', 'yours', 'hers', 'ours', 'theirs',
  'this', 'that', 'these', 'those',
  'who', 'whom', 'whose', 'which', 'what',
  'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves',
  // 介词
  'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
  'up', 'down', 'out', 'off', 'over', 'under', 'about',
  'into', 'through', 'during', 'before', 'after', 'above', 'below',
  'between', 'against', 'without', 'within', 'along', 'across', 'behind', 'beyond',
  // 连词 / 副词
  'and', 'or', 'but', 'so', 'because', 'if', 'when', 'where', 'how', 'why',
  'as', 'than', 'while', 'although', 'though', 'since', 'unless', 'until',
  'not', 'no', 'yes', 'nor',
  'just', 'very', 'too', 'also', 'only', 'even',
  'here', 'there', 'now', 'then', 'still', 'yet', 'already',
  'really', 'actually', 'almost', 'probably', 'maybe', 'perhaps',
  'often', 'always', 'never', 'sometimes', 'usually',
  'well', 'much', 'many', 'more', 'most', 'less', 'least', 'few', 'several',
  'some', 'any', 'all', 'each', 'every', 'both', 'either', 'neither',
  'again', 'once', 'ever',
  // 数字 / 序数
  'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
  'first', 'second', 'third', 'last', 'next',
  // 常见拼写连接词
  "i'm", "you're", "he's", "she's", "it's", "we're", "they're",
  "i've", "you've", "we've", "they've",
  "don't", "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't",
  "haven't", "hasn't", "hadn't",
  "won't", "wouldn't", "shan't", "shouldn't",
  "can't", "cannot", "couldn't", "mayn't", "mightn't", "mustn't",
  "let's", "that's", "who's", "what's", "where's", "there's", "here's",
])

// 单词清洗: 去标点 + 转小写 + 去首尾引号
const cleanWord = (w) => (w || '').toLowerCase().replace(/^[^\w]+|[^\w]+$/g, '')

/**
 * 从句子中提取关键词 (2.6)
 * 规则:
 * - 去标点
 * - 跳过停用词
 * - 长度 >= 3 (避免 is/to/an 等单字母/双字母)
 * - 跳过纯数字
 *
 * @param {string} text - 英文句子
 * @returns {string[]} - 关键词数组(保序,去重)
 */
export function extractKeyWords(text) {
  if (!text) return []
  const seen = new Set()
  const result = []
  for (const raw of text.split(/\s+/)) {
    const w = cleanWord(raw)
    if (!w || w.length < 3) continue  // 长度过滤
    if (/^\d+$/.test(w)) continue  // 纯数字跳过
    if (STOP_WORDS.has(w)) continue  // 停用词
    if (seen.has(w)) continue  // 去重(同句多次出现只算一次)
    seen.add(w)
    result.push(w)
  }
  return result
}

/**
 * 简单字符串 hash (djb2 算法) - 用作 PRNG 种子
 */
function hashString(str) {
  let hash = 5381
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i)  // hash * 33 + c
    hash |= 0  // 转 32 位 int
  }
  return hash >>> 0  // 转无符号
}

/**
 * sfc32 PRNG - 用 hash 作为种子, 产生可复现的伪随机序列
 * 比 Math.random() 慢但稳定: 同 seed 必出同序列
 */
function sfc32(seed) {
  let a = (seed | 0) || 1
  let b = (a ^ 0xdeadbeef) | 0
  let c = (b ^ 0x41c64e6d) | 0
  let d = (c ^ 0x6073) | 0
  return function () {
    a |= 0; b |= 0; c |= 0; d |= 0
    const t = (a + b | 0) + d | 0
    d = d + 1 | 0
    a = b ^ b >>> 9
    b = c + (c << 3) | 0
    c = c << 21 | c >>> 11
    c = c + t | 0
    return (t >>> 0) / 4294967296
  }
}

/**
 * 选择挖空位置 (2.7)
 * 关键: 用 seed 决定 → 同句同 seed 永远挖空同一组词
 *
 * @param {string} text - 英文句子
 * @param {string|number} seed - 种子(用 subtitle.id 最方便)
 * @param {number} count - 挖几个空(默认 2-4)
 * @returns {number[]} - 选中关键词的原始索引(0-based, 在 keyWords 数组里)
 */
export function pickBlankPositions(text, seed, count) {
  const keyWords = extractKeyWords(text)
  if (keyWords.length === 0) return []

  // 挖空数: 关键词少时少挖, 多时 2-4 个
  const targetCount = count ?? Math.min(4, Math.max(2, Math.ceil(keyWords.length * 0.4)))

  // 用 seed 算稳定 PRNG
  const seedNum = typeof seed === 'string' ? hashString(String(seed)) : (seed | 0)
  const rand = sfc32(seedNum)

  // Fisher-Yates 用稳定 PRNG 洗牌
  const indices = keyWords.map((_, i) => i)
  for (let i = indices.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1))
    ;[indices[i], indices[j]] = [indices[j], indices[i]]
  }
  return indices.slice(0, Math.min(targetCount, indices.length))
}

/**
 * Levenshtein 编辑距离 - 用于拼写相似度
 */
function levenshtein(a, b) {
  if (a === b) return 0
  if (!a.length) return b.length
  if (!b.length) return a.length
  const dp = Array(b.length + 1).fill(0).map((_, i) => i)
  for (let i = 1; i <= a.length; i++) {
    let prev = dp[0]
    dp[0] = i
    for (let j = 1; j <= b.length; j++) {
      const tmp = dp[j]
      dp[j] = a[i - 1] === b[j - 1]
        ? prev
        : 1 + Math.min(prev, dp[j], dp[j - 1])
      prev = tmp
    }
  }
  return dp[b.length]
}

/**
 * 生成干扰项 (2.8)
 * 优先级:
 * 1. 句中其他关键词(语义相关)
 * 2. 与正确词拼写相似(Levenshtein 距离 1-2)的同池词
 * 3. 通用基础词池(最后兜底)
 *
 * @param {string} correctWord - 正确单词
 * @param {string[]} contextWords - 句中其他关键词池(从 extractKeyWords(text) 去掉自身)
 * @param {number} count - 需要几个干扰项(默认 3)
 * @returns {string[]} - 干扰项数组(不含 correctWord)
 */
export function buildDistractors(correctWord, contextWords = [], count = 3) {
  const target = count || 3
  const correct = cleanWord(correctWord)
  const result = []
  const seen = new Set([correct])

  // 1. 优先: 句中其他关键词
  for (const w of contextWords) {
    if (result.length >= target) break
    const cw = cleanWord(w)
    if (!seen.has(cw)) {
      result.push(w)
      seen.add(cw)
    }
  }

  // 2. 拼写相似: 距离 1-2 的同池词
  if (result.length < target) {
    const candidates = contextWords
      .map(w => ({ w, dist: levenshtein(cleanWord(w), correct) }))
      .filter(x => x.dist >= 1 && x.dist <= 2)
      .sort((a, b) => a.dist - b.dist)
    for (const c of candidates) {
      if (result.length >= target) break
      if (!seen.has(cleanWord(c.w))) {
        result.push(c.w)
        seen.add(cleanWord(c.w))
      }
    }
  }

  // 3. 兜底: 基础词池(出现频次高的实词, 当 context 不足时使用)
  if (result.length < target) {
    const FALLBACK = [
      'thing', 'place', 'time', 'way', 'year', 'day', 'man', 'woman', 'world',
      'people', 'child', 'friend', 'work', 'home', 'hand', 'part', 'case',
      'week', 'company', 'system', 'program', 'question', 'group', 'number',
      'night', 'point', 'house', 'water', 'mother', 'father', 'room', 'side',
      'idea', 'head', 'story', 'fact', 'book', 'word', 'food', 'city',
    ]
    const shuffled = [...FALLBACK].sort(() => Math.random() - 0.5)
    for (const w of shuffled) {
      if (result.length >= target) break
      if (!seen.has(w)) {
        result.push(w)
        seen.add(w)
      }
    }
  }

  return result.slice(0, target)
}

/**
 * 完整挖空 + 干扰项生成 - DictationMode.vue 一次调用
 *
 * @param {Object} params
 * @param {string} params.text - 句子
 * @param {string|number} params.seed - 种子(推荐 subtitle.id)
 * @param {number} [params.blankCount] - 挖空数
 * @param {number} [params.optionCount] - 每个空的选项数(含正确)
 * @returns {Array<{word, options, index}>} - 挖空列表
 */
export function buildBlanks({ text, seed, blankCount, optionCount = 4 }) {
  if (!text) return []
  const words = text.split(/\s+/)
  const keyWords = extractKeyWords(text)
  const blankIdxs = pickBlankPositions(text, seed, blankCount)

  return blankIdxs.map((kwIdx) => {
    const keyWord = keyWords[kwIdx]
    // 找原句中第一个匹配的位置
    let pos = -1
    for (let i = 0; i < words.length; i++) {
      if (cleanWord(words[i]) === keyWord) {
        pos = i
        break
      }
    }
    if (pos < 0) return null

    // 干扰项: 用其他关键词当 context
    const contextWords = keyWords.filter((_, i) => i !== kwIdx)
    const distractors = buildDistractors(keyWord, contextWords, optionCount - 1)
    const options = [words[pos].replace(/[^\w]+$/g, ''), ...distractors]
      .sort(() => Math.random() - 0.5)  // 选项内部洗牌,每次新位置展示

    return {
      word: words[pos].replace(/[^\w]+$/g, ''),
      index: pos,
      options,
    }
  }).filter(Boolean)
}

/**
 * Vue composable 包装 (方便在 setup 里直接用)
 */
export function useDictationExtractor() {
  return {
    extractKeyWords,
    pickBlankPositions,
    buildDistractors,
    buildBlanks,
    STOP_WORDS,
  }
}
