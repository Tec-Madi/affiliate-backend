from decimal import Decimal
import hashlib
import hmac
from starlette.requests import Request

from core.cryptography import decrypt_data
from core.error.http import UnauthourizedError
from models.admin import PaymentProvider, PaymentProviderName
from providers.base import BasePayment, PaymentRequest

                       
class PaymentPoint(BasePayment):

    def __init__(self, provider: PaymentProvider):
        self.base_url = provider.base_url
        self.account_or_business_id = decrypt_data(provider.credentials.get("account_or_business_id"))
        self.token_or_api_key = decrypt_data(provider.credentials.get("token_or_api_key"))
        self.password_or_secret_key = decrypt_data(provider.credentials.get("password_or_secret_key"))

    async def authenticate(self, credentials):

        return await super().authenticate(credentials)
 
    async def generate_static_account(self, **kwargs):

        payload = kwargs.get("payload")

        nin = payload.get('nin')
        bvn = payload.get('bvn')

        url = self.base_url + "/api/v1/createVirtualAccount"

        headers = {
            'Authorization': f'Bearer {self.password_or_secret_key}',
            'Content-Type': 'application/json',
            'api-key': self.token_or_api_key
        }

        body = {
            'email': payload.get('email'),
            'name': payload.get('name'),
            'phoneNumber': payload.get('number'),
            'bankCode': [str(bank_code) for bank_code in payload.get('bank_code', [])],
            'businessId': self.account_or_business_id,
            'idType': 'nin' if nin else 'bvn',
            'idNumber': nin if nin else bvn
        }

        response_map = {
            "bank_accounts_key": "bankAccounts",
            "account_number_key": "accountNumber",
            "bank_name_key": "bankName",
            "account_name_key": "accountName",
            "account_reference_key": "Reserved_Account_Id",
            "bank_code_key": "bankCode",
            "provider": PaymentProviderName.PAYMENTPOINT.value
        }

        return await super().generate_static_account(url=url, body=body, headers=headers, response_map=response_map)

    async def receive_payment(self, **kwargs):

        request: Request = kwargs.get("request")

        received_signature = request.headers.get('Paymentpoint-Signature')

        generated_signature = hmac.new(
            self.password_or_secret_key.encode(),
            await request.body(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_signature, generated_signature):
            raise UnauthourizedError('invalid signature')

        response_map = {
            "email_key": ["customer", "email"],
            "amount_key": ["amount_paid"],
            "account_number_key": ["receiver", "account_number"],
            "api_response_key": ["description"],
            "provider_reference_key": ["transaction_id"],
            "provider": PaymentProviderName.PAYMENTPOINT.value
        }

        return await super().receive_payment(request=request, response_map=response_map)

    async def verify_bvn(self, payload):
        pass

    async def verify_nin(self, payload):
        pass