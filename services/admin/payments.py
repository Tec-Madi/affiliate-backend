from decimal import Decimal

from sqlalchemy.orm import Session
from core.error.http import AdminOnlyError, NotFoundError
from models.admin import PaymentProviderName
from models.users import IDType, User
from repositories.admin import KYCPlanRepository

def configure_kyc_plan(user: User, db: Session, kyc_plan_id: int, id_type: IDType | None, verification_price: Decimal | None, provider: PaymentProviderName | None):

    if not user.is_admin:
        raise AdminOnlyError()

    kyc_plan_repo = KYCPlanRepository(db)

    if kyc_plan_id:
        if not (kyc_plan := kyc_plan_repo.get_by_id(kyc_plan_id=kyc_plan_id)):
            raise NotFoundError('KYC plan not found')

        to_update = {
            'id_type': id_type,
            'verification_price': verification_price,
            'provider': provider
        }

        for key, value in to_update.items():
            if value is not None:
                setattr(kyc_plan, key, value)

        return {'message': f'{kyc_plan.id_type} editted successfully'}

    else:
        kyc_plan = kyc_plan_repo.create(id_type=id_type, provider=provider, verification_price=verification_price)

        return {'message': f'{kyc_plan.id_type} added successfuly'}