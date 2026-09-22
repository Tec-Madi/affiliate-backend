from datetime import datetime, timedelta
import secrets
from sqlalchemy.orm import Session

from core.cryptography import hash_data, verify_hashed_data
from core.error.http import BadRequestError, NotFoundError, UnauthourizedError, UnprocessibleEntityError
from core.utils import generate_otp
from email_message.resend import ResendEmail
from repositories.users import OTPRepository, UserRepository
from core.config import RESEND_API_KEY


async def request_reset_password_function(email: str, db: Session):
    
    if not email:
        raise BadRequestError('email is required')
    
    user_repo = UserRepository(db)
    otp_repo = OTPRepository(db)

    user = user_repo.get_by_email(email=email.strip().lower())
    if not user:
        raise BadRequestError('user not found')

    otp = str(generate_otp())

    hashed_otp = hash_data(data=otp)

    otp_repo.create(user_id=user.id, otp=hashed_otp, expiry_time=datetime.now() + timedelta(minutes=5))

    try:
        await ResendEmail(api_key=RESEND_API_KEY).send_otp_email(name=user.name, email=user.email, otp=otp)
    except Exception:
        raise 

    return {'message': 'otp generated successfully'}

def validate_otp_function(email: str, otp: str, db: Session):

    if not otp:
        raise BadRequestError('otp is required')

    if len(otp) != 6:
        raise BadRequestError('invalid otp')

    user_repo = UserRepository(db)
    otp_repo = OTPRepository(db)

    user = user_repo.get_by_email(email=email)
    if not user:
        raise BadRequestError('user not found')

    otp_obj = otp_repo.get_latest_by_user_id(user_id=user.id)
    if not otp:
        raise BadRequestError('otp not found')

    if otp_obj.expiry_time < datetime.now():
        raise BadRequestError('otp expired')

    if not verify_hashed_data(data=otp, hashed_data=otp_obj.otp):
        raise BadRequestError('invalid otp')

    if otp_obj.is_used:
        raise BadRequestError('OTP expired')

    token = secrets.token_urlsafe(32)

    hashed_token = hash_data(data=token)
    otp_obj.token = hashed_token
    otp_obj.token_expiry_time = datetime.now() + timedelta(minutes=5)

    db.commit()

    return {
        'message': 'otp verified successfully',
        'token': token
    }

def change_password_function(email: str, token: str, new_password: str, confirm_new_password: str, db: Session):

    if not new_password:
        raise BadRequestError(message='Password field is required')
    
    if new_password != confirm_new_password:
        raise BadRequestError(message='Password field do not match')
    
    if len(new_password) < 8:
        raise BadRequestError(message='Password must be at least 8 digit')

    user_repo = UserRepository(db)
    otp_repo = OTPRepository(db)

    if not (user := user_repo.get_by_email(email=email)):
        raise NotFoundError('user not found')

    otp = otp_repo.get_latest_by_user_id(user_id=user.id)

    if otp.token_expiry_time < datetime.now():
        raise UnauthourizedError(message='Session Expired')

    if verify_hashed_data(data=new_password, hashed_data=user.password):
        raise UnprocessibleEntityError(message='old password and new password cannot be the same')

    if not verify_hashed_data(data=token, hashed_data=otp.token):
        raise UnauthourizedError(message='Unable to verify')

    user.password = hash_data(data=new_password)

    otp.is_used == True

    db.commit()

    return {'message': 'password reset successfully'}
