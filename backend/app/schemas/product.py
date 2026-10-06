from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    cost: Decimal = Field(max_digits=10, decimal_places=2, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    cost: Decimal | None = Field(default=None, max_digits=10, decimal_places=2, ge=0)


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    cost: float
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
