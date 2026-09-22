from decimal import Decimal
from typing import Literal

from sqlalchemy.orm import Session

from core.cryptography import decrypt_data, encrypt_data
from core.error.http import AdminOnlyError
from models.users import User
from repositories.admin import AdminIDRepository, PaymentPlanRepository


def all_payment_plans_function(user: User, db: Session):

    if not user.is_admin:
        raise AdminOnlyError()

    payment_plans = PaymentPlanRepository(db).get_all()

    return[{
        'id': payment_plan.id,
        'name': payment_plan.bank_name,
        'provider': payment_plan.provider,
        'charges_type': payment_plan.charges_type,
        'flat': payment_plan.flat,
        'percentage': payment_plan.percentage,
        'capped': payment_plan.capped,
        'is_active': payment_plan.is_active,
        'bank_code': payment_plan.bank_code
    }for payment_plan in payment_plans]

async def upsert_payment_plan_function(user: User, db: Session, action: Literal["create", "edit"], plan_schema: object, id: int | None = None):

    if not user.is_admin:
        raise AdminOnlyError()

    payment_plan = payment_plan_repo.get_by_id(id=id)

    plan_schema_to_use = {
        'bank_name': plan_schema.bank_name,
        'provider': plan_schema.provider,
        'charges_type': plan_schema.charges_type,
        'flat': plan_schema.flat,
        'percentage': plan_schema.percentage,
        'capped': plan_schema.capped,
        'is_active': plan_schema.is_active,
        'bank_code': plan_schema.bank_code
    }

    if action == "edit":
        payment_plan_repo = PaymentPlanRepository(db)
        for key, value in plan_schema_to_use:
            if value is not None:
                setattr(payment_plan, key, value)

    elif action == "create":
        payment_plan = PaymentPlanRepository(db).create(**plan_schema_to_use)

    db.commit()

    return {'message': 'payment plan updated successfully'}

def delete_payment_plan_fuction(user: User, db: Session, id: int):

    if not user.is_admin:
        raise AdminOnlyError()

    payment_plan = PaymentPlanRepository(db).get_by_id(id=id)    

    db.delete(payment_plan)
    db.commit()

    return {'message': 'payment plan deleted successfully'}



def view_admin_id_function(user: User, db: Session):

    if not user.is_admin:
        raise AdminOnlyError()

    admin_id = AdminIDRepository(db).get_admin_id()

    return {
        'nin': decrypt_data(admin_id.nin),
        'bvn': decrypt_data(admin_id.bvn)
    }

def upsert_admin_id_function(user: User, db: Session, admin_id_schema: object):

    if not user.is_admin:
        raise AdminOnlyError()
    
    nin = encrypt_data(admin_id_schema.nin)
    bvn = encrypt_data(admin_id_schema.bvn)

    if (admin_id := AdminIDRepository(db).get_admin_id()):
        if nin is not None:
            admin_id.nin = nin
        if bvn is not None:
            admin_id.bvn = bvn
    else:
        AdminIDRepository(db).create(nin=nin, bvn=bvn)

    db.commit()

    return {'message': 'Admin ID added successfully'}