from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    cost: Decimal = Field(max_digits=10, decimal_places=2, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    cost: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, ge=0)


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    cost: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
