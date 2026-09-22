from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import require_admin
from core.database import get_db
from services.admin.transactions import *
from models.users import *

admin_transaction_router = APIRouter(
    prefix='/admin',
    tags=['Admin Transaction Management']
)

@admin_transaction_router.get("/transactions")
def query_transaction( 
        page: int = 1,
        limit: int = 50,
        search: str = "",
        service: Services | None = None,
        status: Status | None = None,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return query_transaction_function(user=user, db=db, page=page, limit=limit, service=service, status=status, search_param=search)

@admin_transaction_router.post("/bonus/transaction/all/{page}/{limit}")
def query_bonus_transaction(
        page: int,
        limit: int,
        search: str = "",
        status: Status | None = None,
        txn_type: TxnType | None = None,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return query_bonus_transaction_function(user=user, db=db, page=page, limit=limit, status=status, txn_type=txn_type, search_params=search)

#<<< REFUND OR COMPLETE TRANSACTION >>>

@admin_transaction_router.patch('/{update_type}/{txn_id}')
def update_transaction(txn_id: int, update_type: UpdateTxntype, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return update_transaction_function(user=user, db=db, txn_id=txn_id, update_type=update_type)