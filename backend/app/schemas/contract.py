from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class ContractBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    product_id: int = Field(ge=1)
    start_date: date
    end_date: date
    cost: Decimal = Field(max_digits=10, decimal_places=2, ge=0)

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    product_id: Optional[int] = Field(default=None, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cost: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, ge=0)

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self


class ContractOut(BaseModel):
    id: int
    name: str
    product_id: int
    start_date: date
    end_date: date
    cost: float
    document: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    product_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
