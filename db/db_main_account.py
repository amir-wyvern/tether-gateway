from sqlalchemy.orm.session import Session
from db.models import DbMainAccounts
from schemas import InitMainAccount

def init_table(request: InitMainAccount, db:Session):

    data = get_deposit_address(db)
    if data is None:
        main_account = DbMainAccounts(
            deposit_address= request.deposit_address,
            withdraw_address= request.withdraw_address,
            p_withdraw= request.p_withdraw
        )
        db.add(main_account)
        db.commit()
        db.refresh(main_account)

        return main_account

def get_deposit_address(db:Session):

    resp = db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first() 
    return resp.deposit_address if resp else None

def get_withdraw_address(db:Session):

    resp = db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first()
    
    return resp.withdraw_address if resp else None

def get_p_withdraw(db:Session):

    resp = db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first()
    return resp.p_withdraw if resp else None
