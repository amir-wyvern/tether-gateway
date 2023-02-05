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
    TransferHistoryRequest 
)

from db.database import get_db

from celery_tasks.tasks import TransferCeleryTask 
from celery_tasks.utils import create_worker_from
from sqlalchemy.orm.session import Session
from auth.oauth2 import ( 
    get_current_user
)


router = APIRouter(prefix='/transfer', tags=['Transfer'])

_, transfer_worker = create_worker_from(TransferCeleryTask)

@router.post('/request', response_model=BaseResponse, responses={403:{'model':HTTPError}})
def transfer_request(request: TransferRequest, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    # resp = db_transfer_request.create_request(user_id, request, db)

    # if resp:
        # return JSONResponse(status_code=200, content={'request_id': resp.request_id ,'message':'Deposit request registered'})

    # else:
    raise HTTPException(status_code=403, detail={'internal_code':1011, 'message':'Insufficient inventory'})



@router.post('/history', response_model=TransferHistoryResponse, responses={404:{'model':HTTPError}})
def transfer_comfirmation(request: TransferHistoryRequest, user_id: int=Depends(get_current_user), db: Session=Depends(get_db)):

    return JSONResponse(status_code=200, content={'txs':[] })

