from sqlalchemy.orm.session import Session
from db.models import DbMainAccounts



def get_deposit_address(db:Session):

    resp = db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first() 
    return resp.deposit_address if resp else None

def get_withdraw_address(db:Session):

    resp = db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first()
    
    return resp.withdraw_address if resp else None

def get_p_withdraw(db:Session):

    resp = db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first()
    return resp.p_withdraw if resp else None



# def update_config(request:UpdateConfig , db:Session):

#     user = db.query(DbConfig).filter(DbConfig.index == 1)
#     user.update({
#         DbConfig.name: request.name,
#         DbConfig.lastname: request.lastname,
#         DbConfig.photo: request.photo,
#         DbConfig.phone_number: request.phone_number,
#         DbConfig.email: request.email,
#     })
#     db.commit()

#     return True