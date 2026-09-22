from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.admin import AdminID, GeneralMessage, KYCPlan, PaymentProvider, PlanRoute, Provider, PaymentPlan, SystemInfo

class PlanRouteRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, service: str, plan_id: int, provider: str):
        plan_route = PlanRoute(service=service, plan_id=plan_id, provider=provider)
        self.db.add(plan_route)
        self.db.commit()
        self.db.refresh(plan_route)
        return plan_route
    
    def get_by_id(self, id: int):
        plan_route = self.db.execute(select(PlanRoute).where(PlanRoute.id == id)).scalar_one_or_none()
        return plan_route
    
    def get_all(self):
        plan_routes = self.db.execute(select(PlanRoute)).scalars().all()
        return plan_routes
    
    def get_all_by_services(self, service: str):
        plan_routes = self.db.execute(select(PlanRoute).where(PlanRoute.service == service)).scalars().all()
        return plan_routes
    
    def get_by_service_and_plan_id(self, service: str, plan_id: int):
        plan_route = self.db.execute(select(PlanRoute).where(PlanRoute.service == service, PlanRoute.plan_id == plan_id)).scalar_one_or_none()
        return plan_route

class ProviderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, provider_type: str, base_url: str):
        provider = Provider(name=name, type=provider_type, base_url=base_url)
        self.db.add(provider)
        return provider

    def get_all(self):
        providers = self.db.execute(select(Provider)).scalars().all()
        return providers

    def get_by_id(self, id: int):
        provider = self.db.execute(select(Provider).where(Provider.id == id)).scalar_one_or_none()
        return provider

    def get_by_name(self, name: str):
        provider = self.db.execute(select(Provider).where(Provider.name == name)).scalar_one_or_none()
        return provider

    def get_by_provider_type(self, provider_type: str):
        providers = self.db.execute(select(Provider).where(Provider.type == provider_type)).scalars().all()
        return providers

    def get_all(self):
        providers = self.db.execute(select(Provider)).scalars().all()
        return providers

    def get_provider_names(self):
        providers = self.db.execute(select(Provider.name)).scalars().all()
        return providers

class AdminIDRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, nin: str | None, bvn: str | None):
        admin_id = AdminID(id=1, nin=nin, bvn=bvn)
        self.db.add(admin_id)
        self.db.commit()
        return(admin_id)

    def get_admin_id(self):
        admin_id = self.db.execute(select(AdminID).where(AdminID.id == 1)).scalar_one_or_none()
        return admin_id

class PaymentProviderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, base_url: str):
        payment_provider = PaymentProvider(name=name, base_url=base_url)
        self.db.add(payment_provider)
        return payment_provider
    
    def get_by_id(self, id: int):
        payment_provider = self.db.execute(select(PaymentProvider).where(PaymentProvider.id == id)).scalar_one_or_none()
        return payment_provider

    def get_all(self):
        payment_providers = self.db.execute(select(PaymentProvider)).scalars().all()
        return payment_providers
    
    def get_by_name(self, name: str):
        payment_provider = self.db.execute(select(PaymentProvider).where(PaymentProvider.name == name)).scalar_one_or_none()
        return payment_provider

class KYCPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, id_type: str, provider: str, verification_price: Decimal):
        kyc_plan = KYCPlan(id_type=id_type, provider=provider, verification_price=verification_price)
        self.db.add(kyc_plan)
        self.db.commit()
        self.db.refresh(kyc_plan)
        return kyc_plan

    def get_by_id(self, kyc_plan_id: int):
        kyc_plan = self.db.execute(select(KYCPlan).where(KYCPlan.id == kyc_plan_id)).scalar_one_or_none()
        return kyc_plan

    def get_by_id_type(self, id_type: int):
        kyc_plan = self.db.execute(select(KYCPlan).where(KYCPlan.id_type == id_type)).scalar_one_or_none()
        return kyc_plan

class PaymentPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, bank_name: str, provider: str, charges_type: str, flat: Decimal, percentage: Decimal, capped: Decimal, is_active: bool, bank_code: str):
        payment_plan = PaymentPlan(bank_name=bank_name, provider=provider, charges_type=charges_type, flat=flat, percentage=percentage, capped=capped, is_active=is_active, bank_code=bank_code)
        self.db.add(payment_plan)
        self.db.commit()
        self.db.refresh(payment_plan)
        return payment_plan
    
    def get_by_id(self, id: int):
        payment_plan = self.db.execute(select(PaymentPlan).where(PaymentPlan.id == id)).scalar_one_or_none()
        return payment_plan

    def get_all(self):
        payment_plan = self.db.execute(select(PaymentPlan)).scalars().all()
        return payment_plan

    def get_by_provider(self, provider: str):
        payment_plan = self.db.execute(select(PaymentPlan).where(PaymentPlan.provider == provider, PaymentPlan.is_active == True)).scalars().all()
        return payment_plan
    
    def get_by_bank_code_and_provider(self, bank_code: str, provider: str):
        payment_plan = self.db.execute(select(PaymentPlan).where(PaymentPlan.bank_code == bank_code, PaymentPlan.provider == provider, PaymentPlan.is_active)).scalar_one_or_none()
        return payment_plan
    
    def get_any_by_bank_code_and_provider(self, bank_code: str, provider: str):
        payment_plan = self.db.execute(select(PaymentPlan).where(PaymentPlan.bank_code == bank_code, PaymentPlan.provider == provider)).scalar_one_or_none()
        return payment_plan

class SystemInfoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, phone_number: str | None, whatsapp_link: str | None, x_link: str | None, facebook_link: str | None, tiktok_link: str | None, instagram_link: str | None):
        system_info = SystemInfo(id = 1, email=email, phone_number=phone_number, whatsapp_link=whatsapp_link, x_link=x_link, facebook_link=facebook_link, tiktok_link=tiktok_link, instagram_link=instagram_link)
        self.db.add(system_info)
        self.db.commit()
        self.db.refresh(system_info)
        return system_info

    def get_system_info(self):
        system_info = self.db.execute(select(SystemInfo).where(SystemInfo.id == 1)).scalar_one_or_none()
        return system_info
    
    def get_all(self):
        system_info = self.db.execute(select(SystemInfo)).scalars().all()
        return system_info
    
class GeneralMessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, message: str, is_active: bool,created_at: str):
        general_message = GeneralMessage(title=title, message=message, is_active=is_active, created_at=created_at)
        self.db.add(general_message)
        self.db.commit()
        self.db.refresh(general_message)
        return general_message
    
    def get_all(self):
        general_messages = self.db.execute(select(GeneralMessage).order_by(GeneralMessage.created_at.desc())).scalars().all()
        return general_messages
    
    def get_active(self):
        general_messages = self.db.execute(select(GeneralMessage).where(GeneralMessage.is_active == True).order_by(GeneralMessage.created_at.desc())).scalars().all()
        return general_messages
    
    def get_by_id(self, id: int):
        general_message = self.db.execute(select(GeneralMessage).where(GeneralMessage.id == id)).scalar_one_or_none()
        return general_message