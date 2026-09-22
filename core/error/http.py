from core.error.base import AppError

class InternalServerError(AppError):
    def __init__(self, message, code='INTERNAL_SERVER_ERROR'):
        super().__init__(message=message, status_code=500, code=code)

class NotFoundError(AppError):
    def __init__(self, message, code='NOT_FOUND'):
        super().__init__(message=message, status_code=404, code=code)

class BadRequestError(AppError):
    def __init__(self, message, code='BAD_REQUEST'):
        super().__init__(message=message, status_code=400, code=code)

class UnauthourizedError(AppError):
    def __init__(self, message, code='UNAUTHORIZED'):
        super().__init__(message=message, status_code=401, code=code)

class ForbiddenError(AppError):
    def __init__(self, message, code='FORBIDDEN'):
        super().__init__(message=message, status_code=403, code=code)

class UnprocessibleEntityError(AppError):
    def __init__(self, message, code = 'UNPROCESSIBLE'):
        super().__init__(message=message, status_code=422, code=code)

class BadGateWayError(AppError):
    def __init__(self, message, code = 'BAD_GATE_WAY'):
        super().__init__(message=message, status_code=502, code=code)

class AdminOnlyError(AppError):
    def __init__(self, message='Only admin can access this page', status_code = 403, code = 'FORBIDDEN'):
        super().__init__(message=message, status_code=status_code, code=code)

class InsufficientBalanceError(AppError):
    def __init__(self, message='Insufficient balance', status_code = 400, code = 'BALANCE_ERROR'):
        super().__init__(message=message, status_code=status_code, code=code)

class InconsistenceBalanceError(AppError):
    def __init__(self, message='Inconsistence balance', status_code = 400, code = 'BALANCE_ERROR'):
        super().__init__(message=message, status_code=status_code, code=code)

class APIRequestError(BadGateWayError):
    def __init__(self, message="Failed to communicate with External API", code='BAD_GATE_WAY'):
        super().__init__(message, code)