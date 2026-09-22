from datetime import datetime
from sqlalchemy.orm import Session

from core.error.http import AdminOnlyError, BadRequestError, NotFoundError
from models.users import Status, UpdateTxntype, User
from repositories.users import BonusTxnRepository, TxnRepository, WalletRepository

def query_transaction_function(user: User, db: Session, page: int, limit: int, status: str, service: str, search_param: str):

    if not user.is_admin:
        raise AdminOnlyError()

    txn_repo = TxnRepository(db)

    offset = (page - 1) * limit

    txns = txn_repo.filter_transaction(service=service, status=status, offset=offset, limit=limit, search_param=search_param)

    return [{
        'id': txn.id,
        'user_id': txn.user_id,
        'email': txn.user.email,
        'reference': txn.reference,
        'request_id': txn.request_id,
        'provider_reference': txn.provider_reference,
        'service': txn.service.upper(),
        'service_provider': txn.service_provider.upper(),
        'service_type': txn.service_type.upper() if txn.service_type else None,
        'beneficiary': txn.beneficiary,
        'product': txn.product,
        'message': txn.message,
        'api_response': txn.api_response,
        'amount': txn.amount,
        'old_balance': txn.old_balance,
        'new_balance': txn.new_balance,
        'fee': txn.fee,
        'token': txn.token,
        'service_from': txn.service_from,
        'status': txn.status,
        'created_at': txn.created_at
    } for txn in txns]

def update_transaction_function(user: User, db: Session, txn_id: int, update_type: UpdateTxntype):

    if user.is_admin is not True:
        raise AdminOnlyError()

    txn_repo = TxnRepository(db)
    wallet_repo = WalletRepository(db)

    if not (txn := txn_repo.get_by_id(txn_id=txn_id)):
        raise BadRequestError(message='Transaction not found')
    if not (wallet := wallet_repo.get_for_update(user_id=txn.user_id)):
        raise NotFoundError(message='wallet not Found')

    try:
        if update_type == UpdateTxntype.REFUND:
            if txn.status != Status.SUCCESS.value and txn.status != Status.PENDING.value:
                raise BadRequestError(message='only failed or pending transactions can be refunded')

            new_balance = wallet_repo.update_balance(wallet=wallet, amount=txn.amount)
            txn.message = f'{txn.product} made at {txn.created_at.strftime("%Y-%m-%d %H:%M:%S")} was refunded'
            txn.api_response = None
            txn.old_balance = wallet.balance
            txn.new_balance = new_balance
            txn.status = Status.REVERSED.value
            txn.created_at = datetime.now()

        elif update_type == UpdateTxntype.COMPLETE:
            if txn.status != Status.PENDING.value:
                raise BadRequestError(message='only pending transactions can be make success')

            txn.message = f'{txn.product} was successful'
            txn.api_response = None
            txn.status = Status.COMPLETED.value

        db.commit()

    except Exception:
        db.rollback()
        raise 

    return {'message': f'{txn.reference} {update_type.value}ed'}

def query_bonus_transaction_function(user: User, db: Session, page: int, limit: int, search_params: str, txn_type: str, status: str):

    if not user.is_admin:
        raise AdminOnlyError()

    offset = (page - 1) * limit

    bonus_txn_repo = BonusTxnRepository(db)

    query_params = {
        'txn_type': txn_type if txn_type else None,
        'status': status
    }

    query_params = {
        key: value
        for key, value in query_params.items()
        if value is not None
    }

    bonus_txns = bonus_txn_repo.query_transaction(offset=offset, limit=limit, search_params=search_params, params=query_params)

    return [{
        'id': bonus_txn.id,
        'user_email': bonus_txn.user.email,
        'reference': bonus_txn.reference,
        'message': bonus_txn.message,
        'amount': bonus_txn.amount,
        'old_balance': bonus_txn.old_balance,
        'new_balance': bonus_txn.new_balance,
        'txn_type': bonus_txn.txn_type,
        'status': bonus_txn.status,
        'created_at': bonus_txn.created_at
    } for bonus_txn in bonus_txns]