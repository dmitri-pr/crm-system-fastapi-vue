from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from decimal import Decimal


class AdvertisementBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    product_id: int = Field(ge=1)
    promotion_channel: str = Field(min_length=1, max_length=255)
    budget: Decimal = Field(max_digits=10, decimal_places=2, ge=0)


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    product_id: int | None = Field(default=None, ge=1)
    promotion_channel: str | None = Field(default=None, min_length=1, max_length=255)
    budget: Decimal | None = Field(default=None, max_digits=10, decimal_places=2, ge=0)


class AdvertisementOut(BaseModel):
    id: int
    name: str
    product_id: int
    promotion_channel: str
    budget: float
    created_at: datetime
    updated_at: datetime
    product_name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class AdvertisementDetail(AdvertisementOut):
    leads_count: int | None = None
    customers_count: int | None = None
    profit: float | None = None


class AdvertisementStatsOut(BaseModel):
    id: int
    name: str
    product_name: str | None = None
    budget: float
    leads_count: int
    customers_count: int
    profit: float | None = None
    model_config = ConfigDict(from_attributes=True)
