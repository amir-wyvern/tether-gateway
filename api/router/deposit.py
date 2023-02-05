from fastapi.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from schemas import (
    HTTPError,
    BaseResponse,
    DepositRequest,
    DepositConfirmation,
    DepositRequestResponse,
    DepositHistoryResponse,
    DepositHistoryRequest
)

from db import db_deposit_request
from db.database import get_db

from celery_tasks.tasks import DepositCeleryTask 
from celery_tasks.utils import create_worker_from
from sqlalchemy.orm.session import Session
from auth.oauth2 import ( 
    get_current_user
)


router = APIRouter(prefix='/deposit', tags=['Deposit'])

_, deposit_worker = create_worker_from(DepositCeleryTask)

@router.post('/request', response_model=DepositRequestResponse, responses={403:{'model':HTTPError}})
def deposit_request(request: DepositRequest, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    resp = db_deposit_request.create_request(user_id, request, db)

    if resp:
        return JSONResponse(status_code=200, content={'request_id': resp.request_id ,'message':'Deposit request registered'})

    # else:
    #     raise HTTPException(status_code=403, detail={'internal_code':1003, 'message':'There was a problem in registering the deposit request'})


@router.post('/confirmation', response_model=BaseResponse, responses={404:{'model':HTTPError}})
def deposit_comfirmation(request: DepositConfirmation, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    # send request to celery >> 

    payload = {
        'user_id': user_id,
        'tx_hash': request.tx_hash
    }

    deposit_worker.apply_async(args=(payload, )) 

    return JSONResponse(status_code=200, content={'message':'the request is proccessing'})


@router.get('/history', response_model=DepositHistoryResponse, responses={404:{'model':HTTPError}})
def deposit_comfirmation(offset: int, count: int, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    return JSONResponse(status_code=200, content={'txs':[] })

