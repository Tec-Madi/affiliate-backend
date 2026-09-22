from core.cryptography import decrypt_data
from core.error.http import BadRequestError
from models.admin import Provider
from models.users import Services
from providers.base import BaseProvider

class Ogdams(BaseProvider):

    def __init__(self, provider: Provider):
        self.base_url = provider.base_url
        self.token_or_api_key = decrypt_data(provider.credentials.get("token_or_api_key"))
        self.provider_name = provider.name

    async def authenticate(self, credentials):
        
        if not credentials.get('token_or_api_key'):
            raise BadRequestError('api_key is required')
        
        return super().authenticate(credentials)

    async def virtual_top_up(self, **kwarg):

        service, payload = kwarg.get("service"), dict(kwarg.get("payload"))

        beneficiary = payload.get("beneficiary")
        biller_id = payload.get("biller_id")
        plan_id = payload.get("plan_id")
        amount = payload.get("amount")
        reference = payload.get("reference")

        headers = {'Authorization': "Bearer " + self.token_or_api_key}

        if service == Services.AIRTIME:

            url = self.base_url + "/api/v1/vend/airtime"

            body = {
                'networkId': int(biller_id),
                'amount': amount,
                'phoneNumber': beneficiary,
                'type': 'vtu',
                'reference': reference
            }

        elif service == Services.DATA:

            url = self.base_url + "/api/v1/vend/data"

            body = {
                'networkId': int(biller_id),
                'planId': int(plan_id),
                'phoneNumber': beneficiary,
                'reference': reference
            }

        elif service == Services.CABLE:
            pass

        elif service == Services.DISCO:
            pass

        response_mapping = {
            'status_key': 'status',
            'success_value': True,
            'failure_value': False,
            'api_response_key': ['data', 'msg'],
            'reference_key': ['data', 'ref'],
            'provider_name': self.provider_name,
            'token': 'token'
        }

        return await super().virtual_top_up(url=url, body=body, headers=headers, response_mapping=response_mapping)