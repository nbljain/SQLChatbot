import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Use a hardcoded salt - in production, this would be stored securely
# or use environment variables
SALT = b'sqlchatbot_salt_value_for_encryption'

def get_key():
    """Generate an encryption key from a password for Fernet encryption"""
    # In production, this should be stored as an environment variable
    app_secret = os.environ.get('APP_SECRET', 'default_app_secret_for_sqlchatbot')
    password = app_secret.encode()  # Convert to bytes
    
    # Key derivation function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    
    # Generate the key from the password
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_value(text):
    """Encrypt a string value"""
    if not text:
        return ""
    
    key = get_key()
    fernet = Fernet(key)
    return fernet.encrypt(text.encode()).decode()

def decrypt_value(encrypted_text):
    """Decrypt an encrypted string value"""
    if not encrypted_text:
        return ""
    
    key = get_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text.encode()).decode()