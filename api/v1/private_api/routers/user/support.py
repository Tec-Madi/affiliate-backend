from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.users import User
from services.user.support import get_support_link_function


support_router = APIRouter(
    prefix='/support',
    tags=['User Support']
)

@support_router.get('/link')
def get_support_link(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_support_link_function(user=user, db=db)

@support_router.get('/free-link')
def get_free_support_link(db: Session = Depends(get_db)):
    return get_support_link_function(user=None, db=db)

