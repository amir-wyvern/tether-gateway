from pydantic import BaseModel, EmailStr, Field
from typing import List, Union, Optional
from datetime import datetime
from enum import Enum
import re


class UpdateConfig(BaseModel):

    withdraw_lock: bool
    deposit_lock: bool
    transfer_lock: bool
    transfer_fee_percentage: float = Field(ge=0)
    withdraw_fee_percentage: float = Field(ge=0)
    min_user_balance: float = Field(ge=0)
    referal_bonus_percentage: float = Field(ge=0)


# Auth
class AuthType(str, Enum):
    phone_number = 'phone_number'
    email = 'email' 
    

class AuthPhoneNumberRequest(BaseModel):

    data: str=Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")

class AuthEmailRequest(BaseModel):

    data: EmailStr


class UserAuthDecode(BaseModel):

    data: str
    token: str

class UserAuthConfirmation(BaseModel):

    auth_code: int = Field(ge=100000, le=999999)

class UserAuthResponse(BaseModel):

    access_token: str
    type_token: str



# user Login or Register
class PhoneNumberStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not re.match(r"^\+?[0-9]{3}-?[0-9]{6,12}$", v):
            raise ValueError("Not a valid phone number")
        return v

class UserRegister(BaseModel):

    tel_id: Optional[int] = Field(ge=0, default= None)
    phone_number: Optional[PhoneNumberStr] = None
    email: Optional[EmailStr] = None 
    password: str = Field(min_length=1, max_length=200)
    referal_link: Optional[str] = Field(min_length=1, max_length=50, default=None)
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)


class UserRegisterByEmail(BaseModel):

    tel_id: Optional[int] = Field(ge=0, default= None)
    phone_number: Optional[PhoneNumberStr] = None
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)
    referal_link: Optional[str] = Field(min_length=1, max_length=50, default=None)
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)

class UserRegisterByPhoneNumber(BaseModel):

    tel_id: Optional[int] = Field(ge=0, default= None)
    email: Optional[EmailStr] = None 
    phone_number: PhoneNumberStr
    password: str = Field(min_length=1, max_length=200)
    referal_link: Optional[str] = Field(min_length=1, max_length=50, default=None)
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)




# User
class UserBase(BaseModel):

    tel_id : int

class UserUpdateProfile(BaseModel):

    phone_number:str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
    email:  Union[EmailStr, None] 
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)


class UserAuth(BaseModel):

    auth_code : int

class UserLogin(BaseModel):

    phone_number: str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
    password: str = Field(min_length=1, max_length=100)

class UserDisplay(BaseModel):

    tel_id: Union[None, int]
    phone_number: str
    referal_link: str 
    email: Union[None, EmailStr ] = Field(default=None)
    name: str
    lastname: str
    balance: float
    photo: Union[None, str] = Field(default=None)
    number_of_invited: int
    bonus_of_invited: float
    register_time: datetime
    first_deposit_value: float

    class Config:
        orm_mode = True

class BaseResponse(BaseModel):

    message: str

class UpdatePassword(BaseModel):

    old_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=1, max_length=200)

class HTTPError(BaseModel):

    message: str 
    internal_code: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised.", 'internal_code':1001},
        }
        



# Withdraw modeles

class WithdrawRequestStatus(int, Enum):
    WAITING = 1
    RECEIVED = 2
    FAILED = 3

class WithdrawRequest(BaseModel):

    value: float = Field(gt=0)
    destination_address: str = Field(min_length=1, max_length=100)

class WithdrawRequestResponse(BaseModel):
    
    message: str
    request_id: int

class WithdrawConfirmation(BaseModel):

    auth_code: int = Field(ge=100000,le=999999)

class WithdrawHistoryRequest(BaseModel):

    offset: int
    count: int

class WithdrawHistoryModel(BaseModel):

    address: str
    value: float
    tx_hash: str
    timestamp: int

class WithdrawtHistoryResponse(BaseModel):

    txs: List[WithdrawHistoryModel]



# Transfer modeles
class TransferRequest(BaseModel):

    value: float = Field(gt=0)
    destination_phone_number: str = Field(min_length=1, max_length=100)

class TransferRequestResponse(BaseModel):
    
    message: str
    request_id: int

class TransferHistoryModel(BaseModel):

    origin_address: str
    destination_address: str
    value: float
    tx_hash: str
    timestamp: int

class TransferHistoryResponse(BaseModel):

    txs: List[TransferHistoryModel]

class TransferHistoryRequest(BaseModel):

    offset: int
    count: int



# Deposit
class DepositHistoryStatus(int, Enum):
    RECEIVED = 2
    FAILED = 3

class DepositRequestStatus(int, Enum):
    WAITING = 1
    RECEIVED = 2
    FAILED = 3

class DepositHistoryModelForDataBase(BaseModel):

    tx_hash: Union[str, None]
    request_id: int
    user_id: int
    origin_address: Union[str, None] 
    destination_address: str
    error_message: Union[str, None]
    status: DepositHistoryStatus
    value: float
    timestamp: datetime

class DepositRequestResponse(BaseModel):

    deposit_address: str
    request_id: int

class DepositRequest(BaseModel):

    value: float = Field(gt=0)
    # destination_address: str = Field(min_length=1, max_length=100) # check format addrss with Fields
    # origin_address: str = Field(min_length=1, max_length=100) # check format addrss with Fields

class DepositConfirmation(BaseModel):

    tx_hash: str = Field(min_length=1, max_length=100)

class DepositHistoryRequest(BaseModel):

    offset: int
    count: int

class DepositHistoryModel(BaseModel):

    address: str
    value: float
    tx_hash: str
    timestamp: int

class DepositHistoryResponse(BaseModel):

    txs: List[DepositHistoryModel]

class ReceivedTx(BaseModel):

    tx_hash: str = Field(min_length=1, max_length=100)
    origin_address: str = Field(min_length=1, max_length=100)
    value: float  = Field(gt= 0)
    timestamp: datetime


# Cache
class SessionScheme(BaseModel):
    
    token: str = Field(min_length=1, max_length=300)
    user_id: int = Field(ge=0)

