from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_session
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import Token, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    # verify_password теперь безопасный (возвращает False при ошибке), но ловим на всякий случай
    try:
        pwd_ok = verify_password(form_data.password, user.hashed_password) if user else False
    except Exception:
        pwd_ok = False
    if not user or not pwd_ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя или пароль")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь неактивен")
    # role может быть enum (UserRole), приводим к строковому значению
    role_val = user.role.value if hasattr(user.role, "value") else user.role
    access_token = create_access_token(data={"sub": user.username, "role": role_val})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserOut, status_code=201)
async def register_public():
    # публичная регистрация отключена - только админ создает пользователей
    raise HTTPException(status_code=403, detail="Регистрация только через администратора")
