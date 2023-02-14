import requests

from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

BASE_URL = os.getenv('BASE_URL')

def user_exist_check(token, db):
    
    header = {
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(f'{BASE_URL}/user/info', headers=header)

    if resp.status_code != 200:
        pass

def send_phonenumber(numberphone):
    
    resp = requests.post(f'{BASE_URL}/auth/phonenumber/request', json={'data':numberphone})

    if resp.status_code == 200:
        return resp.json()['access_token'], 200
    
    internal_code = 0
    if 'internal_code' in resp.json():
        internal_code = resp.json()['internal_code']

    return internal_code, resp.status_code

def send_auth_code(auth_code, token):
    
    header = {
        "Authorization": f"Bearer {token}"
    }
    data ={
        'auth_code': auth_code
    }
    resp = requests.post(f'{BASE_URL}/auth/phonenumber/confirmation', json=data ,headers=header)

    if resp.status_code == 200:
        return resp.json()['access_token'], 200
    
    internal_code = 0
    if 'internal_code' in resp.json():
        internal_code = resp.json()['internal_code']

    return internal_code, resp.status_code

def send_data_for_register(data, token):
  
    """
        data >>
            "tel_id": 0,
            "phone_number": "string",
            "password": "string",
            "referal_link": "string",
            "name": "string",
            "lastname": "string"
    """

    header = {
        "Authorization": f"Bearer {token}"
    }
    
    resp = requests.post(f'{BASE_URL}/auth/phonenumber/register', json=data ,headers=header)
    if resp.status_code == 200:
        return resp.json()['access_token'], 200
    
    internal_code = 0
    if 'internal_code' in resp.json():
        internal_code = resp.json()['internal_code']

    return internal_code, resp.status_code

def send_data_for_login(phonenumber, password):
    
    data = {
        'username': phonenumber,
        'password': password
    }

    resp = requests.post(f'{BASE_URL}/auth/phonenumber/login', json=data )
    if resp.status_code == 200:
        return resp.json()['access_token'], 200
    
    internal_code = 0
    if 'internal_code' in resp.json():
        internal_code = resp.json()['internal_code']

    return internal_code, resp.status_code
