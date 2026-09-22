from decimal import Decimal
from sqlalchemy.orm import Session

from core.cryptography import verify_hashed_data
from core.error.http import BadRequestError, NotFoundError, UnprocessibleEntityError
from core.services.transaction import TransactionService
from core.utils import TxnDetails, get_cash_back
from models.plans.network import DataSize
from models.users import Services, User
from providers.router import VTURouter
from repositories.plans.cable import CablePlanRepository
from repositories.plans.disco import DiscoPlanRepository
from repositories.plans.network import AirtimePlanRepository, DataPlanRepository


async def get_biller_function(user: User, db: Session, service: Services):


    if not (repo := (
        AirtimePlanRepository if service == Services.AIRTIME 
        else DataPlanRepository if service == Services.DATA 
        else CablePlanRepository if service == Services.CABLE 
        else DiscoPlanRepository if service == Services.DISCO 
        else None
    )):
        raise UnprocessibleEntityError("Unimplemented service")

    biller_key = "network" if service in [Services.AIRTIME, Services.DATA] else "cable" if service == Services.CABLE else "disco"

    billers = getattr(repo(db), "get_"+biller_key+"s")()

    return [{
        biller_key+"_id": getattr(biller, biller_key+"_id", None),
        biller_key+"_name": getattr(biller, biller_key, "").upper()
    }for biller in billers]

async def get_plan_type_function(user: User, db: Session, service: Services, biller_id: int):

    if not (repo := (
            AirtimePlanRepository if service == Services.AIRTIME 
            else DataPlanRepository if service == Services.DATA 
            else CablePlanRepository if service == Services.CABLE 
            else DiscoPlanRepository if service == Services.DISCO 
            else None
        )):
            raise UnprocessibleEntityError("Unimplemented service")

    return getattr(repo(db), "get_"+service.value+"_types")(biller_id) if service in [Services.DATA, Services.DISCO] else []

async def get_plans_function(user: User, db: Session, service: Services, biller_id: int, plan_type: str | None = None):

    if service == Services.AIRTIME: 
        plan = AirtimePlanRepository(db).get_by_network_id(biller_id)

    elif service == Services.DATA:
        plans = DataPlanRepository(db).get_data_plans(biller_id, plan_type)

    elif service == Services.CABLE:
        plans = CablePlanRepository(db).get_by_cable_id(biller_id)

    elif service == Services.DISCO:
        plan = DiscoPlanRepository(db).get_by_disco_id_and_disco_type(biller_id, plan_type)

    else:
        raise BadRequestError("Invalid Service")

    if service in [Services.DATA, Services.CABLE]:
        return [{
            "id": plan.id,
            "plan_name": f"{plan.name} {getattr(plan, "size", "").upper()}",
            "price": f"₦{plan.price: ,}",
            "discount": get_cash_back(user, plan),
            "validity": plan.validity,
            "description": plan.description
        } for plan in plans]

    elif service in [Services.AIRTIME, Services.DISCO]:
        return {
            "discount": get_cash_back(user, plan),
            "minimum_amount": plan.minimum_amount,
            "maximum_amount": plan.maximum_amount,
        }    

async def virtual_top_up_function(user: User, db: Session, service: Services, payload: object, from_api: bool = False):

    transaction_service = TransactionService(user=user, db=db)
    amount = None

    if not (beneficiary := payload.beneficiary):
        raise BadRequestError("beneficiary field is required")

    if service in [Services.AIRTIME, Services.DISCO]:
        if not (biller_id := payload.biller_id):
            raise BadRequestError("biller_id field is missing")
        if not (amount := payload.amount):
            raise BadRequestError("amount field is missing")
        if not (plan_type := payload.plan_type):
            raise BadRequestError("plan_type is missing")

    if service in [Services.DATA, Services.CABLE]:
        if not (plan_id := payload.plan_id):
            raise BadRequestError("plan_id field is required")

    if not (
        (len(beneficiary) == (length := 11)) and (message_patch := "exactly") if service in [Services.AIRTIME, Services.DATA]
        else (len(beneficiary) == (length := 10)) and (message_patch := "exactly") if service == Services.CABLE
        else (len(beneficiary) > (length := 10)) and (message_patch := "greater than") if service == Services.DISCO
        else False
    ):
        raise BadRequestError("Beneficiary must be " + message_patch + " " + str(length) + " digit")

    if not (plan := (
            AirtimePlanRepository(db).get_by_network_id(int(biller_id)) if service == Services.AIRTIME
            else DataPlanRepository(db).get_by_id(int(plan_id)) if service == Services.DATA
            else CablePlanRepository(db).get_by_id(int(plan_id)) if service == Services.CABLE
            else DiscoPlanRepository(db).get_by_disco_id_and_disco_type(int(biller_id), plan_type) if service == Services.DISCO
            else None
        )):
        raise NotFoundError("Plan not found")

    if service in [Services.AIRTIME, Services.DISCO]:
        if (minimum := plan.minimum_amount) < amount > (maximum := plan.maximum_amount):
            raise BadRequestError("Amount must be between ₦"+str(minimum)+" and ₦"+str(maximum))

    service_provider = getattr(getattr(
        plan,
        "network" if service in [Services.DATA, Services.AIRTIME] 
        else "cable" if service == Services.CABLE 
        else "disco" if service == Services.DISCO else "",
        None
    ), "name", None)

    product = (
        f"{amount} {service_provider} Airtime" if service == Services.AIRTIME
        else f"{plan.name} {str(getattr(plan, "size", "").upper())}" if service == Services.DATA
        else plan.plan_name.upper() if service == Services.CABLE
        else f"{amount} {service_provider} Disco" if service == Services.DISCO
        else ""
    )

    value = (
        (
            Decimal(plan.name)*Decimal(0.001) if plan.size == DataSize.MB.value 
            else Decimal(plan.name) if plan.size == DataSize.GB.value 
            else Decimal(plan.name)*Decimal(1000) if plan.size == DataSize.TB.value 
            else Decimal(0)
        ) if service == Services.DATA 
        else amount if service in [Services.AIRTIME, Services.DISCO]
        else plan.price if service == Services.CABLE else
        Decimal(0)
    )

    plan_type = getattr(plan, "type", None)
    request_id = payload.request_id if from_api else None

    transaction_details = TxnDetails(
        service=service,
        service_type=plan_type, 
        service_provider=service_provider, 
        beneficiary=beneficiary, 
        value=value, 
        product=product,
        request_id=request_id
    )

    try:
        payment_executor = await transaction_service.execute_payment(plan=plan, amount=amount, transaction_details=transaction_details, from_api=from_api)
        amount = payment_executor["amount"]
        cash_back = payment_executor["cash_back"]
        old_balance = payment_executor["old_balance"]
        reference = payment_executor["reference"]

        db.commit()

    except Exception:
        db.rollback()
        raise

    try:
        response = await VTURouter.vend_vtu_service(payload={"beneficiary": beneficiary, "amount": amount, "plan": plan, "reference": reference}, service=service, db=db)
    except Exception as e:
        response = e

    complete_transaction = await transaction_service.update_transaction(reference=reference, cash_back=cash_back, provider_response=response)

    return {
        'status': complete_transaction.get('status'),
        'cash_back': cash_back,
        'message': complete_transaction.get('message'),
        'api_response': complete_transaction.get('api_response'),
        'beneficiary': beneficiary,
        'product': product,
        'amount': amount,
        'old_balance': old_balance,
        'new_balance': complete_transaction.get("new_balance"),
        'reference': reference,
        'request_id': request_id
    }

def purchase_pin_validator_function(user: User, db: Session, pin: str):

    if not pin.isdigit() or len(pin) != 4:
        raise UnprocessibleEntityError('PIN must be a 4 digit number')

    if not verify_hashed_data(data=pin, hashed_data=user.pin):
        raise BadRequestError('Invalid transaction PIN')

    return {'message': 'pin validated successfully'}