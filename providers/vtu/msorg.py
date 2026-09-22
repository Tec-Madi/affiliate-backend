from core.cryptography import decrypt_data
from core.error.http import BadRequestError
from models.admin import Provider
from models.users import Services
from providers.base import BaseProvider

class MsorgProvider(BaseProvider):
    def __init__(self, provider: Provider):
        self.base_url = provider.base_url
        self.provider_name = provider.name
        self.token_or_api_key = decrypt_data(provider.credentials.get("token_or_api_key"))

    async def authenticate(self, credentials: dict):

        if not credentials.get('token_or_api_key'):
            raise BadRequestError('api_key is required')

        return super().authenticate(credentials)

    async def virtual_top_up(self, **kwarg):

        service, payload = kwarg.get("service"), dict(kwarg.get("payload"))

        headers = {'Authorization': "Token " + self.token_or_api_key}

        beneficiary = payload.get("beneficiary")
        biller_id = payload.get("biller_id")
        plan_id = payload.get("plan_id")
        amount = payload.get("amount")

        if service == Services.AIRTIME.value:

            url = f'{self.base_url}/api/topup/'

            body = {
                'network': int(biller_id),
                'amount': amount,
                'mobile_number': beneficiary,
                'Ported_number': True,
                'airtime_type': 'VTU'
            }

        elif service == Services.DATA.value:

            url = f"{self.base_url}/api/data/"

            body = {
                'network': int(biller_id),
                'mobile_number': beneficiary,
                'plan': int(plan_id),
                'Ported_number': True
            }

        elif service == Services.CABLE.value:

            url = f"{self.base_url}/api/cablesub/"

            body = {
                'cablename': biller_id,
                'cableplan': int(plan_id),
                'smart_card_number': beneficiary
            }

        elif service == Services.DISCO.value:

            url = f'{self.base_url}/api/billpayment/'

            payload = {
                'disco_name': biller_id,
                'amount': amount,
                'meter_number': beneficiary,
                'meter_type': plan_id
            }

        response_mapping = {
            'status_key': ['Status'],
            'success_value': 'successful',
            'failure_value': 'failed',
            'api_response_key': ['api_response'],
            'reference_key': ['ident'],
            'provider_name': self.provider_name,
            'token': 'token'
        }

        return await super().virtual_top_up(url=url, body=body, headers=headers, response_mapping=response_mapping)