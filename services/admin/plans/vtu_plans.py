from decimal import Decimal
from typing import Literal
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.error.http import AdminOnlyError, BadRequestError, NotFoundError
from models.plans.cable import CablePlan, ProviderCablePlan
from models.plans.disco import DiscoPlan
from models.plans.network import AirtimePlan, DataPlan, DiscountType, ProviderDataPlan
from models.users import Services, User
from repositories.plans.cable import CablePlanRepository, ProviderCablePlanRepository
from repositories.plans.disco import DiscoPlanRepository
from repositories.plans.network import AirtimePlanRepository, DataPlanRepository, ProviderDataPlanRepository

def view_plans_function(user: User, db: Session, service: Services, view_for: Literal["plan", "linked-plan"], plan_query: object):

    if not user.is_admin:
        raise AdminOnlyError()

    if view_for == "plan":

        repo = (
            AirtimePlanRepository if service == Services.AIRTIME
            else DataPlanRepository if service == Services.DATA
            else CablePlanRepository if service == Services.CABLE
            else DiscoPlanRepository if service == Services.DISCO
            else None
        )

        biller_key = f"{"network" if service in [Services.DATA, Services.AIRTIME] else "cable" if service == Services.CABLE else "disco"}"

        if plan_query.id:
            if not (plan := repo(db).get_by_id(plan_query.id)):
                raise NotFoundError("plan not found")

            return {
                "id": plan.id,
                "biller_id": getattr(getattr(plan, biller_key, None), "id", None),
                **({"name": getattr(plan, "name", None)} if service in [Services.DATA, Services.CABLE] else {}),
                **({"size": getattr(plan, "size", None)} if service == Services.DATA else {}),
                **({"type": getattr(plan, "type", None)} if service in [Services.DATA, Services.DISCO] else {}),
                **({"price": getattr(plan, "price", None)} if service in [Services.DATA, Services.CABLE] else {}),
                **({"validity": getattr(plan, "validity", None)} if service in [Services.DATA, Services.CABLE] else {}),
                **({"description": getattr(plan, "description", None)} if service in [Services.DATA, Services.CABLE] else {}),
                **({"minimum_amount": getattr(plan, "minimum_amount", None)} if service in [Services.AIRTIME, Services.DISCO] else {}),
                **({"maximum_amount": getattr(plan, "maximum_amount", None)} if service in [Services.AIRTIME, Services.DISCO] else {}),
                "discount": plan.discount,
                "discount_type": plan.discount_type,
                "agent_discount": plan.agent_discount,
                "agent_discount_type": plan.agent_discount_type,
                "api_discount": plan.api_discount,
                "api_discount_type": plan.api_discount_type,
                "is_active": plan.is_active,
                **({"is_locked": getattr(plan, "is_locked", None)} if service in [Services.DATA, Services.CABLE] else {}),
                "vend_from": plan.vend_from
            }

        else:
            discount = lambda discount, discount_type: (
                f"₦{discount}" if discount_type == DiscountType.FLAT.value
                else f"{discount}%" if discount_type == DiscountType.PERCENTAGE.value
                else "N/A"
            )

            filter_param_map = {
                "is_active": plan_query.is_active,
                "is_locked": plan_query.is_locked
            }

            filter_param = { key: value for key, value in filter_param_map.items() if value is not None }

            return [{
                "id": plan.id,
                biller_key: getattr(getattr(plan, biller_key, ""), "name", "").upper(),
                **({"name": getattr(plan, "name", None) + getattr(plan, "size", "").upper()} if service in [Services.DATA, Services.CABLE] else {}),
                **({"type": getattr(plan, "type", "").upper()} if service in [Services.DATA, Services.DISCO] else {}),
                **({"price": "₦"+str(getattr(plan, "price", None))} if service in [Services.DATA, Services.CABLE] else {}),
                **({"validity": getattr(plan, "validity", None)} if service in [Services.DATA, Services.CABLE] else {}),
                **({"description": getattr(plan, "description", None)} if service in [Services.DATA, Services.CABLE] else {}),
                **({"minimum_amount": getattr(plan, "minimum_amount", None)} if service in [Services.AIRTIME, Services.DISCO] else {}),
                **({"maximum_amount": getattr(plan, "maximum_amount", None)} if service in [Services.AIRTIME, Services.DISCO] else {}),
                "discount": discount(plan.discount, plan.discount_type),
                "agent_discount": discount(plan.agent_discount, plan.agent_discount_type),
                "api_discount": discount(plan.api_discount, plan.api_discount_type),
                "is_active": plan.is_active,
                **({"is_locked": getattr(plan, "is_locked", None)} if service in [Services.DATA, Services.CABLE] else {}),
                "vend_from": plan.vend_from
            } for plan in repo(db).get_all((plan_query.page - 1)*plan_query.limit, plan_query.limit, plan_query.search, filter_param)]

    elif view_for == "linked-plan":

        if not (repo := (
            ProviderDataPlanRepository if service == Services.DATA 
            else ProviderCablePlanRepository if service == Services.CABLE 
            else None
        )):
            raise BadRequestError(service.value + " plan has no linked providers")

        return [{
            "id": linked_provider.id,
            "provider_name": linked_provider.provider_name,
            "provider_plan_id": linked_provider.provider_plan_id
        }for linked_provider in repo(db).get_by_plan_id(plan_query.id)]

    
def upsert_plan_function(user: User, db: Session, action: Literal["create", "edit"], upsert_for: Literal["plan", "linked-plan"], service: Services, plan_schema: BaseModel, id: int | None = None):

    if not user.is_admin:
        raise AdminOnlyError()

    biller_id_key = "network_id" if service in [Services.DATA, Services.AIRTIME] else "cable_id" if service == Services.CABLE else "disco_id"

    payload = plan_schema.model_dump()

    if upsert_for == "plan":
        repo = (
            DataPlanRepository if service == Services.DATA 
            else AirtimePlanRepository if service == Services.AIRTIME 
            else CablePlanRepository if service == Services.CABLE 
            else DiscoPlanRepository if service == Services.DISCO 
            else None
        )

        payload[biller_id_key] = payload.pop("biller_id")

        payload = {
            key: value
            for key, value in payload.items() if value is not None
        }

        if payload:
            if action == "edit":
                if not (plan := repo(db).get_by_id(id)):
                    raise NotFoundError(f"{service.value}_plan not found")
                for key, value in payload.items():
                    setattr(plan, key, value)

            elif action == "create":
                repo(db).create(**payload)

    elif upsert_for == "linked-plan":

        repo = (
            ProviderDataPlanRepository if service == Services.DATA
            else ProviderCablePlanRepository if service == Services.CABLE
            else None
        )

        linked_plan_payload: dict = payload["linked_plan"]

        payload = {
            key: value
            for key, value in linked_plan_payload.items() if value is not None
        }

        if action == "create":
            repo(db).create(**payload)

        if action == "edit":
            if not (linked_plan := repo(db).get_by_id(id)):
                raise NotFoundError("Linked-plan not found")
            for key, value in payload.items():
                setattr(linked_plan, key, value)

    db.commit()

    return {"message": service.value + " plan " + ("updated" if action == "edit" else "created") + " successfully"}

def delete_plan_function(user: User, db: Session, id: int, service: Services, delete_for: Literal["plan", "linked-plan"]):

    if not user.is_admin:
        raise AdminOnlyError()

    if delete_for == "plan":
        repo = (
            DataPlanRepository if service == Services.DATA
            else AirtimePlanRepository if service == Services.AIRTIME
            else CablePlanRepository if service == Services.CABLE
            else DiscoPlanRepository if service == Services.DISCO
            else None
        )

        if not (plan := repo(db).get_by_id(id)):
            raise NotFoundError(f"{service.value.capitalize()} plan not found")

        db.delete(plan)

    elif delete_for == "linked-plan":
        repo = (
            ProviderDataPlanRepository if service == Services.DATA
            else ProviderCablePlanRepository if service == Services.CABLE
            else None
        )

        if not (linked_plan := repo(db).get_by_id(id)):
            raise NotFoundError(f"{service.value.capitalize()} plan not found")

        db.delete(linked_plan)

    db.commit()

    return {"message": f"{service.value.capitalize()} plan deleted successfully"}

def plan_control_function(
        user: User, 
        db: Session, 
        service: Literal[Services.DATA, Services.AIRTIME, Services.CABLE, Services.DISCO], 
        action: Literal["activation", "dispense"], 
        biller_id: int,
        plan_type: str | None, 
        is_active: bool | None, 
        vend_from: str | None
    ):

    if not user.is_admin:
        raise AdminOnlyError()

    if service == Services.AIRTIME:
        plan_object = AirtimePlanRepository(db).get_by_network_id(biller_id)
        
    elif service == Services.DATA:
        plan_object = DataPlanRepository(db).get_by_network_id_and_type(biller_id, plan_type)

    elif service == Services.CABLE:
        plan_object = CablePlanRepository(db).get_by_cable_id(biller_id)

    elif service == Services.DISCO:
        plan_object = DiscoPlanRepository(db).get_by_disco_id_and_disco_type(biller_id, plan_type)

    if isinstance(plan_object, list):
        for plan in plan_object:
            if not plan.is_locked:
                if action == "activation": plan.is_active = is_active
                elif action == "dispense": plan.vend_from = vend_from

    else:
        if action == "activation": plan_object.is_active = is_active
        elif action == "dispense": plan_object.vend_from = vend_from

    db.commit()

    return {"message": service.value + " plan" + ((" activated" if is_active == True else " deactivated") if action == "activation" else " dispense route is set to " + vend_from)}