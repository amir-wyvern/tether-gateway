import hashlib
import base64
import uuid

import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

SHA_SALT = os.getenv('SHA_SALT')

class Hash:

    salt = SHA_SALT

    @staticmethod
    def sha3_256(password):

        dataBase_password = password + Hash.salt
        hashed_pass = hashlib.sha3_256(dataBase_password.encode()).hexdigest()

        return hashed_pass

    @staticmethod
    def verify(hashed_password, plain_password):

        if hashed_password == Hash.sha3_256(plain_password):
            return True
        
        return False

    @staticmethod
    def generate_referal_link():
        return base64.urlsafe_b64encode(uuid.uuid1().bytes).decode()[:12] 