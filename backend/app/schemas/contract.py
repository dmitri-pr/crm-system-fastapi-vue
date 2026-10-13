from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date, datetime
from decimal import Decimal


class ContractBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    product_id: int = Field(ge=1)
    start_date: date = Field(
        description="Дата начала (должна быть не позже даты окончания)",
        examples=["2026-01-01"],
    )
    end_date: date = Field(
        description="Дата окончания (должна быть не раньше даты начала)",
        examples=["2026-12-31"],
    )
    cost: Decimal = Field(
        max_digits=10,
        decimal_places=2,
        ge=0,
        description="Стоимость, ≥ 0, до 2 знаков после запятой",
        examples=["75000.00"],
    )

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    product_id: int | None = Field(default=None, ge=1)
    start_date: date | None = Field(default=None, description="Новая дата начала")
    end_date: date | None = Field(default=None, description="Новая дата окончания")
    cost: Decimal | None = Field(
        default=None,
        max_digits=10,
        decimal_places=2,
        ge=0,
        description="Новая стоимость, ≥ 0",
    )

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    product_id: int
    start_date: date
    end_date: date
    cost: float
    document: str | None = Field(
        default=None,
        description="Путь к файлу вида /media/contracts/<uuid>.ext или null",
    )
    created_at: datetime
    updated_at: datetime
    product_name: str | None = None
