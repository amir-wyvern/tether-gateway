from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from schemas import (
    UserRegisterByEmail,
    UserRegisterByPhoneNumber,
    HTTPError,
    UserAuthConfirmation,
    AuthEmailRequest,
    AuthPhoneNumberRequest,
    UserAuthResponse,
    UserAuthResponse,
    UserAuthDecode
)
from db import db_user
from db.database import get_db 
from auth.oauth2 import ( 
    get_register_token_by_user_phonenumber,
    get_auth_by_user_email,
    get_auth_by_user_phonenumber,
    get_register_token_by_user_email,
    create_access_token
)

from random import randint
from cache.database import get_redis_cache
from cache.cache_session import (
    create_auth_session,
    get_auth_code_by_session
)
from datetime import timedelta
from db.hash import Hash

router = APIRouter(prefix='/auth')


@router.post('/phonenumber/login', response_model=UserAuthResponse, responses={401:{'model':HTTPError}}, tags=["Login-PhoneNumber"])
def user_login(request: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):

    phone_number = request.username
    data = db_user.get_user_by_phone_number(phone_number, db)

    if data is None :
        raise HTTPException(status_code=401, detail={'internal_code':1009, 'message':'The phone number or password is incorrect'})

    if Hash.verify(data.password, request.password) == False:
        raise HTTPException(status_code=401, detail={'internal_code':1009, 'message':'The phone number or password is incorrect'})

    access_token = create_access_token(data={'user_id': data.user_id})

    resp = {
        'access_token': access_token,
        'type_token': 'bearer',
    }

    return UserAuthResponse(**resp)


@router.post('/phonenumber/request', response_model=UserAuthResponse, responses={403:{'model':HTTPError}}, tags=["Register-PhoneNumber"])
def phonenumber_auth_request(request: AuthPhoneNumberRequest, db: Session=Depends(get_db), db_cache= Depends(get_redis_cache)):


    data_user = db_user.get_user_by_phone_number(request.data, db) 
    
    if data_user is not None :
        raise HTTPException(status_code=403, detail={'internal_code':1005, 'message':'The user already exists!'})

    access_token = create_access_token(data={'data':request.data, 'scope':'auth:phonenumber:confirmation'}, expires_delta= timedelta(seconds=120))
    generated_code = randint(100_000, 999_999)
    
    print(generated_code)

    create_auth_session(access_token, generated_code, db_cache)
    resp = {
        'access_token': access_token,
        'type_token': 'bearer'
    }

    return UserAuthResponse(**resp)


@router.post('/phonenumber/confirmation', response_model=UserAuthResponse, responses={401:{'model':HTTPError}}, tags=["Register-PhoneNumber"])
def phonenumber_auth_confirmation(request: UserAuthConfirmation ,token_info: UserAuthDecode=Depends(get_auth_by_user_phonenumber), db_cache= Depends(get_redis_cache)):

    user_auth_code = request.auth_code
    auth_code = int( get_auth_code_by_session(token_info.token, db_cache) )
    
    if auth_code != user_auth_code :
        raise HTTPException(status_code=401, detail={'internal_code':1012, 'message':'The verification code is wrong'})

    access_token = create_access_token(data={'data':token_info.data, 'scope':'auth:phonenumber:register'}, expires_delta= timedelta(seconds=600))


    resp = {
        'access_token': access_token,
        'type_token': 'bearer'
    }

    return UserAuthResponse(**resp)


@router.post('/phonenumber/register', response_model=UserAuthResponse, responses={403:{'model':HTTPError}}, tags=["Register-PhoneNumber"])
def user_register_by_phonenumber(user: UserRegisterByPhoneNumber, token_info: UserAuthDecode=Depends(get_register_token_by_user_phonenumber), db: Session=Depends(get_db)):

    if user.phone_number != token_info.data:
        raise HTTPException(status_code=401, detail={'internal_code':1013, 'message':'The phone number has not been verified'})

    data = db_user.check_exist_user(['email', 'tel_id', 'phone_number'] ,user, db) 

    if data is not None and data.tel_id == user.tel_id:
        raise HTTPException(status_code=403, detail={'internal_code':1005, 'message':'The user already exists!'})

    if data is not None and data.phone_number == user.phone_number:
        raise HTTPException(status_code=403, detail={'internal_code':1006, 'message':'The phone number already exists!'})

    if data is not None and data.email == user.email:
        raise HTTPException(status_code=403, detail={'internal_code':1007, 'message':'The email already exists!'})

    if user.referal_link is not None:

        resp = db_user.get_user_by_referal_link(user.referal_link, db)

        if resp is None:
            raise HTTPException(status_code=403, detail={'internal_code':1008, 'message':'The referal link not exists!'})
        
        db_user.increase_number_of_invited(resp.user_id, db)

    new_user_data = db_user.create_user(user, db)
    
    if new_user_data is None:
        raise HTTPException(status_code=403, detail={'internal_code':1010, 'message':'There was a problem in registering!'})
    
    access_token = create_access_token(data={'user_id': new_user_data.user_id})

    resp = {
        'access_token': access_token,
        'type_token': 'bearer'
    }

    return UserAuthResponse(**resp)



@router.post('/email/login', response_model=UserAuthResponse, responses={401:{'model':HTTPError}}, tags=["Login-Email"])
def user_login(request: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):

    email = request.username
    data = db_user.get_user_by_email(email, db)

    if data is None :
        raise HTTPException(status_code=401, detail={'internal_code':1015, 'message':'The email or password is incorrect'})

    if Hash.verify(data.password, request.password) == False:
        raise HTTPException(status_code=401, detail={'internal_code':1015, 'message':'The email or password is incorrect'})

    access_token = create_access_token(data={'user_id': data.user_id})

    resp = {
        'access_token': access_token,
        'type_token': 'bearer',
    }

    return UserAuthResponse(**resp)


@router.post('/email/request', response_model=UserAuthResponse, responses={403:{'model':HTTPError}}, tags=["Register-Email"])
def email_auth_request(request: AuthEmailRequest, db: Session=Depends(get_db), db_cache= Depends(get_redis_cache)):

    data_user = db_user.get_user_by_email(request.data, db) 

    if data_user is not None:
        raise HTTPException(status_code=403, detail={'internal_code':1005, 'message':'The user already exists!'})

    access_token = create_access_token(data={'data':request.data, 'scope':'auth:email:confirmation'}, expires_delta= timedelta(seconds=120))
    generated_code = randint(100_000, 999_999)
    
    print(generated_code)

    create_auth_session(access_token, generated_code, db_cache)
    resp = {
        'access_token': access_token,
        'type_token': 'bearer'
    }

    return UserAuthResponse(**resp)


@router.post('/email/confirmation', response_model=UserAuthResponse, responses={401:{'model':HTTPError}}, tags=["Register-Email"])
def email_auth_confirmation(request: UserAuthConfirmation ,token_info: UserAuthDecode=Depends(get_auth_by_user_email), db_cache= Depends(get_redis_cache)):

    user_auth_code = request.auth_code
    auth_code = int( get_auth_code_by_session(token_info.token, db_cache) )
    
    if auth_code != user_auth_code :
        raise HTTPException(status_code=401, detail={'internal_code':1012, 'message':'The verification code is wrong'})

    access_token = create_access_token(data={'data':token_info.data, 'scope':'auth:email:register'}, expires_delta= timedelta(seconds=600))


    resp = {
        'access_token': access_token,
        'type_token': 'bearer'
    }


    return UserAuthResponse(**resp)


@router.post('/email/register', response_model=UserAuthResponse, responses={403:{'model':HTTPError}}, tags=["Register-Email"])
def user_register_by_email(user: UserRegisterByEmail, token_info: UserAuthDecode=Depends(get_register_token_by_user_email), db: Session=Depends(get_db)):

    if user.phone_number != token_info.data:
        raise HTTPException(status_code=401, detail={'internal_code':1014, 'message':'The email has not been verified'})

    old_user = db_user.check_exist_user(['email', 'tel_id', 'phone_number'] ,user, db) 

    if old_user is not None and old_user.tel_id == user.tel_id:
        raise HTTPException(status_code=403, detail={'internal_code':1005, 'message':'The user already exists!'})

    if old_user is not None and old_user.phone_number == user.phone_number:
        raise HTTPException(status_code=403, detail={'internal_code':1006, 'message':'The phone number already exists!'})

    if old_user is not None and old_user.email == user.email:
        raise HTTPException(status_code=403, detail={'internal_code':1007, 'message':'The email already exists!'})

    if user.referal_link is not None:

        resp = db_user.get_user_by_referal_link(user.referal_link, db)

        if resp is None:
            raise HTTPException(status_code=403, detail={'internal_code':1008, 'message':'The referal link is invalid'})
        
        db_user.increase_number_of_invited(resp.user_id, db)

    new_user_data = db_user.create_user(user, db)
    
    if new_user_data is None:
        raise HTTPException(status_code=403, detail={'internal_code':1010, 'message':'There was a problem in registering!'})
    
    access_token = create_access_token(data={'user_id': new_user_data.user_id, 'scope':'user'})

    resp = {
        'access_token': access_token,
        'type_token': 'bearer'
    }

    return UserAuthResponse(**resp)

