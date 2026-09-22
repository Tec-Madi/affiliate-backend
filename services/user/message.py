from requests import Session

from models.users import User
from repositories.admin import GeneralMessageRepository


def welcome_messages_function(user: User, db: Session):

    message_repo = GeneralMessageRepository(db)

    messages = message_repo.get_active()

    return [{
        'title': message.title,
        'message': message.message
    } for message in messages ]