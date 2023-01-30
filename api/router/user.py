from fastapi import (
    APIRouter,
    Query,
    Body,
    Path,
    Depends,
    status,
    HTTPException
)

from fastapi.responses import JSONResponse

from pydantic import BaseModel
from typing import Optional, List, Dict
from schemas import (
    BotUserBase,
    UserDisplay,
    BotUserRegister,
    BotUserUpdateProfile,
    BotUpdatePassword,
    HTTPError,
    BaseResponse
)

from db import db_user
from db.database import get_db
from db.hash import Hash

router_telegram = APIRouter(prefix='/bot/user', tags=['Telegram Users'])


@router_telegram.get('/info/{tel_id}', response_model=UserDisplay, responses={404:{'model':HTTPError}})
def bot_user_info(tel_id: int, db=Depends(get_db)):
    data = db_user.get_user_by_telegram_id(tel_id, db)
    if data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    return data


@router_telegram.post('/register', response_model=UserDisplay, responses={403:{'model':HTTPError}})
def bot_user_register(user: BotUserRegister, db=Depends(get_db)):

    data = db_user.get_user_by_telegram_id(user.tel_id, db)

    if data is not None:
        raise HTTPException(status_code=403, detail={'internal_code':1005, 'message':'The user already exists!'})

    data = db_user.get_user_by_phone_number(user.phone_number, db)

    if data is not None:
        raise HTTPException(status_code=403, detail={'internal_code':1006, 'message':'The phone number already exists!'})

    data = db_user.get_user_by_email(user.email, db)

    if data is not None:
        raise HTTPException(status_code=403, detail={'internal_code':1007, 'message':'The email already exists!'})

    return db_user.create_user(user, db)


@router_telegram.post('/update/{tel_id}', response_model=BaseResponse, responses={404:{'model':HTTPError}} )
def bot_update_user_profile(tel_id:int, user: BotUserUpdateProfile, db=Depends(get_db)):

    old_data = db_user.get_user_by_telegram_id(tel_id, db)

    if old_data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    data = db_user.get_user_by_phone_number(user.phone_number, db)

    if data and data.user_id != old_data.user_id:
        raise HTTPException(status_code=403, detail={'internal_code':1006, 'message':'The phone number already exists!'})

    data = db_user.get_user_by_email(user.email, db)

    if data and data.user_id != old_data.user_id:
        raise HTTPException(status_code=403, detail={'internal_code':1007, 'message':'The email already exists!'})

    resp = db_user.update_user_profile(old_data.user_id, user, db)

    if resp == True:
        return JSONResponse(status_code=200, content={'message':'The user profile updated'})

    else :
        raise HTTPException(status_code=403, detail={'internal_code':1002 ,'message':'It is not possible to edit the information'})
    


@router_telegram.post('/pass/{tel_id}', response_model=BaseResponse, responses={404:{'model':HTTPError}, 403:{'model':HTTPError}})
def bot_update_user_password(tel_id:int, user: BotUpdatePassword, db=Depends(get_db)):

    data = db_user.get_user_by_telegram_id(tel_id, db)
    if data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    if Hash.verify(data.password, user.old_password):

        db_user.update_password(data.user_id, user, db)
        return JSONResponse(status_code=200, content={'message':'The user password updated'})
    
    else:
        raise HTTPException(status_code=403, detail={'internal_code':1001, 'message':'The password is wrong'})



# # delete user
# @router_telegram.get('/delete/{tel_id}')
# def delete_user(tel_id:int, db=Depends(get_db)):
#     return db_user.delete_user(tel_id, db)
