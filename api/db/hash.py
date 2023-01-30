import hashlib
import base64
import uuid

class Hash:

    salt = 'dd211c31dd2abf6875ce5bb570cc71e9523386757d255a4f5155d'

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