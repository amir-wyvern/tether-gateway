from sqlalchemy.orm.session import Session
from db.models import DdDepositRequest, DepositRequestStatus
from datetime import datetime
from typing import Union
from sqlalchemy import or_

def create_request(user_id ,value, destination_address, db: Session):
    
    request_deposit = DdDepositRequest(
        user_id= user_id,
        # origin_address= request.origin_address,
        destination_address= destination_address,
        value= value,
        status= DepositRequestStatus.WAITING,
        error_message=None,
        timestamp= datetime.now()
    )
    db.add(request_deposit)

    db.commit()
    db.refresh(request_deposit)

    return request_deposit


def get_request_deposit_by_id(request_id, db:Session, mode: Union[DepositRequestStatus, None]= None):

    return db.query(DdDepositRequest).filter(DdDepositRequest.request_id == request_id ).first()


def get_request_deposit_by_address(address, db:Session, mode: Union[DepositRequestStatus, None]= None):

    if mode == None:
        return db.query(DdDepositRequest).filter(DdDepositRequest.destination_address == address ).all()
    
    else:
        return db.query(DdDepositRequest).filter(or_(DdDepositRequest.destination_address == address, DdDepositRequest.status == mode) ).all()


def get_request_deposit_by_user(user_id, db:Session, mode: Union[DepositRequestStatus, None]= None):

    if mode == None:
        return db.query(DdDepositRequest).filter(DdDepositRequest.user_id == user_id).all()
    
    else:
        return db.query(DdDepositRequest).filter(or_(DdDepositRequest.user_id == user_id, DdDepositRequest.status == mode)).all()


def update_status_by_request_id(request_id, new_status: DepositRequestStatus, db: Session, error_message: str = None, commit=True):

    obj = db.query(DdDepositRequest).filter(DdDepositRequest.request_id == request_id )
    obj.update({
        DdDepositRequest.status: new_status
    })

    if error_message: 
        obj.update({
            DdDepositRequest.error_message: error_message
        })

    if commit:
        print(db.commit())

