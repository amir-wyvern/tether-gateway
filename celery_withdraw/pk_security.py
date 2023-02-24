from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from hashlib import md5
import base64

def base_cryption(password: str, salt: str) -> str:

    salt = salt.encode() 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    
    return base64.urlsafe_b64encode(kdf.derive(password.encode())) 


def decrypt_private_key(encoded_private_key: str, password: str, salt: str) -> str:

    key = base_cryption(password, salt)
    decoded_private_key = Fernet(key).decrypt(encoded_private_key.encode()).decode()
    return decoded_private_key


def encrypt_private_key(raw_private_key: str, password: str, salt: str):

    key = base_cryption(password, salt)
    encrypted_private_key = Fernet(key).encrypt(raw_private_key.encode()).decode()
    return encrypted_private_key