import os
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

import aiofiles

from app.core.database import get_session
from app.core.dependencies import get_current_user, require_permissions
from app.core.config import get_settings
from app.models.user import User
from app.models.contract import Contract
from app.models.product import Product
from app.schemas.contract import ContractOut, ContractCreate, ContractUpdate

settings = get_settings()
logger = logging.getLogger("crm")
router = APIRouter(prefix="/contracts", tags=["contracts"])

ALLOWED_EXTS = {".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _validate_contract_dates(start: Optional[date], end: Optional[date], existing_start=None, existing_end=None):
    s = start if start is not None else existing_start
    e = end if end is not None else existing_end
    if s and e and s > e:
        raise HTTPException(status_code=400, detail="Дата начала не может быть позже даты окончания")


async def _save_upload_file(upload: UploadFile) -> str:
    # Validate extension
    ext = os.path.splitext(upload.filename)[1].lower() if upload.filename else ""
    if ext and ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"Недопустимый тип файла {ext}. Разрешены: {', '.join(ALLOWED_EXTS)}")
    # Validate size by reading chunks
    media_dir = os.path.join(settings.media_root, "contracts")
    try:
        os.makedirs(media_dir, exist_ok=True)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Не удалось создать директорию: {e}")
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(media_dir, filename)
    try:
        async with aiofiles.open(dest, "wb") as f:
            total = 0
            while True:
                chunk = await upload.read(8192)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_FILE_SIZE:
                    # remove partial file
                    try:
                        await f.close()
                        os.remove(dest)
                    except Exception:
                        pass
                    raise HTTPException(status_code=413, detail="Файл слишком большой (макс 10 MB)")
                await f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"File save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {e}")
    return f"/media/contracts/{filename}"


def _remove_file(doc_path: Optional[str]):
    if not doc_path:
        return
    try:
        # doc_path is /media/contracts/<uuid>.ext -> strip /media/
        rel = doc_path.lstrip("/").replace("media/", "", 1) if doc_path.startswith("/media/") else doc_path
        # Actually settings.media_root is backend/media, so join with rel
        if doc_path.startswith("/media/"):
            rel_path = doc_path[len("/media/"):]
            full = os.path.join(settings.media_root, rel_path)
        else:
            full = os.path.join(settings.media_root, doc_path)
        if os.path.exists(full):
            os.remove(full)
    except Exception as e:
        logger.warning(f"Failed to remove file {doc_path}: {e}")


def to_out(contract: Contract) -> ContractOut:
    return ContractOut(
        id=contract.id,
        name=contract.name,
        product_id=contract.product_id,
        start_date=contract.start_date,
        end_date=contract.end_date,
        cost=float(contract.cost),
        document=contract.document,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
        product_name=contract.product.name if contract.product else None,
    )


@router.get("", response_model=List[ContractOut])
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Contract).options(selectinload(Contract.product)).order_by(Contract.id.desc()).offset(skip).limit(limit))
    contracts = result.scalars().all()
    return [to_out(c) for c in contracts]


@router.post("", response_model=ContractOut, status_code=201)
async def create_contract(
    name: str = Form(...),
    product_id: int = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    cost: float = Form(...),
    document: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["contracts:create"])),
):
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Название не может быть пустым")
    if product_id <= 0:
        raise HTTPException(status_code=400, detail="Некорректный product_id")
    if cost is not None and float(cost) < 0:
        raise HTTPException(status_code=400, detail="Стоимость не может быть отрицательной")
    _validate_contract_dates(start_date, end_date)
    prod = await session.get(Product, product_id)
    if not prod:
        raise HTTPException(status_code=400, detail="Продукт не найден")
    dup = await session.execute(select(Contract).where(Contract.name == name))
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Контракт с таким названием уже существует")
    doc_path = None
    if document and document.filename:
        doc_path = await _save_upload_file(document)

    contract = Contract(
        name=name,
        product_id=product_id,
        start_date=start_date,
        end_date=end_date,
        cost=cost,
        document=doc_path,
    )
    session.add(contract)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        if doc_path:
            _remove_file(doc_path)
        raise HTTPException(status_code=400, detail="Контракт с таким названием уже существует")
    await session.refresh(contract)
    contract.product = prod
    return to_out(contract)


@router.post("/json", response_model=ContractOut, status_code=201)
async def create_contract_json(
    payload: dict,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["contracts:create"])),
):
    # альтернативный JSON endpoint без файла
    try:
        data = ContractCreate(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    if float(data.cost) < 0:
        raise HTTPException(status_code=400, detail="Стоимость не может быть отрицательной")
    _validate_contract_dates(data.start_date, data.end_date)
    prod = await session.get(Product, data.product_id)
    if not prod:
        raise HTTPException(status_code=400, detail="Продукт не найден")
    dup = await session.execute(select(Contract).where(Contract.name == data.name))
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Контракт с таким названием уже существует")
    contract = Contract(
        name=data.name,
        product_id=data.product_id,
        start_date=data.start_date,
        end_date=data.end_date,
        cost=data.cost,
        document=None,
    )
    session.add(contract)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Контракт с таким названием уже существует")
    await session.refresh(contract)
    contract.product = prod
    return to_out(contract)


@router.get("/{contract_id}", response_model=ContractOut)
async def get_contract(
    contract_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(select(Contract).options(selectinload(Contract.product)).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    return to_out(contract)


@router.put("/{contract_id}", response_model=ContractOut)
async def update_contract(
    contract_id: int,
    name: Optional[str] = Form(None),
    product_id: Optional[int] = Form(None),
    start_date: Optional[date] = Form(None),
    end_date: Optional[date] = Form(None),
    cost: Optional[float] = Form(None),
    document: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["contracts:update"])),
):
    result = await session.execute(select(Contract).options(selectinload(Contract.product)).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    if name is not None:
        if not name.strip():
            raise HTTPException(status_code=400, detail="Название не может быть пустым")
        dup = await session.execute(select(Contract).where(Contract.name == name, Contract.id != contract_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Контракт с таким названием уже существует")
        contract.name = name
    if product_id is not None:
        if product_id <= 0:
            raise HTTPException(status_code=400, detail="Некорректный product_id")
        prod = await session.get(Product, product_id)
        if not prod:
            raise HTTPException(status_code=400, detail="Продукт не найден")
        contract.product_id = product_id
    # Validate dates together
    try:
        _validate_contract_dates(start_date, end_date, contract.start_date, contract.end_date)
    except HTTPException:
        raise
    if start_date is not None:
        contract.start_date = start_date
    if end_date is not None:
        contract.end_date = end_date
    if cost is not None:
        if float(cost) < 0:
            raise HTTPException(status_code=400, detail="Стоимость не может быть отрицательной")
        contract.cost = cost
    old_doc = contract.document
    new_doc_path = None
    if document and document.filename:
        new_doc_path = await _save_upload_file(document)
        contract.document = new_doc_path
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        if new_doc_path:
            _remove_file(new_doc_path)
        raise HTTPException(status_code=400, detail="Конфликт данных при обновлении")
    # remove old file only after successful commit and if new uploaded
    if new_doc_path and old_doc:
        _remove_file(old_doc)
    await session.refresh(contract)
    prod = await session.get(Product, contract.product_id)
    contract.product = prod
    return to_out(contract)


@router.put("/{contract_id}/json", response_model=ContractOut)
async def update_contract_json(
    contract_id: int,
    payload: dict,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["contracts:update"])),
):
    result = await session.execute(select(Contract).options(selectinload(Contract.product)).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    # Валидация через схему
    # Собираем только допустимые поля
    allowed = {"name", "product_id", "start_date", "end_date", "cost"}
    filtered = {k: v for k, v in payload.items() if k in allowed}
    if not filtered:
        raise HTTPException(status_code=400, detail="Нет полей для обновления")
    # Парсим даты если строки
    for dfield in ("start_date", "end_date"):
        if dfield in filtered and isinstance(filtered[dfield], str):
            try:
                filtered[dfield] = datetime.strptime(filtered[dfield], "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Неверный формат даты {dfield}, ожидается YYYY-MM-DD")
    if "cost" in filtered and filtered["cost"] is not None and float(filtered["cost"]) < 0:
        raise HTTPException(status_code=400, detail="Стоимость не может быть отрицательной")
    if "name" in filtered and filtered["name"] is not None:
        if not str(filtered["name"]).strip():
            raise HTTPException(status_code=400, detail="Название не может быть пустым")
        dup = await session.execute(select(Contract).where(Contract.name == filtered["name"], Contract.id != contract_id))
        if dup.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Контракт с таким названием уже существует")
        contract.name = filtered["name"]
    if "product_id" in filtered and filtered["product_id"] is not None:
        pid = filtered["product_id"]
        if isinstance(pid, str):
            try: pid = int(pid)
            except: raise HTTPException(status_code=400, detail="Некорректный product_id")
        if pid <= 0:
            raise HTTPException(status_code=400, detail="Некорректный product_id")
        prod = await session.get(Product, pid)
        if not prod:
            raise HTTPException(status_code=400, detail="Продукт не найден")
        contract.product_id = pid
    # валидация дат вместе
    new_start = filtered.get("start_date", contract.start_date)
    new_end = filtered.get("end_date", contract.end_date)
    _validate_contract_dates(new_start, new_end)
    if "start_date" in filtered:
        contract.start_date = filtered["start_date"]
    if "end_date" in filtered:
        contract.end_date = filtered["end_date"]
    if "cost" in filtered and filtered["cost"] is not None:
        contract.cost = filtered["cost"]
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Конфликт данных при обновлении")
    await session.refresh(contract)
    prod = await session.get(Product, contract.product_id)
    contract.product = prod
    return to_out(contract)


@router.delete("/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permissions(["contracts:delete"])),
):
    result = await session.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    doc = contract.document
    await session.delete(contract)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Нельзя удалить контракт, он используется: {e}")
    if doc:
        _remove_file(doc)
    return None
