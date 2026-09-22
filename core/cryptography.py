import bcrypt
from cryptography.fernet import Fernet

from core.config import ENCRYPTION_SECRET_KEY

def hash_data(data: str):
    hashed = bcrypt.hashpw(data.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_hashed_data(data: str, hashed_data: str):
    return bcrypt.checkpw(data.encode('utf-8'), hashed_data.encode('utf-8'))

cipher = Fernet(ENCRYPTION_SECRET_KEY)

def encrypt_data(data: str | None):
    if data:
        encrypted = cipher.encrypt(data.encode('utf-8'))
        return encrypted.decode('utf-8')
    else:
        return None

def decrypt_data(encrypted_data: str | None):
    if encrypted_data:
        return cipher.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
    else:
        return None