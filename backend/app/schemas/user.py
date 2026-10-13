from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=150,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Уникальный логин: только латиница, цифры, '_' и '-'. Пробелы по краям обрезаются",
        examples=["john_doe"],
    )
    email: EmailStr = Field(
        description="Email; приводится к нижнему регистру",
        examples=["john@mail.com"],
    )
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(
        default=UserRole.manager,
        description="Роль: admin — полный доступ, operator — лиды, marketer — товары и реклама, manager — договоры и клиенты",
        examples=["manager"],
    )

    @field_validator("username", "email", "full_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("email", mode="after")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Пароль минимум 8 символов; пробелы по краям не обрезаются — вводите одинаково при регистрации и входе",
        examples=["Str0ngPass!"],
    )
    is_active: bool = Field(
        default=True,
        description="false — вход пользователя запрещён",
    )
    is_superuser: bool = Field(
        default=False,
        description="true допустим только вместе с ролью admin",
    )


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(
        default=None,
        description="Новый email; приводится к нижнему регистру",
    )
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole | None = Field(
        default=None,
        description="Новая роль пользователя",
    )
    is_active: bool | None = Field(
        default=None,
        description="false — вход пользователя запрещён",
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="Новый пароль минимум 8 символов; пробелы по краям не обрезаются",
    )

    @field_validator("email", "full_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("email", mode="after")
    @classmethod
    def lowercase_email(cls, v: str | None) -> str | None:
        return v.lower() if isinstance(v, str) else v


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
