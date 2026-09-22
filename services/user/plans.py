from decimal import Decimal
from typing import Literal

from sqlalchemy.orm import Session

from core.cryptography import decrypt_data, encrypt_data
from core.utils import generate_api_key
from models.plans.network import DiscountType
from models.users import Services, User
from repositories.plans.cable import CablePlanRepository, CableRepository
from repositories.plans.disco import DiscoPlanRepository, DiscoRepository
from repositories.plans.network import AirtimePlanRepository, DataPlanRepository, NetworkRepository
from repositories.users import UserAPIKeyRepository


def user_api_key_function(user: User, db: Session, regenerate: bool):

    user_api_key_repo = UserAPIKeyRepository(db)

    if not (user_api_key := user_api_key_repo.get_by_user_id(user.id)):
        user_api_key = user_api_key_repo.create(user.id, encrypt_data(generate_api_key()), False)
    elif regenerate:
        user_api_key.api_key = encrypt_data(generate_api_key())
        db.commit()

    return {
        "api_key": decrypt_data(user_api_key.api_key),
        "is_active": user_api_key.is_active
    }


def get_billers_function(user: User, service: Services, db: Session):

    repo = (
        NetworkRepository if service == Services.NETWORK
        else CableRepository if service == Services.CABLE
        else DiscoRepository if service == Services.DISCO
        else None
    )

    return[{
        (
            "network" if service == Services.NETWORK
            else "cable" if service == Services.CABLE
            else "disco" if service == Services.DISCO
            else ""
        ) + "_id": biller.id,
        "name": biller.name
    } for biller in repo(db).get_all()]

def get_plans_function(user: User, db: Session, service: Services, page: int, limit: int, search: str = ""):

    offset = (page - 1) * limit

    if service in [Services.AIRTIME, Services.DISCO]:
        repo = (
            AirtimePlanRepository if service == Services.AIRTIME
            else DiscoPlanRepository if service == Services.DISCO
            else None
        )

        plans = [{
            (
                "network" if service == Services.AIRTIME
                else "disco" if service == Services.DISCO
                else ""
             ): getattr(getattr(plan, "network" if service == Services.AIRTIME else "disco", ""), "name", ""),
             **({"plan_type": getattr(plan, "type", "")} if service == Services.DISCO else {}),
            "discount": (
                str(plan.api_discount) + "%" if plan.api_discount_type == DiscountType.PERCENTAGE
                else "₦" + str(plan.api_discount) if plan.api_discount_type == DiscountType.FLAT 
                else Decimal(0)
            ),
            "is_active": plan.is_active
        } for plan in repo(db).get_all(offset, limit, search)]

    if service in [Services.DATA, Services.CABLE]:
        repo = (
            DataPlanRepository if service == Services.DATA
            else CablePlanRepository if service == Services.CABLE 
            else None
        )

        plans = [{
            "id": plan.id,
            (
                "network" if service == Services.DATA 
                else "cable" if service == Services.CABLE
                else ""
            ): getattr(getattr(plan, "network" if service == Services.DATA else "cable"), "name", ""),
            **({"plan_type": getattr(plan, "type", "")} if service == Services.DATA else {}),
            "plan_name": plan.name + getattr(plan, "size", ""),
            "price": plan.price - (
                plan.api_discount if plan.api_discount_type == DiscountType.FLAT.value
                else (plan.api_discount/plan.price)*100 if plan.api_discount_type == DiscountType.PERCENTAGE.value
                else Decimal("0")
            ),
            "validity": plan.validity,
            "description": plan.description,
            "is_active": plan.is_active
        } for plan in repo(db).get_all(offset, limit, search)]

    return plans