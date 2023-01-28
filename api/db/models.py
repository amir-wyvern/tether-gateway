from db.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    VARCHAR,
    Float,
    CheckConstraint,
    DateTime
    )

from sqlalchemy.orm import relationship


class DbUser(Base):

    __tablename__ = 'users'

    user_id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    tel_id = Column(Integer, unique=True, index=True)
    phone_number = Column(VARCHAR(14), index=True, unique=True, nullable=False)
    referal_link = Column(VARCHAR(100), index=True, unique=True, nullable=False)
    
    email = Column(String(100), unique=True, nullable=True)
    name = Column(string(100) ,nullable=False)
    lastname = Column(String(100), nullable=False)
    balance = Column(Float(15,6), nullable=False, default=0.0 ) # CheckConstraint('balance >= 0')
    photo = Column(VARCHAR(200), nullable=True, unique=True)
    number_of_invented = Column(Integer, default=0, nullable=False) # CheckConstraint('number_of_invented >= 0')
    bonus_of_invented = Column(Integer, default=0, nullable=False) # CheckConstraint('bonus_of_invented >= 0')
    register_time = Column(DateTime, nullable=False)
    first_deposit_value = Column(Integer) #  CheckConstraint('first_deposit_value >= 0')

    main = relationship("main")


class DbMainAccounts(Base):
    __tablename__ = 'main_accounts'

    deposit_address = Column(VARCHAR(42), nullable=False)
    withdraw_address = Column(VARCHAR(42), nullable=False)
    p_withdraw = Column(VARCHAR(42), nullable=False)


class DbConfigs(Base):
    __tablename__ = 'configs'

    withdraw_lock = Column(Boolean, nullable=False, default=False)
    deposit_lock = Column(Boolean, nullable=False, default=False)
    transfer_lock = Column(Boolean, nullable=False, default=False)
    transfer_fee_percentage = Column(Float(9,6), nullable=False, default=0.001) # CheckConstraint('transfer_fee_percentage >= 0')
    withdraw_fee_percentage = Column(Float(9,6), nullable=False, default=1.0) # CheckConstraint('withdraw_fee_percentage >= 0')
    min_user_balance = Column(Float(15,6), nullable=False, default=1.0) # CheckConstraint(min_user_balance >= 0)
    referal_bonus_percentage = Column(Float(9,6), nullable=False, default=0.1) # CheckConstraint(referal_bonus_percentage >= 0)


class DbPasswords(Base):
    __tablename__ = 'passwords'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True, nullable=False, unique=True, index=True)
    password = Column(VARCHAR(200), nullable=False)


class DbTransferHistory(Base):
    __tablename__ = 'transfer_history'

    tx_hash = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    origin_user_id = Column(Integer, ForeignKey('users.user_id'), index=True, nullable=False)
    destination_user_id = Column(Integer, ForeignKey('users.user_id'), index=True, nullable=False)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    transfer_fee_percentage = Column(Float(9,6), nullable=False) # CheckConstraint('transfer_fee_percentage > 0')
    transfer_fee_value = Column(Float(15,6), nullable=False) # CheckConstraint('transfer_fee_value > 0')
    timestamp = Column(DateTime, nullable=False)


class DbWithdrawHistory(Base):
    __tablename__ = 'withdraw_history'

    tx_hash = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True, nullable=False)
    destination_address = Column(VARCHAR(42), index=True, nullable=False)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    withdraw_fee_percentage = Column(Float(9,6), nullable=False) # CheckConstraint('transfer_fee_percentage > 0')
    withdraw_fee_value = Column(Float(15,6), nullable=False) # CheckConstraint('withdraw_fee_value > 0')
    timestamp = Column(DateTime, nullable=False)


class DbDepositHistory(Base):
    __tablename__ = 'deposit_history'

    tx_hash = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True, nullable=False)
    origin_address = Column(VARCHAR(42), index=True, nullable=False)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    timestamp = Column(DateTime, nullable=False)


class DdRequestDeposit(Base):
    __tablename__ = 'request_deposit'

    request_id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True, nullable=False)
    origin_address = Column(VARCHAR(42), index=True, nullable=False)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    timestamp = Column(DateTime, nullable=False)




