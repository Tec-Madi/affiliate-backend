from typing import Literal
from sqlalchemy.orm import Session

from core.error.http import AdminOnlyError, BadRequestError, ForbiddenError, NotFoundError
from core.services.wallet import Wallet_Manager
from core.utils import generate_api_key, generate_reference
from models.users import Services, Status, Transaction, TxnType, User
from repositories.users import BonusTxnRepository, TxnRepository, UserAPIKeyRepository, UserRepository, VirtualAccountRepository, WalletRepository

from core.cryptography import decrypt_data, encrypt_data, hash_data

def all_users_function(admin_user: User, db: Session, page: int, limit: int, search: str, is_active: bool | None, is_agent: bool | None, is_admin: bool | None):

    if not admin_user.is_admin:
        raise AdminOnlyError()

    users = UserRepository(db).get_all(offset=((page - 1) * limit), limit=limit, search=search, is_active=is_active, is_agent=is_agent, is_admin=is_admin)

    return [{
        'id': user.id,
        'name': user.name,
        'wallet_balance': user.wallet.balance,
        "bonus_balance": user.wallet.bonus,
        'email': user.email,
        'number': user.number,
        'is_active': user.is_active,
        "is_agent": user.is_agent,
        'is_admin': user.is_admin,
        "api_access_is_allowed": user.user_api_key.is_active if user.user_api_key else False,
        "api_key": decrypt_data(user.user_api_key.api_key) if user.user_api_key else None,
        'created_at': user.created_at,
        'virtual_accounts': [{
            "id": account.id,
            "account_number": account.account_number,
            "account_name": account.account_name,
            "bank_name": account.bank_name,
            "provider": account.payment_provider.name
        }for account in user.accounts]
    } for user in users]

def upsert_user_function(admin_user: User, db: Session, action: Literal["create", "edit"], user_schema: object, user_id: int | None = None):

    if not admin_user.is_admin:
        raise ForbiddenError('only admin can access this page')

    user_repo = UserRepository(db)

    schema_to_use = {
        'name': user_schema.name,
        'email': user_schema.email,
        'number': user_schema.number,
        'is_active': user_schema.is_active,
        'is_admin': user_schema.is_admin,
        'is_agent': user_schema.is_agent,
        'password': hash_data(user_schema.password) if user_schema.password else None,
        'pin': hash_data(user_schema.pin) if user_schema.pin else None
    }

    if action == "edit":
        if not (user := user_repo.get_by_id(user_id=user_id)):
            raise NotFoundError('user not found')

        if schema_to_use:
            for key, value in schema_to_use.items():
                if  value is not None:
                    setattr(user, key, value)

        elif action == "create":
            user = user_repo.create(**schema_to_use)

        if (allow_api_access := user_schema.allow_api_access) is not None:
            if(user_api_key := UserAPIKeyRepository(db).get_by_user_id(user_id=user.id)):
                user_api_key.is_active = allow_api_access
            else:
                api_key = encrypt_data(generate_api_key())
                UserAPIKeyRepository(db).create(user.id, api_key, is_active=allow_api_access)

        if (update_balance := user_schema.update_balance) is not None:

            amount = update_balance.amount
            txn_type = update_balance.txn_type

            wallet_manager = Wallet_Manager(user=user, db=db)

            wallet_manager.lock_wallet()

            if txn_type == TxnType.CREDIT: new_balance = wallet_manager.update_balance(amount)
            elif txn_type == TxnType.DEBIT: new_balance = wallet_manager.update_balance(-amount)
            else: raise BadRequestError("Invalid Operation")

            service = Services.FUNDING.value

            TxnRepository(db).create(
                user_id=user.id, 
                reference=generate_reference(service), 
                service=service,
                service_provider='ADMIN', 
                service_type='MANUAL_BALANCING',
                beneficiary='', 
                product=f'{amount} manual funding',
                message=update_balance.message,
                api_response=None, 
                amount=amount, 
                old_balance=wallet_manager.current_balance(), 
                new_balance=new_balance, 
                status=Status.SUCCESS.value, 
                value=amount
            )

        db.commit()

    return { "message":  "user" + (" created" if action == "create" else " updated") + " successfully" }

def delete_user_function(admin_user: User, db: Session, user_id: int, id: int | None = None, for_va: bool = False):

    if not admin_user.is_admin:
        raise AdminOnlyError()
    
    if not (user := UserRepository(db).get_by_id(user_id=user_id)):
            raise NotFoundError('user not found')

    if for_va:
        if not (virtual_account := VirtualAccountRepository(db).get_by_id(id=id)):
            raise NotFoundError("Virtual account not found")
        db.delete(virtual_account)
    else:
        if user_id == admin_user.id:
            raise BadRequestError("Your can't delete your account because you're the admin")
        if (wallet := WalletRepository(db).get_by_user_id(user.id)):
            db.delete(wallet)
        if (user_api_key := UserAPIKeyRepository(db).get_by_user_id(user.id)):
            db.delete(user_api_key)
        VirtualAccountRepository(db).delete_by_user_id(user_id)
        TxnRepository(db).delete_by_user_id(user.id)
        BonusTxnRepository(db).delete_by_user_id(user.id)
        db.delete(user)

    db.commit()

    return {'message': user.name.capitalize().partition(" ")[0] + "'s" + (" virtual account" if for_va else " account") + " deleted successfully"}