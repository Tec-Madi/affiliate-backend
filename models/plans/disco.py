from decimal import Decimal

from sqlalchemy import Enum, String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as pyEnum

from core.database import Base
from models.admin import Provider

# class DiscoName(str, pyEnum):
#     ABUJA_ELECTRICITY = 'ABUJA ELECTRICITY DISTRIBUTION COMPANY'
#     BENIN_ELECTRICITY = 'BENIN ELECTRICITY DISTRIBUTION COMPANY'
#     EKO_ELECTRICITY = 'EKO ELECTRICITY DISTRIBUTION COMPANY'
#     ENUGU_ELECTRICITY = 'ENUGU ELECTRICITY DISTRIBUTION COMPANY'
#     IBADAN_ELECTRICITY = 'IBADAN ELECTRICITY DISTRIBUTION COMPANY'
#     IKEJA_ELECTRICITY = 'IKEJA ELECTRICIT DISTRIBUTION COMPANY'
#     JOS_ELECTRICITY = 'JOS ELECTRICITY DISTRIBUTION COMPANY'
#     KADUNA_ELECTRICITY = 'KADUNA ELECTRICITY DISTRIBUTION COMPANY'
#     KANO_ELECTRICITY = 'KANO ELECTRICITY DISTRIBUTION COMPANY'
#     PORT_HARCOURT_ELECTRICITY = 'PORT HARCOURT ELECTRICITY DISTRIBUTION COMPANY'
#     YOLA_ELECTRICITY = 'YOLA ELECTRICITY DISTRIBUTION COMPANY'

class Disco(Base):
    __tablename__ = 'discos'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    provider_discos: Mapped[list['ProviderDisco']] = relationship('ProviderDisco', passive_deletes=True)

class ProviderDisco(Base):
    __tablename__ = 'provider_discos'

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_name: Mapped[str] = mapped_column(ForeignKey('providers.name', ondelete='CASCADE'), nullable=False)
    disco_id: Mapped[int] = mapped_column(ForeignKey('discos.id', ondelete='CASCADE'), nullable=False)
    provider_disco_id: Mapped[str] = mapped_column(String(20))

    provider: Mapped['Provider'] = relationship('Provider')

class DiscoType(str, pyEnum):
    PREPAID = 'prepaid'
    POSTPAID = 'postpaid'

class DiscoPlan(Base):
    __tablename__ = 'disco_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    disco_id: Mapped[int] = mapped_column(ForeignKey('discos.id', ondelete='CASCADE'), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    minimum_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    maximum_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    discount_type: Mapped[str | None] = mapped_column(String(20))
    agent_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    agent_discount_type: Mapped[str | None] = mapped_column(String(20))
    api_discount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    api_discount_type: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    vend_from: Mapped[str | None] = mapped_column(ForeignKey('providers.name', ondelete='SET NULL'), nullable=True)

    disco: Mapped['Disco'] = relationship('Disco')
    provider_disco_plans: Mapped["ProviderDiscoPlan"] =  relationship("ProviderDiscoPlan", back_populates="disco_plan")

class ProviderDiscoPlan(Base):
    __tablename__ = "provider_disco_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("disco_plans.id", ondelete="CASCADE"))
    provider_name: Mapped[str] = mapped_column(ForeignKey("providers.name"), onupdate="CASCADE")
    provider_plan_id: Mapped[str] = mapped_column(String(20))

    provider: Mapped['Provider'] = relationship('Provider')
    disco_plan: Mapped['DiscoPlan'] = relationship('DiscoPlan', back_populates='provider_disco_plans')