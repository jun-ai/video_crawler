# Video Interpretation — AI Prompt 优化清单

> **目的**: 把 AI 生成的解读数据(单词/短语/语法/表达)从"看起来像 AI"提升到"贴近真人教学"。
> **触发位置**: `backend/app/services/deepseek.py` 4 个函数 (`generate_word_cards` / `generate_phrase_cards` / `generate_grammar_points` / `generate_idiom_cards`)
> **生效方式**: 用户在管理端触发"重新生成解读"时,新规则会覆盖旧数据。

---

## 1. 例句必须是视频出处句,不是字典例句

### 问题

AI 倾向用 Google Dictionary 提供的"标准句",跟视频内容没关系:

```
❌ figure out  例句: "I can't figure out how to use this machine."
   （字典例句,跟家居翻新视频无关）

✅ 应该: "We can't figure out three spots in this house."
   （取自视频字幕 sequence 3-4）
```

### 修改位置

4 个 prompt 都受影响 —— 都要在 JSON 字段说明里加这条约束:

```text
example_sentence (必填):
- **优先从上方字幕里挑一句原句当例句**(单条或合并相邻字幕),
  不要凭空造一个跟视频无关的"字典标准句"
- 如果字幕里实在没有合适的,可以造例句,但必须场景贴合视频主题
- 中文翻译跟字幕 CN 一致,不要额外润色
```

---

## 2. 音标必须匹配单词在字幕里的形态

### 问题

单词形态 (单复数 / 时态 / 进行时) 直接影响音标,AI 没区分:

```
❌ furnishing /ˈfɜːrnɪʃɪŋ/        (应该是复数 /ˈfɜːrnɪʃɪŋz/)
   tackled  /ˈtækl/                (过去时 /ˈtækld/)
   executing  /ˈeksɪkjuːt/         (doing /ˈeksɪkjuːtɪŋ/)
```

### 修改位置

`generate_word_cards` prompt 加一条:

```text
phonetic 必须跟上方字幕里实际出现的形态一致(单数/复数/过去式/进行时),
不能简单返回原形 (lemma form) 的音标。
例: 字幕里是 "furnishing our space" → phonetic 用名词复数 /ˈfɜːrnɪʃɪŋz/。
```

---

## 3. CN 翻译去"文学化",用口语

### 问题

AI 喜欢用成语 / 抽象大词,跟中阶学习者日常口语脱节:

```
❌ barren    → "空荡荡的;贫瘠的"
   (形容家居空间,用"贫瘠"太正式,口语说"空落落/了无生气")

❌ shine     → "大显身手,高光时刻"
   (原文是 "my skills will really shine",口语应该"展现/发挥")

❌ graveyard → "旧家具的乱葬岗"
   (口语描述性堆积,不该用"乱葬岗")
```

### 修改位置

`generate_word_cards` 和 `generate_phrase_cards` 共用一条约束(加到 `翻译规则`):

```text
**content_cn / content_cn 严禁用四字成语 / 抽象书面语**:
- 用日常口语中文: "空落落的", "展现出来", "堆得满满当当"
- 不要 "贫瘠 / 高光时刻 / 乱葬岗" 这种偏文学 / 偏书面 的词
- 反例 (差): barren → "空荡荡的;贫瘠的"
- 正例 (对): barren → "空落落的;什么也没有"
```

---

## 4. "举一反三 / 相似表达" 不要 placeholder 空句

### 问题

AI 用"我一直在工作 / 她一直在睡觉"这种无信息量句式占位:

```
❌ 举一反三: "现在完成时: 强调结果\n现在进行时: 强调此时此刻"
   (太抽象,等啥没说)

❌ 相似表达: "I have been working. (我一直在工作)
             She has been sleeping. (她一直在睡觉)"
   (空 placeholder,无任何场景信息)
```

### 修改位置

`generate_grammar_points` prompt 加一条,在 `similar_expressions` / `alternative_phrasings` 字段说明里:

```text
similar_expressions / alternative_phrasings:
- **禁止写 "I have been working. (我一直在工作)" 这种场景无关的占位句**
- 用视频里的真实场景或贴近视频主题的例句, 例如 "I've been furnishing this room for hours" (对家具翻新视频),
  "She's been napping since lunch" (对日常问候视频)
- 每个表达不超过 15 个英文单词 + 简短中文
```

---

## 5. 表达卡标题可读性,别太"学术"

### 问题

"Future in the Past (was/were going to)" 这种语法学名,对口语学习者来说太端着。
但**用户学语法确实需要这个术语**,所以保留,但副标题必须明确是中文释义。

### 修改位置

不需要改 AI prompt。表达卡前端显示已经标了"过去将来时" — 现在的歧义是 label 不够明显,可以前端 PR 改成"中文释义"。**已经做了** (v4 PDF 加了 "中文:" 前缀)。

---

## 6. 接收过滤空例句 / placeholder

### 问题

即使 prompt 改了,AI 偶尔还是输出"空 placeholder"。**后端需要在落库前过滤掉**:

```python
# 在 _resolve_subtitle 之后、保存到 VideoInterpretation 之前加一道防线
# example_sentence 是 "AI placeholder" 的常见模式:
PLACEHOLDER_PATTERNS = [
    re.compile(r"^\s*\([\u4e00-\u9fff]+\)\s*$"),                # 纯中文括号占位
    re.compile(r"^(I have been|She has been|They have been|He has been|You have been)\b", re.I),  # 标志性空句
    re.compile(r"^(我|他|她|它|你|我们)\s*(一直|正在)?\s*(在)?\s*(工作|睡觉|吃饭|学习)\s*[。.]?\s*$"),  # 中式空句
]

def _is_placeholder(s: str) -> bool:
    if not s:
        return False
    return any(p.match(s) for p in PLACEHOLDER_PATTERNS)
```

如果 `example_sentence` 命中 PLACEHOLDER_PATTERN,**用 `context_sentence` (字幕原句) 替换**,让 AI 不输出任何看似内容实则 placeholder 的句子。

---

## 7. 音标规范化 (release 内 LLM 不会更新)

音标有 AI 偶尔输出 "IPA 字符 (如 ɜ ʃ ɪ)" 但用得不准,建议**显示前归一化**,这个已在 `learn_card_export.py` 里做了 (font 注册 + 双重斜杠处理)。如有需要可以再补:
- 后置正则: 词典风格音标检查, 替换 AI 错误字符 (这个不优先)。

---

## 优先级

| 优先级 | 项 | 改动 |
|---|---|---|
| 🔴 P0 | #1 例句用字幕原句 | 4 个 prompt 都加 |
| 🔴 P0 | #3 CN 去文学化 | word + phrase prompt |
| 🟡 P1 | #2 音标形态一致 | word prompt |
| 🟡 P1 | #4 相似表达去 placeholder | grammar prompt |
| 🟢 P2 | #6 后端 placeholder 兜底过滤 | interpretation_tasks.py |
| ⚪ 低 | #5 表达卡 label | 前端 PR 已做 |

---

## 验证

按以上清单改完后:
1. 触发一支视频重新生成 (admin 端 `/interpretation/generate`)
2. 导出 PDF 看:
   - 例句是否跟字幕背景吻合
   - furnishing 是否带 z
   - barren / shine / graveyard 中文是否自然
   - 相似表达是否具体场景

不达标就继续迭代。
