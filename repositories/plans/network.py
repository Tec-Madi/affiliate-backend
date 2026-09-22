from decimal import Decimal

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from models.plans.network import AirtimePlan, DataPlan, DiscountType, Network, ProviderDataPlan, ProviderNetwork

class NetworkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, id: int, name: str, is_active: bool):
        network = Network(id=id, name=name, is_active=is_active)
        self.db.add(network)
        self.db.commit()
        self.db.refresh(network)
        return network

    def get_all(self):
        networks = self.db.execute(select(Network).order_by(Network.id)).scalars().all()
        return networks

    def get_by_id(self, id: int):
        network = self.db.execute(select(Network).where(Network.id == id)).scalar_one_or_none()
        return network

class ProviderNetworkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, provider_name: str, network_id: int, provider_network_id: str):
        provider_network = ProviderNetwork(provider_name=provider_name, network_id=network_id, provider_network_id=provider_network_id)
        self.db.add(provider_network)
        self.db.commit()
        self.db.refresh(provider_network)
        return provider_network

    def get_by_id(self, id: int):
        provider_network = self.db.execute(select(ProviderNetwork).where(ProviderNetwork.id == id)).scalar_one_or_none()
        return provider_network

    def get_by_network_id(self, network_id: int):
        provider_network = self.db.execute(select(ProviderNetwork).where(ProviderNetwork.network_id == network_id)).scalars().all()
        return provider_network

    def get_all(self):
        provider_networks = self.db.execute(select(ProviderNetwork)).scalars().all()
        return provider_networks

    def get_by_provider_name(self, provider_name: str):
        provider_networks = self.db.execute(select(ProviderNetwork).where(ProviderNetwork.provider_name == provider_name)).scalars().all()
        return provider_networks

    def get_by_provider_name_and_network_id(self, provider_name: str, network_id: int):
        provider_network = self.db.execute(select(ProviderNetwork).where(ProviderNetwork.network_id == network_id, ProviderNetwork.provider_name == provider_name)).scalar_one_or_none()
        return provider_network

    def get_by_network_id(self, network_id):
        provider_networks = self.db.execute(select(ProviderNetwork).where(ProviderNetwork.network_id == network_id)).scalars().all()
        return provider_networks

class DataPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, network_id: int, type: str, name: str, size: str, description: str, price: Decimal, agent_discount: Decimal, agent_discount_type: Decimal, discount: Decimal, discount_type: str, api_discount: Decimal, 
        api_discount_type: DiscountType, validity: str, is_active: bool, is_locked: bool, vend_from: str
    ):
        data_plan = DataPlan(
            network_id=network_id, type=type, name=name, size=size, description=description, price=price, discount=discount, discount_type=discount_type, agent_discount=agent_discount, agent_discount_type=agent_discount_type, 
            api_discount=api_discount, api_discount_type=api_discount_type, validity=validity, is_active=is_active, is_locked=is_locked, vend_from=vend_from
        )
        self.db.add(data_plan)
        self.db.commit()
        self.db.refresh(data_plan)
        return data_plan

    def get_all(self, offset: int, limit: int, search_param: str = "", filter_param: dict | None = None):
        data_plans = self.db.execute(
            select(DataPlan)
            .options(
                joinedload(DataPlan.network),
                joinedload(DataPlan.providers_data_plans)
            )
            .join(Network)
            .where(
                or_(
                    Network.name.ilike(f"%{search_param}%"),
                    DataPlan.name.ilike(f"%{search_param}%"),
                    DataPlan.type.ilike(f"%{search_param}%"),
                    DataPlan.validity.ilike(f"%{search_param}%"),
                    DataPlan.description.ilike(f"%{search_param}%")
                ),
                and_(getattr(DataPlan, key, None) == value for key, value in filter_param.items()) if filter_param else True
            )
            .order_by(DataPlan.id.desc())
            .limit(limit)
            .offset(offset)
            ).unique().scalars().all()
        return data_plans

    def get_by_id(self, id: int):
        data_plan = self.db.execute(select(DataPlan).where(DataPlan.id == id)).scalar_one_or_none()
        return data_plan

    def get_networks(self):
        data_plans = self.db.execute(
            select(DataPlan.network_id, Network.name.label('network'), func.bool_or(DataPlan.is_active).label('is_active'))
            .join(Network)
            .group_by(DataPlan.network_id, Network.name)
            .order_by(DataPlan.network_id)
        ).all()
        return data_plans

    def get_data_types(self, network_id: int):
        data_plans = self.db.execute(
            select(DataPlan.type)
            .where(DataPlan.network_id == network_id, DataPlan.is_active == True)
            .distinct()
        ).scalars().all()
        return data_plans

    def get_data_plans(self, network_id: int, data_type: str | None):
        data_plans = self.db.execute(
            select(DataPlan)
            .where(
                DataPlan.network_id == network_id, 
                (DataPlan.type == data_type) if data_type else True
            )
            .order_by(DataPlan.price)
        ).scalars().all()
        return data_plans
    
    def get_by_network_id_and_type(self, network_id: int, type: str):
        data_plans = self.db.execute(
            select(DataPlan).where(DataPlan.network_id == network_id, DataPlan.type == type)
        ).scalars().all()
        return data_plans

class ProviderDataPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, provider_name: str, plan_id: int, provider_plan_id: str):
        provider_data_plan = ProviderDataPlan(provider_name=provider_name, plan_id=plan_id, provider_plan_id=provider_plan_id)
        self.db.add(provider_data_plan)
        self.db.commit()
        self.db.refresh(provider_data_plan)
        return provider_data_plan

    def get_by_id(self, id: int):
        provider_data_plan = self.db.execute(select(ProviderDataPlan).where(ProviderDataPlan.id == id)).scalar_one_or_none()
        return provider_data_plan

    def get_by_plan_id(self, plan_id: int):
        provider_data_plan = self.db.execute(select(ProviderDataPlan).where(ProviderDataPlan.plan_id == plan_id)).scalars().all()
        return provider_data_plan

    def get_by_provider_name(self, provider_name: str):
        provider_data_plans = self.db.execute(
            select(ProviderDataPlan).where(ProviderDataPlan.provider_name == provider_name)
            .options(
                joinedload(ProviderDataPlan.provider),
                joinedload(ProviderDataPlan.data_plan)  
            )
            ).scalars().all()
        return provider_data_plans

    def get_all_by_provider_name(self, provider_name: str):
        provider_data_plan = self.db.execute(select(ProviderDataPlan).where(ProviderDataPlan.provider_name == provider_name)).scalars().all()
        return provider_data_plan

    def get_by_provider_name_and_plan_id(self, provider_name: str, plan_id: int):
        provider_data_plan = self.db.execute(select(ProviderDataPlan).where(ProviderDataPlan.provider_name == provider_name, ProviderDataPlan.plan_id == plan_id)).scalar_one_or_none()
        return provider_data_plan

class AirtimePlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        airtime_plan = AirtimePlan(**kwargs)
        self.db.add(airtime_plan)
        self.db.commit()
        self.db.refresh(airtime_plan)
        return airtime_plan

    def get_by_id(self, id):
        airtime_plan = self.db.execute(select(AirtimePlan).where(AirtimePlan.id == id)).scalar_one_or_none()
        return airtime_plan

    def get_all(self, offset: int | None = None, limit: int | None = None, search_param: str = "", filter_param: dict | None = None):
        airtime_plans = self.db.execute(
            select(AirtimePlan)
            .options(joinedload(AirtimePlan.network))
        ).unique().scalars().all()
        return airtime_plans

    def get_by_network_id(self, network_id: int):
        return self.db.execute(
            select(AirtimePlan)
            .where(AirtimePlan.network_id == network_id)
        ).scalar_one_or_none()

    def get_networks(self):
        return self.db.execute(
            select(AirtimePlan.network_id, Network.name.label("network"))
            .join(Network)
            .distinct()
        ).all()