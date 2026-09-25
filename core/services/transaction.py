from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from core.error.http import InconsistenceBalanceError, InsufficientBalanceError, NotFoundError
from core.utils import PaymentExecutorResponse, ProviderResponse, TxnDetails, generate_reference
from core.services.wallet import Wallet_Manager
from models.plans.network import DataPlan, DiscountType
from models.users import Status, TxnType, User
from repositories.users import BonusTxnRepository, TxnRepository



class TransactionService:
    def __init__(self, user: User, db: Session):
        self.db = db
        self.user = user
        self.wallet_manager = Wallet_Manager(user=user, db=db)
        self.txn_repo = TxnRepository(db)

    async def execute_payment(self, plan: object, amount: Decimal | None, transaction_details: TxnDetails, from_api: bool):

        txn_details = transaction_details.model_dump()

        reference = generate_reference(txn_details.get("service"))
        amount = getattr(plan, 'price', amount)

        discount = (
            plan.api_discount if from_api
            else plan.agent_discount if self.user.is_agent
            else plan.discount
        ) or Decimal("0")

        discount_type = (
            plan.api_discount_type if from_api
            else plan.agent_discount_type if self.user.is_agent
            else plan.discount_type
        ) or DiscountType.FLAT.value

        amount = amount - discount if from_api else amount
        cash_back = (
            Decimal("0") if from_api 
            else discount if discount_type == DiscountType.FLAT.value
            else amount*discount/Decimal('100') if discount_type == DiscountType.PERCENTAGE.value
            else Decimal("0")
        )

        self.wallet_manager.lock_wallet()

        if not self.wallet_manager.has_sufficient_balance(amount): 
            raise InsufficientBalanceError()

        old_balance = self.wallet_manager.current_balance()
        new_balance = self.wallet_manager.update_balance(-amount)

        self.txn_repo.create(
            user_id=self.user.id,
            reference=reference,
            request_id=txn_details.get('request_id'),
            service=txn_details.get('service'),
            service_provider=txn_details.get('service_provider'),
            service_type=txn_details.get('service_type'),
            beneficiary=txn_details.get('beneficiary'),
            value=txn_details.get('value'),
            product=txn_details.get('product'),
            message='Transaction on progress',
            api_response=None,
            amount=amount,
            old_balance=old_balance,
            new_balance=new_balance,
            status=Status.PENDING.value
        )

        return PaymentExecutorResponse(
            cash_back=cash_back,
            amount=amount,
            old_balance=old_balance,
            reference=reference
        )

    async def update_transaction(self, reference: str, cash_back: Decimal | None, provider_response: ProviderResponse | Exception):

        if not (txn := self.txn_repo.get_by_reference(reference=reference)):
            raise NotFoundError("Unable to retrieve transaction for update")

        plan_label = f'{txn.product} for {txn.beneficiary}'

        message_map = {
            Status.SUCCESS.value: f'{plan_label} was successful',
            Status.PENDING.value: f'{plan_label} is on progress',
            Status.FAIL.value: f'{plan_label} was unsuccessful'
        }

        if isinstance(provider_response, Exception):
            status = Status.FAIL.value
            api_response = str(provider_response)
        else:
            response = provider_response.model_dump()
            status = response.get('status')
            api_response = response.get('api_response')
            txn.service_from = response.get('provider_name')
            txn.provider_reference = response.get('provider_ref')

        message = message_map.get(status)

        if status == Status.FAIL.value:
            if txn.status != Status.FAIL.value:
                amount = txn.amount
                txn.new_balance = (new_balance := self.wallet_manager.update_balance(amount))
                txn.message = message
                txn.status = Status.FAIL.value

        else:
            txn.message = message
            txn.status = status
            txn.api_response = api_response
            new_balance = txn.new_balance

            if cash_back and status == Status.SUCCESS.value:
                bonus_txn_repo = BonusTxnRepository(self.db)

                self.wallet_manager.lock_wallet()
                old_bonus = self.wallet_manager.wallet.bonus
                self.wallet_manager.wallet.bonus += cash_back
                bonus_txn_repo.create(
                    user_id=self.user.id,
                    reference=reference,
                    message=f'Earned ₦{cash_back.normalize()}',
                    amount=cash_back,
                    old_balance=old_bonus,
                    new_balance=self.wallet_manager.wallet.bonus,
                    txn_type=TxnType.CREDIT.value,
                    status=Status.SUCCESS.value,
                    created_at=datetime.now()
                )

        self.db.commit()

        return {
            'status': status,
            'api_response': api_response,
            'message': message,
            "new_balance": new_balance
        }