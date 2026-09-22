from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class BulkSMSPlan(Base):
    __tablename__ = 'bulk_sms_plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_active: Mapped[bool] = mapped_column(default=True)