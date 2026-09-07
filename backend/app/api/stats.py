import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.advertisement import Advertisement
from app.models.lead import Lead
from app.models.customer import Customer

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/dashboard")
async def dashboard(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Параллельно считаем, вместо последовательных await
    results = await asyncio.gather(
        session.execute(select(func.count(Product.id))),
        session.execute(select(func.count(Advertisement.id))),
        session.execute(select(func.count(Lead.id))),
        session.execute(select(func.count(Customer.id))),
    )
    prod_cnt = results[0].scalar() or 0
    ads_cnt = results[1].scalar() or 0
    leads_cnt = results[2].scalar() or 0
    cust_cnt = results[3].scalar() or 0
    return {
        "products_count": prod_cnt,
        "advertisements_count": ads_cnt,
        "leads_count": leads_cnt,
        "customers_count": cust_cnt,
    }
