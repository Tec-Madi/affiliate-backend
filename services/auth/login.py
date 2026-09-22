from sqlalchemy.orm import Session

from api.deps import create_access_token
from repositories.users import UserRepository
from core.error.http import UnauthourizedError
from core.cryptography import verify_hashed_data

def login_function(email: str, password: str, db: Session):

    user_repo = UserRepository(db)

    user = user_repo.get_by_email(email=email.strip().lower())
    if not user:
        raise UnauthourizedError('invalid credentials')

    hashed_password = user.password

    if not verify_hashed_data(data=password, hashed_data=hashed_password):
        raise UnauthourizedError('invalid credentials')

    token = create_access_token(sub={'user_id': user.id})

    return {
        'access_token': token,
        'token_type': 'bearer',
        'is_admin': user.is_admin,
        'email': user.email,
        'balance': user.wallet.balance
    }