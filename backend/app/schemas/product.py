from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    cost: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        ge=0,
        description="Стоимость, ≥ 0, до 2 знаков после запятой",
        examples=["120000.00"],
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    cost: Decimal | None = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        ge=0,
        description="Новая стоимость, ≥ 0",
    )


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    cost: float = Field(description="Стоимость (на выходе сериализуется как float)")
    created_at: datetime
    updated_at: datetime
