import secrets

from sqlalchemy.orm import Session

from core.cryptography import decrypt_data, encrypt_data, hash_data, verify_hashed_data
from core.error.http import UnauthourizedError
from core.utils import CredentialsType
from models.users import User
from repositories.users import UserAPIKeyRepository


def get_user_details_function(user: User, db: Session):

    return {
        "full_name": user.name,
        "email": user.email,
        "is_active": user.is_active,
        "nin_is_verified": user.user_kyc.nin_is_verified,
        "bvn_is_verified": user.user_kyc.bvn_is_verified
    }

def update_crednetials_function(user: User, db: Session, credential_type: CredentialsType, old_credential: str, new_credential: str):

    if not verify_hashed_data(data=old_credential, hashed_data=getattr(user, credential_type.value)):
        raise UnauthourizedError(f"Invalid {credential_type.value}")

    try:
        setattr(user, credential_type.value, hash_data(new_credential))
        db.commit()
    except Exception:
        db.rollback()

    return {'message': 'password updated successfully'}

def api_key_function(user: User, db: Session):

    user_api_key_repo = UserAPIKeyRepository(db)

    if not (user_api_key := user_api_key_repo.get_by_user_id(user.id)):
        user_api_key = user_api_key_repo.create(user_id=user.id, api_key=encrypt_data(secrets.token_urlsafe(32)), is_active=False)

    return {
        "api_key": decrypt_data(user_api_key.api_key),
        "is_active": user_api_key.is_active
    }