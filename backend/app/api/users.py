from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_session
from app.core.dependencies import get_current_user, require_roles
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserOut])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(["admin"])),
):
    result = await session.execute(select(User).order_by(User.id).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(["admin"])),
):
    # check uniqueness
    result = await session.execute(select(User).where((User.username == payload.username) | (User.email == payload.email)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с таким username или email уже существует")
    # валидация role теперь выполняется Pydantic через UserRole Enum
    if payload.is_superuser and payload.role != UserRole.admin:
        raise HTTPException(status_code=400, detail="Только admin может быть superuser")
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role.value,
        is_active=payload.is_active,
        is_superuser=payload.is_superuser if payload.role == UserRole.admin else False,
        hashed_password=get_password_hash(payload.password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Пользователь с таким username или email уже существует")
    await session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    _role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if current_user.id != user_id and _role != "admin" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(["admin"])),
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if payload.email is not None:
        dup = await session.execute(select(User).where(User.email == payload.email, User.id != user_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email уже занят другим пользователем")
        user.email = payload.email
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.role is not None:
        # валидация role уже выполнена Pydantic (UserRole Enum)
        user.role = payload.role.value
        # Синхронизируем is_superuser с ролью
        if payload.role == UserRole.admin:
            # оставляем как есть, но если ранее не был superuser, можно повысить
            pass
        else:
            user.is_superuser = False
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.hashed_password = get_password_hash(payload.password)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Конфликт данных: email уже существует")
    await session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(["admin"])),
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")
    await session.delete(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Не удалось удалить пользователя")
    return None
