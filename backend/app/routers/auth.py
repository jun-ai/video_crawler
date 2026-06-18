"""
用户认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
import re
import time

from app.database import get_db
from app.utils.rate_limit import limiter
from app.models.models import User, UserRole, ActivationCode
from app.schemas.schemas import UserCreate, UserResponse, UserLogin, Token, MessageResponse
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from datetime import datetime, timezone

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

    # 验证激活码
    activation_code_record = None
    if user_data.invite_code:
        result = await db.execute(
            select(ActivationCode).where(ActivationCode.code == user_data.invite_code)
        )
        activation_code_record = result.scalar_one_or_none()

        if not activation_code_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="激活码无效"
            )

        if activation_code_record.use_count >= activation_code_record.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="激活码已用完"
            )

        if activation_code_record.expires_at and activation_code_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="激活码已过期"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入激活码"
        )

    # 创建用户
    user = User(
        username=user_data.username,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        activation_code_id=activation_code_record.id if activation_code_record else None,
        status='approved',
        activated_at=datetime.now(timezone.utc)
    )

    db.add(user)
    await db.flush()

    # 更新激活码使用计数
    if activation_code_record:
        activation_code_record.use_count += 1
        activation_code_record.used_by = user.id
        activation_code_record.used_at = datetime.now(timezone.utc)

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

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建 Token (sub 必须是字符串)
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token)


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """获取当前用户信息"""
    return current_user
