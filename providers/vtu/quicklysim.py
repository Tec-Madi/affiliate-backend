from core.cryptography import decrypt_data
from core.error.http import BadRequestError
from core.utils import request
from models.admin import Provider
from models.users import Services
from providers.base import BaseProvider


class QuicklySim(BaseProvider):

    def __init__(self, provider: Provider):
        self.base_url = provider.base_url
        self.provider_name = provider.name
        self.username_or_public_key = decrypt_data(provider.credentials.get("username_or_public_key"))
        self.password_or_secret_key = decrypt_data(provider.credentials.get("password_or_secret_key"))

    async def authenticate(self, credentials: dict):

        if not (username_or_public_key := credentials.get('username_or_public_key')):
            raise BadRequestError('username is required')
        if not (password_or_secret_key := credentials.get('password_or_secret_key')):
            raise BadRequestError('password is required')

        response = await request(method="POST", url=f'{self.base_url}/api/user', auth=(username_or_public_key, password_or_secret_key))

        credentials["token_or_api_key"] = response.json()["AccessToken"]

        return await super().authenticate(credentials)

    async def virtual_top_up(self, **kwarg):

        service, payload = kwarg.get('service'), dict(kwarg.get('payload'))
  
        beneficiary = payload.get("beneficiary")
        biller_id = payload.get("biller_id")
        plan_id = payload.get("plan_id")
        amount = payload.get("amount")
        reference = payload.get("reference")

        authentication = await self.authenticate({"username_or_public_key": self.username_or_public_key, "password_or_secret_key": self.password_or_secret_key})

        headers = {'Authorization': "Token " + authentication["token_or_api_key"]}

        if service == Services.AIRTIME:

            url = self.base_url + "/api/topup"

            body = {
                'phone': beneficiary,
                'network': int(biller_id),
                'amount': float(amount),
                'request-id': reference
            }

        elif service == Services.DATA:

            url = self.base_url + "/api/data"

            body = {
                'phone': beneficiary,
                'data_plan': int(plan_id), 
                'request-id': reference
            }

        response_mapping = {
            'status_key': ['status'],
            'success_value': 'success',
            'failure_value': 'fail',
            'api_response_key': ['api_response'],
            'reference_key': ['request-id'],
            'provider_name': self.provider_name,
            'token': 'token'
        }

        return await super().virtual_top_up(url=url, body=body, headers=headers, response_mapping=response_mapping)