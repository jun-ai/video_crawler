from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import foreign
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class DifficultyLevel(enum.IntEnum):
    """难度等级"""
    BEGINNER = 1      # 初级
    ELEMENTARY = 2    # 基础
    INTERMEDIATE = 3  # 中级
    UPPER = 4         # 中高级
    ADVANCED = 5      # 高级


class UserRole(enum.IntEnum):
    """用户角色"""
    USER = 0        # 普通用户
    ADMIN = 1       # 管理员


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)  # 手机号
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    level = Column(Integer, default=1)
    role = Column(Integer, default=UserRole.USER)  # 用户角色
    is_active = Column(Boolean, default=True)
    activation_code_id = Column(Integer, nullable=True)
    status = Column(String(20), default='approved')  # pending/approved/rejected
    activated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    learning_records = relationship("LearningRecord", back_populates="user")
    vocabularies = relationship("Vocabulary", back_populates="user")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    interpretation_learning_records = relationship("InterpretationLearning", back_populates="user", cascade="all, delete-orphan")
    dictation_records = relationship("DictationRecord", back_populates="user", cascade="all, delete-orphan")
    subtitle_annotations = relationship("SubtitleAnnotation", back_populates="user", cascade="all, delete-orphan")
    subtitle_bookmarks = relationship("SubtitleBookmark", back_populates="user", cascade="all, delete-orphan")


class Material(Base):
    """语料表"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    video_path = Column(String(500), nullable=False)    # 扩展长度支持URL
    subtitle_path = Column(String(500), nullable=False)
    cover_path = Column(String(500), nullable=False)
    storage_type = Column(String(20), default='local')  # local, aliyun_oss, tencent_cos
    video_size = Column(Integer, nullable=True)         # 视频文件大小(字节)
    category = Column(String(50), nullable=True, index=True)
    difficulty = Column(Integer, default=2)
    duration = Column(Integer, nullable=True)           # 时长(秒)
    view_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    interpretation_status = Column(String(20), default='pending')  # pending, generating, done, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    subtitles = relationship("Subtitle", back_populates="material", cascade="all, delete-orphan")
    learning_records = relationship("LearningRecord", back_populates="material")
    favorites = relationship("Favorite", back_populates="material", cascade="all, delete-orphan")
    interpretations = relationship("VideoInterpretation", back_populates="material", cascade="all, delete-orphan")
    vocabularies = relationship("Vocabulary", back_populates="material")
    tags = relationship("MaterialTag", back_populates="material", cascade="all, delete-orphan")


class Subtitle(Base):
    """字幕句子表"""
    __tablename__ = "subtitles"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    sequence = Column(Integer, nullable=False)  # 句子序号
    start_time = Column(Integer, nullable=False)  # 开始时间(毫秒)
    end_time = Column(Integer, nullable=False)    # 结束时间(毫秒)
    text_en = Column(Text, nullable=False)        # 英文文本
    text_cn = Column(Text, nullable=True)         # 中文翻译
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    material = relationship("Material", back_populates="subtitles")
    vocabularies = relationship("Vocabulary", back_populates="subtitle")
    annotations = relationship("SubtitleAnnotation", back_populates="subtitle", cascade="all, delete-orphan")
    bookmarks = relationship("SubtitleBookmark", back_populates="subtitle", cascade="all, delete-orphan")


class LearningRecord(Base):
    """学习记录表"""
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    progress = Column(Integer, default=0)       # 学习进度(%)
    last_position = Column(Integer, default=0)  # 上次播放位置(秒)
    watch_duration = Column(Integer, default=0) # 累计观看秒数
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)    # 完成时间
    last_watched_at = Column(DateTime(timezone=True), nullable=True)  # 最后观看时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    user = relationship("User", back_populates="learning_records")
    material = relationship("Material", back_populates="learning_records")


class Vocabulary(Base):
    """生词本表"""
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True)
    subtitle_id = Column(Integer, ForeignKey("subtitles.id"), nullable=True)
    word = Column(String(100), nullable=False, index=True)
    context = Column(Text, nullable=True)      # 上下文句子
    mastered = Column(Boolean, default=False)
    # 5-P2-5: 重点词标记 (用户主动 star 的词, 与 mastered 是两个维度)
    # mastered = 客观算法判定已掌握, starred = 用户主观标记重点
    starred = Column(Boolean, default=False, index=True)
    # SM-2 间隔重复字段
    next_review_at = Column(DateTime(timezone=True), nullable=True)  # 下次复习时间
    review_count = Column(Integer, default=0)                        # 复习次数
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True) # 上次复习时间
    ease_factor = Column(Float, default=2.5)                          # SM-2 易度因子
    interval_days = Column(Integer, default=0)                        # 复习间隔天数
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    user = relationship("User", back_populates="vocabularies")
    subtitle = relationship("Subtitle", back_populates="vocabularies")
    material = relationship("Material", back_populates="vocabularies")


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    type = Column(String(20), nullable=False)  # 'creator' or 'topic'
    color = Column(String(20), default='#5c6ef5')  # 标签颜色
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MaterialTag(Base):
    """材料-标签关联表"""
    __tablename__ = "material_tags"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    # 关联
    material = relationship("Material", back_populates="tags")
    tag = relationship("Tag")


class Favorite(Base):
    """收藏表"""
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    user = relationship("User", back_populates="favorites")
    material = relationship("Material", back_populates="favorites")


class VideoInterpretation(Base):
    """视频解读内容表"""
    __tablename__ = "video_interpretations"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(20), nullable=False, index=True)  # 'word', 'phrase', 'grammar', 'idiom'
    content_en = Column(String(500), nullable=False)  # 英文内容
    content_cn = Column(String(500), nullable=True)   # 中文翻译/解释
    explanation = Column(Text, nullable=True)          # 详细解释
    example_sentence = Column(Text, nullable=True)     # 例句
    difficulty = Column(Integer, default=2)            # 难度 1-5
    sequence = Column(Integer, default=0)              # 排序
    timestamp = Column(Integer, nullable=True)          # 视频时间戳（毫秒），用于跳转
    # --- 富字段（AI 预生成时填充） ---
    phonetic = Column(String(100), nullable=True)           # 音标 /rɪˈtɜːn/
    part_of_speech = Column(String(50), nullable=True)      # 词性 n. / v. / adj.
    english_definition = Column(Text, nullable=True)         # 英英释义
    synonyms = Column(String(500), nullable=True)            # 同义词，逗号分隔
    subtitle_id = Column(Integer, ForeignKey("subtitles.id", ondelete="SET NULL"), nullable=True)
    first_appearance_time = Column(Integer, nullable=True)   # 首次出现的毫秒时间
    context_sentence = Column(Text, nullable=True)           # 原始字幕句子
    context_translation = Column(Text, nullable=True)        # 该句中文翻译
    other_pos_definitions = Column(Text, nullable=True)      # 其他词性释义
    structure_analysis = Column(Text, nullable=True)          # 结构解析（语法用）
    similar_expressions = Column(Text, nullable=True)         # 举一反三（语法用）
    usage_scenario = Column(Text, nullable=True)              # 使用场景（语法用）
    alternative_phrasings = Column(Text, nullable=True)       # 相似表达（语法用）
    frequency_rank = Column(Integer, nullable=True)           # 词频排名（越低越常见）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    material = relationship("Material", back_populates="interpretations")
    source_subtitle = relationship("Subtitle", foreign_keys=[subtitle_id])
    learning_status_records = relationship("InterpretationLearning", back_populates="interpretation", cascade="all, delete-orphan")


class InterpretationLearning(Base):
    """解读项学习状态"""
    __tablename__ = "interpretation_learning"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    interpretation_id = Column(Integer, ForeignKey("video_interpretations.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="unknown")  # known, unknown, vague
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    user = relationship("User", back_populates="interpretation_learning_records")
    interpretation = relationship("VideoInterpretation", back_populates="learning_status_records")


class DictationRecord(Base):
    """听写练习记录表"""
    __tablename__ = "dictation_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    subtitle_id = Column(Integer, ForeignKey("subtitles.id"), nullable=False)
    user_input = Column(Text, nullable=False)           # 用户输入
    correct_text = Column(Text, nullable=False)         # 正确答案
    score = Column(Integer, default=0)                  # 得分 0-100
    accuracy_details = Column(Text, nullable=True)      # 逐词校验结果 JSON
    passed = Column(Boolean, default=False)             # 是否通过
    attempts = Column(Integer, default=1)               # 尝试次数
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    user = relationship("User", back_populates="dictation_records")
    subtitle = relationship("Subtitle")


class SubtitleAnnotation(Base):
    """字幕标注表 - 用户标注重点词汇/短语"""
    __tablename__ = "subtitle_annotations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    subtitle_id = Column(Integer, ForeignKey("subtitles.id"), nullable=False, index=True)
    start_offset = Column(Integer, nullable=False)      # 标注文本在字幕中的起始位置
    end_offset = Column(Integer, nullable=False)        # 标注文本在字幕中的结束位置
    annotated_text = Column(String(200), nullable=False) # 标注的文本内容
    annotation_type = Column(String(20), nullable=False) # 标注类型: 'vocabulary', 'phrase', 'important'
    note = Column(Text, nullable=True)                   # 用户备注
    color = Column(String(20), default='#ff0000')       # 高亮颜色
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    user = relationship("User", back_populates="subtitle_annotations")
    subtitle = relationship("Subtitle", back_populates="annotations")


class SubtitleBookmark(Base):
    """字幕收藏表 - 用户收藏单个字幕行"""
    __tablename__ = "subtitle_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    subtitle_id = Column(Integer, ForeignKey("subtitles.id"), nullable=False, index=True)
    note = Column(Text, nullable=True)                   # 用户备注
    practice_count = Column(Integer, default=0)          # 跟读练习次数
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    user = relationship("User", back_populates="subtitle_bookmarks")
    subtitle = relationship("Subtitle", back_populates="bookmarks")
    material = relationship("Material")


class ActivationCode(Base):
    """激活码表"""
    __tablename__ = "activation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    max_uses = Column(Integer, default=1)
    use_count = Column(Integer, default=0)
    created_by = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Announcement(Base):
    """公告表"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(20), default='info')       # info/warning/success/update
    priority = Column(Integer, default=0)            # 0=普通, 1=重要, 2=紧急
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
