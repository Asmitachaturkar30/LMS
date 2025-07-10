# utils/encryption.py
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class DataEncryptor:
    @staticmethod
    def generate_key_from_password(password: str, salt: bytes) -> bytes:
        """Generate encryption key from password (store password in env vars)"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt_data(data: str) -> str:
        """Encrypt string data before storage"""
        if not data:
            return data
            
        try:
            f = Fernet(settings.ENCRYPTION_KEY)
            encrypted_data = f.encrypt(data.encode())
            return encrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise ValueError("Data encryption failed")

    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Decrypt string data after retrieval"""
        if not encrypted_data:
            return encrypted_data
            
        try:
            f = Fernet(settings.ENCRYPTION_KEY)
            decrypted_data = f.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise ValueError("Data decryption failed")