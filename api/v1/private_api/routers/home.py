from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from core.error.http import ForbiddenError
from models.users import User
from repositories.users import UserRepository
from services.home import home_page_function

home_router = APIRouter(
    prefix='/home',
    tags=['Home Page']
)

@home_router.get('/')
def home_page():
    return home_page_function()