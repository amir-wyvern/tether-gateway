from schemas import WithdrawHistoryModelForDataBase, WithdrawHistoryModelForUpdateDataBase
from sqlalchemy.orm.session import Session
from sqlalchemy import and_

from db.models import DbWithdrawHistory
from typing import Union


def create_withdraw_history(request: WithdrawHistoryModelForDataBase, db: Session, commit=True):
    
    withdraw_history = DbWithdrawHistory(
        request_id= request.request_id,
        tx_hash= request.tx_hash,
        user_id= request.user_id,
        from_address= request.from_address,
        to_address= request.to_address,
        error_message= request.error_message,
        status= request.status,
        value= request.value,
        withdraw_fee_percentage= request.withdraw_fee_percentage,
        withdraw_fee_value= request.withdraw_fee_value,
        request_time= request.request_time,
        processingـcompletionـtime= request.processingـcompletionـtime
    )
    db.add(withdraw_history)

    if commit:
        db.commit()
        db.refresh(withdraw_history)

        return withdraw_history




def get_deposit_history_by_time(user_id, start_time, end_time, db:Session, status: Union[DbWithdrawHistory, None]= None):

    if status == None:
        return db.query(DbWithdrawHistory).filter(and_(
            DbWithdrawHistory.user_id == user_id, 
            DbWithdrawHistory.request_time >= start_time, 
            DbWithdrawHistory.request_time <= end_time
            )).all()
    
    else:
        return db.query(DbWithdrawHistory).filter(and_(
            DbWithdrawHistory.user_id == user_id, 
            DbWithdrawHistory.request_time >= start_time, 
            DbWithdrawHistory.request_time <= end_time,
            DbWithdrawHistory.status == status
            )).all()


def update_withdraw_history_by_request_id(request_id, new_data: WithdrawHistoryModelForUpdateDataBase, db: Session, commit=True):

    obj = db.query(DbWithdrawHistory).filter(DbWithdrawHistory.request_id == request_id )

    for key, value in new_data.items():
        if value is not None:
            obj.update({getattr(DbWithdrawHistory, key): value})

    if commit:
        
        db.commit()


