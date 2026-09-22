from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.users import Services, User
from services.user.plans import get_billers_function, get_plans_function, user_api_key_function


plans_router = APIRouter(
    prefix="",
    tags=["User API plans"]
)

@plans_router.get("/api-key")
def user_api_key(regenerate: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_api_key_function(user=user, db=db, regenerate=regenerate)

@plans_router.get("/{service}/billers")
def get_billers(
        service: Literal[Services.NETWORK, Services.CABLE, Services.DISCO], 
        user: User = Depends(get_current_user), 
        db: Session = Depends(get_db)
    ):
    return get_billers_function(user=user, db=db, service=service)

@plans_router.get("/{service}/plans")
def get_plans(
        service: Literal[Services.AIRTIME, Services.DATA, Services.CABLE, Services.DISCO],
        page: int | None = 1,
        limit: int | None = 50,
        search: str | None = "",
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    return get_plans_function(user=user, db=db, service=service, page=page, limit=limit, search=search)