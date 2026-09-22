from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.handlers import app_error_handler, mimick_error_handler
from core.error.base import AppError, MimickError

from api.v1.private_api.routers.home import home_router

from api.v1.private_api.routers.auth import auth_router

from api.v1.private_api.routers.user.dashboard import dashboard_router
from api.v1.private_api.routers.user.message import messages_router
from api.v1.private_api.routers.user.support import support_router
from api.v1.private_api.routers.user.settings import user_settings_router
from api.v1.private_api.routers.user.purchases import vtu_purchase_router
from api.v1.private_api.routers.user.transactions import user_transaction_router
from api.v1.private_api.routers.user.plans import plans_router

from api.v1.private_api.routers.admin.overview import admin_overview_router
from api.v1.private_api.routers.admin.info import admin_system_info_router
from api.v1.private_api.routers.admin.users import admin_user_router
from api.v1.private_api.routers.admin.transactions import admin_transaction_router
from api.v1.private_api.routers.admin.providers import admin_provider_router
from api.v1.private_api.routers.admin.plans import admin_plan_router, admin_biller_router, admin_pgw_plan_router

from api.v1.private_api.routers.webhook import webhook_router
from api.v1.public_api.routers import user_api_purchase, api_mimick_router


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

origins = [
    "https://aishorasub.com",
    "https://www.aishorasub.com",
    "https://hzquicklink.com",
    "https://www.hzquicklink.com",
    "https://meeralinks.com",
    "https://www.meeralinks.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#<---------- ERROR ---------->
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(MimickError, mimick_error_handler)

####################################################
#################### PRIVATE API ####################
####################################################

#<---------- HOME ---------->
app.include_router(home_router, prefix='/api/v1')
#<---------- AUTH ---------->
app.include_router(auth_router, prefix='/api/v1')
#<---------- USER ---------->
app.include_router(dashboard_router, prefix='/api/v1')
app.include_router(messages_router, prefix='/api/v1')
app.include_router(support_router, prefix='/api/v1')
app.include_router(user_settings_router, prefix='/api/v1')
app.include_router(vtu_purchase_router, prefix="/api/v1")
app.include_router(user_transaction_router, prefix='/api/v1')
app.include_router(plans_router, prefix="/api/v1")

#<---------- ADMIN ---------->
app.include_router(admin_overview_router, prefix='/api/v1')
app.include_router(admin_system_info_router, prefix='/api/v1')
app.include_router(admin_user_router, prefix='/api/v1')
app.include_router(admin_transaction_router, prefix='/api/v1')
app.include_router(admin_provider_router, prefix='/api/v1')
app.include_router(admin_pgw_plan_router, prefix='/api/v1')
app.include_router(admin_biller_router, prefix="/api/v1")
app.include_router(admin_plan_router, prefix="/api/v1")

#<---------- WEBHOOK --------->
app.include_router(webhook_router, prefix='/webook')

####################################################
#################### PUBLIC API ####################
####################################################

#<--------- API PURCHASE -------->
app.include_router(user_api_purchase, prefix='/v1')

app.include_router(api_mimick_router)