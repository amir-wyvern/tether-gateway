from sqlalchemy.orm.session import Session
from db.models import DbMainAccounts



def get_deposit_address(db:Session):

    return db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first().get("deposit_address")

def get_withdraw_address(db:Session):

    return db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first().get("withdraw_address")

def get_p_withdraw(db:Session):

    return db.query(DbMainAccounts).filter(DbMainAccounts.index == 1).first().get("p_withdraw")



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