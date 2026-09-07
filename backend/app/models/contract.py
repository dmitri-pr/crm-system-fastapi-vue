from sqlalchemy import String, ForeignKey, Numeric, Date, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime, timezone
from decimal import Decimal

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    document: Mapped[str | None] = mapped_column(String(500), nullable=True)  # path to file
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    product: Mapped["Product"] = relationship(back_populates="contracts")
    customers: Mapped[list["Customer"]] = relationship(back_populates="contract")
