from sqlalchemy.orm import Session
from decimal import Decimal

from models.users import User
from repositories.users import TxnRepository, WalletRepository

class Wallet_Manager:
    def __init__(self, user: User, db: Session):
        self.user_id = user.id
        self.wallet = user.wallet
        self.db = db

    def lock_wallet(self):
        wallet_repo = WalletRepository(self.db)
        self.wallet = wallet_repo.get_for_update(self.user_id)

    def current_balance(self):
        return self.wallet.balance

    def has_sufficient_balance(self, amount: Decimal):
        return amount <= self.wallet.balance

    def has_consistent_balance(self):
        txn_repo = TxnRepository(self.db)
        return self.wallet.balance == txn_repo.get_by_user_id(self.user_id)[0].new_balance

    def update_balance(self, amount: Decimal):
        self.wallet.balance += amount
        self.db.flush()
        return self.wallet.balance