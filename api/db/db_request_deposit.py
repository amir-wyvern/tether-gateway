import hashlib
from sqlalchemy.orm.session import Session
from schemas import (
    RequestDeposit
)
from db.models import DdRequestDeposit, DepositRequestStatus
from datetime import datetime


def create_request(user_id ,request: RequestDeposit, db: Session):

    request_deposit = DdRequestDeposit(
        user_id= user_id,
        origin_address= request.origin_address,
        value= request.value,
        status= DepositRequestStatus.WAITING,
        timestamp= datetime.now()
    )
    db.add(request_deposit)

    db.commit()
    db.refresh(request_deposit)
    return request_deposit


def get_request_deposit_by_id(request_id, db:Session):
    return db.query(DdRequestDeposit).filter(DdRequestDeposit.request_id == request_id ).first()


def get_request_deposit_by_address(address, db:Session):
    return db.query(DdRequestDeposit).filter(DdRequestDeposit.origin_address == address ).all()


def get_request_deposit_by_user(user_id, db:Session):
    return db.query(DdRequestDeposit).filter(DdRequestDeposit.user_id == user_id).all()

