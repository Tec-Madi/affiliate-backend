from sqlalchemy.orm import Session

from core.cryptography import verify_hashed_data
from core.error.http import BadRequestError, UnprocessibleEntityError
from models.users import User


def pin_validator_function(user: User, db: Session, pin: str):

    if not pin.isdigit() or len(pin) != 4:
        raise UnprocessibleEntityError('PIN must be a 4 digit number')

    if not verify_hashed_data(data=pin, hashed_data=user.pin):
        raise BadRequestError('Invalid transaction PIN')

    return {'message': 'pin validated successfully'}