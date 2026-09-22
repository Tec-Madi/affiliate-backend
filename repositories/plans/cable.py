from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, select, func

from models.plans.cable import Cable, CablePlan, ProviderCable, ProviderCablePlan



class CableRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, id: int, name: str, is_active: bool):
        cable = Cable(id=id, name=name, is_active=is_active)
        self.db.add(cable)
        self.db.commit()
        self.db.refresh(cable)
        return cable

    def get_by_id(self, id: int):
        cable = self.db.execute(select(Cable).where(Cable.id == id)).scalar_one_or_none()
        return cable

    def get_all(self):
        cables = self.db.execute(
            select(Cable)
            .options(
                joinedload(Cable.provider_cables)
                .joinedload(ProviderCable.provider)
            ).order_by(Cable.id.asc())
            ).unique().scalars().all()
        return cables

class ProviderCableRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, provider_name: str, cable_id: int, provider_cable_id: str):
        provider_cable = ProviderCable(provider_name=provider_name, cable_id=cable_id, provider_cable_id=provider_cable_id)
        self.db.add(provider_cable)
        self.db.commit()
        self.db.refresh(provider_cable)
        return provider_cable
    
    def get_by_id(self, id: int):
        provider_cable = self.db.execute(select(ProviderCable).where(ProviderCable.id == id)).scalar_one_or_none()
        return provider_cable
    
    def get_all(self):
        provider_cables = self.db.execute(select(ProviderCable)).scalars().all()
        return provider_cables
    
    def get_by_cable_id(self, cable_id: int):
        provider_cables = self.db.execute(select(ProviderCable).where(ProviderCable.cable_id == cable_id)).scalars().all()
        return provider_cables
    
    def get_by_provider_name(self, provider_name: str):
        provider_cables = self.db.execute(select(ProviderCable).where(ProviderCable.provider_name == provider_name)).scalars().all()
        return provider_cables
    
    def get_by_provider_name_and_cable_id(self, provider_name: str, cable_id):
        provider_cable = self.db.execute(select(ProviderCable).where(ProviderCable.provider_name == provider_name, ProviderCable.cable_id == cable_id)).scalar_one_or_none()
        return provider_cable

class CablePlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        
        cable_plan = CablePlan(**kwargs)
        self.db.add(cable_plan)
        self.db.commit()
        self.db.refresh(cable_plan)
        return cable_plan

    def get_by_id(self, id: int):
        cable_plan = self.db.execute(select(CablePlan).where(CablePlan.id == id)).scalar_one_or_none()
        return cable_plan

    def get_all(self, offset: int, limit: int, search_param: str = "", filter_param: dict | None = None):
        cable_plans = self.db.execute(
            select(CablePlan)
            .options(
                joinedload(CablePlan.cable),
                joinedload(CablePlan.provider_cable_plan)
            )
            .join(Cable)
            .where(
                or_(
                    Cable.name.ilike(f"%{search_param}%"),
                    CablePlan.name.ilike(f"%{search_param}%"),
                    CablePlan.description.ilike(f"&{search_param}&"),
                    CablePlan.validity.ilike(f"&{search_param}&")
                ),
                and_(getattr(CablePlan, key, None) == value for key, value in filter_param.items()) if filter_param else True
            )
            .limit(limit)
            .offset(offset)
            ).unique().scalars().all()
        return cable_plans

    def get_cables(self):
        cable_plans = self.db.execute(
            select(CablePlan.cable_id, Cable.name.label('cable'), func.bool_or(CablePlan.is_active).label('is_active'))
            .join(Cable, CablePlan.cable_id == Cable.id)
            .group_by(CablePlan.cable_id, Cable.name)
        ).all()
        return cable_plans

    def get_cable_plans(self, cable_id: int):
        cable_plans = self.db.execute(select(CablePlan).where(CablePlan.cable_id == cable_id)).scalars().all()
        return cable_plans
    
    def get_by_cable_id(self, cable_id: int):
        cable_plans = self.db.execute(select(CablePlan).where(CablePlan.cable_id == cable_id)).scalars().all()
        return cable_plans
 
class ProviderCablePlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, provider_name: str, plan_id: int, provider_plan_id: str):
        provider_cable_plan = ProviderCablePlan(provider_name=provider_name, plan_id=plan_id, provider_plan_id=provider_plan_id)
        self.db.add(provider_cable_plan)
        self.db.commit()
        self.db.refresh(provider_cable_plan)
        return provider_cable_plan

    def get_by_id(self, id: int):
        provider_cable_plan = self.db.execute(select(ProviderCablePlan).where(ProviderCablePlan.id == id)).scalar_one_or_none()
        return provider_cable_plan

    def get_all(self):
        provider_cable_plans = self.db.execute(select(ProviderCablePlan)).scalars().all()
        return provider_cable_plans

    def get_by_provider_name(self, provider_name: str):
        provider_cable_plans = self.db.execute(select(ProviderCablePlan).where(ProviderCablePlan.provider_name == provider_name)).scalars().all()
        return provider_cable_plans

    def get_by_provider_name_and_plan_id(self, provider_name: str, plan_id: int):
        provider_cable_plan = self.db.execute(
            select(ProviderCablePlan)
            .where(
                ProviderCablePlan.provider_name == provider_name, 
                ProviderCablePlan.plan_id == plan_id)
            ).scalar_one_or_none()
        return provider_cable_plan
    
    def get_by_plan_id(self, plan_id: int):
        provider_cable_plans = self.db.execute(select(ProviderCablePlan).where(ProviderCablePlan.plan_id == plan_id)).scalars().all()
        return provider_cable_plans