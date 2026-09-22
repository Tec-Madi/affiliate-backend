from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import require_admin
from api.v1.private_api.schemas.admin.users import UpsertUser
from core.database import get_db
from models.users import User
from services.admin.users import all_users_function, delete_user_function, upsert_user_function

admin_user_router = APIRouter(
    prefix='/admin/users',
    tags=['Admin User Management']
)

@admin_user_router.get("")
def all_users(
        page: int | None = 1, 
        limit: int | None = 50,
        search: str | None = "",
        is_active: bool | None = None,
        is_agent: bool | None = None,
        is_admin: bool | None = None,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return all_users_function(admin_user=user, db=db, page=page, limit=limit, search=search, is_active=is_active, is_agent=is_agent, is_admin=is_admin)

@admin_user_router.post("")
def create_user(data: UpsertUser, user: User = Depends(require_admin), db: User = Depends(get_db)):
    return upsert_user_function(admin_user=user, db=db, action="create", user_schema=data)

@admin_user_router.patch('/{user_id}')
def edit_user(
        data: UpsertUser, 
        user_id: int,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return upsert_user_function(admin_user=user, db=db, action="edit", user_schema=data, user_id=user_id)

@admin_user_router.delete('/{user_id}')
def delete_user(
        user_id: int,
        id: int | None = None,
        for_va: bool = False,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return delete_user_function(admin_user=user, db=db, user_id=user_id, id=id, for_va=for_va)