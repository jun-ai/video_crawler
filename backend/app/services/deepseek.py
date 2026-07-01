"""
AI 服务 - 多 provider fallback
支持协议:
  - OpenAI 兼容 (DeepSeek / 智谱 GLM paas / OpenAI 自身等)
  - Anthropic 兼容 (智谱 GLM anthropic / MiniMax anthropic 等)

按优先级顺序自动切换:401/402/429/5xx/timeout → 切下一个 provider
每个 provider 独立熔断器(默认 5 分钟),互不影响
"""
import httpx
import json
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# ==================== Provider 列表(按优先级排序)====================
# 顺序就是 fallback 顺序:第一个失败 → 第二个 → 第三个
# 没配 api_key 的 provider 自动跳过
PROVIDERS = [
    {
        "name": "deepseek",
        "protocol": "openai",
        "base_url": settings.deepseek_base_url,
        "api_key": settings.deepseek_api_key,
        "model": settings.deepseek_model,
        "unavailable_until": 0.0,
        "lock": asyncio.Lock(),
    },
    {
        "name": "glm",
        "protocol": "anthropic",
        "base_url": settings.glm_base_url,
        "api_key": settings.glm_api_key,
        "model": settings.glm_model,
        "unavailable_until": 0.0,
        "lock": asyncio.Lock(),
    },
    {
        "name": "minimax",
        "protocol": "openai",  # MiniMax 走 OpenAI 协议 (Authorization Bearer)
        "base_url": settings.minimax_base_url,
        "api_key": settings.minimax_api_key,
        "model": settings.minimax_model,
        "unavailable_until": 0.0,
        "lock": asyncio.Lock(),
    },
]

# 熔断时长:触发后 5 分钟内不再尝试这个 provider
_CIRCUIT_BREAKER_SECONDS = 300

# 重试时长
_RETRYABLE_STATUS_CODES = {401, 402, 403, 408, 413, 429, 500, 502, 503, 504}


def _available_providers():
    """返回当前可用(provider 配了 key 且没在熔断中)的 provider 列表"""
    now = time.time()
    return [
        p for p in PROVIDERS
        if p["api_key"] and now > p["unavailable_until"]
    ]


def _trip_provider(provider: dict, reason: str):
    """熔断单个 provider"""
    provider["unavailable_until"] = time.time() + _CIRCUIT_BREAKER_SECONDS
    logger.warning(
        f"[AI] provider '{provider['name']}' 熔断 {_CIRCUIT_BREAKER_SECONDS}s "
        f"({reason}) — 自动 fallback 到下一个"
    )


def _parse_json_response(content: str) -> Any:
    """从 AI 返回中提取 JSON(支持 markdown 代码块)"""
    if "```json" in content:
        json_str = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_str = content.split("```")[1].split("```")[0].strip()
    else:
        json_str = content.strip()
    return json.loads(json_str)


# ==================== OpenAI 协议调用 ====================

async def _call_openai(provider: dict, system_prompt: str, user_prompt: str,
                       max_tokens: int, temperature: float) -> str:
    """调用 OpenAI 兼容协议(DeepSeek / 智谱 paas 等)"""
    async with provider["lock"]:
        if time.time() < provider["unavailable_until"]:
            raise Exception(f"provider {provider['name']} 熔断中")

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    f"{provider['base_url']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {provider['api_key']}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": provider["model"],
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                _trip_provider(provider, f"网络/超时: {type(e).__name__}")
                raise

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

            if response.status_code in _RETRYABLE_STATUS_CODES:
                snippet = response.text[:200].replace("\n", " ")
                _trip_provider(provider, f"HTTP {response.status_code} - {snippet[:120]}")
                raise Exception(
                    f"{provider['name']} HTTP {response.status_code}: {snippet}"
                )

            raise Exception(
                f"{provider['name']} HTTP {response.status_code}: {response.text[:200]}"
            )


# ==================== Anthropic 协议调用 ====================

async def _call_anthropic(provider: dict, system_prompt: str, user_prompt: str,
                          max_tokens: int, temperature: float) -> str:
    """调用 Anthropic 兼容协议(智谱 anthropic / MiniMax anthropic 等)"""
    async with provider["lock"]:
        if time.time() < provider["unavailable_until"]:
            raise Exception(f"provider {provider['name']} 熔断中")

        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                # Anthropic 用 max_tokens(必填),不接受 temperature 范围外值
                body = {
                    "model": provider["model"],
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_prompt},
                    ],
                }
                # temperature 是可选的,Anthropic 默认 1.0
                if temperature is not None:
                    body["temperature"] = temperature

                response = await client.post(
                    f"{provider['base_url']}/v1/messages",
                    headers={
                        "x-api-key": provider["api_key"],
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                _trip_provider(provider, f"网络/超时: {type(e).__name__}")
                raise

            if response.status_code == 200:
                # Anthropic 返回 content 是数组 [{type, text}, ...]
                data = response.json()
                content_blocks = data.get("content", [])
                text_parts = [
                    b.get("text", "")
                    for b in content_blocks
                    if b.get("type") == "text"
                ]
                return "\n".join(text_parts)

            if response.status_code in _RETRYABLE_STATUS_CODES:
                snippet = response.text[:200].replace("\n", " ")
                _trip_provider(provider, f"HTTP {response.status_code} - {snippet[:120]}")
                raise Exception(
                    f"{provider['name']} HTTP {response.status_code}: {snippet}"
                )

            raise Exception(
                f"{provider['name']} HTTP {response.status_code}: {response.text[:200]}"
            )


# ==================== 统一调用入口 ====================

async def _call_one_provider(provider: dict, system_prompt: str, user_prompt: str,
                            max_tokens: int, temperature: float) -> str:
    """根据 provider 协议分发"""
    if provider["protocol"] == "openai":
        return await _call_openai(provider, system_prompt, user_prompt, max_tokens, temperature)
    elif provider["protocol"] == "anthropic":
        return await _call_anthropic(provider, system_prompt, user_prompt, max_tokens, temperature)
    else:
        raise ValueError(f"未知协议: {provider['protocol']}")


async def _call_ai(system_prompt: str, user_prompt: str,
                   max_tokens: int = 4000, temperature: float = 0.3) -> str:
    """
    统一调用 AI,自动 fallback
    遍历 PROVIDERS,跳过没配 key 或在熔断中的,试到成功为止
    全失败 → raise 最后一个错误
    """
    available = _available_providers()
    if not available:
        raise Exception(
            "所有 AI provider 都不可用(未配置或全部熔断中)。"
            "请检查 DEEPSEEK_API_KEY / GLM_API_KEY / MINIMAX_API_KEY 配置"
        )

    last_error: Optional[Exception] = None
    for p in available:
        try:
            content = await _call_one_provider(p, system_prompt, user_prompt, max_tokens, temperature)
            if p["name"] != PROVIDERS[0]["name"]:
                logger.info(f"[AI] {p['name']} 响应成功(fallback 路径)")
            return content
        except Exception as e:
            last_error = e
            logger.warning(f"[AI] {p['name']} 调用失败: {e}")
            continue

    raise Exception(f"所有 AI provider 调用失败: {last_error}")


# 兼容旧接口名
_call_deepseek = _call_ai


# ==================== 单词卡片生成 ====================

async def generate_word_cards(subtitles: List[Dict[str, Any]]) -> List[Dict]:
    """
    从字幕中提取重点单词,返回结构化单词卡片数据。
    """
    subtitle_text = "\n".join([
        f"[{s['sequence']}] {s['text_en']} | {s.get('text_cn', '')}"
        for s in subtitles
    ])

    if len(subtitle_text) > 5000:
        subtitle_text = subtitle_text[:5000] + "\n..."

    prompt = f"""你是一位母语中文的资深英语教师,正在从一段视频字幕里挑出对中国学习者最有价值的单词,做成学习卡片。

字幕(每行:[序号] 英文 | 中文翻译, EN+CN 配套展示,用来判断单词在视频里的实际含义):
{subtitle_text}

请挑 8-15 个学习价值最高的单词。返回 JSON 数组,每个元素:
{{
    "content_en": "paddle",
    "phonetic": "/ˈpædl/",
    "part_of_speech": "n.",
    "content_cn": "n. 球拍",
    "english_definition": "a flat tool used for hitting the ball in table tennis",
    "subtitle_sequence": 3,
    "other_pos_definitions": "v. 划船",
    "difficulty": 2,
    "frequency_rank": 3500
}}

翻译规则(关键):
1. **content_cn 用视频语境下最贴切的那个义,别把所有词典义项都抄过来**
   - 反例(差): paddle → "n. 球拍" + other_pos = "v. 划船;v. 涉水;v. 拍水" (词典罗列)
   - 正例(对): 看视频里 paddle 是打乒乓球 → content_cn = "n. 球拍", other_pos = "v. 划船" (只列本视频未用到的其他主要词性)
2. content_cn 词性用 n./v./adj./adv. 等缩写,多个义项最多 2 个且用分号隔开,**不要 4-5 个义项大杂烩**
3. english_definition 写一句简单英文解释,只解释最常用意
4. frequency_rank 估算词频排名(1-10000): 数字越小越常见(the=1, apple≈1500, ephemeral≈8000)
5. 跳过基础词 (a/the/is/and/it 等),不要凑数
6. 只返回 JSON 数组, 不要其他文字"""

    try:
        content = await _call_ai(
            system_prompt="你是一位母语中文的英语老师,帮中国学生从视频里挑值得记的单词。你只返回JSON格式数据。",
            user_prompt=prompt,
            max_tokens=4000,
            temperature=0.3
        )
        return _parse_json_response(content)
    except Exception as e:
        logger.error(f"[AI] generate_word_cards failed: {e}")
        raise


# ==================== 短语卡片生成 ====================

async def generate_phrase_cards(subtitles: List[Dict[str, Any]]) -> List[Dict]:
    """从字幕中提取重点短语,返回结构化短语卡片数据。"""
    subtitle_text = "\n".join([
        f"[{s['sequence']}] {s['text_en']} | {s.get('text_cn', '')}"
        for s in subtitles
    ])

    if len(subtitle_text) > 5000:
        subtitle_text = subtitle_text[:5000] + "\n..."

    prompt = f"""你是一位母语中文的资深英语口语老师,擅长教中国学生怎么用地道的英语短语/搭配。从一段英语视频字幕里挑出 5-10 个**最有学习价值**的短语/搭配(动词短语、习语、固定搭配)。

字幕(每行:[序号] 英文 | 中文翻译, EN+CN 配套,用来判断短语在视频里的具体用法):
{subtitle_text}

请挑最有学习价值的 5-10 个短语。返回 JSON 数组,每个元素:
{{
    "content_en": "get back into it",
    "phonetic": "/ɡet bæk ˈɪntu ɪt/",
    "content_cn": "回到正事,继续刚才的活儿",
    "example_sentence": "OK, break's over—let's get back into it. (休息完了,继续刚才的事)",
    "synonyms": "resume",
    "subtitle_sequence": 24,
    "difficulty": 2
}}

翻译规则(关键,直接影响学习体验):
1. **content_cn 严禁写"phr." / "习语" / "口语" 这些字典标签**,直接写中文释义,1-2 句话讲清楚是什么意思
2. **必须看字幕的 EN+CN 配套来定译文,翻译要"贴合视频里的用法",不要写脱离语境的字典释义**
   - 反例(差,就是当前问题): get back into it → "phr. 重新投入;回到(某种状态)" (字典式 + 分号罗列 + 抽象)
   - 正例(对): get back into it → "回到正事,继续刚才的活儿" (结合视频里"refreshed, we're going to get back into it"这个语境)
3. **不要用分号";" 罗列多个近义同义释义** — 这会让卡片看起来像词典不像口语教学
4. **example_sentence 必填** — 造一个简单的英文句子 + 中文翻译, 帮学生记住短语的典型用法(1 行,60 字符以内)
5. **synonyms 同义短语最多 1-2 个**,没有就不写; 列的是短语不是单词(列 "resume" 比列 "go back" 更典型)
6. phonetic 用国际音标, /.../ 包起来
7. subtitle_sequence 必须是上面字幕的序号 (这个短语出现的最早位置)
8. difficulty 1-5: 1=基础短语, 3=中级, 5=地道母语级
9. 只返回 JSON 数组, 不要其他文字"""

    try:
        content = await _call_ai(
            system_prompt="你是一位母语中文的英语口语老师,帮中国学生理解并记住地道英语短语。你只返回JSON格式数据。",
            user_prompt=prompt,
            max_tokens=3000,
            temperature=0.3
        )
        return _parse_json_response(content)
    except Exception as e:
        logger.error(f"[AI] generate_phrase_cards failed: {e}")
        raise


# ==================== 语法点生成 ====================

async def generate_grammar_points(subtitles: List[Dict[str, Any]]) -> List[Dict]:
    """从字幕中提取语法点"""
    text = " ".join([s.get("text_en", "") for s in subtitles])
    if len(text) > 3000:
        text = text[:3000] + "..."

    prompt = f"""分析以下英语视频字幕,提取 2-3 个值得学习的语法点。每个语法点用**结构化字段**填,不要把所有内容塞进 explanation 一个字段。

字幕内容:
{text}

返回 JSON 数组,每个元素:
{{
    "content_en": "Present Perfect vs Past Simple",
    "content_cn": "现在完成时与一般过去时的区别",
    "subtitle_sequence": 5,
    "structure_analysis": "have/has + 过去分词 vs 一般过去时用动词过去式",
    "similar_expressions": "现在完成进行时: 强调动作持续\\n一般过去时: 强调动作发生过",
    "usage_scenario": "日常对话 / 视频叙事 / 邮件回复 工作汇报",
    "alternative_phrasings": "I have done it. (现在完成时) | I did it. (一般过去时)",
    "example_sentence": "I have been to Paris. (现在完成时) vs I went to Paris last year. (一般过去时)",
    "difficulty": 3
}}

【重要】不要在 JSON 里加 explanation 字段! 解释全部用下面的结构化字段表达,后端会自动按顺序拼成一段可读的解释:
1. **structure_analysis (必填, 1 句话, 短公式)**: 讲清结构公式, 例 "have/has been + doing"。这是这张卡的"标题句"
2. **similar_expressions (必填, 1-3 个, 用 \\n 分隔)**: 相关语法/用法对比。例如"现在完成进行时: 强调动作持续\\n一般过去时: 强调动作发生过"。每个对比 1 句话, 不要写很长的解释
3. **usage_scenario (必填, 1 句话)**: 讲常见使用场景 (日常对话 / 视频叙事 / 邮件回复 / 工作汇报 等)
4. **alternative_phrasings (必填, 1-3 个, 用 \\n 分隔)**: 英文例句, 用 "I have done it. (现在完成时)" 这种格式直接给, 不需要详细解释
5. **example_sentence (必填)**: 带中文翻译的英文例句
6. difficulty 1-5
7. **JSON 格式注意**: 字段值要用真换行 ("\\n" 实际是 1 个字符), 不要写成字符串 "\\\\n" (2 个字符)
8. 只返回 JSON 数组, 不要其他文字"""

    try:
        content = await _call_ai(
            system_prompt="你是一个母语中文的英语语法老师,擅长把复杂语法用简单中文讲明白。你会按字段分门别类输出,不让内容堆在一个字段里。",
            user_prompt=prompt,
            max_tokens=2500,
            temperature=0.5
        )
        return _parse_json_response(content)
    except Exception as e:
        logger.error(f"[AI] generate_grammar_points failed: {e}")
        raise


# ==================== 地道表达卡片生成 ====================

async def generate_idiom_cards(subtitles: List[Dict[str, Any]]) -> List[Dict]:
    """从字幕中提取地道表达(习语、俚语、口语表达)"""
    subtitle_text = "\n".join([
        f"[{s['sequence']}] {s['text_en']} | {s.get('text_cn', '')}"
        for s in subtitles
    ])

    if len(subtitle_text) > 5000:
        subtitle_text = subtitle_text[:5000] + "\n..."

    prompt = f"""你是一位母语中文的英语口语老师,专攻习语/俚语/口语表达。从一段英语视频字幕里挑出 3-5 个**真正地道**的英语表达(idiom / slang / colloquialism)。

字幕(每行:[序号] 英文 | 中文翻译,用来判断该地道表达在视频里的具体用法):
{subtitle_text}

请挑最有代表性的 3-5 个地道表达。返回 JSON 数组,每个元素:
{{
    "content_en": "hit the nail on the head",
    "content_cn": "一针见血,说得太准了",
    "subtitle_sequence": 12,
    "explanation": "这个表达源自木工活,形容把钉子精确地敲进正确位置,比喻说话或做事非常准确。中国学生日常聊天可以直接说'你说得太准了'。",
    "origin": "源自木工行业,指用锤子准确地敲击钉子的头部。14世纪开始在英语中使用。",
    "example_sentence": "You really hit the nail on the head with that analysis.",
    "difficulty": 3
}}

翻译规则:
1. **content_cn 写地道自然的中文,不要";"罗列多个近义词** (反例: "一针见血;说到点子上;切中要害" 词典罗列)
   - 正例: "一针见血,说得太准了" (口语 + 接地气)
2. **subtitle_sequence (必填)**: 这个地道表达最早出现的字幕序号 (1-based, 对应上方字幕里 [N] 里的数字)。如果不填用户看不到具体出处
3. **explanation (必填)**: 详细解释该表达的用法 + 中国学生怎么在日常聊天里替换它 (比方说 "形容说话非常准确,口语里你可以直接说'你说得太对了'")
4. **origin (必填)**: 介绍文化背景 (1-2 句话讲来源 / 词根 / 历史典故)。没有明确来源的就写"民间口语流传,具体出处已不可考"
5. **example_sentence (必填)**: 造一个地道的使用例句 (英文, 可附简短中文翻译)
6. **difficulty 1-5**: 1=日常常见 3=中等地道 5=非常口语化/罕见
7. 只返回 JSON 数组, 不要其他文字"""

    try:
        content = await _call_ai(
            system_prompt="你是一位母语中文的英语口语老师,专攻习语和俚语。你只返回JSON格式数据。",
            user_prompt=prompt,
            max_tokens=3000,
            temperature=0.3
        )
        return _parse_json_response(content)
    except Exception as e:
        logger.error(f"[AI] generate_idiom_cards failed: {e}")
        raise


# ==================== 编排器:并行生成全部 ====================

async def generate_all_interpretations(subtitles: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """
    并行生成单词卡片 + 短语卡片 + 语法点 + 地道表达卡片。
    返回 { "words": [...], "phrases": [...], "grammar": [...], "idioms": [...] }
    """
    results = await asyncio.gather(
        generate_word_cards(subtitles),
        generate_phrase_cards(subtitles),
        generate_grammar_points(subtitles),
        generate_idiom_cards(subtitles),
        return_exceptions=True,
    )

    words = results[0] if not isinstance(results[0], Exception) else []
    phrases = results[1] if not isinstance(results[1], Exception) else []
    grammar = results[2] if not isinstance(results[2], Exception) else []
    idioms = results[3] if not isinstance(results[3], Exception) else []

    for i, r in enumerate(results):
        if isinstance(r, Exception):
            names = ["words", "phrases", "grammar", "idioms"]
            logger.error(f"[AI] {names[i]} generation failed: {r}")

    return {
        "words": words if isinstance(words, list) else [],
        "phrases": phrases if isinstance(phrases, list) else [],
        "grammar": grammar if isinstance(grammar, list) else [],
        "idioms": idioms if isinstance(idioms, list) else [],
    }


# ==================== 兼容旧接口 ====================

async def generate_interpretation(subtitles: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """兼容旧调用方式"""
    return await generate_all_interpretations(subtitles)


# ==================== 发音评测 ====================

async def evaluate_pronunciation(spoken_text: str, expected_text: str) -> Dict[str, Any]:
    """评测用户发音"""
    available = _available_providers()
    if not available:
        return {
            "score": 70,
            "accuracy": "评估服务暂时不可用",
            "fluency": "请稍后重试",
            "problems": ["所有 AI provider 都不可用"],
            "suggestions": ["请检查 API key 配置或稍后重试"],
        }

    prompt = f"""请作为一个专业的英语口语老师,评估学生的发音练习。

学生应该说的句子:
"{expected_text}"

学生实际说的内容(语音识别结果):
"{spoken_text}"

请评估学生的发音并给出反馈。以 JSON 格式返回:
{{
    "score": 85,
    "accuracy": "准确度评价",
    "fluency": "流利度评价",
    "problems": ["problem1", "problem2"],
    "suggestions": ["建议1", "建议2"]
}}

要求:
1. score 范围 0-100
2. problems 列出具体的发音问题(2-3个)
3. suggestions 给出改进建议(2-3个)
4. 如果差异很大,score 应该较低
5. 只返回 JSON"""

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英语口语教练,擅长评估学生的发音并给出建设性反馈。",
            user_prompt=prompt,
            max_tokens=500,
            temperature=0.5
        )
        return _parse_json_response(content)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"[AI] evaluate_pronunciation failed: {e}")
        return {
            "score": 70,
            "accuracy": "无法精确评估",
            "fluency": "请重试",
            "problems": ["评估服务暂时不可用"],
            "suggestions": ["请稍后重试"],
        }


# ==================== 字幕翻译 ====================

async def translate_subtitles(subtitles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """批量翻译字幕"""
    if not _available_providers():
        return subtitles

    texts = [sub.get("text_en", "") for sub in subtitles]
    combined_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])

    prompt = f"""请将以下英语句子翻译成中文。保持翻译自然、准确、口语化。

{combined_text}

请以 JSON 数组格式返回翻译结果,只包含翻译文本:
["翻译1", "翻译2", "翻译3", ...]

注意:只返回 JSON 数组,不要其他内容。数组长度必须与输入句子数量一致。"""

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英汉翻译助手,擅长翻译日常口语和对话。",
            user_prompt=prompt,
            max_tokens=3000,
            temperature=0.3
        )
        translations = _parse_json_response(content)
        result_subtitles = []
        for i, sub in enumerate(subtitles):
            new_sub = dict(sub)
            if i < len(translations):
                new_sub["text_cn"] = translations[i]
            result_subtitles.append(new_sub)
        return result_subtitles
    except (json.JSONDecodeError, KeyError, Exception) as e:
        logger.error(f"[AI] translate_subtitles failed: {e}")
        return subtitles


# ==================== 单词查询 ====================

async def lookup_word(word: str) -> Dict[str, str]:
    """查询单词的音标、释义和例句"""
    if not _available_providers():
        return {"phonetic": "", "translation": word, "example": ""}

    prompt = f"""请查询单词 "{word}" 的信息,以 JSON 格式返回:
{{
    "phonetic": "音标,如 /ˈwɜːrd/",
    "translation": "中文释义,多个释义用分号分隔",
    "example": "一个简单的英语例句"
}}

要求:1. phonetic 使用国际音标  2. 只返回 JSON"""

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英语词典助手。",
            user_prompt=prompt,
            max_tokens=300,
            temperature=0.3
        )
        return _parse_json_response(content)
    except Exception as e:
        logger.error(f"[AI] lookup_word failed: {e}")
        return {"phonetic": "", "translation": word, "example": ""}


# ==================== 文本翻译 ====================

async def translate_text(text: str) -> Dict[str, str]:
    """翻译文本"""
    if not _available_providers():
        return {"translation": text}

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英汉翻译助手。",
            user_prompt=f'请将以下英语翻译成中文:\n\n"{text}"\n\n只返回翻译结果,不要其他内容。',
            max_tokens=200,
            temperature=0.3
        )
        return {"translation": content.strip()}
    except Exception as e:
        logger.error(f"[AI] translate_text failed: {e}")
        return {"translation": text}


# ==================== 服务状态 ====================

def get_deepseek_service() -> bool:
    """兼容旧接口:返回是否有任何 AI provider 可用"""
    return len(_available_providers()) > 0


def get_ai_providers_status() -> Dict[str, Any]:
    """返回所有 provider 状态(供 admin 查看)"""
    now = time.time()
    return {
        "providers": [
            {
                "name": p["name"],
                "protocol": p["protocol"],
                "model": p["model"],
                "configured": bool(p["api_key"]),
                "available": bool(p["api_key"]) and now > p["unavailable_until"],
                "unavailable_seconds_left": max(0, int(p["unavailable_until"] - now)),
            }
            for p in PROVIDERS
        ],
        "any_available": len(_available_providers()) > 0,
    }
