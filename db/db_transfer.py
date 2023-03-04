from schemas import TransferHistoryModelForDataBase, TransferHistoryModelForUpdateDataBase, TransferHistoryStatus
from sqlalchemy.orm.session import Session
from sqlalchemy import and_

from db.models import DbTransferHistory
from typing import Union


def create_transfer_history(request: TransferHistoryModelForDataBase, db: Session, commit=True):

    transfer_history = DbTransferHistory(
        request_id= request.request_id,
        from_user= request.from_user,
        to_user= request.to_user,
        error_message= request.error_message,
        status= request.status,
        value= request.value,
        transfer_fee_percentage= request.transfer_fee_percentage,
        transfer_fee_value= request.transfer_fee_value,
        request_time= request.request_time,
        processingـcompletionـtime= request.processingـcompletionـtime
    )
    db.add(transfer_history)

    if commit:
        db.commit()
        db.refresh(transfer_history)

        return transfer_history


def get_transfer_history_by_time_and_user(user_id, start_time, end_time, db:Session, status: Union[TransferHistoryStatus, None]= None):

    if status == None:
        return db.query(DbTransferHistory).filter(and_(
            DbTransferHistory.from_user == user_id, 
            DbTransferHistory.request_time >= start_time, 
            DbTransferHistory.request_time <= end_time
            )).all()
    
    else:
        return db.query(DbTransferHistory).filter(and_(
            DbTransferHistory.from_user == user_id, 
            DbTransferHistory.request_time >= start_time, 
            DbTransferHistory.request_time <= end_time,
            DbTransferHistory.status == status
            )).all()

def update_transfer_history_by_request_id(request_id, new_data: TransferHistoryModelForUpdateDataBase, db: Session, commit=True):

    obj = db.query(DbTransferHistory).filter(DbTransferHistory.request_id == request_id )

    for key, value in new_data:
        if value is not None:
            obj.update({getattr(DbTransferHistory, key): value})

    if commit:
        
        db.commit()


