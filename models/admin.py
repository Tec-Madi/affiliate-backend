from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, Numeric, String, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableDict
from enum import Enum as pyEnum

from core.database import Base


class ProviderType(str, pyEnum):
    MADIX = "MADI-X"
    ADEX = 'ADEX'
    MSORG = 'MSORG'
    TOPUPMATE = 'TOPUPMATE',
    SMEPLUG = 'SMEPLUG'
    OGDAMS = 'OGDAMS'
    QUICKLYSIM = 'QUICKLYSIM'

class PaymentProviderName(str, pyEnum):
    SECUREWAVENG = 'SECUREWAVENG'
    PAYMENTPOINT = 'PAYMENTPOINT'
    XIXAPAY = 'XIXAPAY'

class ChargesType(str, pyEnum):
    PERCENTAGE = 'percentage'
    FLAT = 'flat'
    PERCENTAGE_CAPPED = 'percentage_capped'

class Provider(Base):
    __tablename__ = 'providers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    base_url: Mapped[str] = mapped_column(String(300), nullable=True)
    credentials: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

class PlanRoute(Base):
    __tablename__ = 'plan_routes'

    id: Mapped[int] = mapped_column(primary_key=True)
    service: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(nullable=False, index=True)
    provider: Mapped[str] = mapped_column(ForeignKey('providers.name', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('service', 'plan_id'),
    )

class PaymentPlan(Base):
    __tablename__ = 'payment_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    bank_name: Mapped[str] = mapped_column(String(20), nullable=False)
    provider: Mapped[str] = mapped_column(ForeignKey('payment_providers.name'))
    charges_type: Mapped[str] = mapped_column(String(30))
    flat: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    percentage: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    capped: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(default=True)
    bank_code: Mapped[str] = mapped_column(String(20), index=True)

    __table_args__ = (
        UniqueConstraint('provider', 'bank_code'),
    )

class KYCPlan(Base):
    __tablename__ = 'kyc_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_type: Mapped[str] = mapped_column(String(20), unique=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    provider: Mapped[str] = mapped_column(ForeignKey('payment_providers.name', ondelete='CASCADE'))

class PaymentProvider(Base):
    __tablename__ = 'payment_providers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    base_url: Mapped[str] = mapped_column(String(300), nullable=True)
    credentials: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON), nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

class AdminID(Base):
    __tablename__ = 'admin_ids'

    id: Mapped['int'] = mapped_column(primary_key=True)
    nin: Mapped[str] = mapped_column(String(250), unique=True, nullable=True)
    bvn: Mapped[str] = mapped_column(String(250), unique=True, nullable=True)

class GeneralMessage(Base):
    __tablename__ = 'general_messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(String(50), nullable=False)

class SystemInfo(Base):
    __tablename__ = 'system_infos'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    whatsapp_link: Mapped[str] = mapped_column(String(300), nullable=True)
    x_link: Mapped[str] = mapped_column(String(300), nullable=True)
    facebook_link: Mapped[str] = mapped_column(String(300), nullable=True)
    tiktok_link: Mapped[str] = mapped_column(String(300), nullable=True)
    instagram_link: Mapped[str] = mapped_column(String(300), nullable=True)