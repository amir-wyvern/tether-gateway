from sqlalchemy.orm.session import Session
from schemas import (
    DepositRequest
)
from db.models import DdDepositRequest, DepositRequestStatus
from datetime import datetime


def create_request(user_id ,request: DepositRequest, db: Session):
    
    request_deposit = DdDepositRequest(
        user_id= user_id,
        origin_address= request.origin_address,
        destination_address= request.destination_address,
        value= request.value,
        status= DepositRequestStatus.WAITING,
        error_message=None,
        timestamp= datetime.now()
    )
    db.add(request_deposit)

    db.commit()
    db.refresh(request_deposit)

    return request_deposit


def get_request_deposit_by_id(request_id, db:Session):
    return db.query(DdDepositRequest).filter(DdDepositRequest.request_id == request_id ).first()


def get_request_deposit_by_address(address, db:Session):
    return db.query(DdDepositRequest).filter(DdDepositRequest.origin_address == address ).all()


def get_request_deposit_by_user(user_id, db:Session):
    return db.query(DdDepositRequest).filter(DdDepositRequest.user_id == user_id).all()

