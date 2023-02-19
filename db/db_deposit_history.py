from sqlalchemy.orm.session import Session
from db.models import DbDepositHistory
from schemas import DepositHistoryModelForDataBase


def create_deposit_history(request: DepositHistoryModelForDataBase, db: Session):
    
    deposit_history = DbDepositHistory(
        request_id= request.request_id,
        tx_hash= request.tx_hash,
        user_id= request.user_id,
        origin_address= request.origin_address,
        destination_address= request.destination_address,
        error_message= request.error_message,
        status= request.status,
        value= request.value,
        timestamp= request.timestamp
    )
    db.add(deposit_history)

    db.commit()
    db.refresh(deposit_history)

    return deposit_history


# def get_request_deposit_by_id(request_id, db:Session, mode: Union[DepositRequestStatus, None]= None):

#     return db.query(DdDepositRequest).filter(DdDepositRequest.request_id == request_id ).first()

# def get_history_deposit_by_address(address, db:Session, mode: Union[DepositHistoryStatus, None]= None):

#     if mode == None:
#         return db.query(DbDepositHistory).filter(DbDepositHistory.destination_address == address ).all()
    
#     else:
#         return db.query(DbDepositHistory).filter(or_(DbDepositHistory.destination_address == address, DbDepositHistory.status == mode) ).all()

def get_history_deposit_by_tx_hash(tx_hash, db:Session):

    return db.query(DbDepositHistory).filter(DbDepositHistory.tx_hash == tx_hash ).first()


# def get_request_deposit_by_user(user_id, db:Session, mode: Union[DepositRequestStatus, None]= None):

#     if mode == None:
#         return db.query(DdDepositRequest).filter(DdDepositRequest.user_id == user_id).all()
    
#     else:
#         return db.query(DdDepositRequest).filter(or_(DdDepositRequest.user_id == user_id, DdDepositRequest.status == mode)).all()



