from decimal import Decimal
import hashlib
import hmac
import httpx
from fastapi import Request

from core.cryptography import decrypt_data
from core.error.http import BadGateWayError, BadRequestError, UnauthourizedError, UnprocessibleEntityError
from models.admin import PaymentProvider, PaymentProviderName
from models.users import Gender, KYCStatus
from providers.base import BasePayment, KYCResponse, PaymentRequest

class SecureWaveNg(BasePayment):

    def __init__(self, provider: PaymentProvider):
        self.base_url = provider.base_url
        self.account_or_business_id = decrypt_data(provider.credentials.get("account_or_business_id"))
        self.username_or_public_key = decrypt_data(provider.credentials.get("username_or_public_key"))
        self.password_or_secret_key = decrypt_data(provider.credentials.get("password_or_secret_key"))

    async def authenticate(self, credentials):
        return await super().authenticate(credentials)

    async def generate_static_account(self, payload: dict):

        nin = payload.get('nin')
        bvn = payload.get('bvn')

        url = f'{self.base_url}/api/virtual_accounts/generate'

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.password_or_secret_key}',
            'x-api-key': self.username_or_public_key
        }

        body = {
            "email": payload.get('email'),
            "first_name": payload.get('name'),
            "last_name": payload.get('name'),
            "phone_number": payload.get('number'),
            "bank_code": [int(bank_code) for bank_code in payload.get('bank_code', []) if bank_code.isdigit()],
            "business_id": self.account_or_business_id,
            "account_type": "static",
            "id_type": 'bvn' if bvn else 'nin',
            "id_number": bvn if bvn else nin
        }

        response_map = {
            "accounts_key": "data",
            "account_number_key": "account_number",
            "bank_name_key": "account_bank",
            "account_name_key": "account_name",
            "account_reference_key": "account_reference",
            "bank_code_key": "bank_code",
            "provider": PaymentProviderName.SECUREWAVENG.value
        }

        return await super().generate_static_account(url=url, body=body, headers=headers, response_map=response_map)

    async def receive_payment(self, request: Request):

        secret_key = self.password_or_secret_key

        received_signature = request.headers.get("X-Signature")
        if not received_signature:
            raise UnprocessibleEntityError('no signature')

        generated_signature = hmac.new(
            secret_key.encode(),
            await request.body(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(generated_signature, received_signature):
            raise UnauthourizedError('invalid signature')

        response_map = {
            "email_key": ["customer", "email"],
            "amount_key": ["amount"],
            "account_number_key": ["receiver", "account_number"],
            "api_response_key": ["notification_status"],
            "provider_reference_key": ["transaction_id"],
            "provider": PaymentProviderName.SECUREWAVENG.value
        }

        return await super().receive_payment(request=request, response_map=response_map)

    async def verify_bvn(self, payload):

        encrypt_secret_key = self.credentials['secret_key']
        encrypt_public_key = self.credentials['public_key']

        secret_key = decrypt_data(encrypted_data=encrypt_secret_key)
        public_key = decrypt_data(encrypted_data=encrypt_public_key)

        bvn = payload.get('bvn')
        number = payload.get('nin')

        url = f'{self.base_url}/api/verify-bvn'

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {secret_key}',
            'x-api-key': public_key
        }

        payload = {
            'bvn': bvn,
            'phone': number
        }

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(url=url, json=payload, headers=headers)
                print(response.json())
                if not 200 <= response.status_code < 300:
                    raise BadRequestError(message='Unable to verify kyc')

            parsedJson = response.json()

            if parsedJson.get('status') == True and parsedJson.get('verification_status') == 'VERIFIED':

                personal_info: dict = parsedJson.get('data', {}).get('personal_info')
                gender_map = {
                    'male': Gender.MALE.value,
                    'female': Gender.FEMALE.value
                }

                return KYCResponse(
                    status=KYCStatus.VERIFIED.value,
                    first_name=personal_info.get('first_name'),
                    last_name=personal_info.get('last_name'),
                    middle_name=personal_info.get('middle_name'),
                    full_name=personal_info.get('full_name'),
                    email=personal_info.get('email'),
                    gender=gender_map.get(personal_info.get('gender')),
                    state_of_origin=personal_info.get('state_of_origin'),
                    nationality=personal_info.get('nationality'),
                    LGA=personal_info.get('lga_of_origin'),
                    date_of_birth=personal_info.get('date_of_birth')
                )

            else:
                return KYCResponse(status=KYCStatus.REJECTED.value)

        except Exception as e:
            raise BadGateWayError(str(e))

    async def verify_nin(self, payload):
        pass