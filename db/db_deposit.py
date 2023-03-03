from sqlalchemy.orm.session import Session
from db.models import DbDepositHistory
from schemas import (
    DepositHistoryModelForDataBase,
    DepositHistoryStatus,
    DepositHistoryModelForUpdateDataBase
)
from typing import Union
from sqlalchemy import and_


def create_deposit_history(request: DepositHistoryModelForDataBase, db: Session, commit=True):
    
    deposit_history = DbDepositHistory(
        request_id= request.request_id,
        tx_hash= request.tx_hash,
        user_id= request.user_id,
        from_address= request.from_address,
        to_address= request.to_address,
        error_message= request.error_message,
        status= request.status,
        value= request.value,
        request_time= request.request_time,
        processingـcompletionـtime= request.processingـcompletionـtime
    )

    db.add(deposit_history)

    if commit:
        db.commit()
        db.refresh(deposit_history)

        return deposit_history


def get_deposit_history_by_tx_hash(tx_hash, db:Session, status: Union[DepositHistoryStatus, None]= None):

    if status == None:
        return db.query(DbDepositHistory).filter(DbDepositHistory.tx_hash == tx_hash ).all()
    
    else:
        return db.query(DbDepositHistory).filter(and_(DbDepositHistory.tx_hash == tx_hash, DbDepositHistory.status == status) ).all()


def get_deposit_history_by_status(status: DepositHistoryStatus, db:Session):
    return db.query(DbDepositHistory).filter(DbDepositHistory.status == status ).all()


def get_deposit_history_by_user_id(user_id, db:Session, status: Union[DepositHistoryStatus, None]= None):

    if status == None:
        return db.query(DbDepositHistory).filter(DbDepositHistory.user_id == user_id).all()
    
    else:
        return db.query(DbDepositHistory).filter(and_(DbDepositHistory.user_id == user_id, DbDepositHistory.status == status)).all()
    
def get_deposit_history_by_time_and_user(user_id, start_time, end_time, db:Session, status: Union[DepositHistoryStatus, None]= None):

    if status == None:
        return db.query(DbDepositHistory).filter(and_(
            DbDepositHistory.user_id == user_id, 
            DbDepositHistory.request_time >= start_time, 
            DbDepositHistory.request_time <= end_time
            )).all()
    
    else:
        return db.query(DbDepositHistory).filter(and_(
            DbDepositHistory.user_id == user_id, 
            DbDepositHistory.request_time >= start_time, 
            DbDepositHistory.request_time <= end_time,
            DbDepositHistory.status == status
            )).all()


def update_deposit_history_by_request_id(request_id, new_data: DepositHistoryModelForUpdateDataBase, db: Session, commit=True):

    obj = db.query(DbDepositHistory).filter(DbDepositHistory.request_id == request_id )

    for key, value in new_data.items():
        if value is not None:
            obj.update({getattr(DbDepositHistory, key): value})

    if commit:
        
        db.commit()




