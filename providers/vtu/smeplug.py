from  models.admin import Provider
from providers.base import BaseProvider, ProviderAuthResponse
from core.cryptography import decrypt_data
from core.error.http import BadRequestError
from models.users import Services


class SmePlug(BaseProvider):

    def __init__(self, provider: Provider):
        self.base_url = provider.base_url
        self.provider_name = provider.name,
        self.token_or_api_key = decrypt_data(provider.credentials.get("token_or_api_key"))

    async def authenticate(self, credentials):

        if not credentials.get('token_or_api_key'):
            raise BadRequestError('api_key is required')

        return super().authenticate(credentials)

    async def virtual_top_up(self, **kwarg):

        service, payload = kwarg.get('service'), dict(kwarg.get('payload'))
    
        beneficiary = payload.get("beneficiary")
        biller_id = payload.get("biller_id")
        plan_id = payload.get("plan_id")
        amount = payload.get("amount")
        reference = payload.get("reference")

        headers = {'Authorization': "Bearer " + self.token_or_api_key}

        if service == Services.AIRTIME:

            url = self.base_url + "/api/v1/airtime/purchase"

            body = {
                'network_id': int(biller_id),
                'amount': float(amount),
                'phone': beneficiary,
                'customer_reference': reference
            }

        if service == Services.DATA:

            url = f'{self.base_url}/api/v1/data/purchase'

            body = {
                'network_id': int(biller_id),
                'plan_id': int(plan_id),
                'phone': beneficiary,
                'customer_reference': reference
            }

        response_mapping = {
            'status_key': 'status',
            'success_value': True,
            'failure_value': False,
            'api_response_key': ['data', 'msg'],
            'reference_key': ['data', 'reference'],
            'provider_name': self.provider_name,
            'token': 'token'
        }

        return await super().virtual_top_up(url=url, body=body, headers=headers, response_mapping=response_mapping)    