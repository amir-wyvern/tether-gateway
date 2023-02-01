import hashlib
from sqlalchemy.orm.session import Session
from sqlalchemy import or_
from schemas import (
    UserRegister,
    UserBase,
    UserUpdateProfile,
    UpdatePassword
)
from db.models import DbUser
from db.hash import Hash
from exceptions import EmailNotValid
from datetime import datetime


def create_user(request: UserRegister, db: Session):

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

def check_exist_user(items ,user:UserRegister, db:Session):

    ls = []
    for item in items:
        if getattr(user, item) != None:
            ls.append(getattr(DbUser, item) == getattr(user, item))

    return db.query(DbUser).filter( or_(*ls)).first()

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


def update_password(user_id, request:UpdatePassword, db:Session):

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

def update_user_profile(user_id, request:UserUpdateProfile, db:Session):

    user = db.query(DbUser).filter(DbUser.user_id == user_id)
    user.update({
        DbUser.name: request.name,
        DbUser.lastname: request.lastname,
        DbUser.phone_number: request.phone_number,
        DbUser.email: request.email,
    })
    db.commit()

    return True



# (tel_id, phone_number, referal_link, password, email, name, lastname, balance, photo, number_of_invented, bonus_of_invented, register_time, first_deposit_value) VALUES (%(tel_id)s, %(phone_number)s, %(referal_link)s, %(password)s, %(email)s, %(name)s, %(lastname)s, %(balance)s, %(photo)s, %(number_of_invented)s, %(bonus_of_invented)s, %(register_time)s, %(first_deposit_value)s)]
# [{'tel_id': 1011, 'phone_number': 'string2222', 'referal_link': '_XFjeKJLEe2e', 'password': '077d15fd0686819a58a140a3693de9fbd4be46523add63afea3baaad28c0d9fe', 'email': 'user1@example.com', 'name': 'string', 'lastname': 'string', 'balance': 0, 'photo': 'string', 'number_of_invented': 0, 'bonus_of_invented': 0, 'register_time': datetime.datetime(2023, 2, 1, 19, 47, 57, 669329), 'first_deposit_value': 0}]
