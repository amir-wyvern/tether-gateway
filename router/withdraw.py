from fastapi.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends
)
from schemas import (
    HTTPError,
    WithdrawRequest,
    WithdrawRequestResponse,
    WithdrawtHistoryResponse,
    WithdrawHistoryModelForDataBase,
    WithdrawHistoryStatus
)

from uuid import uuid4
from db.database import get_db
from db import db_withdraw_history, db_main_account, db_config

from celery_tasks.tasks import WithdrawCeleryTask 
from celery_tasks.utils import create_worker_from
from sqlalchemy.orm.session import Session
from datetime import datetime
from auth.oauth2 import ( 
    get_current_user
)

router = APIRouter(prefix='/withdraw', tags=['Withdraw'])

_, withdraw_worker = create_worker_from(WithdrawCeleryTask)

@router.post('/request', response_model=WithdrawRequestResponse, responses={403:{'model':HTTPError}})
def withdraw_request(request: WithdrawRequest, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    request_id = uuid4().hex[:12]

    withdraw_address = db_main_account.get_withdraw_address(db)
    config = db_config.get_config(db)

    request_data = {
        'request_id': request_id,
        'tx_hash': None,
        'user_id': user_id,
        'from_address': withdraw_address,
        'to_address': request.to_address,
        'value': request.value,
        'status': WithdrawHistoryStatus.PROCESSING,
        'error_message': None,
        'withdraw_fee_percentage': config.withdraw_fee_percentage,
        'withdraw_fee_value': None,
        'request_time': datetime.now(),
        'processingـcompletionـtime': None
    }

    resp = db_withdraw_history.create_withdraw_history(WithdrawHistoryModelForDataBase(**request_data), db)

    payload = {
        'request_id': request_id,
        'user_id': user_id,
        'value': request.value,
        'to_address': request.to_address
    }

    withdraw_worker.apply_async(args=(payload,))

    return JSONResponse(status_code=200, content={'request_id': request_id ,'message':'Withdraw request registered'})


@router.get('/history', response_model=WithdrawtHistoryResponse, responses={404:{'model':HTTPError}})
def withdraw_comfirmation(start_time: datetime, end_time: datetime, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    history = db_withdraw_history.get_deposit_history_by_time(user_id, start_time, end_time, db)
    return JSONResponse(status_code=200, content={'txs': history })

