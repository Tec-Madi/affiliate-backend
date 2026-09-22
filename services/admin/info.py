from datetime import datetime

from sqlalchemy.orm import Session

from core.error.http import AdminOnlyError
from models.users import User
from repositories.admin import GeneralMessageRepository, SystemInfoRepository


def get_system_info_function(user: User, db: Session):
    
    if not user.is_admin:
        raise AdminOnlyError()

    system_info_repo = SystemInfoRepository(db)

    system_info = system_info_repo.get_system_info()

    return {
        'email': system_info.email if system_info else None,
        'phone_number': system_info.phone_number if system_info else None,
        'whatsapp_link': system_info.whatsapp_link if system_info else None,
        'x_link': system_info.x_link if system_info else None,
        'facebook_link': system_info.facebook_link if system_info else None,
        'tiktok_link': system_info.tiktok_link if system_info else None,
        'instagram_link': system_info.instagram_link if system_info else None
    }

def update_system_info_function(user: User, db: Session, email: str | None, phone_number: str | None, whatsapp_link: str | None, x_link: str | None, facebook_link: str | None, tiktok_link: str | None, instagram_link: str | None):

    if not user.is_admin:
        raise AdminOnlyError()

    system_info_repo = SystemInfoRepository(db)

    system_info = system_info_repo.get_system_info()

    if not system_info:
        system_info_repo.create(email=email, phone_number=phone_number, whatsapp_link=whatsapp_link, x_link=x_link, facebook_link=facebook_link, tiktok_link=tiktok_link, instagram_link=instagram_link)
    else:
        to_update = {
            'email': email,
            'phone_number': phone_number,
            'whatsapp_link': whatsapp_link,
            'x_link': x_link,
            'facebook_link': facebook_link,
            'tiktok_link': tiktok_link,
            'instagram_link': instagram_link
        }

        for key, value in to_update.items():
            if value is not None:
                setattr(system_info, key, value)

    db.commit()

    return {'message': 'System info updated successfully'}

def get_all_messages_function(user: User, db: Session):

    if not user.is_admin:
        raise AdminOnlyError()
    
    message_repo = GeneralMessageRepository(db)

    messages = message_repo.get_all()

    return [{
        'id': message.id,
        'title': message.title,
        'message': message.message,
        'is_active': message.is_active,
        'created_at': message.created_at
    } for message in messages]

def create_message_function(user: User, db: Session, title: str, message: str, is_active: bool):

    if not user.is_admin:
        raise AdminOnlyError()
    
    message_repo = GeneralMessageRepository(db)

    message_repo.create(title=title, message=message, is_active=is_active, created_at=datetime.now())

    return {'message': 'Message created successfully'}

def edit_message_function(user: User, db: Session, id: int, title: str | None, message: str | None, is_active: bool):

    if not user.is_admin:
        raise AdminOnlyError()

    message_repo = GeneralMessageRepository(db)

    message_obj = message_repo.get_by_id(id)
    if not message_obj:
        return {'message': 'Message not found'}

    to_update = {
        'title': title,
        'message': message,
        'is_active': is_active
    }

    if to_update:
        for key, value in to_update.items():
            if value is not None:
                setattr(message_obj, key, value)

    db.commit()

    return {'message': 'Message updated successfully'}

def delete_message_function(user: User, db: Session, id: int):

    if not user.is_admin:
        raise AdminOnlyError()

    message_repo = GeneralMessageRepository(db)

    message = message_repo.get_by_id(id)
    if not message:
        return {'message': 'Message not found'}

    db.delete(message)
    db.commit()

    return {'message': 'Message deleted successfully'}