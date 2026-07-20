"""
用户认证路由
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
from typing import Annotated
import re
import time

from app.database import get_db
from app.utils.rate_limit import limiter
from app.models.models import User, UserRole, ActivationCode
from app.schemas.schemas import UserCreate, UserResponse, UserLogin, Token, MessageResponse, ForgotPasswordRequest
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ==================== 用户查询短时缓存 ====================
# 同一个 token 在 15 秒内只查一次 DB，避免前端页面加载并发 6+ 个请求时重复查 user
_user_cache: dict[str, tuple[float, User]] = {}
_USER_CACHE_TTL = 15  # 秒


def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前登录用户（带 15s 短时缓存）"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # 检查短时缓存
    cached = _user_cache.get(token)
    if cached:
        cached_at, cached_user = cached
        if time.time() - cached_at < _USER_CACHE_TTL:
            return cached_user

    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # 写入缓存
    _user_cache[token] = (time.time(), user)
    # 清理过期条目（防止内存泄漏）
    if len(_user_cache) > 200:
        now = time.time()
        expired = [k for k, (t, _) in _user_cache.items() if now - t > _USER_CACHE_TTL]
        for k in expired:
            del _user_cache[k]

    return user


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """获取当前管理员用户（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


@router.post("/register", response_model=MessageResponse)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册（需要激活码）"""
    # 验证手机号格式
    if not validate_phone(user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )

    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查手机号是否已存在
    result = await db.execute(select(User).where(User.phone == user_data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被注册"
        )

    if not user_data.invite_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入激活码"
        )

    result = await db.execute(
        select(ActivationCode).where(ActivationCode.code == user_data.invite_code)
    )
    activation_code_record = result.scalar_one_or_none()

    if not activation_code_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活码无效"
        )

    if activation_code_record.expires_at:
        # MySQL DATETIME 返回 naive datetime, 比较前统一加 UTC tz
        exp = activation_code_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="激活码已过期"
            )

    # 7-20: 原子扣 use_count (注册时必填激活码, 直接走 TOCTOU 防御)
    # 注意: MySQL DATETIME 列读出来是 naive, SQLAlchemy WHERE 跟 aware 必崩.
    # 这里用 naive 比较; 用户.activated_at 是 MySQL DATETIME 也会 strip tz, 兼容.
    # 两段式: 先 atomic 扣 use_count, flush user 后再 update used_by (user.id 当时还不存在)
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    atomic_update = await db.execute(
        update(ActivationCode)
        .where(
            ActivationCode.id == activation_code_record.id,
            ActivationCode.use_count < ActivationCode.max_uses,
            or_(ActivationCode.expires_at.is_(None), ActivationCode.expires_at > now_naive)
        )
        .values(
            use_count=ActivationCode.use_count + 1,
            used_at=now_naive
        )
    )
    if atomic_update.rowcount == 0:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活码已被使用或已过期"
        )

    user = User(
        username=user_data.username,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        activation_code_id=activation_code_record.id,
        status='approved',
        activated_at=datetime.now(timezone.utc)
    )

    db.add(user)
    await db.flush()

    # 7-20: 绑死 used_by (回填最后使用者, admin 列表展示用)
    await db.execute(
        update(ActivationCode)
        .where(ActivationCode.id == activation_code_record.id)
        .values(used_by=user.id)
    )

    await db.commit()
    await db.refresh(user)

    return MessageResponse(message="注册成功", success=True)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录（手机号+密码）"""
    # 验证手机号格式
    if not validate_phone(user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )

    # 查找用户
    result = await db.execute(select(User).where(User.phone == user_data.phone))
    user = result.scalar_one_or_none()

    if not user:
        # 故意跟"密码错误"返同样的 detail, 不泄露用户是否存在
        # (bcrypt 仍然要跑一次, 防 timing attack)
        get_password_hash("dummy")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # P1 安全: bcrypt 抛 Invalid salt 时返 401 而不是 500
    # (DB 哈希被截断/损坏时, 不应该让攻击者通过 500 错误区分)
    try:
        password_ok = verify_password(user_data.password, user.password_hash)
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"bcrypt verify failed for user {user.id}: {e}")
        password_ok = False

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建 Token (sub 必须是字符串)
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token)


@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """忘记密码重置 (P0 商业化必需)

    用户填: 手机号 + 注册时用的激活码 + 新密码
    验证: phone 找到 user, 且 user.activation_code_id 对应的 ActivationCode.code 匹配
    通过: 改 password_hash, 返 200
    失败: 返 400 通用错误 (不泄露码是否有效, 防止暴力枚举)
    """
    if not validate_phone(data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )

    if not data.invite_code or len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活码和新密码（至少 6 位）必填"
        )

    # 找用户
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()

    if user is None or user.activation_code_id is None:
        # 用户不存在 / 没绑定激活码 (admin 这种直接创建的用户)
        # 返通用错误, 防枚举
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活码与手机号不匹配"
        )

    # 验证激活码
    result = await db.execute(
        select(ActivationCode).where(ActivationCode.id == user.activation_code_id)
    )
    code_record = result.scalar_one_or_none()

    if code_record is None or str(code_record.code) != data.invite_code:
        # 激活码跟用户绑定的那个不匹配
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="激活码与手机号不匹配"
        )

    # 改密码
    user.password_hash = get_password_hash(data.new_password)
    await db.commit()

    return MessageResponse(message="密码已重置，请用新密码登录", success=True)


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户信息 (P0-8: 含激活码详情, 让前端能显示会员到期)"""
    from app.schemas.schemas import ActivationCodeInfo

    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return current_user

    # 嵌套激活码 (用 dict 而非 ORM 属性赋值, 避开 SQLAlchemy Column 推断)
    activation_code_info = None
    if user.activation_code_id is not None:
        ac_result = await db.execute(
            select(ActivationCode).where(ActivationCode.id == user.activation_code_id)
        )
        ac = ac_result.scalar_one_or_none()
        if ac:
            activation_code_info = ActivationCodeInfo(
                code=str(ac.code),
                expires_at=ac.expires_at,
                activated_at=user.activated_at,  # 用 user 表的 activated_at
                is_used=bool(ac.is_used) if ac.is_used is not None else False,
            )

    # 用 Pydantic .model_validate (Pydantic v2) 或 UserResponse(...) 构造响应
    # 这样 activation_code 嵌套字段能被序列化
    return UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        avatar=user.avatar,
        level=user.level or 1,
        role=user.role or 0,
        activation_code_id=user.activation_code_id,
        status=user.status or 'approved',
        activated_at=user.activated_at,
        created_at=user.created_at,
        activation_code=activation_code_info,
    )
