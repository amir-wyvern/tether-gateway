import hashlib
from sqlalchemy.orm.session import Session
from schemas import (
    BotUserRegister,
    BotUserBase,
    BotUserUpdateProfile
)
from db.models import DbUser
# from db.hash import Hash
from exceptions import EmailNotValid
from datetime import datetime


def hashPass(password):

    salt = "dd211c31dd2abf6875ce5bb570cc71e9523386757d255a4f5155d"    
    dataBase_password = password+salt
    hashed_pass = hashlib.sha3_256(dataBase_password.encode()).hexdigest()

    return hashed_pass

def create_user(request: BotUserRegister, db: Session):

    password_hash = hashPass(request.password)  


    relferal_link = base64.urlsafe_b64encode(uuid.uuid1().bytes).decode()[:12] 

    user = DbUser(
        tel_id= request.tel_id,
        phone_number= request.phone_number,
        referal_link= relferal_link,
        password= password_hash,
        email= request.email,
        name= request.name,
        lastname= request.lastname,
        balance= 0,
        photo= request.photo,
        number_of_invented= 0,
        bonus_of_invented= 0,
        register_time= datetime.now(),
        first_deposit_value= 0
    )
    db.add(user)

    db.commit()
    db.refresh(user)
    return user


def get_all_users(db:Session):
    return db.query(DbUser).all()


def get_user(user_id, db:Session):
    return db.query(DbUser).filter(DbUser.user_id == user_id ).first()

def get_user_by_telegram_id(tel_id, db:Session):
    print(1)
    return db.query(DbUser).filter(DbUser.tel_id == tel_id ).first()


def delete_user(user_id, db:Session):
    user = get_user(user_id, db)
    db.delete(user)
    db.commit()
    return True


def update_password(user_id, db:Session):

    password_hash = hashPass(request.password)  

    user = db.query(DbUser).filter(DbUser.user_id == user_id)
    user.update({
        DbUser.password: password_hash,
    })

    db.commit()

    return True

def update_balance(user_id, new_balance, db:Session):

    user = db.query(DbUser).filter(DbUser.user_id == user_id)
    user.update({
        DbUser.balance: new_balance,
    })
    db.commit()

    return True

def update_user_profile(user_id, request:BotUserUpdateProfile, db:Session):

    user = db.query(DbUser).filter(DbUser.user_id == user_id)
    user.update({
        DbUser.name: request.name,
        DbUser.lastname: request.lastname,
        DbUser.photo: request.photo,
        DbUser.phone_number: request.phone_number,
        DbUser.email: request.email,
    })
    db.commit()

    return True