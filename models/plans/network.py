from decimal import Decimal

from sqlalchemy import String, Numeric, Enum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as pyEnum

from core.database import Base
from models.admin import Provider

class DataType(str, pyEnum):
    DIRECT = 'direct'
    DATASHARE = 'datashares'
    SME = 'sme'
    CORPORATE = 'corporate'
    SPECIAL = 'special'

class DataSize(str, pyEnum):
    MB = 'mb'
    GB = 'gb'
    TB = 'tb'

class Validity(str, pyEnum):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'

class DiscountType(str, pyEnum):
    PERCENTAGE = 'percentage'
    FLAT = 'flat'

class Network(Base):
    __tablename__ = 'networks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    provider_networks: Mapped[list['ProviderNetwork']] = relationship('ProviderNetwork', back_populates='network', passive_deletes=True)
    data_plans: Mapped[list["DataPlan"]] = relationship("DataPlan", back_populates="network")

class ProviderNetwork(Base):
    __tablename__ = 'provider_networks'

    id: Mapped[int] = mapped_column(primary_key=True)
    network_id: Mapped[int] = mapped_column(ForeignKey('networks.id', ondelete='CASCADE'))
    provider_name: Mapped[str] = mapped_column(ForeignKey('providers.name', ondelete='CASCADE'), nullable=True)
    provider_network_id: Mapped[str] = mapped_column(String(20))

    provider: Mapped['Provider'] = relationship('Provider')
    network: Mapped['Network'] = relationship('Network', back_populates='provider_networks')

class DataPlan(Base):
    __tablename__ = 'data_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    network_id: Mapped[int] = mapped_column(ForeignKey('networks.id', ondelete='CASCADE'))
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    size: Mapped[str] = mapped_column(String(20), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    discount_type: Mapped[str | None] = mapped_column(String(20))
    agent_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    agent_discount_type: Mapped[str | None] = mapped_column(String(20))
    api_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    api_discount_type: Mapped[str | None] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    validity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, index=True)
    is_locked: Mapped[bool] = mapped_column(default=False)
    vend_from: Mapped[str | None] = mapped_column(ForeignKey('providers.name', ondelete='SET NULL'), nullable=True)

    providers_data_plans: Mapped[list['ProviderDataPlan']] = relationship('ProviderDataPlan', back_populates='data_plan', passive_deletes=True)
    network: Mapped['Network'] = relationship('Network')

class ProviderDataPlan(Base):
    __tablename__ = 'provider_data_plan'

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey('data_plans.id', ondelete='CASCADE'), nullable=False)
    provider_name: Mapped[str] = mapped_column(ForeignKey('providers.name', ondelete='CASCADE'), nullable=True)
    provider_plan_id: Mapped[str] = mapped_column(String(20))

    provider: Mapped['Provider'] = relationship('Provider')
    data_plan: Mapped['DataPlan'] = relationship('DataPlan', back_populates='providers_data_plans')

class AirtimePlan(Base):
    __tablename__ = 'airtime_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    network_id: Mapped[int] = mapped_column(ForeignKey('networks.id', ondelete='CASCADE'), nullable=False)
    minimum_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    maximum_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=False)
    discount_type: Mapped[str | None] = mapped_column(String(20))
    agent_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    agent_discount_type: Mapped[str | None] = mapped_column(String(20))
    api_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    api_discount_type: Mapped[str | None] = mapped_column(String(20))
    agent_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    api_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(default=True)
    vend_from: Mapped[str | None] = mapped_column(ForeignKey('providers.name', ondelete='SET NULL'), nullable=True)

    network: Mapped['Network'] = relationship('Network')