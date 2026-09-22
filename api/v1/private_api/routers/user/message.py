from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.users import User
from services.user.message import welcome_messages_function

messages_router = APIRouter(
    prefix='/messages',
    tags=['Messages']
)

@messages_router.get('/get')
def welcome_messages(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return welcome_messages_function(user=user, db=db)