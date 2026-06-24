from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any


# ==================== User Schemas ====================

class UserBase(BaseModel):
    username: str
    phone: str


class UserCreate(UserBase):
    password: str
    invite_code: Optional[str] = None  # 激活码


class UserLogin(BaseModel):
    phone: str       # 手机号登录
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    phone: str
    avatar: Optional[str] = None
    level: Optional[int] = 1
    role: int = 0  # 用户角色：0普通用户，1管理员
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ==================== Material Schemas ====================

class MaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: int = 2


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    """管理后台更新语料信息（所有字段可选）"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[int] = None
    duration: Optional[int] = None
    is_active: Optional[bool] = None


class TagResponse(BaseModel):
    """标签响应"""
    id: int
    name: str
    type: str  # 'creator' or 'topic'
    color: str = '#5c6ef5'
    display_order: int = 0

    class Config:
        from_attributes = True


class MaterialResponse(MaterialBase):
    id: int
    video_path: str
    subtitle_path: str
    cover_path: str
    duration: Optional[int] = None
    view_count: int = 0
    is_active: bool = True  # 是否已发布
    interpretation_status: Optional[str] = 'pending'  # pending, generating, done, failed
    tags: List[TagResponse] = []  # 关联的标签
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialListResponse(BaseModel):
    items: List[MaterialResponse]
    total: int
    page: int
    page_size: int


# ==================== Subtitle Schemas ====================

class SubtitleBase(BaseModel):
    sequence: int
    start_time: int
    end_time: int
    text_en: str
    text_cn: Optional[str] = None


class SubtitleCreate(SubtitleBase):
    material_id: int


class SubtitleResponse(SubtitleBase):
    id: int
    material_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Learning Record Schemas ====================

class LearningRecordBase(BaseModel):
    # 允许 null (前端视频 metadata 未加载时 NaN→null 序列化),默认 0
    progress: Optional[int] = 0
    last_position: Optional[int] = 0
    watch_duration: Optional[int] = None  # 本次上报的观看秒数（增量）
    completed: Optional[bool] = False


class LearningRecordCreate(LearningRecordBase):
    material_id: int


# ==================== 直传 OSS presign / finalize ====================

class PresignUploadRequest(BaseModel):
    """前端请求预签名 URL 时发送的文件元信息"""
    video_name: str
    subtitle_name: str
    cover_name: str


class PresignedFileInfo(BaseModel):
    url: str        # 前端用这个 PUT 文件到 OSS
    key: str        # OSS 对象键
    content_type: str


class PresignUploadResponse(BaseModel):
    video: PresignedFileInfo
    subtitle: PresignedFileInfo
    cover: PresignedFileInfo


class FinalizeUploadRequest(BaseModel):
    """前端直传完成后,调这个接口创建 Material 记录"""
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: int = 2
    video_key: str
    subtitle_key: str
    cover_key: str


class LearningRecordResponse(LearningRecordBase):
    id: int
    user_id: int
    material_id: int
    total_watch_duration: int = 0  # 累计观看秒数
    completed_at: Optional[datetime] = None
    last_watched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== Vocabulary Schemas ====================

class VocabularyBase(BaseModel):
    word: str
    context: Optional[str] = None


class VocabularyCreate(VocabularyBase):
    material_id: Optional[int] = None
    subtitle_id: Optional[int] = None


class VocabularyResponse(VocabularyBase):
    id: int
    user_id: int
    material_id: Optional[int] = None
    material_title: Optional[str] = None  # 语料标题
    subtitle_id: Optional[int] = None
    mastered: bool = False
    context_cn: Optional[str] = None  # 中文翻译
    # SM-2 间隔重复字段
    next_review_at: Optional[datetime] = None
    review_count: int = 0
    last_reviewed_at: Optional[datetime] = None
    ease_factor: float = 2.5
    interval_days: int = 0
    created_at: datetime
    # 6 档 quality 对应的下次复习天数 (review-queue 填,其他端点可空)
    # key 是 quality (0-5), value 是天数。前端只展示不重算。
    next_intervals: Optional[Dict[str, int]] = None

    class Config:
        from_attributes = True


# ==================== Common Schemas ====================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class CategoryResponse(BaseModel):
    name: str
    count: int


# ==================== Video Interpretation Schemas ====================

class InterpretationBase(BaseModel):
    category: str  # 'word', 'phrase', 'grammar', 'idiom'
    content_en: str
    content_cn: Optional[str] = None
    explanation: Optional[str] = None
    example_sentence: Optional[str] = None
    difficulty: int = 2
    # 富字段
    phonetic: Optional[str] = None
    part_of_speech: Optional[str] = None
    english_definition: Optional[str] = None
    synonyms: Optional[str] = None
    subtitle_id: Optional[int] = None
    first_appearance_time: Optional[int] = None
    context_sentence: Optional[str] = None
    context_translation: Optional[str] = None
    other_pos_definitions: Optional[str] = None
    structure_analysis: Optional[str] = None
    similar_expressions: Optional[str] = None
    usage_scenario: Optional[str] = None
    alternative_phrasings: Optional[str] = None
    frequency_rank: Optional[int] = None
    timestamp: Optional[int] = None


class InterpretationCreate(InterpretationBase):
    material_id: int
    sequence: int = 0


class InterpretationResponse(InterpretationBase):
    id: int
    material_id: int
    sequence: int
    created_at: datetime

    class Config:
        from_attributes = True


class InterpretationListResponse(BaseModel):
    words: List[InterpretationResponse] = []
    phrases: List[InterpretationResponse] = []
    grammar: List[InterpretationResponse] = []
    idioms: List[InterpretationResponse] = []


class PronunciationEvaluateRequest(BaseModel):
    spoken_text: str  # 用户说的话（语音识别结果）
    expected_text: str  # 期望的文本（原字幕）


class PronunciationEvaluateResponse(BaseModel):
    score: int  # 评分 0-100
    accuracy: str  # 准确度评价
    fluency: str  # 流利度评价
    problems: List[str] = []  # 发音问题
    suggestions: List[str] = []  # 改进建议





# ==================== 解读项学习状态 ====================

class InterpretationLearningBase(BaseModel):
    status: str = "unknown"  # known, unknown, vague


class InterpretationLearningCreate(InterpretationLearningBase):
    interpretation_id: int
    material_id: int


class InterpretationLearningResponse(InterpretationLearningBase):
    id: int
    user_id: int
    interpretation_id: int
    material_id: int
    content_en: str
    content_cn: Optional[str] = None
    category: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 学习统计 Schemas ====================

class LearningStatisticsResponse(BaseModel):
    """学习统计响应"""
    total_materials: int = 0           # 学习过的材料总数
    completed_materials: int = 0       # 已完成的材料数
    in_progress_materials: int = 0     # 学习中的材料数
    total_vocabulary: int = 0          # 生词总数
    mastered_vocabulary: int = 0       # 已掌握生词数
    total_learning_days: int = 0       # 累计学习天数
    this_week_learning_days: int = 0   # 本周学习天数
    streak_days: int = 0               # 连续学习天数
    total_watch_minutes: int = 0       # 累计观看分钟数


class LearningCalendarResponse(BaseModel):
    """学习日历响应"""
    dates: List[str] = []              # 有学习记录的日期列表 (YYYY-MM-DD)
    streak: int = 0                    # 当前连续学习天数
    max_streak: int = 0                # 历史最长连续天数
    total_days: int = 0                # 累计学习天数
    monthly_minutes: int = 0           # 当月累计观看分钟数
    daily_counts: Dict[str, int] = {}   # 每日学习材料数量 {YYYY-MM-DD: count}


class LearningTrendResponse(BaseModel):
    """学习趋势响应"""
    dates: List[str] = []              # 日期列表 (YYYY-MM-DD)
    counts: List[int] = []              # 每日学习材料数量


class LearningRecordWithMaterialResponse(BaseModel):
    """带材料信息的学习记录响应"""
    id: int
    user_id: int
    material_id: int
    progress: int = 0
    last_position: int = 0
    completed: bool = False
    total_watch_duration: int = 0  # 累计观看秒数
    created_at: datetime
    updated_at: Optional[datetime] = None
    # 材料信息
    material_title: str
    material_cover: Optional[str] = None
    material_category: Optional[str] = None
    material_difficulty: int = 2
    material_duration: Optional[int] = None

    class Config:
        from_attributes = True


class LearningRecordListResponse(BaseModel):
    """学习记录列表响应"""
    items: List[LearningRecordWithMaterialResponse]
    total: int
    page: int
    page_size: int


class BatchIdsRequest(BaseModel):
    """4-P1-5: 批量操作通用请求体 (删除/收藏等)"""
    ids: List[int]


class DashboardResponse(BaseModel):
    """LearningCenter 仪表盘合并响应 (3.1)

    一次返回 5 个视图所需数据,前端从 5 HTTP → 1 HTTP。
    - statistics: 9 个核心指标 (含 streak_days)
    - trend: 最近 7 天每日学习材料数
    - recent: 最近 10 条未完成记录
    - completed: 最近 10 条已完成记录
    - records: 第一页 10 条全部记录(分页用)
    """
    statistics: "LearningStatisticsResponse"
    trend: "LearningTrendResponse"
    recent: List["LearningRecordWithMaterialResponse"]
    completed: List["LearningRecordWithMaterialResponse"]
    records: "LearningRecordListResponse"


# ==================== 语音识别 Schemas ====================

class SpeechRecognizeResponse(BaseModel):
    """语音识别响应"""
    success: bool
    recognized_text: str = ""
    confidence: float = 0.0
    pronunciation_result: Optional[PronunciationEvaluateResponse] = None
    error: Optional[str] = None


# ==================== 听写练习 Schemas ====================

class DictationSubmitRequest(BaseModel):
    """听写提交请求"""
    material_id: int
    subtitle_id: int
    user_input: str


class DictationResultDetail(BaseModel):
    """单词级别的校验结果"""
    text: str
    correct: bool
    type: str  # 'correct', 'missing', 'extra', 'wrong'


class DictationSubmitResponse(BaseModel):
    """听写提交响应"""
    id: int
    user_input: str
    correct_text: str
    score: int
    passed: bool
    details: List[DictationResultDetail]
    feedback: str


class DictationRecordResponse(BaseModel):
    """听写记录响应"""
    id: int
    material_id: int
    subtitle_id: int
    user_input: str
    correct_text: str
    score: int
    passed: bool
    attempts: int
    created_at: datetime

    class Config:
        from_attributes = True


class DictationStatisticsResponse(BaseModel):
    """听写统计响应"""
    total_attempts: int
    passed_count: int
    average_score: float


# ==================== 字幕标注 Schemas ====================

class SubtitleAnnotationBase(BaseModel):
    """字幕标注基础"""
    start_offset: int
    end_offset: int
    annotated_text: str
    annotation_type: str = 'vocabulary'  # 'vocabulary', 'phrase', 'important'
    note: Optional[str] = None
    color: str = '#ff0000'


class SubtitleAnnotationCreate(SubtitleAnnotationBase):
    """创建字幕标注"""
    material_id: int
    subtitle_id: int


class SubtitleAnnotationResponse(SubtitleAnnotationBase):
    """字幕标注响应"""
    id: int
    user_id: int
    material_id: int
    subtitle_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SubtitleAnnotationListResponse(BaseModel):
    """字幕标注列表响应"""
    items: List[SubtitleAnnotationResponse]
    total: int


# ==================== Interpretation Status Schema ====================

class InterpretationStatusResponse(BaseModel):
    """解读生成状态响应"""
    material_id: int
    status: str  # pending, generating, done, failed
    words_count: int = 0
    phrases_count: int = 0
    grammar_count: int = 0
    idioms_count: int = 0


# ==================== 字幕收藏 Schemas ====================

class SubtitleBookmarkCreate(BaseModel):
    """创建字幕收藏"""
    material_id: int
    subtitle_id: int
    note: Optional[str] = None
    folder_id: Optional[int] = None  # 5-P1-2 (后缀): 可选指定所属文件夹


class SubtitleBookmarkUpdate(BaseModel):
    """5-P1-2: 更新字幕收藏 (目前只支持 note)"""
    note: Optional[str] = None
    folder_id: Optional[int] = None  # 5-P1-2 (后缀): 移动到文件夹 (None=移出)


class SubtitleBookmarkResponse(BaseModel):
    """字幕收藏响应"""
    id: int
    user_id: int
    material_id: int
    subtitle_id: int
    note: Optional[str] = None
    practice_count: int = 0
    last_practiced_at: Optional[datetime] = None
    created_at: datetime
    # 关联的字幕信息
    subtitle_text_en: Optional[str] = None
    subtitle_text_cn: Optional[str] = None
    subtitle_start_time: Optional[int] = None
    # 关联的视频信息（/bookmarks/all 端点填充）
    material_title: Optional[str] = None
    material_cover: Optional[str] = None
    # 5-P1-2: 用户标签 (bookmark 维度)
    tags: List[Dict[str, Any]] = []
    # 5-P1-2 (后缀): 文件夹 (bookmark 所属文件夹, nullable)
    folder_id: Optional[int] = None
    folder_name: Optional[str] = None
    folder_color: Optional[str] = None

    class Config:
        from_attributes = True


class UserTagResponse(BaseModel):
    """5-P1-2: 用户标签响应"""
    id: int
    name: str
    color: str = '#5c6ef5'
    usage_count: int = 0  # 被多少个 bookmark 使用

    class Config:
        from_attributes = True


class UserTagCreateRequest(BaseModel):
    """5-P1-2: 创建标签"""
    name: str
    color: Optional[str] = None


class BookmarkTagsRequest(BaseModel):
    """5-P1-2: 设置 bookmark 的标签 (按名字, 自动创建不存在的)"""
    tag_names: List[str]


# ==================== 5-P1-2 (后缀): 收藏文件夹 Schemas ====================

class BookmarkFolderResponse(BaseModel):
    """文件夹响应 (含 bookmark 数量)"""
    id: int
    name: str
    color: str = '#5c6ef5'
    icon: str = 'folder'
    sort_order: int = 0
    bookmark_count: int = 0  # 该文件夹下 bookmark 数量
    created_at: datetime

    class Config:
        from_attributes = True


class BookmarkFolderCreateRequest(BaseModel):
    """创建文件夹"""
    name: str
    color: Optional[str] = None
    icon: Optional[str] = None


class BookmarkFolderUpdateRequest(BaseModel):
    """更新文件夹 (部分更新)"""
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class BookmarkMoveFolderRequest(BaseModel):
    """移动 bookmark 到文件夹 (folder_id=null 表示移出文件夹)"""
    folder_id: Optional[int] = None


class BatchMoveFolderRequest(BaseModel):
    """批量移动 bookmarks 到文件夹"""
    ids: List[int]
    folder_id: Optional[int] = None


# ==================== 生词复习 Schemas ====================

class ReviewSubmitRequest(BaseModel):
    """复习提交请求"""
    vocabulary_id: int
    quality: int  # 0-5 (0=完全不记得, 5=完美回忆)


class ReviewQueueResponse(BaseModel):
    """复习队列响应"""
    items: List[VocabularyResponse]
    total_due: int       # 待复习数量
    total_learning: int  # 学习中的数量


class ReviewStatsResponse(BaseModel):
    """复习统计响应"""
    total_due: int        # 待复习
    total_learning: int   # 学习中
    total_mastered: int   # 已掌握


# ==================== 激活码 Schemas ====================

class ActivationCodeResponse(BaseModel):
    """激活码响应"""
    id: int
    code: str
    is_used: bool
    used_by: Optional[int] = None
    used_at: Optional[datetime] = None
    max_uses: int = 1
    use_count: int = 0
    created_by: Optional[int] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateCodesRequest(BaseModel):
    """批量生成激活码请求"""
    count: int = 1          # 生成数量
    max_uses: int = 1       # 每个码最大使用次数
    expires_days: Optional[int] = None  # 有效期天数，None 表示永不过期


# ==================== 公告 Schemas ====================

class AnnouncementResponse(BaseModel):
    """公告响应"""
    id: int
    title: str
    content: str
    type: str = 'info'
    priority: int = 0
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class AnnouncementCreate(BaseModel):
    """创建公告请求"""
    title: str
    content: str
    type: str = 'info'      # info/warning/success/update
    priority: int = 0       # 0=普通, 1=重要, 2=紧急


class AnnouncementUpdate(BaseModel):
    """更新公告请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
