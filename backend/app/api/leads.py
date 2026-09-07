from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_session
from app.core.dependencies import get_current_user, require_permissions
from app.models.user import User
from app.models.lead import Lead
from app.models.advertisement import Advertisement
from app.models.customer import Customer
from app.schemas.lead import LeadCreate, LeadUpdate, LeadOut

router = APIRouter(prefix="/leads", tags=["leads"])


async def to_out(lead: Lead, session: AsyncSession = None) -> LeadOut:
    ad_name = None
    if lead.advertisement:
        ad_name = lead.advertisement.name
    elif lead.advertisement_id and session:
        res = await session.get(Advertisement, lead.advertisement_id)
        if res:
            ad_name = res.name
    # check converted
    is_conv = lead.customer is not None if hasattr(lead, "customer") else False
    if not is_conv and session:
        res = await session.execute(select(Customer).where(Customer.lead_id == lead.id))
        is_conv = res.scalar_one_or_none() is not None
    return LeadOut(
        id=lead.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        patronymic=lead.patronymic,
        phone=lead.phone,
        email=lead.email,
        advertisement_id=lead.advertisement_id,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        advertisement_name=ad_name,
        is_converted=is_conv,
    )


@router.get("", response_model=List[LeadOut])
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Lead).options(selectinload(Lead.advertisement), selectinload(Lead.customer)).order_by(Lead.id.desc()).offset(skip).limit(limit)
    )
    leads = result.scalars().all()
    out = []
    for l in leads:
        is_conv = l.customer is not None
        ad_name = l.advertisement.name if l.advertisement else None
        out.append(LeadOut(
            id=l.id,
            first_name=l.first_name,
            last_name=l.last_name,
            patronymic=l.patronymic,
            phone=l.phone,
            email=l.email,
            advertisement_id=l.advertisement_id,
            created_at=l.created_at,
            updated_at=l.updated_at,
            advertisement_name=ad_name,
            is_converted=is_conv,
        ))
    return out


@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(
    payload: LeadCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["leads:create"])),
):
    # advertisement_id может быть 0 -> трактуем как None
    adv_id = payload.advertisement_id
    if adv_id == 0:
        adv_id = None
    if adv_id is not None:
        if adv_id <= 0:
            raise HTTPException(status_code=400, detail="Некорректный advertisement_id")
        ad = await session.get(Advertisement, adv_id)
        if not ad:
            raise HTTPException(status_code=400, detail="Рекламная кампания не найдена")
    lead = Lead(
        first_name=payload.first_name,
        last_name=payload.last_name,
        patronymic=payload.patronymic,
        phone=payload.phone,
        email=payload.email,
        advertisement_id=adv_id,
    )
    session.add(lead)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка создания лида: {e}")
    await session.refresh(lead)
    # load ad name
    ad_name = None
    if lead.advertisement_id:
        ad = await session.get(Advertisement, lead.advertisement_id)
        if ad:
            ad_name = ad.name
            lead.advertisement = ad
    return LeadOut(
        id=lead.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        patronymic=lead.patronymic,
        phone=lead.phone,
        email=lead.email,
        advertisement_id=lead.advertisement_id,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        advertisement_name=ad_name,
        is_converted=False,
    )


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(
    lead_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Lead).options(selectinload(Lead.advertisement), selectinload(Lead.customer)).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Лид не найден")
    ad_name = lead.advertisement.name if lead.advertisement else None
    is_conv = lead.customer is not None
    return LeadOut(
        id=lead.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        patronymic=lead.patronymic,
        phone=lead.phone,
        email=lead.email,
        advertisement_id=lead.advertisement_id,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        advertisement_name=ad_name,
        is_converted=is_conv,
    )


@router.put("/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["leads:update"])),
):
    result = await session.execute(select(Lead).options(selectinload(Lead.advertisement), selectinload(Lead.customer)).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Лид не найден")
    data = payload.model_dump(exclude_unset=True)
    if "first_name" in data and data["first_name"] is not None:
        if not data["first_name"].strip():
            raise HTTPException(status_code=400, detail="Имя не может быть пустым")
        lead.first_name = data["first_name"]
    if "last_name" in data and data["last_name"] is not None:
        if not data["last_name"].strip():
            raise HTTPException(status_code=400, detail="Фамилия не может быть пустой")
        lead.last_name = data["last_name"]
    if "patronymic" in data:
        lead.patronymic = data["patronymic"]
    if "phone" in data and data["phone"] is not None:
        lead.phone = data["phone"]
    if "email" in data and data["email"] is not None:
        lead.email = data["email"]
    if "advertisement_id" in data:
        adv = data["advertisement_id"]
        if adv is None or adv == 0:
            lead.advertisement_id = None
        else:
            if adv <= 0:
                raise HTTPException(status_code=400, detail="Некорректный advertisement_id")
            ad = await session.get(Advertisement, adv)
            if not ad:
                raise HTTPException(status_code=400, detail="Рекламная кампания не найдена")
            lead.advertisement_id = adv
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Ошибка обновления лида: {e}")
    await session.refresh(lead)
    await session.refresh(lead, attribute_names=["customer"])
    # re-fetch advertisement
    ad_name = None
    if lead.advertisement_id:
        ad = await session.get(Advertisement, lead.advertisement_id)
        if ad:
            ad_name = ad.name
    is_conv = lead.customer is not None
    return LeadOut(
        id=lead.id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        patronymic=lead.patronymic,
        phone=lead.phone,
        email=lead.email,
        advertisement_id=lead.advertisement_id,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
        advertisement_name=ad_name,
        is_converted=is_conv,
    )


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["leads:delete"])),
):
    result = await session.execute(select(Lead).options(selectinload(Lead.customer)).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Лид не найден")
    if lead.customer is not None:
        raise HTTPException(status_code=400, detail="Нельзя удалить лида, уже конвертированного в клиента. Сначала удалите клиента.")
    await session.delete(lead)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Нельзя удалить лида: {e}")
    return None
