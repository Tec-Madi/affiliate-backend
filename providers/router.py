from types import NoneType

from fastapi import Request
from sqlalchemy.orm import Session

from core.error.http import BadRequestError, NotFoundError
from models.admin import PaymentProviderName, ProviderType
from models.plans.cable import CablePlan, ProviderCable, ProviderCablePlan
from models.plans.disco import DiscoPlan, ProviderDisco, ProviderDiscoPlan
from models.plans.network import AirtimePlan, DataPlan, ProviderDataPlan, ProviderNetwork
from models.users import Services
from providers.pgw.paymentpoint import PaymentPoint
from providers.pgw.securewaveng import SecureWaveNg
from providers.vtu.madix import MadixProvider
from providers.vtu.ogdams import Ogdams
from providers.vtu.quicklysim import QuicklySim
from providers.vtu.smeplug import SmePlug
from providers.base import BasePayment, BaseProvider
from providers.vtu.adex import AdexProvider
from providers.vtu.msorg import MsorgProvider
from repositories.admin import PaymentPlanRepository, PaymentProviderRepository, ProviderRepository
from repositories.plans.cable import ProviderCablePlanRepository, ProviderCableRepository
from repositories.plans.disco import ProviderDiscoRepository, ProviderDiscoPlanRepository
from repositories.plans.network import ProviderDataPlanRepository, ProviderNetworkRepository
from repositories.users import VirtualAccountRepository


class VTURouter:

    @staticmethod
    async def vend_vtu_service(payload: dict, service: Services, db: Session):

        provider_repo = ProviderRepository(db)

        biller_key = f"{"network" if service in [Services.DATA, Services.AIRTIME] else "cable" if service == Services.CABLE else "disco"}"

        plan: DataPlan | AirtimePlan | CablePlan | DiscoPlan = payload.get("plan")
        beneficiary = payload.get("beneficiary")
        amount = payload.get("amount")
        reference = payload.get("reference")
        provider_name = plan.vend_from

        plan_biller_id =  getattr(plan, biller_key+"_id", None)

        if not (provider := provider_repo.get_by_name(name=provider_name)):
            raise NotFoundError("Plan Error, Contact Admin")

        provider_biller_repo = (
            ProviderNetworkRepository if service in [Services.AIRTIME, Services.DATA]
            else ProviderCableRepository if service == Services.CABLE 
            else ProviderDiscoRepository if service == Services.DISCO
            else None
        )

        provider_plan_repo = (
            ProviderDataPlanRepository if service == Services.DATA
            else ProviderCablePlanRepository if service == Services.CABLE
            else ProviderDiscoPlanRepository if service == Services.DISCO
            else None
        )

        provider_biller: ProviderNetwork | ProviderCable | ProviderDisco = getattr(provider_biller_repo(db), "get_by_provider_name_and_"+biller_key+"_id")(provider_name, plan_biller_id)

        provider_plan: ProviderDataPlan | ProviderDiscoPlan | ProviderCablePlan = provider_plan_repo(db).get_by_provider_name_and_plan_id(provider_name, plan.id) if callable(provider_plan_repo) else None

        if not (biller_id := getattr(provider_biller, "provider_"+biller_key+"_id", None)):
            raise NotFoundError("Provider biller_id not found")
        if not (plan_id := getattr(provider_plan, "provider_plan_id", True if service == Services.AIRTIME else None)):
            raise NotFoundError("Provider plan_id not found")

        base_provider_map = {
            ProviderType.MADIX.value: MadixProvider,
            ProviderType.ADEX.value: AdexProvider,
            ProviderType.MSORG.value: MsorgProvider,
            ProviderType.QUICKLYSIM.value: QuicklySim,
            ProviderType.SMEPLUG.value: SmePlug,
            ProviderType.OGDAMS.value: Ogdams
        }

        if not (provider_class := base_provider_map.get(provider.type)):
            raise BadRequestError("Provider not found")

        base_provider: BaseProvider = provider_class(provider)

        return await base_provider.virtual_top_up(
            service=service, 
            payload={
                "biller_id": biller_id, 
                "plan_id": plan_id, 
                "beneficiary": beneficiary, 
                "amount": amount, 
                "reference": reference
            })

    @staticmethod
    async def vtu_webhook_completion():
        pass


class PGWRouter:

    @staticmethod
    async def generate_account_router(user_id: int, payload: dict, db: Session):

        payment_provider_repo = PaymentProviderRepository(db)
        payment_plan_repo = PaymentPlanRepository(db)
        virtual_account_repo = VirtualAccountRepository(db)

        base_payment_map = {
            PaymentProviderName.SECUREWAVENG.value: SecureWaveNg,
            PaymentProviderName.PAYMENTPOINT.value: PaymentPoint
        }

        for provider_name, base_payment in base_payment_map.items():

            provider = payment_provider_repo.get_by_name(name=provider_name)
            if not base_payment:
                continue

            payment_plans = payment_plan_repo.get_by_provider(provider=provider_name)
            
            bank_codes = [payment_plan.bank_code for payment_plan in payment_plans]

            virtual_accounts =  virtual_account_repo.get_by_user_id_and_provider(user_id=user_id, provider=provider_name)
            existing_bank_code = [virtual_account.bank_code for virtual_account in virtual_accounts]

            payload['bank_code'] = [
                bank_code for bank_code in bank_codes
                if bank_code not in existing_bank_code
            ]

            if not (provider_class := base_payment_map.get(provider_name)):
                raise NotFoundError(message="Provider not Found")

            base_payment: BasePayment = provider_class(provider)

            try:
                return await base_payment.generate_static_account(payload=payload)
            except Exception:
                continue

    @staticmethod
    async def receive_payment_router(provider_name: PaymentProviderName, request: Request, db: Session):

        payment_provider_repo =  PaymentProviderRepository(db)

        payment_provider_map = {
            PaymentProviderName.SECUREWAVENG.value: SecureWaveNg,
            PaymentProviderName.PAYMENTPOINT.value: PaymentPoint
        }

        if not (payment_provider := payment_provider_repo.get_by_name(name=provider_name)):
            raise NotFoundError(message='provider not found')

        provider_class: BasePayment = payment_provider_map[provider_name](payment_provider)

        return await provider_class.receive_payment(request=request)