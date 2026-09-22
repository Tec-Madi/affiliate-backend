from sqlalchemy.orm import Session

from repositories.users import UserRepository
from core.error.http import BadRequestError, UnprocessibleEntityError
from core.cryptography import hash_data

def register_function(db: Session, name: str, email: str, number: str, pin: str, password: str):

    if not pin.isdigit():
        raise UnprocessibleEntityError('pin can only be digit')

    if not number.isdigit():
        raise UnprocessibleEntityError('number can only be digit')

    if len(pin) != 4:
        raise BadRequestError('pin must be exactly 4 digit')

    if len(password) < 8:
        raise BadRequestError('password must be greater than 8 character')

    user_repo = UserRepository(db)

    if user_repo.get_by_email(email=email.strip().lower()):
        raise BadRequestError('email already exist')

    if user_repo.get_by_number(number=number):
        raise BadRequestError('number already exist')
    
    hashed_password = hash_data(data=password)
    hashed_pin = hash_data(data=pin)
    
    user_repo.create(name=name, email=email.strip().lower(), number=number, password=hashed_password, pin=hashed_pin, is_active=None, is_admin=None)

    return {'message': 'user created successfully'} 