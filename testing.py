from decimal import Decimal

import httpx
from sqlalchemy import select

from core.database import hzquicklink_session, aishorasub_session, meeralinks_session
from models.admin import Provider, ProviderType
from models.users import User

# with meeralinks_session() as db:
#     user = db.execute(select(User).where(User.email == "medtiatetech@gmail.com")).scalar_one_or_none()
#     user.is_admin = True
#     db.commit()

# with aishorasub_session() as db:
#     provider = Provider(id=1, name="ipremierlink", type=ProviderType.MADIX, base_url="https://api.ipremierlink.com")
#     db.add(provider)
#     db.commit()

# with aishorasub_session() as db:
    
#     provider = db.execute(select(Provider).where(Provider.id == 1)).scalar_one_or_none()
#     db.delete(provider)
#     db.commit()

response = httpx.post(
    url = "https://api.ipremierlink.com/v1/airtime", 
    json = {
        "biller_id": 1,
        "plan_type": "VTU",
        "amount": 100,
        "beneficiary": "09169728552"
    },
    headers={"Authorization": "Token sk_EQhamsPdzVoBTN2xGbZnwi1kdTUeVTPia9FHtQTao8I"},
    timeout=120
    )

print(response.json())