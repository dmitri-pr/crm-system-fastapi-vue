from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_session
from app.core.dependencies import get_current_user, require_permissions
from app.models.user import User
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.contract import Contract
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut

router = APIRouter(prefix="/customers", tags=["customers"])


def to_out(cust: Customer) -> CustomerOut:
    from app.schemas.lead import LeadOut
    from app.schemas.contract import ContractOut
    lead_out = None
    if cust.lead:
        lead_out = LeadOut(
            id=cust.lead.id,
            first_name=cust.lead.first_name,
            last_name=cust.lead.last_name,
            patronymic=cust.lead.patronymic,
            phone=cust.lead.phone,
            email=cust.lead.email,
            advertisement_id=cust.lead.advertisement_id,
            created_at=cust.lead.created_at,
            updated_at=cust.lead.updated_at,
            advertisement_name=cust.lead.advertisement.name if cust.lead.advertisement else None,
            is_converted=True,
        )
    contract_out = None
    if cust.contract:
        contract_out = ContractOut(
            id=cust.contract.id,
            name=cust.contract.name,
            product_id=cust.contract.product_id,
            start_date=cust.contract.start_date,
            end_date=cust.contract.end_date,
            cost=float(cust.contract.cost),
            document=cust.contract.document,
            created_at=cust.contract.created_at,
            updated_at=cust.contract.updated_at,
            product_name=cust.contract.product.name if cust.contract.product else None,
        )
    return CustomerOut(
        id=cust.id,
        lead_id=cust.lead_id,
        contract_id=cust.contract_id,
        created_at=cust.created_at,
        updated_at=cust.updated_at,
        lead=lead_out,
        contract=contract_out,
    )


@router.get("", response_model=List[CustomerOut])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Customer)
        .options(
            selectinload(Customer.lead).selectinload(Lead.advertisement),
            selectinload(Customer.contract).selectinload(Contract.product),
        )
        .order_by(Customer.id.desc()).offset(skip).limit(limit)
    )
    customers = result.scalars().all()
    return [to_out(c) for c in customers]


@router.post("", response_model=CustomerOut, status_code=201)
async def create_customer(
    payload: CustomerCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["customers:create"])),
):
    if payload.lead_id <= 0 or payload.contract_id <= 0:
        raise HTTPException(status_code=400, detail="Некорректные ID")
    lead = await session.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=400, detail="Лид не найден")
    existing = await session.execute(select(Customer).where(Customer.lead_id == payload.lead_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Этот лид уже конвертирован в активного клиента")
    contract = await session.get(Contract, payload.contract_id)
    if not contract:
        raise HTTPException(status_code=400, detail="Контракт не найден")
    cust = Customer(lead_id=payload.lead_id, contract_id=payload.contract_id)
    session.add(cust)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Этот лид уже конвертирован (гонка)")
    await session.refresh(cust)
    result = await session.execute(
        select(Customer)
        .options(
            selectinload(Customer.lead).selectinload(Lead.advertisement),
            selectinload(Customer.contract).selectinload(Contract.product),
        )
        .where(Customer.id == cust.id)
    )
    cust = result.scalar_one()
    return to_out(cust)


@router.get("/available/leads", response_model=List[dict])
async def available_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Lead).outerjoin(Customer, Customer.lead_id == Lead.id).where(Customer.id.is_(None)).order_by(Lead.id.desc()).offset(skip).limit(limit)
    )
    leads = result.scalars().all()
    return [
        {
            "id": l.id,
            "first_name": l.first_name,
            "last_name": l.last_name,
            "patronymic": l.patronymic,
            "email": l.email,
            "phone": l.phone,
            "advertisement_id": l.advertisement_id,
        }
        for l in leads
    ]


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Customer)
        .options(
            selectinload(Customer.lead).selectinload(Lead.advertisement),
            selectinload(Customer.contract).selectinload(Contract.product),
        )
        .where(Customer.id == customer_id)
    )
    cust = result.scalar_one_or_none()
    if not cust:
        raise HTTPException(status_code=404, detail="Активный клиент не найден")
    return to_out(cust)


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["customers:update"])),
):
    result = await session.execute(
        select(Customer)
        .options(
            selectinload(Customer.lead).selectinload(Lead.advertisement),
            selectinload(Customer.contract).selectinload(Contract.product),
        )
        .where(Customer.id == customer_id)
    )
    cust = result.scalar_one_or_none()
    if not cust:
        raise HTTPException(status_code=404, detail="Активный клиент не найден")
    data = payload.model_dump(exclude_unset=True)
    if "contract_id" in data and data["contract_id"] is not None:
        if data["contract_id"] <= 0:
            raise HTTPException(status_code=400, detail="Некорректный contract_id")
        contract = await session.get(Contract, data["contract_id"])
        if not contract:
            raise HTTPException(status_code=400, detail="Контракт не найден")
        cust.contract_id = data["contract_id"]
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Ошибка обновления клиента")
    await session.refresh(cust)
    result = await session.execute(
        select(Customer)
        .options(
            selectinload(Customer.lead).selectinload(Lead.advertisement),
            selectinload(Customer.contract).selectinload(Contract.product),
        )
        .where(Customer.id == cust.id)
    )
    cust = result.scalar_one()
    return to_out(cust)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["customers:delete"])),
):
    result = await session.execute(select(Customer).where(Customer.id == customer_id))
    cust = result.scalar_one_or_none()
    if not cust:
        raise HTTPException(status_code=404, detail="Активный клиент не найден")
    await session.delete(cust)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Нельзя удалить клиента: {e}")
    return None
