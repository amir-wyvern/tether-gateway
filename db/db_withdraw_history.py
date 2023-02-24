from sqlalchemy.orm.session import Session
from db.models import DbWithdrawHistory
from schemas import WithdrawHistoryModelForDataBase


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
        timestamp= request.timestamp
    )
    db.add(withdraw_history)

    if commit:
        db.commit()
        db.refresh(withdraw_history)

        return withdraw_history


# def get_request_deposit_by_id(request_id, db:Session, mode: Union[DepositRequestStatus, None]= None):

#     return db.query(DdDepositRequest).filter(DdDepositRequest.request_id == request_id ).first()

# def get_history_deposit_by_address(address, db:Session, mode: Union[DepositHistoryStatus, None]= None):

#     if mode == None:
#         return db.query(DbDepositHistory).filter(DbDepositHistory.to_address == address ).all()
    
#     else:
#         return db.query(DbDepositHistory).filter(or_(DbDepositHistory.to_address == address, DbDepositHistory.status == mode) ).all()

# def get_history_deposit_by_tx_hash(tx_hash, db:Session):

#     return db.query(DbDepositHistory).filter(DbDepositHistory.tx_hash == tx_hash ).first()


# def get_request_deposit_by_user(user_id, db:Session, mode: Union[DepositRequestStatus, None]= None):

#     if mode == None:
#         return db.query(DdDepositRequest).filter(DdDepositRequest.user_id == user_id).all()
    
#     else:
#         return db.query(DdDepositRequest).filter(or_(DdDepositRequest.user_id == user_id, DdDepositRequest.status == mode)).all()



