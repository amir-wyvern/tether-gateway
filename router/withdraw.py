from fastapi.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from schemas import (
    HTTPError,
    BaseResponse,
    WithdrawRequest,
    WithdrawConfirmation,
    WithdrawRequestResponse,
    WithdrawtHistoryResponse,
    WithdrawHistoryRequest
)

from db import db_withdraw_request
from db.database import get_db

from celery_tasks.tasks import WithdrawCeleryTask 
from celery_tasks.utils import create_worker_from
from sqlalchemy.orm.session import Session
from auth.oauth2 import ( 
    get_current_user
)


router = APIRouter(prefix='/withdraw', tags=['Withdraw'])

_, withdraw_worker = create_worker_from(WithdrawCeleryTask)

@router.post('/request', response_model=WithdrawRequestResponse, responses={403:{'model':HTTPError}})
def withdraw_request(request: WithdrawRequest, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    resp = db_withdraw_request.create_request(user_id, request, db)

    if resp:
        return JSONResponse(status_code=200, content={'request_id': resp.request_id ,'message':'Deposit request registered'})

    else:
        raise HTTPException(status_code=403, detail={'internal_code':1003, 'message':'There was a problem in registering the deposit request'})


@router.post('/confirmation', response_model=BaseResponse, responses={404:{'model':HTTPError}})
def withdraw_comfirmation(request: WithdrawConfirmation, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    # send request to celery >> 

    # payload = {
    #     'user_id': user_id,
    #     'auth_code': request.auth_code
    # }

    # withdraw_worker.apply_async(args=(payload, )) 

    return JSONResponse(status_code=200, content={'message':'the request is proccessing'})


@router.get('/history', response_model=WithdrawtHistoryResponse, responses={404:{'model':HTTPError}})
def withdraw_comfirmation(offset: int, count: int, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    return JSONResponse(status_code=200, content={'txs':[] })

