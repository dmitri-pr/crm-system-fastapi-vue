from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.database import get_session
from app.core.dependencies import get_current_user, require_permissions
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductOut])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Product).order_by(Product.id.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["products:create"])),
):
    # unique check
    result = await session.execute(select(Product).where(Product.name == payload.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Услуга с таким названием уже существует")
    product = Product(name=payload.name, description=payload.description, cost=payload.cost)
    session.add(product)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Услуга с таким названием уже существует")
    await session.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["products:update"])),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        if not data["name"] or not data["name"].strip():
            raise HTTPException(status_code=400, detail="Название не может быть пустым")
        dup = await session.execute(select(Product).where(Product.name == data["name"], Product.id != product_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Услуга с таким названием уже существует")
        product.name = data["name"]
    if "description" in data:
        product.description = data["description"]
    if "cost" in data:
        if data["cost"] is not None and float(data["cost"]) < 0:
            raise HTTPException(status_code=400, detail="Стоимость не может быть отрицательной")
        product.cost = data["cost"]
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Конфликт данных при обновлении")
    await session.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["products:delete"])),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    await session.delete(product)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Нельзя удалить услугу с привязанными объектами: {e}")
    return None
