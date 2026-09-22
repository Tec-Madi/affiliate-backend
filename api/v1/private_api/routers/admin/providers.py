from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import require_admin
from api.v1.private_api.schemas.admin.providers import UpsertProvider
from core.database import get_db
from models.users import User
from services.admin.providers import all_providers_function, delete_provider_function, upsert_provider_function


admin_provider_router = APIRouter(
    prefix='/admin/providers/{action_for}',
    tags=['Admin Provider Manager']
)

@admin_provider_router.get("")
def all_providers(
        action_for: Literal["vtu", "pgw"], 
        names_only: bool = False, 
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return all_providers_function(user=user, db=db, query_for=action_for, names_only=names_only)

@admin_provider_router.post("")
async def add_provider(
        data: UpsertProvider,
        action_for: Literal["vtu", "pgw"], 
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return await upsert_provider_function(user=user, db=db, upsert_for=action_for, action="create", provider_schema=data)

@admin_provider_router.patch('/{id}')
async def update_provider(
        data: UpsertProvider,
        id: int,
        action_for: Literal["vtu", "pgw"], 
        user: User = Depends(require_admin), 
        db: User = Depends(get_db)
    ):
    return await upsert_provider_function(user=user, db=db, upsert_for=action_for, action="edit", provider_schema=data, id=id)

@admin_provider_router.delete('/{delete_for}/{id}')
def delete_provide(
        id: int,
        action_for: Literal["vtu", "pgw"], 
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return delete_provider_function(user=user, db=db, delete_for=action_for, id=id)