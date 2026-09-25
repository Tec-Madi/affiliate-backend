from abc import ABC, abstractmethod
from decimal import Decimal
import json
from types import NoneType
from typing import Any, TypedDict

from fastapi import Request

from core.cryptography import encrypt_data
from core.error.http import APIRequestError
from core.utils import BankAccount, CredentialsToAuth, KYCResponse, PaymentRequest, ProviderAuthResponse, ProviderResponse, request
from models.users import Status

class BaseProvider(ABC):

    @abstractmethod
    async def authenticate(self, credentials: dict) -> ProviderAuthResponse:
        return credentials

    @abstractmethod
    async def virtual_top_up(self, **kwarg) -> ProviderAuthResponse:

        url, body, headers = kwarg.get("url"), kwarg.get("body"), kwarg.get("headers")

        response_mapping: dict = kwarg.get("response_mapping")
        provider_name = response_mapping.get("provider_name")

        try:
            response = await request(method="POST", url=url, headers=headers, body=body)
            response.raise_for_status()

            data: dict = response.json()

            api_response = provider_status = provider_reference = data

            for key in response_mapping["status_key"]:
                if isinstance((provider_status := provider_status.get(key)), NoneType):
                    break

            for key in response_mapping["api_response_key"]:
                if isinstance((api_response := api_response.get(key)), NoneType):
                    break

            for key in response_mapping["reference_key"]:
               if isinstance((provider_reference := provider_reference.get(key)), NoneType):
                   break

            status = (
                Status.SUCCESS.value if provider_status == response_mapping["success_value"]
                else Status.FAIL.value if provider_status == response_mapping["failure_value"]
                else Status.PENDING.value
            )

        except APIRequestError:
            status = Status.PENDING.value
            api_response = "An Error occured with the provider"
            provider_reference = None

        except Exception:
            status = Status.FAIL.value
            api_response = "An unexpected error occur while processing request"
            provider_reference = None

        return ProviderResponse(
            status=status,
            api_response=api_response,
            provider_name=provider_name,
            provider_ref=provider_reference
        )

class BasePayment(ABC):

    @abstractmethod
    async def authenticate(self, credentials: CredentialsToAuth) -> ProviderAuthResponse:
        return {
            "account_or_business_id": credentials.get("account_or_business_id"),
            "token_or_api_key": credentials.get("token_or_api_key"),
            "username_or_public_key": credentials.get("username_or_public_key"),
            "password_or_secret_key": credentials.get("password_or_secret_key")
        }

    @abstractmethod
    async def generate_static_account(self, **kwargs) -> list[BankAccount]:

        url, body, headers = kwargs.get("url"), kwargs.get("body"), kwargs.get("headers")
        response_map: dict = kwargs.get("response_map")

        response = await request("POST", url, headers, None, body)
        response.raise_for_status()

        data: dict = response.json()

        bank_accounts: list[BankAccount] = []

        accounts: list[dict[str, Any]] = data.get(response_map.get("accounts_key"), [])

        for account in accounts:
            account_number = account.get(response_map["account_number_key"])
            bank_name = account.get(response_map["bank_name_key"])
            account_name = account.get(response_map["account_name_key"])
            account_reference = account.get(response_map["account_reference_key"])
            bank_code = account.get(response_map["bank_code_key"])

            bank_accounts.append(BankAccount(
                bank_name=bank_name, 
                account_number=account_number, 
                account_name=account_name,
                account_reference=account_reference,
                bank_code=str(bank_code),
                provider=response_map["provider"]
            ))

        print(bank_accounts)

        return bank_accounts
    
    @abstractmethod
    async def receive_payment(self, **kwargs) -> PaymentRequest:

        request: Request = kwargs.get("request")
        response_map: dict[str] = kwargs.get("response_map")

        payload: dict = await request.json()

        email = payload
        for key in response_map["email_key"]:
            email = email.get(key, {})

        account_number = payload
        for key in response_map["account_number_key"]:
            account_number = account_number.get(key, {})

        amount = payload
        for key in response_map["amount_key"]:
            amount = amount.get(key, {})

        api_response = payload
        for key in response_map["api_response_key"]:
            api_response = api_response.get(key, {})

        provider_reference = payload
        for key in response_map["provider_reference_key"]:
            provider_reference = provider_reference.get(key, {})

        provider = response_map["provider"]

        return PaymentRequest(
            email=email,
            amount=Decimal(str(amount)),
            account_number=account_number,
            api_response=api_response,
            provider=provider,
            provider_reference=provider_reference
        )

    @abstractmethod
    async def verify_bvn(self, payload: dict) -> KYCResponse:
        pass

    @abstractmethod
    async def verify_nin(self, payload: dict) -> KYCResponse:
        pass