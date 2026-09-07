from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    if not isinstance(username, str) or not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


# RBAC
ROLE_PERMISSIONS = {
    "admin": {"*"},
    "operator": {
        "leads:read", "leads:create", "leads:update", "leads:delete",
        "contracts:read",  # менеджер смотрит? но оператор не должен? даем минимум
        "stats:read",
        "products:read", "ads:read", "customers:read",
    },
    "marketer": {
        "products:read", "products:create", "products:update", "products:delete",
        "ads:read", "ads:create", "ads:update", "ads:delete",
        "stats:read",
        "leads:read", "contracts:read", "customers:read",
    },
    "manager": {
        "contracts:read", "contracts:create", "contracts:update", "contracts:delete",
        "customers:read", "customers:create", "customers:update", "customers:delete",
        "leads:read", "products:read", "ads:read",
        "stats:read",
    },
}


def has_permission(user: User, permission: str) -> bool:
    if user.role == "admin" or user.is_superuser:
        return True
    perms = ROLE_PERMISSIONS.get(user.role, set())
    return permission in perms or "*" in perms


def require_permissions(permissions: List[str]):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser or current_user.role == "admin":
            return current_user
        user_perms = ROLE_PERMISSIONS.get(current_user.role, set())
        for p in permissions:
            if p not in user_perms:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Недостаточно прав: требуется {p} (ваша роль: {current_user.role})")
        return current_user
    return checker


def require_roles(roles: List[str]):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser or current_user.role == "admin":
            return current_user
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Требуется роль одна из: {', '.join(roles)} (ваша: {current_user.role})")
        return current_user
    return checker
