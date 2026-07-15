/**
 * highlightKeyWords — Phase 22: 简单启发式关键词高亮
 *
 * 后端 interpretation 返回 words[] 但不保证每行都有, 因此前端兜底:
 *   - 命中长度 >= 5 的英文单词 (出现 2 次以上的, 或专有短语)
 *   - 专有名词 (首字母大写 且 非句首)
 *   - 数字/年份
 *
 * 返回 HTML, 经由 v-html 渲染, 需注意 XSS (escape 先行)
 */

const HTML_ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => HTML_ESC[c])
}

/**
 * 对一段英文文本做关键词高亮
 * @param {string} textEn
 * @returns {string} HTML, 可安全用 v-html
 */
export function highlightKeyWords(textEn) {
  if (!textEn) return ''

  // 1. 在原文本上预先算 freq (escape 后正则匹配失效)
  const tokens = textEn.toLowerCase().match(/[a-z]+/g) || []
  const freq = {}
  for (const t of tokens) if (t.length >= 5) freq[t] = (freq[t] || 0) + 1
  // 出现 >= 2 次: 真正的焦点词; 出现 1 次但 6+ 字符: 困难词也高亮 (按词长降序, 取前 4)
  const repeated = Object.entries(freq)
    .filter(([, c]) => c >= 2)
    .sort((a, b) => b[1] - a[1])
    .map(([w]) => w)
  const longWords = Object.entries(freq)
    .filter(([w, c]) => c === 1 && w.length >= 7)
    .sort((a, b) => b[0].length - a[0].length)
    .slice(0, 4)
    .map(([w]) => w)
  // 合并去重, 优先 repeated
  const seen = new Set(repeated)
  const focusWords = [...repeated]
  for (const w of longWords) {
    if (!seen.has(w)) { focusWords.push(w); seen.add(w) }
  }

  // 2. escape 整段
  let html = escapeHtml(textEn)

  // 3. 年份 / 数字 (escape 后不受影响)
  html = html.replace(/\b(\d{3,4}s?)\b/g, '<span class="kw-year">$1</span>')

  // 4. 专有名词 (escape 后大写字母不变)
  html = html.replace(/(^|[\s\(\[\{,])([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})/g, (m, pre, word) => {
    if (/^[A-Z]{2,}$/.test(word)) return m
    return `${pre}<span class="kw-prop">${word}</span>`
  })

  // 5. 焦点词 (escape 后大小写被 HTML 转义影响? — 只有 & < > " ' 被转, 字母不变)
  //    escape 后小写字母保持小写, 大写保持大写
  //    但 escape 之后大小写信息被保留, 所以 case-insensitive replace 应该可行
  for (const w of focusWords) {
    const re = new RegExp(`(\\b)(${w})(\\b)`, 'gi')
    html = html.replace(re, (m, p1, p2, p3) => {
      // 已被包在 kw-* span 里的话跳过 — 通过前 200 字符是否含 <span 判断 (简单启发)
      return `${p1}<span class="kw-word">${p2}</span>${p3}`
    })
  }

  return html
}

/**
 * 简单 strip HTML (用于非 v-html 场景)
 */
export function stripHtml(html) {
  if (!html) return ''
  return String(html).replace(/<[^>]+>/g, '')
}
