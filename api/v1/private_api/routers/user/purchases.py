from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import Depends, get_current_user
from api.v1.private_api.schemas.user.purchase import PurchaseSchema
from core.database import get_db
from models.users import Services, User
from services.user.vtu import *


vtu_purchase_router = APIRouter(
    prefix="/user/{service}",
    tags=['VTU Purchase']
)

@vtu_purchase_router.get("/billers")
async def get_billers(
        service: Literal[Services.DATA, Services.AIRTIME, Services.CABLE, Services.DISCO],
        user: User = Depends(get_current_user), 
        db: Session = Depends(get_db),
    ):
    return await get_biller_function(user=user, db=db, service=service)

@vtu_purchase_router.get("/plan-type/{biller_id}")
async def get_biller_types(
        service: Literal[Services.DATA, Services.AIRTIME, Services.CABLE, Services.DISCO],
        biller_id: int,
        user: User = Depends(get_current_user), 
        db: Session = Depends(get_db),
    ):
    return await get_plan_type_function(user=user, db=db, service=service, biller_id=biller_id)

@vtu_purchase_router.get("/plans")
async def get_plans(
        service: Literal[Services.DATA, Services.AIRTIME, Services.CABLE, Services.DISCO],
        biller_id: int,
        plan_type: str | None = None,
        user: User = Depends(get_current_user), 
        db: Session = Depends(get_db),
    ):
    return await get_plans_function(user=user, db=db, service=service, biller_id=biller_id, plan_type=plan_type)

@vtu_purchase_router.post("/purchase")
async def virtual_top_up(
        data: PurchaseSchema, 
        service: Literal[Services.DATA, Services.AIRTIME, Services.CABLE, Services.DISCO], 
        user: User = Depends(get_current_user), 
        db: Session = Depends(get_db)):
    return await virtual_top_up_function(user=user, db=db, service=service, payload=data)