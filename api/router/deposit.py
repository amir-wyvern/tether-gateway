
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
    UserBase,
    UserDisplay,
    UserRegister,
    UserUpdateProfile,
    UpdatePassword,
    HTTPError,
    BaseResponse,
    RequestDeposit,
    ConfirmationDeposit,
    RequestDepositResponse
)

from db import db_request_deposit, db_user
from db.database import get_db
from db.hash import Hash

from celery_tasks.tasks import DepositCeleryTask #, DivisionCeleryTask
from celery_tasks.utils import create_worker_from


router_telegram = APIRouter(prefix='/deposit', tags=['Telegram Users', 'Deposit'])

_, deposit_worker = create_worker_from(DepositCeleryTask)


@router_telegram.post('/request/{tel_id}', response_model=RequestDepositResponse, responses={403:{'model':HTTPError}})
def _request_deposit(tel_id: int, user: RequestDeposit, db=Depends(get_db)):

    data = db_user.get_user_by_telegram_id(tel_id, db)
    if data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    resp = db_request_deposit.create_request(user, db)
    
    if resp == True:
        JSONResponse(status_code=200, content={'request_id': resp.request_id ,'message':'Deposit request registered'})

    else:
        raise HTTPException(status_code=403, detail={'internal_code':1003, 'message':'There was a problem in registering the deposit request'})


@router_telegram.post('/confirmation/{tel_id}', response_model=BaseResponse, responses={404:{'model':HTTPError}})
def _comfirmation_deposit(tel_id: int, user: ConfirmationDeposit, db=Depends(get_db)):

    data = db_user.get_user_by_telegram_id(tel_id, db)
    if data is None:
        raise HTTPException(status_code=404, detail={'internal_code':1004, 'message':'The user not found'})

    # send request to celery >> 

    payload = {
        'user_id': data.user_id,
        'tx_hash': data.tx_hash
    }

    deposit_worker.apply_async(args=(payload, )) 



    # resp = db_request_deposit.create_request(user, db)
    # if resp and resp.request_id:
    #     JSONResponse(status_code=200, content={'message':'Deposit request registered'})

    # else:
    #     raise HTTPException(status_code=403, detail={'internal_code':1003, 'message':'There was a problem in registering the deposit request'})

