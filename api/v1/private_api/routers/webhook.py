from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request

from core.database import get_db
from models.admin import PaymentProviderName
from services.user.wallet import receive_payment


webhook_router = APIRouter(
  tags=['Our webhook']
)

@webhook_router.post('/wfknf93t25/securewave')
async def securewave_webhook(request: Request, db: Session = Depends(get_db)):
  return await receive_payment(db=db, request=request, payment_provider_name=PaymentProviderName.SECUREWAVENG)

@webhook_router.post('/HaDjORovhh5whZE6oSARK1u3V9JCyb2Tp2r4rbuDcik/paymentpoint')
async def paymentpoint_webhook(request: Request, db: Session = Depends(get_db)):
  return await receive_payment(db=db, request=request, payment_provider_name=PaymentProviderName.PAYMENTPOINT)