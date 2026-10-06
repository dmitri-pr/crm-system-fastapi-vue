from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime


class LeadBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    patronymic: str | None = Field(default=None, max_length=100)
    phone: str = Field(min_length=5, max_length=20, pattern=r"^\+?[0-9\s\-\(\)]+$")
    email: EmailStr
    advertisement_id: int | None = Field(default=None, ge=1)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    patronymic: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, min_length=5, max_length=20, pattern=r"^\+?[0-9\s\-\(\)]+$")
    email: EmailStr | None = None
    advertisement_id: int | None = Field(default=None, ge=1)


class LeadOut(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime
    advertisement_name: str | None = None
    is_converted: bool = False
    model_config = ConfigDict(from_attributes=True)
