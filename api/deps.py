from jose import jwt, JWTError
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from fastapi import Depends, Header, Cookie
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from core.cryptography import decrypt_data
from core.error.http import BadRequestError, NotFoundError, UnauthourizedError, ForbiddenError
from core.database import get_db
from models.users import User
from repositories.users import UserAPIKeyRepository, UserRepository
from core.config import SECRET_KEY, ALGORITHMS_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

SECRET_KEY = SECRET_KEY
ALGORITHM = ALGORITHMS_KEY
ACCESS_TOKEN_EXPIRY_MINUTE = ACCESS_TOKEN_EXPIRE_MINUTES

Oauthscheme = OAuth2PasswordBearer(tokenUrl='api/v1/auth/login')

def create_access_token(sub: dict):
    to_encode = sub.copy()
    expiry = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTE)
    to_encode.update({'exp': expiry})
    token = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM) 
    return token 

def get_current_user(access_token: str = Cookie(default=None, alias='access_token'), db: Session = Depends(get_db)):
    if not access_token:
        raise UnauthourizedError(message='Invalid or No Token')

    user_repo = UserRepository(db)

    try:
        paylaod = jwt.decode(token=access_token, key=SECRET_KEY, algorithms=[ALGORITHM])
        if not paylaod:
            raise UnauthourizedError('unauthozized')

        user_id = paylaod.get('user_id')
        user = user_repo.get_by_id(user_id=user_id)
        if not user:
            raise NotFoundError('User not found')

        if not user.is_active:
            raise ForbiddenError('only active user can access this page')

        return user

    except JWTError:
        raise UnauthourizedError('unauthorized')
    
def require_admin(user: User = Depends(get_current_user)):
    if user.is_admin is not True:
        raise ForbiddenError('only admin can access this page')
    return user

auth_scheme = APIKeyHeader(
    name="Authorization",
    scheme_name="Token",
    description="Format: Token <your_token>"
)

def get_api_user(authorization: str = Depends(auth_scheme), db: Session = Depends(get_db)):

    if not authorization:
        raise BadRequestError('Token is required')

    user_repo = UserRepository(db)
    user_api_key_repo = UserAPIKeyRepository(db)

    scheme, _, token = authorization.partition(" ")
    user_id = None

    if scheme != 'Token':
        raise UnauthourizedError('Header must be: Authorization: Token <token>', code='UNAUTHORIZED')

    try:
        try:
            payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload.get('user_id')
        except JWTError:
            pass

        if not user_id:
            api_keys = user_api_key_repo.get_all()
            for api_key in api_keys:
                if decrypt_data(api_key) == token:
                    user_api_key = user_api_key_repo.get_by_api_key(api_key)
                    
            user_id = user_api_key.user_id

        if not (user := user_repo.get_by_id(user_id=user_id)):
            raise NotFoundError('user not found')
        return user
    except Exception as e:
        raise UnauthourizedError(f'unauthorized: {str(e)}')