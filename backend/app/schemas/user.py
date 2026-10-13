from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=150, pattern=r"^[a-zA-Z0-9_\-]+$")
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.manager)

    @field_validator("username", "email", "full_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("email", mode="after")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole | None = Field(default=None)
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

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
