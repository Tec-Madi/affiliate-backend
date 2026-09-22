from core.cryptography import decrypt_data
from core.error.http import BadRequestError
from models.admin import Provider
from providers.base import BaseProvider
from models.users import Services


class MadixProvider(BaseProvider):
    def __init__(self, provider: Provider):
        self.base_url = provider.base_url
        self.provider_name = provider.name
        self.token_or_api_key = decrypt_data(provider.credentials.get("token_or_api_key"))

    def authenticate(self, credentials):
        if not credentials.get("token_or_api_key"):
            raise BadRequestError("API Key is required")
        
        return super().authenticate(credentials)

    def virtual_top_up(self, **kwarg):

        service, payload = kwarg.get("service"), dict(kwarg.get("payload"))

        biller_id = payload.get("biller_id")
        plan_id = payload.get("plan_id")
        plan_type = payload.get("plan_type")
        beneficiary = payload.get("beneficiary")
        request_id = payload.get("request_id")

        headers = {"Authorization": "Token " + self.token_or_api_key}

        if service == Services.AIRTIME:

            url = self.base_url + "/v1/airtime"

            body = {
                "biller_id": biller_id,
                "plan_id": plan_id,
                "beneficiary": beneficiary,
                "request_id": request_id,
            }

        elif service == Services.DATA:

            url = self.base_url + "/v1/data"

            body = {
                "plan_id": plan_id,
                "beneficiary": beneficiary,
                "request_id": request_id
            }   

        elif service == Services.CABLE:

            url = self.base_url + "/v1/cable"

            body = {
                "plan_id": plan_id,
                "beneficiary": beneficiary,
                "request_id": request_id
            }

        elif service == Services.DISCO:

            url = self.base_url + "/v1/disco"

            body = {
                "biller_id": biller_id,
                "plan_id": plan_id,
                "plan_type": plan_type
            }

        response_param = {
            "status_key": ["status"],
            "success_value": "successful",
            "failure_value": "failed",
            "api_response_key": ["api_response"],
            "reference_key": ["reference"],
            "token_key": [""],
            "provider_name": self.provider_name
        }

        return super().virtual_top_up(url=url, body=body, headers=headers, response_param=response_param)