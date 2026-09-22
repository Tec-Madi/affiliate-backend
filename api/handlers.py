from fastapi import Request
from fastapi.responses import JSONResponse
from core.error.base import AppError, MimickError
from models.admin import ProviderType

async def app_error_handler(request: Request, exc: AppError):

    respnse = JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "code": exc.code
        }
    )

    if respnse.status_code in (401, 403):
        respnse.delete_cookie(
            key='access_token',
            httponly=True,
            secure=True,
            samesite='lax'
        )

    return respnse

async def mimick_error_handler(_: Request, exc: MimickError):

    error_map = {
        ProviderType.ADEX: JSONResponse(
            status_code=exc.status_code,
            content={
                'status': 'fail',
                'message': exc.message
            }
        ),
        ProviderType.MSORG: JSONResponse(
            status_code=exc.status_code,
            content={
                'error': [exc.message]
            }
        )
    }

    return error_map.get(exc.provider)