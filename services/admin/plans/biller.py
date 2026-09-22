from typing import Literal
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.error.http import AdminOnlyError, NotFoundError
from models.plans.cable import Cable, ProviderCable
from models.plans.disco import Disco, ProviderDisco
from models.plans.network import Network, ProviderNetwork
from models.users import Services, User
from repositories.plans.cable import CableRepository, ProviderCableRepository
from repositories.plans.disco import DiscoRepository, ProviderDiscoRepository
from repositories.plans.network import NetworkRepository, ProviderNetworkRepository


def view_biller_function(user: User, db: Session, action_for: Literal["biller","linked-biller"], service: Services, id: int = None):

    if not user.is_admin:
        raise AdminOnlyError()

    if action_for == "biller":
        repo = (
            NetworkRepository if service == Services.NETWORK
            else CableRepository if service == Services.CABLE
            else DiscoRepository if service == Services.DISCO
            else None
        )

        if id:
            if not (biller := repo(db).get_by_id(id)):
                raise NotFoundError(service.value + "not found")
            return {
                "id": biller.id,
                service.value: biller.name.upper(),
                "is_active": biller.is_active
            }
            
        else:
            return [{
                "id": biller.id,
                service.value: biller.name.upper(),
                "is_active": biller.is_active,
            } for biller in repo(db).get_all()]

    elif action_for == "linked-biller":

        repo = (
            ProviderNetworkRepository if service == Services.NETWORK 
            else ProviderCableRepository if service == Services.CABLE 
            else ProviderDiscoRepository if service == Services.DISCO
            else None
        )

        return [{
            "id": linked_provider.id,
            "provider_name": linked_provider.provider_name,
            "provider_" + service.value + "_id": getattr(linked_provider, "provider_"+service.value+"_id", None)
        } for linked_provider in getattr(repo(db), "get_by_"+service.value+"_id", None)(id)]

def upsert_biller_function(user: User, db: Session, service: Services, action_for: Literal["biller","linked-biller"], action: Literal["edit", "create"], biller_schema: BaseModel, id: int |None = None,):

    if not user.is_admin:
        raise AdminOnlyError()

    if action_for == "biller":

        repo = (
            NetworkRepository if service == Services.NETWORK
            else CableRepository if service == Services.CABLE
            else DiscoRepository if service == Services.DISCO
            else None
        )

        payload = biller_schema.model_dump()
        payload = {
            key: value
            for key, value in payload.items() if value is not None
        }

        if action == "edit":
            if not (biller := repo(db).get_by_id(id)):
                raise NotFoundError("Biller not found")
            for key, value in payload.items():
                setattr(biller, key, value)

        elif action == "create":
            repo(db).create(**payload)

    elif action_for == "linked-biller":

        repo = (
            ProviderNetworkRepository if service == Services.NETWORK 
            else ProviderCableRepository if service == Services.CABLE 
            else ProviderDiscoRepository if service == Services.DISCO 
            else None
        )

        linked_biller_schema = {
            service.value+"_id": (biller_id := biller_schema.linked_biller.biller_id),
            "provider_name": (provider_name := biller_schema.linked_biller.provider_name),
            "provider_"+service.value+"_id": (provider_biller_id := biller_schema.linked_biller.provider_biller_id)
        }

        if action == "edit":
            linked_biller = repo(db).get_by_id(id)
            for key, value in linked_biller_schema.items():
                if value is not None:
                    setattr(linked_biller, key, value)

        elif action == "create":
            repo(db).create(provider_name, biller_id, provider_biller_id)

    db.commit()

    return {"message": f"{service.value} {"updated" if action == "edit" else "created"} successfully"}

def delete_biller_function(user: User, db: Session, service: Literal["network", Services.DISCO, Services.CABLE], id: int, action_for: Literal["biller","linked-biller"]):

    if not user.is_admin:
        raise AdminOnlyError()

    if action_for == "biller":
        repo = (
            NetworkRepository if service == Services.NETWORK
            else CableRepository if service == Services.AIRTIME
            else DiscoRepository if service == Services.DISCO
            else None
        )
        if not (biller := repo(db).get_by_id(id)):
            raise NotFoundError(f"{service.value.capitalize()} not found")
        db.delete(biller)

    elif action_for == "linked-biller":
        repo = (
            ProviderNetworkRepository if service == Services.NETWORK
            else ProviderCableRepository if service == Services.AIRTIME
            else ProviderDiscoRepository if service == Services.DISCO
            else None
        )
        if not (linked_biller := repo(db).get_by_id(id)):
            raise NotFoundError(f"Linked {service.value} not found")
        db.delete(linked_biller)

    db.commit()

    return {"message": f"{service.value} deleted successfully"}