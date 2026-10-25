from __future__ import annotations
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Boolean, Column, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database.engine import Base

class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    
    is_active_vpn: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at_vless: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at_wireguard: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    remnawave_uuid: Mapped[str | None] = mapped_column(String(255))
    wg_id: Mapped[str | None] = mapped_column(String(255))

    referrer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    bonus_balance: Mapped[float] = mapped_column(default=0)

    is_trial_available: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        server_default="true", 
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )   

    orders: Mapped[list[Order]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))

    payment_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    vpn_type: Mapped[str] = mapped_column(String(50))
    days: Mapped[int] = mapped_column(Integer)
    amount_value: Mapped[int] = mapped_column(Integer)

    status: Mapped[str] = mapped_column(String(50), default="pending")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="orders")

    bonuses_spent: Mapped[int] = mapped_column(Integer, default=0)

class PurchasedKeys(Base):
    __tablename__ = "purchased_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Ссылка на пользователя-покупателя
    buyer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Тип VPN: 'vless' или 'wireguard'
    vpn_type: Mapped[str] = mapped_column(String(32))

    # Идентификаторы для разных панелей
    remnawave_uuid: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    wg_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )

    name: Mapped[str] = mapped_column(
        String(64), default="Подарочный ключ"
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)