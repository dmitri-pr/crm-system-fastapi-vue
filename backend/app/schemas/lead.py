from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime


class LeadBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    patronymic: str | None = Field(default=None, max_length=100)
    phone: str = Field(
        min_length=5,
        max_length=20,
        pattern=r"^\+?[0-9\s\-\(\)]+$",
        description="Телефон: цифры, пробелы, '-', '()', в начале может быть '+'",
        examples=["+7 999 123-45-67"],
    )
    email: EmailStr
    advertisement_id: int | None = Field(
        default=None,
        ge=1,
        description="ID рекламы-источника; можно не указывать",
    )


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    patronymic: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(
        default=None,
        min_length=5,
        max_length=20,
        pattern=r"^\+?[0-9\s\-\(\)]+$",
        description="Новый телефон в том же формате",
    )
    email: EmailStr | None = None
    advertisement_id: int | None = Field(
        default=None,
        ge=1,
        description="Новый ID рекламы-источника",
    )


class LeadOut(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    advertisement_name: str | None = None
    is_converted: bool = Field(
        default=False,
        description="true — лид уже преобразован в клиента",
    )
