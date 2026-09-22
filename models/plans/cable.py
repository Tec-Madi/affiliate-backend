from decimal import Decimal

from sqlalchemy import String, Enum, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as pyEnum

from core.database import Base
from models.admin import Provider

class Cable(Base):
    __tablename__ = 'cables'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    provider_cables: Mapped[list['ProviderCable']] = relationship('ProviderCable', back_populates='cable', passive_deletes=True)

class ProviderCable(Base):
    __tablename__ = 'provider_cables'

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_name: Mapped[str] = mapped_column(ForeignKey('providers.name', ondelete='CASCADE'), nullable=False)
    cable_id: Mapped[int] = mapped_column(ForeignKey('cables.id', ondelete='CASCADE'), nullable=False)
    provider_cable_id: Mapped[str] = mapped_column(String(10))

    provider: Mapped['Provider'] = relationship('Provider')
    cable: Mapped['Cable'] = relationship('Cable', back_populates='provider_cables')

class CablePlan(Base):
    __tablename__ = 'cable_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    cable_id: Mapped[int] = mapped_column(ForeignKey('cables.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    discount_type: Mapped[str | None] = mapped_column(String(20))
    agent_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    agent_discount_type: Mapped[str | None] = mapped_column(String(20))
    api_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    api_discount_type: Mapped[str | None] = mapped_column(String(20))
    validity: Mapped[str] = mapped_column(String(10))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_locked: Mapped[bool] = mapped_column(default=False)
    vend_from: Mapped[str | None] = mapped_column(ForeignKey('providers.name', ondelete='SET NULL'), nullable=True)

    cable: Mapped['Cable'] = relationship('Cable', passive_deletes=True)
    provider_cable_plan: Mapped[list['ProviderCablePlan']] = relationship('ProviderCablePlan', back_populates='cable_plan', passive_deletes=True)

class ProviderCablePlan(Base):
    __tablename__ = 'provider_cable_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_name: Mapped[str] = mapped_column(ForeignKey('providers.name', ondelete='CASCADE'), nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey('cable_plans.id', ondelete='CASCADE'), nullable=False)
    provider_plan_id: Mapped[str] = mapped_column(String(10))

    provider: Mapped['Provider'] = relationship('Provider')
    cable_plan: Mapped['CablePlan'] = relationship('CablePlan', back_populates='provider_cable_plan')