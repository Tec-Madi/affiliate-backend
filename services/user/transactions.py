from sqlalchemy.orm import Session

from models.users import User
from repositories.users import TxnRepository


def transaction_summary_function(user: User, db: Session, search: str | None, service: str | None, page: int, limit: int):

    txn_repo = TxnRepository(db)

    offset = (page - 1)  * limit

    txns = txn_repo.filter_by_user_id(user_id=user.id, search=search, service=service, limit=limit, offset=offset)

    return [{
        'id': txn.id,
        'reference': txn.reference,
        'service': txn.service,
        'service_provider': txn.service_provider,
        'service_type': txn.service_type,
        'beneficiary': txn.beneficiary,
        'message': txn.message,
        'product': txn.product,
        'amount': txn.amount,
        'old_balance': txn.old_balance,
        'new_balance': txn.new_balance,
        'status': txn.status,
        'created_at': txn.created_at
    } for txn in txns]