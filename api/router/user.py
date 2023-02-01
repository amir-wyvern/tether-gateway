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
    UserDisplay,
    UserRegister,
    UserUpdateProfile,
    UpdatePassword,
    HTTPError,
    BaseResponse
)

from db import db_user
from db.database import get_db
from db.hash import Hash

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/info/{user_id}', response_model=UserDisplay, responses={404:{'model':HTTPError}})
def user_info(user_id: int, db=Depends(get_db)):
    data = db_user.get_user(user_id, db)
    if data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    return data


@router.post('/register', response_model=UserDisplay, responses={403:{'model':HTTPError}})
def user_register(user: UserRegister, db=Depends(get_db)):

    data = db_user.check_exist_user(['email', 'tel_id', 'phone_number'] ,user, db) 

    if data is not None and data.tel_id == user.tel_id:
        raise HTTPException(status_code=403, detail={'internal_code':1005, 'message':'The user already exists!'})

    if data is not None and data.phone_number == user.phone_number:
        raise HTTPException(status_code=403, detail={'internal_code':1006, 'message':'The phone number already exists!'})

    if data is not None and data.email == user.email:
        raise HTTPException(status_code=403, detail={'internal_code':1007, 'message':'The email already exists!'})

    return db_user.create_user(user, db)


@router.post('/update/{user_id}', response_model=BaseResponse, responses={404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def update_user_profile(user_id:int, user: UserUpdateProfile, db=Depends(get_db)):

    old_data = db_user.get_user(user_id, db)

    if old_data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    data = db_user.check_exist_user(['email', 'phone_number'], user, db) 

    if data and user_id != data.user_id and data.phone_number == user.phone_number: 
        raise HTTPException(status_code=403, detail={'internal_code':1006, 'message':'The phone number already exists!'})

    if data and user_id != data.user_id and data.email == user.email:
        raise HTTPException(status_code=403, detail={'internal_code':1007, 'message':'The email already exists!'})

    resp = db_user.update_user_profile(user_id, user, db)

    if resp == True:
        return JSONResponse(status_code=200, content={'message':'The user profile updated'})

    else :
        raise HTTPException(status_code=403, detail={'internal_code':1002 ,'message':'It is not possible to edit the information'})
    

@router.post('/pass/{user_id}', response_model=BaseResponse, responses={404:{'model':HTTPError}, 403:{'model':HTTPError}})
def update_user_password(user_id:int, user: UpdatePassword, db=Depends(get_db)):

    data = db_user.get_user(tel_id, db)
    if data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    if Hash.verify(data.password, user.old_password):

        db_user.update_password(user_id, user, db)
        return JSONResponse(status_code=200, content={'message':'The user password updated'})
    
    else:
        raise HTTPException(status_code=403, detail={'internal_code':1001, 'message':'The password is wrong'})


@router.post('/test/')
def update_user_password(user: UserRegister, db=Depends(get_db)):

    # attrs = {UserRegister.email:user.email, UserRegister.phone_number:user.phone_number}
    x = db_user.check_exist_user(user, db)
    print(x[0].email )
# # delete user
# @router.get('/delete/{tel_id}')
# def delete_user(tel_id:int, db=Depends(get_db)):
#     return db_user.delete_user(tel_id, db)
