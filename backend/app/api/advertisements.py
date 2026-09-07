from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_session
from app.core.dependencies import get_current_user, require_permissions
from app.models.user import User
from app.models.advertisement import Advertisement
from app.models.product import Product
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.contract import Contract
from app.schemas.advertisement import AdvertisementCreate, AdvertisementUpdate, AdvertisementOut, AdvertisementStatsOut

router = APIRouter(prefix="/ads", tags=["ads"])


def to_out(ad: Advertisement) -> AdvertisementOut:
    return AdvertisementOut(
        id=ad.id,
        name=ad.name,
        product_id=ad.product_id,
        promotion_channel=ad.promotion_channel,
        budget=float(ad.budget),
        created_at=ad.created_at,
        updated_at=ad.updated_at,
        product_name=ad.product.name if ad.product else None,
    )


@router.get("", response_model=List[AdvertisementOut])
async def list_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Advertisement).options(selectinload(Advertisement.product)).order_by(Advertisement.id.desc()).offset(skip).limit(limit))
    ads = result.scalars().all()
    return [to_out(a) for a in ads]


@router.get("/statistic", response_model=List[AdvertisementStatsOut])
async def ads_statistic(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["stats:read"])),
):
    # Один агрегирующий запрос вместо 3N+1
    result = await session.execute(
        select(
            Advertisement.id,
            Advertisement.name,
            Advertisement.budget,
            Product.name.label("product_name"),
            func.count(func.distinct(Lead.id)).label("leads_count"),
            func.count(func.distinct(Customer.id)).label("customers_count"),
            func.coalesce(func.sum(Contract.cost), 0).label("income"),
        )
        .outerjoin(Product, Advertisement.product_id == Product.id)
        .outerjoin(Lead, Lead.advertisement_id == Advertisement.id)
        .outerjoin(Customer, Customer.lead_id == Lead.id)
        .outerjoin(Contract, Contract.id == Customer.contract_id)
        .group_by(Advertisement.id, Advertisement.name, Advertisement.budget, Product.name)
        .order_by(Advertisement.id.desc())
    )
    rows = result.all()
    stats = []
    for r in rows:
        budget = float(r.budget) if r.budget else 0
        income = float(r.income or 0)
        profit = None
        if budget and budget != 0:
            profit = round(income / budget, 2) if income else 0.0
        stats.append(AdvertisementStatsOut(
            id=r.id,
            name=r.name,
            product_name=r.product_name,
            budget=budget,
            leads_count=int(r.leads_count or 0),
            customers_count=int(r.customers_count or 0),
            profit=profit,
        ))
    return stats


@router.post("", response_model=AdvertisementOut, status_code=201)
async def create_ad(
    payload: AdvertisementCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["ads:create"])),
):
    if payload.product_id is not None and payload.product_id <= 0:
        raise HTTPException(status_code=400, detail="Некорректный product_id")
    if payload.budget is not None and float(payload.budget) < 0:
        raise HTTPException(status_code=400, detail="Бюджет не может быть отрицательным")
    prod = await session.get(Product, payload.product_id)
    if not prod:
        raise HTTPException(status_code=400, detail="Продукт не найден")
    dup = await session.execute(select(Advertisement).where(Advertisement.name == payload.name))
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Рекламная кампания с таким названием уже существует")
    ad = Advertisement(
        name=payload.name,
        product_id=payload.product_id,
        promotion_channel=payload.promotion_channel,
        budget=payload.budget,
    )
    session.add(ad)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Рекламная кампания с таким названием уже существует")
    await session.refresh(ad, attribute_names=["product"])
    return to_out(ad)


@router.get("/{ad_id}", response_model=AdvertisementOut)
async def get_ad(
    ad_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Advertisement).options(selectinload(Advertisement.product)).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Рекламная кампания не найдена")
    return to_out(ad)


@router.put("/{ad_id}", response_model=AdvertisementOut)
async def update_ad(
    ad_id: int,
    payload: AdvertisementUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["ads:update"])),
):
    result = await session.execute(select(Advertisement).options(selectinload(Advertisement.product)).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Рекламная кампания не найдена")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        if not data["name"].strip():
            raise HTTPException(status_code=400, detail="Название не может быть пустым")
        dup = await session.execute(select(Advertisement).where(Advertisement.name == data["name"], Advertisement.id != ad_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Рекламная кампания с таким названием уже существует")
        ad.name = data["name"]
    if "product_id" in data and data["product_id"] is not None:
        if data["product_id"] <= 0:
            raise HTTPException(status_code=400, detail="Некорректный product_id")
        prod = await session.get(Product, data["product_id"])
        if not prod:
            raise HTTPException(status_code=400, detail="Продукт не найден")
        ad.product_id = data["product_id"]
    if "promotion_channel" in data and data["promotion_channel"] is not None:
        ad.promotion_channel = data["promotion_channel"]
    if "budget" in data and data["budget"] is not None:
        if float(data["budget"]) < 0:
            raise HTTPException(status_code=400, detail="Бюджет не может быть отрицательным")
        ad.budget = data["budget"]
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Конфликт данных при обновлении")
    await session.refresh(ad, attribute_names=["product"])
    return to_out(ad)


@router.delete("/{ad_id}", status_code=204)
async def delete_ad(
    ad_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["ads:delete"])),
):
    result = await session.execute(select(Advertisement).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status_code=404, detail="Рекламная кампания не найдена")
    await session.delete(ad)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Нельзя удалить кампанию с привязанными лидами: {e}")
    return None
