from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import and_, delete, func, not_, select, or_
from sqlalchemy.orm import Session, joinedload
from core.cryptography import decrypt_data
from models.users import OTP, BonusTransaction, Services, Status, TxnType, User, UserAPIKey, UserKYC, VirtualAccount, Wallet, Transaction


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str, number: str, password: str, pin: str, is_active: bool | None, is_agent: bool | None = False, is_admin: bool | None = False,):
        user = User(name=name, email=email, number=number, pin=pin, password=password, is_active=is_active, is_admin=is_admin, is_agent=is_agent)
        self.db.add(user)
        self.db.flush()

        wallet = Wallet(user_id=user.id)
        self.db.add(wallet)
        self.db.flush()

        self.db.commit()

        return user

    def get_by_id(self, user_id: int):
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        return user
    
    def get_by_email(self, email: str):
        user = self.db.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()
        return user

    def get_by_number(self, number: str):
        user = self.db.execute(select(User).where(User.number == number)).scalar_one_or_none()
        return user

    def get_all(self, offset: int, limit: int, is_active: bool | None, is_agent: bool | None, is_admin: bool | None, search: str = ""):
        return self.db.execute(
            select(User)
            .options(
                joinedload(User.wallet),
                joinedload(User.user_api_key),
                joinedload(User.accounts)
            )
            .where(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.number.ilike(f"%{search}%"),
                    User.name.ilike(f"%{search}%"),
                ),
                or_(is_active is None, User.is_active == is_active),
                or_(is_agent is None, User.is_agent == is_agent),
                or_(is_admin is None, User.is_admin == is_admin)
            )
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).unique().scalars().all()

    def get_total(self, start_date: date | None = None, end_date: date | None = None):
        return self.db.execute(
            select(
                func.count(User.id).label("total_users"),
                func.count(User.id).filter(User.is_active is True).label("active_users"),
                func.count(User.id).filter(not_(User.is_agent is True)).label("smart_users"),
                func.count(User.id).filter(User.is_agent is True).label("agent_users"),
                func.count(User.id).filter(User.is_admin).label("total_admin")
            )
            .where(
                User.created_at >= datetime.combine(start_date, time.min) if start_date else True, 
                User.created_at <= datetime.combine(end_date, time.max) if end_date else True
            )).one()

    def user_leaderboard(self, limit: int, start_date: date | None = None, end_date: date | None = None):
        return  self.db.execute(
            select(
                User.name,
                User.email,
                func.sum(Transaction.amount).label("amount"),
                func.count(Transaction.id).label("total")
            ).join(Transaction)
            .where(
                Transaction.status.in_([Status.SUCCESS.value, Status.COMPLETED.value]),
                Transaction.service.in_(["data", "airtime", "cable", "disco"]),
                or_(start_date is None, Transaction.created_at >= datetime.combine(start_date, time.min) if start_date else True),
                or_(end_date is None, Transaction.created_at <= datetime.combine(end_date, time.max) if end_date else True)
            ).group_by(User.name, User.email)
            .order_by(
                func.sum(Transaction.amount).desc()
            ).limit(limit)
        ).all()

class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id):
        wallet = self.db.execute(select(Wallet).where(Wallet.user_id == user_id)).scalar_one_or_none()
        return wallet

    def get_for_update(self, user_id: int):
        wallet = self.db.execute(select(Wallet).where(Wallet.user_id == user_id).with_for_update()).scalar_one_or_none()
        return wallet
    
    def update_balance(self, wallet: Wallet, amount: Decimal):
        wallet.balance += amount
        self.db.flush()
        return wallet.balance

    def get_total(self):
        wallets = self.db.execute(
            select(
                func.sum(Wallet.balance).label("total_balance"),
                func.sum(Wallet.bonus).label("total_bonus_balance")
            )).one()
        return wallets

class OTPRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, otp: str, expiry_time: datetime):
        otp = OTP(user_id=user_id, otp=otp, expiry_time=expiry_time)
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        return otp
    
    def get_by_token(self, token: str):
        otp = self.db.execute(select(OTP).where(OTP.token == token)).scalar_one_or_none()
        return otp

    def get_latest_by_user_id(self, user_id: int):
        otp = self.db.execute(select(OTP).where(OTP.user_id == user_id).order_by(OTP.id.desc())).scalars().first()
        return otp

    def get_latest_by_user_id(self, user_id: int):
        otp = self.db.execute(
            select(OTP)
            .where(OTP.user_id == user_id)
            .order_by(OTP.id.desc())
        ).scalars().first()
        return otp

class TxnRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_id: int, reference: str, service: str, service_provider: str, service_type: str | None, beneficiary: str, value: Decimal | None,
        product: str | None, message: str, api_response: str | None, amount: Decimal, old_balance: Decimal, new_balance: Decimal, status: str, request_id: str = None
    ):
        txn = Transaction(
            reference=reference, request_id=request_id, user_id=user_id, service=service, service_provider=service_provider, service_type=service_type, product=product, value=value,
            beneficiary=beneficiary, message=message, api_response=api_response, amount=amount, old_balance=old_balance, new_balance=new_balance, status=status
        )
        self.db.add(txn)
        self.db.flush()
        return txn

    def create_funding_txn(
        self, user_id: int, reference: str, provider_reference: str, service: str, service_provider: str, service_type: str, beneficiary: str, product: str,
        message: str, api_response: str, amount: Decimal, old_balance: Decimal, new_balance: Decimal, service_from: str, value: Decimal, status: str
    ):
        txn = Transaction(
            user_id=user_id, reference=reference, 
            provider_reference=provider_reference, 
            service=service, service_provider=service_provider, service_type=service_type, beneficiary=beneficiary,
            value=value, product=product, message=message, api_response=api_response, amount=amount, old_balance=old_balance, new_balance=new_balance, service_from=service_from, status=status
        )
        self.db.add(txn)
        self.db.flush()
        return txn

    def create_kyc_txn(
            self, user_id: int, reference: str, service: str, service_provider: str, service_type: str, beneficiary: str, product: str, message: str,
            amount: Decimal, old_balance: Decimal, new_balance: Decimal, status: str
    ):
        txn = Transaction(
            user_id=user_id, reference=reference, service=service, service_provider=service_provider, service_type=service_type, beneficiary=beneficiary,
            product=product, message=message, amount=amount, old_balance=old_balance, new_balance=new_balance, status=status
        )
        self.db.add(txn)
        self.db.flush()
        return txn

    def get_all(self, offset: int, limit: int):
        txns = self.db.execute(
            select(Transaction)
            .options(joinedload(Transaction.user))
            .order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
            ).scalars().all()
        return txns

    def get_by_id(self, txn_id):
        txn = self.db.execute(select(Transaction).where(Transaction.id == txn_id)).scalar_one_or_none()
        return txn

    def service_txn_by_status(self, service: str, status: str, offset: int, limit: int):
        txns = self.db.execute(select(Transaction)
            .options(joinedload(Transaction.user))
            .where(Transaction.service == service, Transaction.status == status)
            .order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).unique().scalars().all()
        return txns

    def get_by_user_id(self, user_id):
        txns = self.db.execute(select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.created_at.desc())).scalars().all()
        return txns

    def filter_by_user_id(self, user_id: int, search: str | None, service: str | None, limit: int, offset: int):
        txns = self.db.execute(
            select(Transaction)
            .options(joinedload(Transaction.user))
            .join(Transaction.user)
            .where(
                or_(
                    Transaction.reference.ilike(f'%{search}%'),
                    Transaction.beneficiary.ilike(f'%{search}%')
                ),
                Transaction.user_id == user_id,
                or_(service is None, Transaction.service == service)
            )
            .offset(offset=offset)
            .limit(limit=limit)
            .order_by(Transaction.created_at.desc())
        ).scalars().all()
        return txns

    def get_by_reference(self, reference):
        txn = self.db.execute(
            select(Transaction)
            .where(Transaction.reference == reference)
        ).scalar_one_or_none()
        return txn

    def get_recent_transactions(self, user_id: int, limit: int):
        txns = self.db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            ).scalars().all()
        return txns

    def get_total(self, start_date: date | None = None, end_date: date | None = None):
        success = Transaction.status == Status.SUCCESS.value
        failed = Transaction.status == Status.FAIL.value
        pending = Transaction.status == Status.PENDING.value
        completed = Transaction.status == Status.COMPLETED.value
        reversed = Transaction.status == Status.REVERSED.value
        start_d = start_date or date.today()
        end_d = end_date or date.today()
        txns = self.db.execute(
            select(
                func.count(Transaction.id).label("total_txn"),
                func.count(Transaction.status).filter(success).label("total_success"),
                func.count(Transaction.status).filter(failed).label("total_failed"),
                func.count(Transaction.status).filter(pending).label("total_pending"),
                func.count(Transaction.status).filter(reversed).label("total_reversed"),
                func.count(Transaction.status).filter(completed).label("total_completed"),
                func.sum(Transaction.amount).filter(or_(success, completed), not_(Transaction.service == Services.FUNDING.value)).label("total_sold"),
                func.sum(Transaction.amount).filter(or_(success, completed), Transaction.service == Services.FUNDING.value).label("total_funding"),
                func.sum(Transaction.value).filter(or_(success, completed), Transaction.service == Services.DATA.value).label("data_sold"),
                func.sum(Transaction.value).filter(or_(success, completed), Transaction.service == Services.AIRTIME.value).label("airtime_sold"),
                func.sum(Transaction.value).filter(or_(success, completed), Transaction.service == Services.CABLE.value).label("cable_sold"),
                func.sum(Transaction.value).filter(or_(success, completed), Transaction.service == Services.DISCO.value).label("disco_sold")
            ).where(
                Transaction.created_at >= datetime.combine(start_d, time.min) if start_date else True,
                Transaction.created_at < datetime.combine(end_d, time.max) if end_date else True
            )).one()
        return txns

    def sales(self, start_date: date | None = None, end_date: date | None = None):
        return self.db.execute(
            select(
                Transaction.service,
                Transaction.service_provider.label("biller"),
                Transaction.service_type.label("biller_type"),
                func.sum(Transaction.value).filter(Transaction.service == Services.AIRTIME.value).label("airtime_value"),
                func.sum(Transaction.amount).filter(Transaction.service == Services.AIRTIME.value).label("airtime_amount"),
                func.sum(Transaction.value).filter(Transaction.service == Services.DATA.value).label("data_value"),
                func.sum(Transaction.amount).filter(Transaction.service == Services.DATA.value).label("data_amount"),
                func.sum(Transaction.value).filter(Transaction.service == Services.CABLE.value).label("cable_value"),
                func.sum(Transaction.amount).filter(Transaction.service == Services.CABLE.value).label("cable_amount"),
                func.sum(Transaction.value).filter(Transaction.service == Services.DISCO.value).label("disco_value"),
                func.sum(Transaction.amount).filter(Transaction.service == Services.DATA.value).label("disco_amount"),
            ).where(
                Transaction.status.in_([Status.SUCCESS.value, Status.COMPLETED.value]),
                Transaction.created_at >= datetime.combine(start_date, time.min) if start_date else True, 
                Transaction.created_at <= datetime.combine(end_date, time.max) if end_date else True,
                not_(Transaction.service == Services.FUNDING.value)
            ).group_by(
                Transaction.service,
                Transaction.service_provider,
                Transaction.service_type
            )).mappings().all()

    def filter_transaction(self, service: str | None, status: str | None, offset: int, limit: int, search_param: str):
        txns = self.db.execute(
            select(Transaction)
            .options(joinedload(Transaction.user))
            .join(User)
            .where(
                or_(
                    Transaction.reference.ilike(f'%{search_param}%'),
                    Transaction.provider_reference.ilike(f'%{search_param}%'),
                    Transaction.request_id.ilike(f'%{search_param}%'),
                    Transaction.beneficiary.ilike(f'%{search_param}%'),
                    User.email.ilike(f'%{search_param}%')
                ),
                or_(service is None, Transaction.service == service),
                or_(status is None, Transaction.status == status)
            )
            .order_by(Transaction.created_at.desc())
            .offset(offset=offset)
            .limit(limit=limit)
        ).scalars().all()
        return txns

    def delete_by_user_id(self, user_id: int):
        self.db.execute(delete(Transaction).where(Transaction.user_id == user_id))

class BonusTxnRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, reference: str, message: str, amount: Decimal, old_balance: Decimal, new_balance: Decimal, txn_type: str, status: str, created_at: datetime):
        bonus_txn = BonusTransaction(
            user_id=user_id,
            reference=reference,
            message=message,
            amount=amount,
            old_balance=old_balance,
            new_balance=new_balance,
            txn_type=txn_type,
            status=status,
            created_at=created_at
        )
        self.db.add(bonus_txn)
        return bonus_txn

    def get_all(self, offset: int, limit: int):
        bonus_txn = self.db.execute(
            select(BonusTransaction)
            .options(joinedload(BonusTransaction.user))
            .order_by(BonusTransaction.created_at.desc())
            .offset(offset=offset)
            .limit(limit=limit)
        ).scalars().all()
        return bonus_txn

    def query_transaction(self, offset: int, limit: int, params: dict, search_params: str):
        txns = self.db.execute(
            select(BonusTransaction)
            .join(BonusTransaction.user)
            .options(joinedload(BonusTransaction.user))
            .where(
                or_(
                    BonusTransaction.reference.ilike(f'%{search_params}%'),
                    User.email.ilike(f'%{search_params}%')
                ),
                and_(
                    *(getattr(BonusTransaction, key, None).ilike(f'%{value}%') for key, value in params.items())
                )
            )
            .order_by(BonusTransaction.created_at.desc())
            .limit(limit=limit)
            .offset(offset=offset)
        ).scalars().all()
        return txns

    def get_by_reference(self, reference: str):
        bonus_txn = self.db.execute(select(BonusTransaction).where(BonusTransaction.reference == reference)).scalar_one_or_none()
        return bonus_txn

    def get_recent_txn(self, user_id: int, limit: int):
        bonus_txns = self.db.execute(
            select(BonusTransaction).where(
                BonusTransaction.user_id == user_id
            )
            .order_by(BonusTransaction.created_at.desc())
            .limit(limit)
        ).scalars().all()
        return bonus_txns

    def all_time_earned(self, user_id: int):
        bonus_txn = self.db.execute(
            select(func.sum(BonusTransaction.amount)).where(
                BonusTransaction.user_id == user_id, 
                BonusTransaction.status == Status.SUCCESS.value,
                BonusTransaction.txn_type == TxnType.CREDIT.value
        )).scalar()
        return bonus_txn

    def search_from_bonus_txns(self, search: str, offset: int, limit: int):
        bonus_txns = self.db.execute(
            select(BonusTransaction)
            .join(BonusTransaction.user)
            .options(joinedload(BonusTransaction.user))
            .where(
                or_(
                    BonusTransaction.reference.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                ))
            .order_by(BonusTransaction.created_at.desc())
            .limit(limit=limit)
            .offset(offset=offset)
        ).scalars().all()
        return bonus_txns

    def delete_by_user_id(self, user_id: int):
        self.db.execute(delete(BonusTransaction).where(BonusTransaction.user_id == user_id))

class VirtualAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, bank_code: str, provider: str, account_number: str, bank_name: str, account_name: str, account_reference: str):
        virtual_account = VirtualAccount(
            user_id=user_id, bank_code=bank_code, provider=provider, account_number=account_number, 
            bank_name=bank_name, account_name=account_name, account_reference=account_reference
        )
        self.db.add(virtual_account)
        return virtual_account

    def get_by_id(self, id: int):
        virtual_account = self.db.execute(select(VirtualAccount).where(VirtualAccount.id == id)).scalar_one_or_none()
        return virtual_account

    def get_by_user_id(self, user_id: int):
        virtual_account = self.db.execute(select(VirtualAccount).where(VirtualAccount.user_id == user_id)).scalars().all()
        return virtual_account

    def get_by_account_number(self, account_number: str):
        virtual_account = self.db.execute(select(VirtualAccount).where(VirtualAccount.account_number == account_number)).scalars().first()
        return virtual_account

    def get_by_user_id_and_provider(self, user_id, provider: str):
        virtual_account = self.db.execute(
            select(VirtualAccount)
            .where(
                VirtualAccount.user_id == user_id,
                VirtualAccount.provider == provider
            )).scalars().all()
        return virtual_account

    def get_all(self, offset: int, limit: int):
        virtual_accounts = self.db.execute(
            select(VirtualAccount)
            .options(joinedload(VirtualAccount.user))
            .order_by(VirtualAccount.id.desc())
            .offset(offset)
            .limit(limit)
        ).unique().scalars().all()
        return virtual_accounts

    def filter_all(self, search_param: str, provider: str | None, offset: int, limit: int):
        virtual_accounts = self.db.execute(
            select(VirtualAccount)
            .join(VirtualAccount.user)
            .options(joinedload(VirtualAccount.user))
            .where(
                or_(
                    VirtualAccount.account_number.ilike(f'%{search_param}%'),
                    VirtualAccount.account_number.ilike(f'%{search_param}%'),
                    VirtualAccount.account_reference.ilike(f'%{search_param}%'),
                    User.email.ilike(f'%{search_param}%')
                ),
                or_(provider is None, VirtualAccount.provider == provider)
            )
            .offset(offset=offset)
            .limit(limit=limit)
            .order_by(VirtualAccount.id.desc())
        ).scalars().all()
        return virtual_accounts

    def get_by_bank_code_and_provider(self, user_id: int, bank_code: str, provider: str):
        virtual_accounts = self.db.execute(
            select(VirtualAccount)
            .where(
                VirtualAccount.bank_code == bank_code,
                VirtualAccount.provider == provider,
                VirtualAccount.user_id == user_id
            )
        ).scalar()
        return virtual_accounts

    def delete_by_user_id(self, user_id: int):
        self.db.execute(delete(VirtualAccount).where(VirtualAccount.user_id == user_id))

class UserKYCRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int):
        user_kyc = UserKYC(user_id = user_id)
        self.db.add(user_kyc)
        self.db.commit()
        self.db.refresh(user_kyc)
        return user_kyc

    def get_by_user_id(self, user_id: int):
        user_kyc = self.db.execute(select(UserKYC).where(UserKYC.user_id == user_id)).scalar_one_or_none()
        return user_kyc

class UserAPIKeyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, api_key: str, is_active: bool):
        user_api_key = UserAPIKey(user_id=user_id, api_key=api_key, is_active=is_active)
        self.db.add(user_api_key)
        self.db.commit()
        self.db.refresh(user_api_key)
        return user_api_key

    def get_all(self):
        users_api_key = self.db.execute(select(UserAPIKey.api_key).where(UserAPIKey != None)).scalars().all()
        return users_api_key

    def get_by_user_id(self, user_id: int):
        user_api_key = self.db.execute(select(UserAPIKey).where(UserAPIKey.user_id == user_id)).scalar_one_or_none()
        return user_api_key
    
    def get_by_api_key(self, api_key: str):
        user_api_key = self.db.execute(select(UserAPIKey).where(UserAPIKey.api_key == api_key)).scalar_one_or_none()
        return user_api_key