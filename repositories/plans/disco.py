from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func

from models.plans.disco import Disco, DiscoPlan, ProviderDisco, ProviderDiscoPlan



class DiscoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, id: int, name: str, is_active: bool):
        disco = Disco(id =id, name=name, is_active=is_active)
        self.db.add(disco)
        self.db.commit()
        self.db.refresh(disco)
        return disco

    def get_by_id(self, id: int):
        disco = self.db.execute(select(Disco).where(Disco.id == id)).scalar_one_or_none()
        return disco
    
    def get_all(self):
        discos = self.db.execute(
            select(Disco).options(
                joinedload(Disco.provider_discos)
                .joinedload(ProviderDisco.provider)
            )                     
        ).unique().scalars().all()
        return discos

class ProviderDiscoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, provider_name: str, disco_id: int, provider_disco_id: str):
        provider_disco = ProviderDisco(provider_name=provider_name, disco_id=disco_id, provider_disco_id=provider_disco_id)
        self.db.add(provider_disco)
        self.db.commit()
        self.db.refresh(provider_disco)
        return provider_disco

    def get_by_id(self, id: int):
        return self.db.execute(select(ProviderDisco).where(ProviderDisco.id == id)).scalar_one_or_none()

    def get_all(self, disco_id: int):
        provider_discos = self.db.execute(select(ProviderDisco).where(ProviderDisco.disco_id == disco_id)).scalars().all()
        return provider_discos

    def get_by_disco_id(self, disco_id):
        return self.db.execute(select(ProviderDisco).where(ProviderDisco.disco_id == disco_id)).scalars().all()
    
    def get_by_provider_name_and_disco_id(self, provider_name: str, disco_id: int):
        provider_disco = self.db.execute(select(ProviderDisco).where(ProviderDisco.provider_name == provider_name, ProviderDisco.disco_id == disco_id)).scalar_one_or_none()
        self.db.add(provider_disco)
        self.db.commit()
        self.db.refresh(provider_disco)
        return provider_disco

class DiscoPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        disco_plan = DiscoPlan(**kwargs)
        self.db.add(disco_plan)
        self.db.commit()
        self.db.refresh(disco_plan)
        return disco_plan

    def get_all(self, offset: int, linmit: int, search_param: str = "", filter_param: dict = None):
        disco_plans = self.db.execute(
            select(DiscoPlan)
            .options(
                joinedload(DiscoPlan.disco)
                .joinedload(Disco.provider_discos)
            )).unique().scalars().all()
        return disco_plans

    def get_by_id(self, id: int):
        disco_plan = self.db.execute(select(DiscoPlan).where(DiscoPlan.id == id)).scalar_one_or_none()
        return disco_plan

    def get_by_disco_id(self, disco_id: int):
        return self.db.execute(
            select(DiscoPlan).where(
                DiscoPlan.disco_id == disco_id
            )).scalar_one_or_none()

    def get_by_disco_id_and_disco_type(self, disco_id: int, type: str):
        return self.db.execute(
            select(DiscoPlan)
            .where(
                DiscoPlan.disco_id == disco_id,
                DiscoPlan.type == type
            )).scalar_one_or_none()

    def get_discos(self):
        disco_plans = self.db.execute(
            select(DiscoPlan.disco_id, Disco.name.label('disco'))
            .join(Disco)
            .group_by(DiscoPlan.disco_id, Disco.name)
            ).all()
        return disco_plans

    def get_disco_types(self, disco_id: int):
        disco_types = self.db.execute(
            select(DiscoPlan.type)
            .where(DiscoPlan.disco_id == disco_id, DiscoPlan.is_active == True)
        ).scalars().all()
        return disco_types

class ProviderDiscoPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, provider_name: str, plan_id: int, provider_plan_id: str):
        provider_disco_plan = ProviderDiscoPlan(provider_name=provider_name, disco_type=plan_id, provider_plan_id=provider_plan_id)
        self.db.add(provider_disco_plan)
        self.db.commit()
        self.db.refresh(provider_disco_plan)
        return provider_disco_plan
    
    def get_by_id(self, id: int):
        provider_disco_plan = self.db.execute(select(ProviderDiscoPlan).where(ProviderDiscoPlan.id == id)).scalar_one_or_none()
        return provider_disco_plan
    
    def get_by_provider_name(self, provider_name: str):
        provider_disco_plans = self.db.execute(select(ProviderDiscoPlan).where(ProviderDiscoPlan.provider_name == provider_name)).scalars().all()
        return provider_disco_plans

    def get_by_provider_name_and_plan_id(self, provider_name: str, plan_id: int):
        provider_disco_plan = self.db.execute(
            select(ProviderDiscoPlan)
            .where(ProviderDiscoPlan.provider_name == provider_name, ProviderDiscoPlan.plan_id == plan_id)
            ).scalar_one_or_none()
        return provider_disco_plan