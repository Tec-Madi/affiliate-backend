from decimal import Decimal

from sqlalchemy import Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as pyEnum

from core.database import Base

class ExamName(str, pyEnum):
    WAEC = 'waec'
    NECO = 'neco'
    NABTEB = 'nabteb'

class Exam(Base):
    __tablename__ = 'exams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    providers_exam: Mapped[list['ProviderExam']] = relationship('ProviderExam')

class ProviderExam(Base):
    __tablename__ = 'provider_exams'

    id: Mapped[int] = mapped_column(primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey('exams.id', ondelete='CASCADE'), index=True)
    provider_exam_id: Mapped[str] = mapped_column(String(20))

class ExamPlan(Base):
    __tablename__ = 'exam_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey('exams.id', ondelete='CASCADE'), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_type: Mapped[str] = mapped_column(String(10))
    agent_discount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    agent_discount_type: Mapped[str] = mapped_column(String(10))
    api_discount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    api_discount_type: Mapped[str] = mapped_column(String(10))
    is_active: Mapped[bool] = mapped_column(default=True)

    exam: Mapped['Exam'] = relationship('Exam')