from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from api.deps import require_admin
from models.users import User
from core.database import get_db
from services.admin.info import create_message_function, delete_message_function, edit_message_function, get_all_messages_function, get_system_info_function, update_system_info_function
from api.v1.private_api.schemas.admin.info import AddMessage, EditMessage, UpdateSystemInfo


admin_system_info_router = APIRouter(
    prefix='/system-info',
    tags=['System Information']
)

@admin_system_info_router.get('/')
def get_system_info(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return get_system_info_function(user=user, db=db)

@admin_system_info_router.patch('/update')
def update_system_info(data: UpdateSystemInfo, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return update_system_info_function(user=user, db=db, email=data.email, phone_number=data.phone_number, whatsapp_link=data.whatsapp_link, x_link=data.x_link, facebook_link=data.facebook_link, tiktok_link=data.tiktok_link, instagram_link=data.instagram_link)

@admin_system_info_router.get('/messages')
def get_all_messages(user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return get_all_messages_function(user=user, db=db)

@admin_system_info_router.post('/messages/add')
def create_message(data: AddMessage, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return create_message_function(user=user, db=db, title=data.title, message=data.message, is_active=data.is_active)

@admin_system_info_router.patch('/messages/edit/{id}')
def edit_message(id: int, data: EditMessage, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return edit_message_function(user=user, db=db, id=id, title=data.title, message=data.message, is_active=data.is_active)

@admin_system_info_router.delete('/messages/delete/{id}')
def delete_message(id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return delete_message_function(user=user, db=db, id=id)