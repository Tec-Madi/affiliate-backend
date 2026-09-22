from typing import Literal

from fastapi import Depends, APIRouter, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from api.deps import get_api_user
from api.v1.public_api.schemas import VTUPurchase
from core.database import get_db
from core.error.base import AppError, MimickError
from models.admin import ProviderType
from models.users import Services, Status, User

from services.auth.login import login_function
from services.user.vtu import virtual_top_up_function


user_api_purchase = APIRouter(
    prefix='/{service}',
    tags=['User API Purchase']
)

@user_api_purchase.post("")
def vtu_purchase(
        service: Literal[Services.AIRTIME, Services.DATA, Services.CABLE, Services.DISCO],
        payload: VTUPurchase,
        user: User = Depends(get_api_user), 
        db: Session = Depends(get_db)
    ):
    return virtual_top_up_function(user=user, db=db, service=service, payload=payload, from_api=True)


api_mimick_router = APIRouter(
    tags=['MIMICK EXTERNAL PROVIDER VTU']
)

@api_mimick_router.post('/api/user')
def ADEX_CRED_DETAILS(credentials: HTTPBasicCredentials = Depends(HTTPBasic()), db: Session = Depends(get_db)):
    return get_user_function(provider=ProviderType.ADEX, credentials=credentials, db=db)

@api_mimick_router.post('/api/{service_path}')
async def adex_vtu_purchase(
        service_path: Literal["data", "topup", "cable", "bill"],
        body: dict = Body(),
        user: User = Depends(get_api_user),
        db: Session = Depends(get_db)
    ):
    return await vtu_purchase_mimick_function(user=user, db=db, provider=ProviderType.ADEX, body=body, service_path=service_path)

@api_mimick_router.get('/api/user/')
def MSORG_CRED_DETAILS(credentials: User = Depends(get_api_user), db: Session = Depends(get_db)):
    return get_user_function(provider=ProviderType.MSORG, credentials=credentials, db=db)

@api_mimick_router.post("/api/{service_path}/")
async def msorg_vtu_purchase(
        service_path: Literal["data", "topup", "billpayment", "cablesub"],
        body: dict = Body(),
        user: User = Depends(get_api_user),
        db: Session = Depends(get_db)
    ):
    return await vtu_purchase_mimick_function(user=user, db=db, provider=ProviderType.MSORG, body=body, service_path=service_path)














def get_user_function(provider: ProviderType, credentials: HTTPBasicCredentials | User, db: Session):

    try:
        if provider == ProviderType.ADEX:
            response = login_function(email=credentials.username, password=credentials.password, db=db)
            return {
                'status': 'success',
                'AccessToken': response['access_token'],
                'username': response['email'],
                'balance': response['balance']
            }

        elif provider == ProviderType.MSORG:
            return {
                'user': {
                    'email': credentials.email,
                    'username': credentials.email,
                    'FullName': credentials.name,
                    'Account_Balance': credentials.wallet.balance,
                    'wallet_balance': credentials.wallet.balance
                }
            }

    except AppError as e:
        raise MimickError(provider=ProviderType.ADEX, message=e.message, status_code=e.status_code)

async def vtu_purchase_mimick_function(user: User, db: Session, provider: ProviderType, body: dict, service_path: str):

    payload = {
        ProviderType.ADEX: VTUPurchase(
            biller_id = body.get("network") or body.get("cable") or body.get("disco"),
            plan_id = body.get("data_plan") or body.get("cable_plan"), 
            beneficiary = body.get("phone") or body.get("iuc"),
            plan_type = body.get("plan_type") or body.get("meter_type"),
            request_id = body.get("request-id")
        ),
        ProviderType.MSORG: VTUPurchase(
            biller_id = body.get("network") or body.get("disco_name") or body.get("cablename"),
            plan_id = body.get("plan") or body.get("cableplan"),
            plan_type = body.get("airtime_type") or body.get("MeterType"),
            beneficiary = body.get("mobile_number") or body.get("meter_number") or body.get("smart_card_number")
        ),
    }[provider]

    service = {
        ProviderType.ADEX: {
            "data": Services.DATA,
            "topup": Services.AIRTIME,
            "cable": Services.CABLE,
            "bill": Services.DISCO
        },
        ProviderType.MSORG: {
            "data": Services.DATA,
            "topup": Services.AIRTIME,
            "cablesub": Services.CABLE,
            "billpaymnet": Services.DISCO
        }
    }[provider][service_path]

    try:

        response = await virtual_top_up_function(user=user, db=db, service=service, payload=payload, from_api=True)
        
        actual_status = response.get('status')
        api_response, message = response.get('api_response'), response.get('message')
        number, reference, request_id = response.get('number'), response.get('reference'), response.get('request_id')
        amount, new_balance, old_balance = response.get('amount'), response.get('new_balance'), response.get('old_balance')
        product = response.get('product')
        

        status_map = {
            ProviderType.ADEX: {Status.SUCCESS: 'success', Status.FAIL: 'failed'},
            ProviderType.MSORG: {Status.SUCCESS: 'successful', Status.FAIL: 'failed'} 
        }

        status = status_map[provider].get(actual_status)

        to_return_map = {
            ProviderType.ADEX.value: {
                "status": status,
                'message': message,
                'response': api_response,
                'request-id': request_id,
                'amount': amount,
                'oldbal': old_balance,
                'newbal': new_balance,
                'dataplan': product,
                'system': 'API',
                'wallet_vending': 'wallet'
            },
            ProviderType.MSORG.value: {
                'Status': status,
                'api_response': api_response,
                'ident': reference,
                'plan_amount': amount,
                'balance_before': old_balance,
                'balance_after': new_balance,
                'ident': reference,
                'plan_name': product
            }
        }

        return to_return_map[provider]

    except Exception as e:
        raise MimickError(provider=provider, message=e.message, status_code=e.status_code)

