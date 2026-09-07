from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional


class LeadBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    patronymic: Optional[str] = Field(default=None, max_length=100)
    phone: str = Field(min_length=5, max_length=20, pattern=r"^\+?[0-9\s\-\(\)]+$")
    email: EmailStr
    advertisement_id: Optional[int] = Field(default=None, ge=1)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    patronymic: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=5, max_length=20, pattern=r"^\+?[0-9\s\-\(\)]+$")
    email: Optional[EmailStr] = None
    advertisement_id: Optional[int] = Field(default=None, ge=1)


class LeadOut(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime
    advertisement_name: Optional[str] = None
    is_converted: bool = False
    model_config = ConfigDict(from_attributes=True)
