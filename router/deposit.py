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
    DepositHistoryModelForDataBase,
    DepositHistoryStatus
)

from db import db_main_account, db_deposit_history
from db.database import get_db

from celery_tasks.tasks import DepositCeleryTask 
from celery_tasks.utils import create_worker_from
from sqlalchemy.orm.session import Session
from auth.oauth2 import ( 
    get_current_user
)
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix='/deposit', tags=['Deposit'])

_, deposit_worker = create_worker_from(DepositCeleryTask)

@router.post('/request', response_model=DepositRequestResponse, responses={403:{'model':HTTPError}})
def deposit_request(request: DepositRequest, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    deposit_address = db_main_account.get_deposit_address(db)
    
    request_id = uuid4().hex[:12]
    request_data = {
        'request_id': request_id,
        'tx_hash': None,
        'user_id': user_id,
        'from_address': None,
        'to_address': deposit_address,
        'value': request.value,
        'status': DepositHistoryStatus.WAITING,
        'error_message': None,
        'request_time': datetime.now(),
        'processingـcompletionـtime': None
    }

    resp = db_deposit_history.create_deposit_history(DepositHistoryModelForDataBase(**request_data), db)

    if resp:
        return JSONResponse(status_code=200, content={'request_id': resp.request_id ,'deposit_address': deposit_address})

    else:
        raise HTTPException(status_code=403, detail={'internal_code':1003, 'message':'There was a problem in registering the deposit request'})


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
def deposit_comfirmation(start_time: datetime, end_time: datetime, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    history = db_deposit_history.get_deposit_history_by_time(user_id, start_time, end_time, db)

    return JSONResponse(status_code=200, content={'txs': history })

