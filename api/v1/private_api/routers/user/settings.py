from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from api.deps import get_current_user, require_admin
from api.v1.private_api.schemas.user.settings import UpdateCredentials
from core.database import get_db
from core.utils import CredentialsType
from models.users import User
from services.user.settings import api_key_function, get_user_details_function, update_crednetials_function


user_settings_router = APIRouter(
    prefix='/settings',
    tags=['User Settings']
)

@user_settings_router.get('/user')
def get_user_detail(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_details_function(user=user, db=db)

@user_settings_router.post("/user/update/{credentials_type}")
def update_credentials(data: UpdateCredentials, credentials_type: CredentialsType, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_crednetials_function(user=user, db=db, credential_type=credentials_type, old_credential=data.old_credential, new_credential=data.new_credential)

@user_settings_router.post('/generate/api-key')
def user_api_key(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return api_key_function(user=user, db=db)

