from fastapi.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from schemas import (
    HTTPError,
    BaseResponse,
    TransferRequest,
    TransferHistoryResponse,
    TransferHistoryStatus,
    TransferHistoryModelForDataBase
)

from db.database import get_db
from db import db_config, db_transfer, db_user

from celery_tasks.tasks import TransferCeleryTask 
from celery_tasks.utils import create_worker_from
from sqlalchemy.orm.session import Session
from auth.oauth2 import ( 
    get_current_user
)
from uuid import uuid4
from datetime import datetime
import logging
import os

if not os.path.exists('logs') :
    os.mkdir('logs')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler to show logs on terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create a file handler to save logs to a file
file_handler = logging.FileHandler('logs/transfer_route.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


router = APIRouter(prefix='/transfer', tags=['Transfer'])

_, transfer_worker = create_worker_from(TransferCeleryTask)

@router.post('/request', response_model=BaseResponse, responses={403:{'model':HTTPError}})
def transfer_request(request: TransferRequest, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    request_id = uuid4().hex[:12]

    if user_id == request.to_user:
        logger.info(f'to_user is same from_user [request_id: {request_id} -user_id: {user_id}]')
        raise HTTPException(status_code=403, detail={'internal_code':1021, 'message':'to_user is same from_user'})
    
    if db_user.get_user(request.to_user, db) == None:
        logger.info(f'the to_user not found [request_id: {request_id} -user_id: {user_id} -to_user: {request.to_user}]')
        raise HTTPException(status_code=403, detail={'internal_code':1022, 'message':'the to_user not found'})
    
    config = db_config.get_config(db)

    if config.transfer_lock == True:
        logger.info(f'transfer has locked [request_id: {request_id} -user_id: {user_id}]')
        raise HTTPException(status_code=403, detail={'internal_code':1020, 'message':'transfer has locked'})

    user_data = db_user.get_user(user_id, db)
    
    balance = float(user_data.balance)

    transfer_fee = float(config.transfer_fee_percentage) / 100 * request.value 
    min_user_balance = float(config.min_user_balance)

    if ( min_user_balance + transfer_fee + request.value ) > balance :
        
        logger.info(f'The user does not have enough balance to transfer the desired amount ( config.min_user_balance + transfer_fee + value ) > balance [request_id: {request_id} -user_id: {user_id}]')
        raise HTTPException(status_code=403, detail={'internal_code':1011, 'message':'Insufficient inventory'})


    request_data = {
        'request_id': request_id,
        'from_user': user_id,
        'to_user': request.to_user,
        'value': request.value,
        'status': TransferHistoryStatus.PROCESSING,
        'error_message': None,
        'transfer_fee_percentage': config.transfer_fee_percentage,
        'transfer_fee_value': None,
        'request_time': datetime.now(),
        'processingـcompletionـtime': None
    }
    
    resp = db_transfer.create_transfer_history(TransferHistoryModelForDataBase(**request_data), db)

    payload = {
        'request_id': request_id,
        'from_user': user_id,
        'to_user': request.to_user,
        'value': request.value
    }

    transfer_worker.apply_async(args=(payload,))

    return {'request_id': request_id ,'message':'transfer request registered'}


@router.get('/history', response_model=TransferHistoryResponse, responses={404:{'model':HTTPError}})
def transfer_history(start_time: datetime, end_time: datetime, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    history = db_transfer.get_transfer_history_by_time_and_user(user_id, start_time, end_time, db)
    return {'txs': history }
