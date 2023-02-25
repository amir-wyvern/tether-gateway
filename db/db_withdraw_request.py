from sqlalchemy.orm.session import Session
from schemas import (
    WithdrawRequest
)
from db.models import DdWithdrawRequest, WithdrawRequestStatus
from datetime import datetime


def create_request(user_id ,request: WithdrawRequest, db: Session):
    
    request_withdraw = DdWithdrawRequest(
        user_id= user_id,
        to_address= request.to_address,
        value= request.value,
        status= WithdrawRequestStatus.WAITING,
        error_message= None,
        timestamp= datetime.now()
    )
    db.add(request_withdraw)

    db.commit()
    db.refresh(request_withdraw)

    return request_withdraw


def get_request_withdraw_by_id(request_id, db:Session):
    return db.query(DdWithdrawRequest).filter(DdWithdrawRequest.request_id == request_id ).first()


def get_request_withdraw_by_address(address, db:Session):
    return db.query(DdWithdrawRequest).filter(DdWithdrawRequest.to_address == address ).all()


def get_request_withdraw_by_user(user_id, db:Session):
    return db.query(DdWithdrawRequest).filter(DdWithdrawRequest.user_id == user_id).all()

