from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request

from core.database import get_db
from models.admin import PaymentProviderName
from services.user.wallet import receive_payment


webhook_router = APIRouter(
  tags=['Our webhook'],
  prefix="/webhook/{provider}"
)

@webhook_router.post("")
def receive_payments(request: Request, provider: PaymentProviderName, db: Session = Depends(get_db)):
  return receive_payment(db=db, request=request, payment_provider_name=provider)