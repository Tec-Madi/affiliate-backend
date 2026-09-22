import httpx

from core.error.http import BadGateWayError

class ResendEmail:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def send_otp_email(self, name: str, email: str, otp: str):
    
        base_url = 'https://api.resend.com/emails'

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'my-app/1.0'
        }

        payload = {
            "from": "noreply@mail.madisync.com",
            "to": [email],
            "subject": " Madisync Password Reset OTP",
            "html": f"""
            <h2>Password Reset Request</h2>

            <p>Hello {name},</p>

            <p>Your password reset code is:</p>

            <div style="
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 5px;
                padding: 20px;
                background: #f4f4f4;
                text-align: center;
                border-radius: 8px;
            ">
                {otp}
            </div>

            <p>This code expires in 5 minutes.</p>

            <p>If you did not request a password reset, please ignore this email.</p>
            """
        }
    
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(base_url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise BadGateWayError(f'failed to send email: {str(e)}')
        