import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func

from app.core.config import get_settings
from app.core.database import init_db, async_session_factory
from app.core.security import get_password_hash

from app.api import auth, users, products, advertisements, leads, contracts, customers, stats

settings = get_settings()
logger = logging.getLogger("crm")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init db
    try:
        await init_db()
    except Exception as e:
        logger.exception(f"init_db failed: {e}")
        raise
    # ensure media dir
    try:
        os.makedirs(settings.media_root, exist_ok=True)
    except PermissionError as e:
        logger.exception(f"Failed to create media dir {settings.media_root}: {e}")
        raise
    # create default admin if not exists
    async with async_session_factory() as session:
        from app.models.user import User
        try:
            result = await session.execute(select(User).where(User.username == "admin"))
        except Exception as e:
            logger.exception(f"Failed to query admin user: {e}")
            yield
            return
        if not result.scalar_one_or_none():
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Администратор",
                role="admin",
                is_active=True,
                is_superuser=True,
            )
            session.add(admin)
            # демо пользователи для каждой роли
            demo = [
                ("operator1", "operator@example.com", "operator123", "Оператор", "operator"),
                ("marketer1", "marketer@example.com", "marketer123", "Маркетолог", "marketer"),
                ("manager1", "manager@example.com", "manager123", "Менеджер", "manager"),
            ]
            for uname, email, pwd, fname, role in demo:
                result2 = await session.execute(select(User).where(User.username == uname))
                if not result2.scalar_one_or_none():
                    u = User(
                        username=uname,
                        email=email,
                        hashed_password=get_password_hash(pwd),
                        full_name=fname,
                        role=role,
                        is_active=True,
                        is_superuser=False,
                    )
                    session.add(u)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.exception(f"Failed to create default users: {e}")
            else:
                logger.info("Default users created: admin/admin123, operator1/operator123, marketer1/marketer123, manager1/manager123")
        # seed demo data if empty
        from app.models.product import Product
        prod_cnt = (await session.execute(select(func.count(Product.id)))).scalar() or 0
        if prod_cnt == 0:
            # create demo products, ads, leads etc
            p1 = Product(name="Консалтинг", description="Бизнес-консалтинг", cost=50000)
            p2 = Product(name="Разработка сайта", description="Создание сайтов под ключ", cost=120000)
            session.add_all([p1, p2])
            await session.flush()
            from app.models.advertisement import Advertisement
            ad1 = Advertisement(name="Яндекс Директ - Консалтинг", product_id=p1.id, promotion_channel="Яндекс Директ", budget=30000)
            ad2 = Advertisement(name="VK Реклама - Сайты", product_id=p2.id, promotion_channel="VK", budget=50000)
            session.add_all([ad1, ad2])
            await session.flush()
            from app.models.lead import Lead
            l1 = Lead(first_name="Иван", last_name="Петров", patronymic="Сергеевич", phone="+7 999 123-45-67", email="ivan@example.com", advertisement_id=ad1.id)
            l2 = Lead(first_name="Анна", last_name="Сидорова", phone="+7 999 765-43-21", email="anna@example.com", advertisement_id=ad2.id)
            session.add_all([l1, l2])
            await session.flush()
            from app.models.contract import Contract
            from datetime import date, timedelta
            c1 = Contract(name="Договор-001", product_id=p1.id, start_date=date.today(), end_date=date.today()+timedelta(days=365), cost=75000)
            session.add(c1)
            await session.flush()
            from app.models.customer import Customer
            cust = Customer(lead_id=l1.id, contract_id=c1.id)
            session.add(cust)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.exception(f"Demo seed failed: {e}")
            else:
                logger.info("Demo data seeded")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if not origins:
    origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Media static
try:
    os.makedirs(settings.media_root, exist_ok=True)
except PermissionError as e:
    logger.warning(f"Cannot create media dir {settings.media_root}: {e}")
app.mount("/media", StaticFiles(directory=settings.media_root), name="media")

# include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(advertisements.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(contracts.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "CRM FastAPI Vue - API работает", "docs": "/docs"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
