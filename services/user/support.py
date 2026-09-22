from sqlalchemy.orm import Session

from models.users import User
from repositories.admin import SystemInfoRepository


def get_support_link_function(user: User | None, db: Session):

    system_info_repo = SystemInfoRepository(db)

    system_info = system_info_repo.get_system_info()

    return {
        'email': system_info.email,
        'phone_number': system_info.phone_number,
        'whatsapp_link': system_info.whatsapp_link,
        'x_link': system_info.x_link,
        'instagram_link': system_info.instagram_link,
        'facebook_link': system_info.facebook_link,
        'tiktok_link': system_info.tiktok_link
    }