from decimal import Decimal

from sqlalchemy.orm import Session
#from rapidfuzz import fuzz

from core.error.http import NotFoundError
from core.services.transaction import TransactionService
from core.utils import TxnDetails, generate_reference
from models.users import IDType, Services, User
from repositories.users import UserKYCRepository
from repositories.admin import KYCPlanRepository


async def kyc_verification_function(user: User, db: Session, id_type: IDType, id_number: str, number: str, date_of_birth: str):

    transaction_service = TransactionService(user=user, db=db)

    user_kyc_repo = UserKYCRepository(db)
    kyc_plan_repo = KYCPlanRepository(db)

    service = Services.KYC.value
    reference = generate_reference(prefix=service)

    if not (user_kyc := user_kyc_repo.get_by_user_id(user_id=user.id)):
        user_kyc = user_kyc_repo.create(user_id=user.id)

    payload = {
        'id_number': id_number,
        'number': number,
        'date_of_birth': date_of_birth,
        'plan': kyc_plan
    }

    if not (kyc_plan := kyc_plan_repo.get_by_id_type(id_type=id_type)):
        raise NotFoundError(message='No provider Found')

    txn_details = TxnDetails(
        service=Services.KYC.value,
        service_type=id_type.value,
        service_provider='###',
        value=Decimal(0),
        product=f'{id_type.value} verification',
        beneficiary='Wallet',
        reference=reference
    )

    try:
        await transaction_service.execute_payment(plan=kyc_plan, txn_details=txn_details, from_api=False,)
        db.commit()
    except Exception:
        db.rollback()
        raise

    try:
        #response = verify_kyc_router(payload=payload, db=db)
        pass
    except Exception as e:
        response = e

    complete_transaction = await transaction_service.update_transaction(reference=reference, cash_back=None, response=response)

    