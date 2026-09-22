from models.admin import ProviderType

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500, code: str = None):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message, status_code, code)

class MimickError(Exception):
    def __init__(self, provider: ProviderType, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        self.provider = provider
        super().__init__(message, status_code)