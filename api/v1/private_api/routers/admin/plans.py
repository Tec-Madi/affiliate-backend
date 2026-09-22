from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import require_admin
from api.v1.private_api.schemas.admin.plans import *
from core.database import get_db
from models.users import Services, User
from services.admin.plans.biller import *
from services.admin.plans.pgw_plans import *
from services.admin.plans.vtu_plans import *


admin_biller_router = APIRouter(
    prefix="/admin/{action_for}/{service}",
    tags=["ADMIN BILLER MANAGER"]
)

@admin_biller_router.get("")
def all_billers(
        action_for: Literal["biller", "linked-biller"],
        service: Literal[Services.NETWORK, Services.CABLE, Services.DISCO],
        id: int | None = None,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return view_biller_function(user=user, db=db, action_for=action_for, service=service, id=id)

@admin_biller_router.post("")
def create_biller(
        data: UpsertBillerSchema,
        action_for: Literal["biller", "linked-biller"],
        service: Literal[Services.NETWORK, Services.CABLE, Services.DISCO], 
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return upsert_biller_function(user=user, db=db, service=service, action_for=action_for, action="create", biller_schema=data)

@admin_biller_router.patch("/{id}")
def edit_biller(
        data: UpsertBillerSchema,
        action_for: Literal["biller", "linked-biller"],
        service: Literal[Services.NETWORK, Services.CABLE, Services.DISCO],
        id: int,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return upsert_biller_function(user=user, db=db, action="edit", service=service, action_for=action_for, biller_schema=data, id=id)

@admin_biller_router.delete("/{id}")
def delete_biller(
        service: Literal[Services.NETWORK, Services.CABLE, Services.DISCO], 
        action_for: Literal["biller", "linked-biller"],
        id: int,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return delete_biller_function(user=user, db=db, service=service, id=id, action_for=action_for)

admin_plan_router = APIRouter(
    prefix="/admin/vtu/{action_for}/{service}",
    tags=["ADMIN PLAN MANAGER"]
)

@admin_plan_router.get("")
def all_plans(
        action_for: Literal["plan", "linked-plan"],
        service: Literal[Services.AIRTIME, Services.DATA, Services.CABLE, Services.DISCO],
        data: PlanQuery = Query(),
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return view_plans_function(user=user, db=db, service=service, view_for=action_for, plan_query=data)

@admin_plan_router.post("")
def create_plan(
        data: UpsertPlanSchema,
        action_for: Literal["plan", "linked-plan"],
        service: Literal[Services.AIRTIME, Services.DATA, Services.CABLE, Services.DISCO],
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return upsert_plan_function(user=user, db=db, action="create", upsert_for=action_for, service=service, plan_schema=data)

@admin_plan_router.patch("/{id}")
def edit_plan(
        data: UpsertPlanSchema,
        action_for: Literal["plan", "linked-plan"],
        service: Literal[Services.AIRTIME, Services.DATA, Services.CABLE, Services.DISCO], 
        id: int, 
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return upsert_plan_function(user=user, db=db, action="edit", service=service, upsert_for=action_for, plan_schema=data, id=id)

@admin_plan_router.delete("/{id}")
def delete_plan(
        service: Literal[Services.AIRTIME, Services.DATA, Services.CABLE, Services.DISCO],
        action_for: Literal["plan", "linked-plan"],
        id: int,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return delete_plan_function(user=user, db=db, id=id, service=service, delete_for=action_for)

@admin_plan_router.patch("/")
def plan_control(
        data: PlanControlSchema,
        service: Literal[Services.AIRTIME, Services.DATA, Services.CABLE, Services.DISCO],
        action_for: Literal["activation", "dispense"],
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return plan_control_function(user=user, db=db, service=service, action=action_for, biller_id=data.biller_id, plan_type=data.plan_type, is_active=data.is_active, vend_from=data.vend_from)


admin_pgw_plan_router = APIRouter(
    prefix="/admin/pgw-plan",
    tags=["ADMIN PAYMENT PLAN MANAGEMENT"]
)

@admin_pgw_plan_router.get("")
def all_payment_plans(user: User =  Depends(require_admin), db: Session = Depends(get_db)):
    return all_payment_plans_function(user=user, db=db)

@admin_pgw_plan_router.post("")
async def add_payment_plan(data: UpsertPGWPlanSchema, user: User =  Depends(require_admin), db: Session = Depends(get_db)):
    return await upsert_payment_plan_function(user=user, db=db, action="create", plan_schema=data)

@admin_pgw_plan_router.patch("/{id}")
async def edit_payment_plan(id: int, data: UpsertPGWPlanSchema, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return await upsert_payment_plan_function(user=user, db=db, action="edit", id=id, plan_schema=data)

@admin_pgw_plan_router.delete("/{id}")
def delete_payment_plan(id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return delete_payment_plan_fuction(user=user, db=db, id=id)

@admin_pgw_plan_router.get("/creds")
def view_admin_ids(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return view_admin_id_function(user=user, db=db)

@admin_pgw_plan_router.post("/creds")
def upsert_admin_ids(data: AdminIDs ,user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return upsert_admin_id_function(user=user, db=db, admin_id_schema=data)