from datetime import datetime

from sqlalchemy.orm import Session
from decimal import Decimal

from core.error.http import InsufficientBalanceError
from core.utils import generate_reference
from models.users import Services, Status, TxnType, User
from repositories.users import BonusTxnRepository, TxnRepository, WalletRepository

def dashboard_function(user: User, db: Session):

    recent_txns = TxnRepository(db).get_recent_transactions(user_id=user.id, limit=3)

    return{
        'name': user.name,
        'email': user.email,
        'balance': user.wallet.balance,
        'is_active': user.is_active,
        "is_agent": user.is_agent,
        "is_admin": user.is_admin,
        'bonus': user.wallet.bonus,
        'recent_transactions': [
            {
                'reference': txn.reference,
                'service': txn.service,
                'service_provider': txn.service_provider,
                'service_type': txn.service_type,
                'beneficiary': txn.beneficiary,
                'product': txn.product,
                'message': txn.message,
                'amount': str(txn.amount),
                'status': txn.status,
                'created_at': txn.created_at
            }
            for txn in recent_txns
        ]
    }

def view_bonus_details_function(user: User, db: Session):

    bonus_txn_repo = BonusTxnRepository(db)

    bonus_txns = bonus_txn_repo.get_recent_txn(user_id=user.id, limit=5)
    all_time_earned = bonus_txn_repo.all_time_earned(user_id=user.id) or Decimal('0')

    return {
        'bonus_balance': user.wallet.bonus,
        'all-time-earned': f'{all_time_earned.normalize()}',
        'recent_txn': [{
            'message': bonus_txn.message,
            'amount': f'{bonus_txn.amount.normalize()}',
            'time': bonus_txn.created_at,
            'txn_type': bonus_txn.txn_type
        } for bonus_txn in bonus_txns]
    }

def withdraw_cashback_function(user: User, db: Session, amount: Decimal):

    wallet_repo = WalletRepository(db)
    bonus_txn_repo = BonusTxnRepository(db)
    txn_repo = TxnRepository(db)

    reference = generate_reference(prefix = Services.FUNDING.value)

    try:
        wallet = wallet_repo.get_for_update(user_id=user.id)

        old_bonus_balance = wallet.bonus
        old_balance = wallet.balance

        if amount > wallet.bonus:
            raise InsufficientBalanceError(message='Insufficient bonus balance')

        wallet.bonus -= amount

        new_balance  = wallet_repo.update_balance(wallet=wallet, amount=amount)

        bonus_txn_repo.create(
            user_id=user.id,
            reference=reference,
            message=f'{amount} withrawn to wallet',
            amount=amount,
            old_balance=old_bonus_balance,
            new_balance=wallet.bonus,
            txn_type=TxnType.CREDIT.value,
            status=Status.SUCCESS.value,
            created_at=datetime.now()
        )

        txn_repo.create_funding_txn(
            user_id=user.id,
            reference=reference,
            provider_reference=reference,
            service=Services.FUNDING.value,
            service_provider='Bonus Wallet',
            service_type='Bonus Withdrwal', 
            beneficiary='Wallet',
            product=f'{amount} funding',
            message=f'Funding of {amount} was successful',
            api_response=f'Funding of {amount} was successful',
            amount=amount,
            old_balance=old_balance,
            new_balance=new_balance,
            service_from='Bonus Wallet',
            value=0,
            status=Status.SUCCESS.value
        )

        db.commit()

        return {'message': f'{amount} withdrawn to wallet'}

    except Exception:
        db.rollback()
        raise