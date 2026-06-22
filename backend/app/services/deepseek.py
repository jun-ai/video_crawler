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
        "protocol": "anthropic",
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

    prompt = f"""你是一位专业的英语教学AI,正在分析一个英语学习视频的字幕,需要提取重点单词。

字幕内容(每行格式:[序号] 英文 | 中文翻译):
{subtitle_text}

请提取 8-15 个适合中国英语学习者学习的重点单词。返回 JSON 数组,每个元素格式:
{{
    "content_en": "paddle",
    "phonetic": "/ˈpædl/",
    "part_of_speech": "n.",
    "content_cn": "n. 球拍",
    "english_definition": "a flat tool used for hitting the ball in table tennis",
    "subtitle_sequence": 3,
    "other_pos_definitions": "v. 划船;涉水",
    "difficulty": 2,
    "frequency_rank": 3500
}}

规则:
1. 选择有学习价值的词,跳过基础词(a/the/is/and 等)
2. phonetic 使用国际音标格式,带斜杠
3. part_of_speech 用缩写:n./v./adj./adv./prep./conj./interj.
4. content_cn 格式为 "词性. 中文释义",多个释义用分号分隔
5. english_definition 用简单英文解释
6. subtitle_sequence 必须是上面字幕的序号,表示该词首次出现的位置
7. other_pos_definitions 列出其他词性的释义,没有则设为 null
8. difficulty 1-5:1=初学 3=中级 5=高级
9. frequency_rank 估算该词在英语中的词频排名(1-10000),数字越小越常见,如 the=1, apple≈1500, ephemeral≈8000
10. 只返回 JSON 数组,不要其他文字"""

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英语教学助手,擅长从视频字幕中提取词汇并生成学习卡片。你只返回JSON格式数据。",
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

    prompt = f"""你是一位专业的英语教学AI,正在分析一个英语学习视频的字幕,需要提取常用短语和搭配。

字幕内容(每行格式:[序号] 英文 | 中文翻译):
{subtitle_text}

请提取 5-10 个常用短语或搭配。返回 JSON 数组,每个元素格式:
{{
    "content_en": "shoot off",
    "phonetic": "/ʃuːt ɒf/",
    "content_cn": "phr. 匆忙离开;赶紧走",
    "synonyms": "rush off, hurry away, leave quickly",
    "subtitle_sequence": 12,
    "difficulty": 2
}}

规则:
1. 选择有学习价值的短语/搭配/习语,不只是简单组合
2. phonetic 使用国际音标
3. content_cn 格式为 "phr. 中文释义"
4. synonyms 用英文近义词,逗号分隔,2-4个
5. subtitle_sequence 必须是上面字幕的序号
6. difficulty 1-5
7. 只返回 JSON 数组"""

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英语教学助手,擅长从视频字幕中提取短语和搭配并生成学习卡片。你只返回JSON格式数据。",
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

    prompt = f"""分析以下英语视频字幕,提取 2-3 个值得学习的语法点。

字幕内容:
{text}

返回 JSON 数组,每个元素:
{{
    "content_en": "Present Perfect vs Past Simple",
    "content_cn": "现在完成时与一般过去时的区别",
    "explanation": "详细解释该语法点的用法...",
    "example_sentence": "I have been to Paris. (现在完成时) vs I went to Paris last year. (一般过去时)",
    "difficulty": 3
}}

规则:
1. 选择视频中实际出现的语法现象
2. explanation 要详细,用中文解释
3. example_sentence 可以结合字幕内容
4. difficulty 1-5
5. 只返回 JSON 数组"""

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英语语法教学助手。",
            user_prompt=prompt,
            max_tokens=2000,
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

    prompt = f"""你是一位专业的英语教学AI,正在分析一个英语学习视频的字幕,需要提取地道表达(习语、俚语、口语表达)。

字幕内容(每行格式:[序号] 英文 | 中文翻译):
{subtitle_text}

请提取 3-5 个地道表达、俚语或口语表达。返回 JSON 数组,每个元素格式:
{{
    "content_en": "hit the nail on the head",
    "content_cn": "一针见血;说到点子上",
    "explanation": "这个表达源自木工活,形容把钉子精确地敲进正确位置,比喻说话或做事非常准确。",
    "origin": "源自木工行业,指用锤子准确地敲击钉子的头部。14世纪开始在英语中使用。",
    "example_sentence": "You really hit the nail on the head with that analysis.",
    "difficulty": 3
}}

规则:
1. 选择有学习价值的地道表达,包括习语(idioms)、俚语(slang)、口语表达(colloquialisms)
2. content_cn 给出简洁准确的中文翻译
3. explanation 用中文详细解释该表达的用法和使用场景
4. origin 介绍该表达的来源或文化背景
5. example_sentence 提供一个自然的使用例句
6. difficulty 1-5:1=日常常见 3=中等地道 5=非常口语化/罕见
7. 只返回 JSON 数组"""

    try:
        content = await _call_ai(
            system_prompt="你是一个专业的英语教学助手,擅长从视频字幕中提取地道表达和文化内涵并生成学习卡片。你只返回JSON格式数据。",
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
