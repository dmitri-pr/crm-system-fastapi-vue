from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

from app.schemas.lead import LeadOut
from app.schemas.contract import ContractOut


class CustomerBase(BaseModel):
    lead_id: int = Field(ge=1)
    contract_id: int = Field(ge=1)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    contract_id: Optional[int] = Field(default=None, ge=1)


class CustomerOut(BaseModel):
    id: int
    lead_id: int
    contract_id: int
    created_at: datetime
    updated_at: datetime
    lead: Optional[LeadOut] = None
    contract: Optional[ContractOut] = None
    model_config = ConfigDict(from_attributes=True)


class CustomerListOut(BaseModel):
    id: int
    lead_id: int
    contract_id: int
    created_at: datetime
    lead_first_name: Optional[str] = None
    lead_last_name: Optional[str] = None
    lead_email: Optional[str] = None
    lead_phone: Optional[str] = None
    contract_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
