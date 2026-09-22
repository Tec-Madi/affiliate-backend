from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.users import User
from api.deps import require_admin
from core.database import get_db
from services.admin.overview import admin_overview_function, sales_overview_function

admin_overview_router = APIRouter(
    prefix='/admin',
    tags=['Admin Overview']
)

@admin_overview_router.get('/overview')
def admin_overview(
        start_date: date | None = None,
        end_date: date | None = None, 
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return admin_overview_function(user=user, db=db, start_date=start_date, end_date=end_date)

@admin_overview_router.get("/sales/overview")
def sales_overview(
        start_date: date | None = None,
        end_date: date | None = None,
        user: User = Depends(require_admin), 
        db: Session = Depends(get_db)
    ):
    return sales_overview_function(user=user, db=db, start_date=start_date, end_date=end_date)