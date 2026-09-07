from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class AdvertisementBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    product_id: int = Field(ge=1)
    promotion_channel: str = Field(min_length=1, max_length=255)
    budget: Decimal = Field(max_digits=10, decimal_places=2, ge=0)


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    product_id: Optional[int] = Field(default=None, ge=1)
    promotion_channel: Optional[str] = Field(default=None, min_length=1, max_length=255)
    budget: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, ge=0)


class AdvertisementOut(BaseModel):
    id: int
    name: str
    product_id: int
    promotion_channel: str
    budget: float
    created_at: datetime
    updated_at: datetime
    product_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AdvertisementDetail(AdvertisementOut):
    leads_count: Optional[int] = None
    customers_count: Optional[int] = None
    profit: Optional[float] = None


class AdvertisementStatsOut(BaseModel):
    id: int
    name: str
    product_name: Optional[str] = None
    budget: float
    leads_count: int
    customers_count: int
    profit: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)
