from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from schemas import (
    UserDisplay,
    UserRegister,
    UserUpdateProfile,
    UpdatePassword,
    HTTPError,
    BaseResponse,
    UserAuthResponse
)
from db import db_user
from db.database import get_db
from db.hash import Hash
from auth.oauth2 import ( 
    get_current_user,
    create_access_token
)

router = APIRouter(prefix='/user', tags=['User'])


@router.get('/info', response_model=UserDisplay, responses={404:{'model':HTTPError}})
def user_info(user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):
    
    return db_user.get_user(user_id, db)


@router.post('/register', response_model=UserAuthResponse, responses={403:{'model':HTTPError}})
def user_register(user: UserRegister, db: Session=Depends(get_db)):

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
        
        db_user.increase_number_of_invented(resp.user_id, db)

    new_user_data = db_user.create_user(user, db)
    
    if new_user_data is None:
        raise HTTPException(status_code=403, detail={'internal_code':1010, 'message':'There was a problem in registering!'})
    
    access_token = create_access_token(data={'sub': new_user_data.user_id})

    resp = {
        'access_token': access_token,
        'type_token': 'bearer'
    }

    return UserAuthResponse(**resp)


@router.post('/login', response_model=UserAuthResponse, responses={401:{'model':HTTPError}})
def user_login(request: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):

    number_phone = request.username
    data = db_user.get_user_by_phone_number(number_phone, db)

    print(number_phone, data.__dict__)
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


@router.post('/update', response_model=BaseResponse, responses={404:{'model':HTTPError}, 403:{'model':HTTPError}} )
def update_user_profile(request: UserUpdateProfile, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    data = db_user.check_exist_user(['email', 'phone_number'], request, db) 

    if data and user_id != data.user_id and data.phone_number == request.phone_number: 
        raise HTTPException(status_code=403, detail={'internal_code':1006, 'message':'The phone number already exists!'})

    if data and user_id != data.user_id and data.email == request.email:
        raise HTTPException(status_code=403, detail={'internal_code':1007, 'message':'The email already exists!'})

    resp = db_user.update_user_profile(user_id, request, db)

    if resp == True:
        return JSONResponse(status_code=200, content={'message':'The user profile updated'})

    else :
        raise HTTPException(status_code=403, detail={'internal_code':1002 ,'message':'It is not possible to edit the information'})
    

@router.post('/pass', response_model=BaseResponse, responses={404:{'model':HTTPError}, 403:{'model':HTTPError}})
def update_user_password(request: UpdatePassword, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    data = db_user.get_user(user_id, db)
    if Hash.verify(data.password, request.old_password):

        db_user.update_password(user_id, request, db)
        return JSONResponse(status_code=200, content={'message':'The user password updated'})
    
    else:
        raise HTTPException(status_code=403, detail={'internal_code':1001, 'message':'The password is wrong'})
