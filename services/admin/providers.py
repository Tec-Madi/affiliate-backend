from typing import Literal

from sqlalchemy.orm import Session

from core.cryptography import decrypt_data, encrypt_data
from core.error.http import AdminOnlyError, ForbiddenError, NotFoundError
from models.admin import PaymentProviderName, ProviderType
from models.users import User
from providers.pgw.paymentpoint import PaymentPoint
from providers.pgw.securewaveng import SecureWaveNg
from providers.vtu.madix import MadixProvider
from providers.vtu.ogdams import Ogdams
from providers.vtu.quicklysim import QuicklySim
from providers.vtu.smeplug import SmePlug
from providers.base import BaseProvider, BasePayment
from providers.vtu.adex import AdexProvider
from providers.vtu.msorg import MsorgProvider
from repositories.admin import PaymentProviderRepository, ProviderRepository


def all_providers_function(user: User, db: Session, query_for: Literal["vtu", "pgw"], names_only: bool = False):

    if user.is_admin is not True:
        raise ForbiddenError(message='only admin can access this page')

    provider_repo = ProviderRepository(db)
    if names_only is True:
        providers = [provider for provider in (provider_repo.get_provider_names() if query_for == "vtu" else [PaymentProviderName.PAYMENTPOINT.value, PaymentProviderName.SECUREWAVENG.value])]
    else:
        providers =  [{
            "id": provider.id,
            "provider_name": provider.name,
            "provider_base_url": provider.base_url,
            "provider_type": getattr(provider, "type", provider.name),
            "is_active": provider.is_active,
            "crednetials": {
                "account_or_business_id": decrypt_data(provider.credentials.get("account_or_business_id")),
                "username_or_public_key": decrypt_data(provider.credentials.get("username_or_public_key")),
                "token_or_api_key": decrypt_data(provider.credentials.get("token_or_api_key")),
                "password_or_secret_key": decrypt_data(provider.credentials.get("password_or_secret_key"))
            }
        } for provider in (provider_repo.get_all() if query_for == "vtu" else PaymentProviderRepository(db).get_all())]

    return providers

async def upsert_provider_function(user: User, db: Session, upsert_for: Literal["vtu", "pgw"], action: Literal["edit", "create"], provider_schema: object, id: int | None = None):
  
    if not user.is_admin:
        raise AdminOnlyError()

    if action == "edit":
        if not (provider := (ProviderRepository if upsert_for =="vtu" else PaymentProviderRepository)(db).get_by_id(id)):
            raise NotFoundError("Provider not found")

    elif action == "create":

        provider = (ProviderRepository if upsert_for=="vtu" else PaymentProviderRepository)(db).create(
            name=provider_schema.provider_name,
            **({"provider_type":provider_schema.provider_type} if upsert_for == "vtu" else {}),
            base_url=provider_schema.base_url
        )
        db.flush()

    provider_class_map = {
        ProviderType.MADIX: MadixProvider,
        ProviderType.ADEX: AdexProvider,
        ProviderType.MSORG: MsorgProvider,
        ProviderType.QUICKLYSIM: QuicklySim,
        ProviderType.OGDAMS: Ogdams,
        ProviderType.SMEPLUG: SmePlug,
        PaymentProviderName.SECUREWAVENG: SecureWaveNg,
        PaymentProviderName.PAYMENTPOINT: PaymentPoint
    }

    if not (provider_class := provider_class_map.get(provider_schema.provider_type)):
        raise NotFoundError("Unsupported provider")

    base_provider: BaseProvider | BasePayment = provider_class(provider)

    if (provider_credentials := provider_schema.credentials):
        response = await base_provider.authenticate({
                "account_or_business_id": provider_credentials.account_or_business_id,
                "username_or_public_key": provider_credentials.username_or_public_key,
                "token_or_api_key": provider_credentials.token_or_api_key,
                "password_or_secret_key": provider_credentials.password_or_secret_key
            })

        provider.credentials = ({
            "account_or_business_id": encrypt_data(response.get("account_or_business_id")),
            "token_or_api_key": encrypt_data(response.get("token_or_api_key")),
            "username_or_public_key": encrypt_data(response.get("username_or_public_key")),
            "password_or_secret_key": encrypt_data(response.get("password_or_secret_key"))
        })

    db.commit()

    return {"message": provider.name + " added" if action == "create" else " updated" + "successfully"}

def delete_provider_function(user: User, db: Session, delete_for: Literal["vtu", "pgw"], id: int):

    if user.is_admin is not True:
        raise ForbiddenError(message='only admin can access this page')

    provider_repo = (ProviderRepository(db) if delete_for == "vtu" else PaymentProviderRepository(db))

    provider = provider_repo.get_by_id(id=id)

    db.delete(provider)
    db.commit()

    return {'message': f'provider {provider.name} deleted successfully'}