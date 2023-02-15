from db.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    VARCHAR,
    Float,
    DateTime,
    Enum
    )
import enum


class DbUser(Base):

    __tablename__ = 'user'

    user_id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    tel_id = Column(Integer, unique=True, index=True, nullable=True)
    phone_number = Column(VARCHAR(14), index=True, unique=True, nullable=True)
    referal_link = Column(VARCHAR(100), index=True, unique=True, nullable=False)
    
    password = Column(String(200), nullable=False)
    email = Column(String(100), index=True, unique=True, nullable=True)
    name = Column(String(100) ,nullable=False)
    lastname = Column(String(100), nullable=False)
    balance = Column(Float(15,6), nullable=False, default=0.0 ) # CheckConstraint('balance >= 0')
    photo = Column(VARCHAR(200), nullable=True, unique=True)
    number_of_invited = Column(Integer, default=0, nullable=False) # CheckConstraint('number_of_invited >= 0')
    bonus_of_invited = Column(Float(15,6), default=0.0, nullable=False) # CheckConstraint('bonus_of_invited >= 0.0')
    register_time = Column(DateTime, nullable=False)
    first_deposit_value = Column(Integer) #  CheckConstraint('first_deposit_value >= 0')

    # relTransferHistory = relationship("DbTransferHistory")
    # relWithdrawHistory = relationship("DbWithdrawHistory")
    # relDepositHistory = relationship("DbDepositHistory")
    # relRequestDeposit = relationship("DdRequestDeposit")


class DbMainAccounts(Base):
    __tablename__ = 'main_accounts'

    index = Column(Integer, primary_key=True)
    deposit_address = Column(VARCHAR(42), nullable=False)
    withdraw_address = Column(VARCHAR(42), nullable=False)
    p_withdraw = Column(VARCHAR(42), nullable=False)


class DbConfig(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    index = Column(Integer, default=1, unique=True)
    withdraw_lock = Column(Boolean, nullable=False, default=False) 
    deposit_lock = Column(Boolean, nullable=False, default=False)
    transfer_lock = Column(Boolean, nullable=False, default=False)
    transfer_fee_percentage = Column(Float(9,6), nullable=False, default=0.001) # CheckConstraint('transfer_fee_percentage >= 0')
    withdraw_fee_percentage = Column(Float(9,6), nullable=False, default=1.0) # CheckConstraint('withdraw_fee_percentage >= 0')
    min_user_balance = Column(Float(15,6), nullable=False, default=1.0) # CheckConstraint(min_user_balance >= 0)
    referal_bonus_percentage = Column(Float(9,6), nullable=False, default=0.1) # CheckConstraint(referal_bonus_percentage >= 0)


# class DbPassword(Base):
#     __tablename__ = 'password'

#     user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True, nullable=False, unique=True, index=True)
#     password = Column(VARCHAR(200), nullable=False)


class DbTransferHistory(Base):
    __tablename__ = 'transfer_history'

    tx_hash = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    origin_user_id = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    destination_user_id = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    error_message = Column(VARCHAR(400), nullable=True)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    transfer_fee_percentage = Column(Float(9,6), nullable=False) # CheckConstraint('transfer_fee_percentage > 0')
    transfer_fee_value = Column(Float(15,6), nullable=False) # CheckConstraint('transfer_fee_value > 0')
    timestamp = Column(DateTime, nullable=False)

    # relUser = relationship("DbUser")



class DbWithdrawHistory(Base):
    __tablename__ = 'withdraw_history'

    tx_hash = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    destination_address = Column(VARCHAR(42), index=True, nullable=False)
    error_message = Column(VARCHAR(400), nullable=True)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    withdraw_fee_percentage = Column(Float(9,6), nullable=False) # CheckConstraint('transfer_fee_percentage > 0')
    withdraw_fee_value = Column(Float(15,6), nullable=False) # CheckConstraint('withdraw_fee_value > 0')
    timestamp = Column(DateTime, nullable=False)

    # relUser = relationship("DbUser")


class DbDepositHistory(Base):
    __tablename__ = 'deposit_history'

    tx_hash = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    origin_address = Column(VARCHAR(42), index=True, nullable=False)
    error_message = Column(VARCHAR(400), nullable=True)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    timestamp = Column(DateTime, nullable=False)

    # relUser = relationship("DbUser")

class DepositRequestStatus(enum.Enum):
    WAITING = 1
    RECEIVED = 2
    FAILED = 3


class DdDepositRequest(Base):
    __tablename__ = 'deposit_request'

    request_id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    origin_address = Column(VARCHAR(42), index=True, nullable=False)
    destination_address = Column(VARCHAR(42), index=True, nullable=False)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    status = Column(Enum(DepositRequestStatus), nullable=False)
    error_message = Column(VARCHAR(400), nullable=True)
    timestamp = Column(DateTime, nullable=False)


class WithdrawRequestStatus(enum.Enum):
    WAITING = 1
    RECEIVED = 2
    FAILED = 3

class DdWithdrawRequest(Base):
    __tablename__ = 'withdraw_request'

    request_id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), index=True, nullable=False)
    destintion_address = Column(VARCHAR(42), index=True, nullable=False)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    status = Column(Enum(WithdrawRequestStatus), nullable=False)
    error_message = Column(VARCHAR(400), nullable=True)
    timestamp = Column(DateTime, nullable=False)

    
class DdReceiveTx(Base):
    __tablename__ = 'receive_tx'

    tx_hash = Column(VARCHAR(100), primary_key=True, unique=True, index=True)
    origin_address = Column(VARCHAR(42), index=True, nullable=False)
    value = Column(Float(15,6), nullable=False) # CheckConstraint('value > 0')
    timestamp = Column(DateTime, nullable=False)




