import hashlib
from sqlalchemy.orm.session import Session
from schemas import (
    BotUserRegister,
    BotUserBase,
    BotUserUpdateProfile,
    BotUpdatePassword
)
from db.models import DbUser
from db.hash import Hash
from exceptions import EmailNotValid
from datetime import datetime


def create_user(request: BotUserRegister, db: Session):

    password_hash = Hash.sha3_256(request.password)  
    relferal_link = Hash.generate_referal_link()

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
    return db.query(DbUser).filter(DbUser.tel_id == tel_id ).first()


def get_user_by_phone_number(phone_number, db:Session):
    return db.query(DbUser).filter(DbUser.phone_number == phone_number).first()


def get_user_by_email(email, db:Session):
    return db.query(DbUser).filter(DbUser.email == email).first()


def delete_user(user_id, db:Session):
    user = get_user(user_id, db)
    db.delete(user)
    db.commit()
    return True


def update_password(user_id, request:BotUpdatePassword, db:Session):

    password_hash = Hash.sha3_256(request.new_password)  

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