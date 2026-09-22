from decimal import Decimal
from sqlalchemy.orm import Session
from starlette.requests import Request

from core.cryptography import decrypt_data
from core.error.http import UnprocessibleEntityError
from core.utils import generate_reference
from models.users import Services, Status, User
from providers.router import PGWRouter
from repositories.admin import AdminIDRepository, PaymentPlanRepository
from models.admin import ChargesType, PaymentProviderName
from repositories.users import TxnRepository, UserKYCRepository, UserRepository, VirtualAccountRepository, WalletRepository

def get_virtual_accounts_function(user: User, db: Session):

    virual_account_repo = VirtualAccountRepository(db)
    payment_plan_repo = PaymentPlanRepository(db)

    virtual_accounts = virual_account_repo.get_by_user_id(user_id=user.id)

    accounts = []

    for virtual_account in virtual_accounts:
        payment_plan = payment_plan_repo.get_by_bank_code_and_provider(bank_code=virtual_account.bank_code, provider=virtual_account.provider)
        if not payment_plan:
            continue
        charges_map = {
            ChargesType.FLAT.value: f'₦{int(payment_plan.flat.normalize())}' if payment_plan.flat else 'FREE',
            ChargesType.PERCENTAGE.value: f'{int(payment_plan.percentage.normalize())}%' if payment_plan.percentage else 'FREE',
            ChargesType.PERCENTAGE_CAPPED.value: f'{int(payment_plan.percentage.normalize())}% capped at ₦{int(payment_plan.capped.normalize())}' if payment_plan.percentage else 'FREE'
        }

        charges = charges_map.get(payment_plan.charges_type)

        account = {
            'id': virtual_account.id,
            'account_number': virtual_account.account_number,
            'account_name': virtual_account.account_name,
            'bank_name': virtual_account.bank_name,
            'charges': charges
        }

        accounts.append(account)

    return accounts


async def generate_account_function(user: User, db: Session):

    virtual_account_repo = VirtualAccountRepository(db)
    admin_id_repo = AdminIDRepository(db)
    user_kyc_repo = UserKYCRepository(db)

    user_kyc = user_kyc_repo.get_by_user_id(user.id)
    admin_cred = admin_id_repo.get_admin_id()

    admin_nin = decrypt_data(admin_cred.nin) 
    admin_bvn = decrypt_data(admin_cred.bvn)

    user_nin = decrypt_data(getattr(user_kyc, "nin", None))
    user_bvn =  decrypt_data(getattr(user_kyc, "bvn", None))
    nin_is_verified = getattr(user_kyc, "nin_is_verified", False)
    bvn_is_verified = getattr(user_kyc, "bvn_is_verified", False)

    nin = user_nin if user_nin and nin_is_verified else admin_nin
    bvn = user_bvn if user_bvn and bvn_is_verified else admin_bvn

    payload = {
        'name': user.name,
        'email': user.email,
        'number': user.number,
        'nin': nin,
        'bvn': bvn,
    }

    try:
        if (bank_accounts := await PGWRouter.generate_account_router(user_id=user.id, payload=payload, db=db)):

            for bank_account in bank_accounts:
                account = bank_account.model_dump()
                account_number = account['account_number']
                bank_name = account['bank_name']
                account_name = account['account_name']
                account_reference = account['account_reference']
                generated_bank_code = account['bank_code']
                provider_name = account['provider']

                if virtual_account_repo.get_by_bank_code_and_provider(user_id=user.id, bank_code=str(generated_bank_code), provider=provider_name):
                    continue

                virtual_account_repo.create(
                    user_id=user.id, 
                    bank_code=str(generated_bank_code), 
                    provider=provider_name, 
                    account_number=account_number, 
                    bank_name=bank_name, 
                    account_name=account_name, 
                    account_reference=account_reference
                )

                db.commit()

        return {'message': 'account created successfully'}

    except Exception as e:
        raise UnprocessibleEntityError(str(e))


async def receive_payment(db: Session, request: Request, payment_provider_name: PaymentProviderName):

    service = Services.FUNDING.value
    reference = generate_reference(service)

    user_repo = UserRepository(db)
    wallet_repo = WalletRepository(db)
    txn_repo = TxnRepository(db)
    payment_plan_repo = PaymentPlanRepository(db)
    virtual_account_repo = VirtualAccountRepository(db)

    payment_request = await PGWRouter.receive_payment_router(provider_name=payment_provider_name, request=request, db=db)

    payload = payment_request.model_dump()

    email  = payload.get('email')
    amount = payload.get('amount')
    account_number = payload.get('account_number')
    api_reponse = payload.get('api_response')
    provider = payload.get('provider')
    provider_reference = payload.get('provider_reference')

    virtual_account = virtual_account_repo.get_by_account_number(account_number=account_number)

    bank_code = virtual_account.bank_code

    payment_plan = payment_plan_repo.get_any_by_bank_code_and_provider(bank_code=bank_code, provider=provider)

    if payment_plan.charges_type == ChargesType.FLAT.value:
        amount_to_credit = amount - payment_plan.flat
    elif payment_plan.charges_type == ChargesType.PERCENTAGE.value:
        amount_to_credit = amount*(Decimal('1')- payment_plan.percentage/Decimal('100'))
    elif payment_plan.charges_type == ChargesType.PERCENTAGE_CAPPED.value:
        accumulated_charges = amount*(payment_plan.percentage/Decimal('100'))
        amount_to_credit = amount - min(accumulated_charges, payment_plan.capped)
    else:
        amount_to_credit = amount

    try:
        user = user_repo.get_by_email(email=email)
        wallet = wallet_repo.get_for_update(user_id=user.id)

        old_balance = wallet.balance

        new_balance = wallet_repo.update_balance(wallet=wallet, amount=amount_to_credit)

        txn_repo.create_funding_txn(
            user_id=user.id, 
            reference=reference, 
            provider_reference=provider_reference, 
            service=Services.FUNDING.value, 
            service_provider='Bank', 
            service_type='Automated', 
            beneficiary=account_number,
            product=f'{amount} funding', 
            message=f'Funding of {amount} was successful', 
            api_response=api_reponse, 
            amount=amount, 
            old_balance=old_balance,
            new_balance=new_balance, 
            status=Status.SUCCESS.value, 
            value=amount, 
            service_from=provider
        )

        db.commit()

    except Exception as e:
        db.rollback()
        raise e

    return {'message': 'payment received successfully'}