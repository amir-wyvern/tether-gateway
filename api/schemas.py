from pydantic import BaseModel, EmailStr, Field
from typing import List, Union
from datetime import datetime


class UpdateConfig(BaseModel):

    withdraw_lock: bool
    deposit_lock: bool
    transfer_lock: bool
    transfer_fee_percentage: float = Field(ge=0)
    withdraw_fee_percentage: float = Field(ge=0)
    min_user_balance: float = Field(ge=0)
    referal_bonus_percentage: float = Field(ge=0)


# Withdraw modeles
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
    origin_phone_number: str = Field(min_length=1, max_length=100)

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






# User
class UserBase(BaseModel):

    tel_id : int

class UserUpdateProfile(BaseModel):

    phone_number:str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
    email:  Union[EmailStr, None] 
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)

class UserRegister(BaseModel):

    tel_id: Union[int, None] = Field(ge=0)
    phone_number:str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
    password: str = Field(min_length=1, max_length=200)
    email: Union[EmailStr, None] 
    referal_link: Union[str, None] = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    lastname: str = Field(min_length=1, max_length=100)

class UserLogin(BaseModel):

    phone_number: str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
    password: str = Field(min_length=1, max_length=100)

class UserAuthResponse(BaseModel):

    access_token: str
    type_token: str

class UserDisplay(BaseModel):

    tel_id: Union[None, int]
    phone_number: str
    referal_link: str 
    email: Union[None, EmailStr ] = Field(default=None)
    name: str
    lastname: str
    balance: float
    photo: Union[None, str] = Field(default=None)
    number_of_invented: int
    bonus_of_invented: float
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
        

# Deposit
class DepositRequestResponse(BaseModel):

    message: str
    request_id: int

class DepositRequest(BaseModel):

    value: float = Field(gt=0)
    origin_address: str = Field(min_length=1, max_length=100) # check format addrss with Fields

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
class CreateSession(BaseModel):

    token: str = Field(min_length=1, max_length=300)
    user_id: int = Field(ge=0)

class SessionScheme(BaseModel):
    
    token: str = Field(min_length=1, max_length=300)
    user_id: int = Field(ge=0)

# class Message(BaseModel):
#     message: str


# class WithdrawBody(BaseModel):
#     tel_id: int
#     destination_address: str
#     amount: float
#     secret: str
    

# class Status(str, Enum):
#     REQUEST = 'REQUEST'
#     SUBMIT = 'SUBMIT'

# class RequstsModelInDeposit(BaseModel):
#     amount: float = Field(gt=0)
#     origin_address: str = Field(min_length=1, max_length=100)

# class SubmitModelInDeposit(BaseModel):
#     tx_hash: str

# class DepositBody(BaseModel):
#     tel_id: int
#     status: Status
#     arg: Union[RequstsModelInDeposit, SubmitModelInDeposit]
#     secret: str

# class TransferBody(BaseModel):
#     te_id: int
#     destination_phone_number: str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
#     amount: int
#     secret: str

# class RegisterBody(BaseModel):
#     tel_id: int
#     code: int
#     phone_number: str = Field(regex=r"^\+?[0-9]{3}-?[0-9]{6,12}$")
#     name: str
#     lastname: str
#     secret: str


# class ProfileBody(BaseModel):
#     tel_id: int
#     secret: str


# class GenerateCodeBody(BaseModel):
#     tel_id: int
#     secret: str


# class CheckCodeBody(BaseModel):
#     tel_id: int
#     secret: str
#     code: int


# class DepositHistoryBody(BaseModel):
#     tel_id: int
#     secret: str
#     start_time:int
#     end_time:int


# class WithdrawHistoryBody(BaseModel):
#     tel_id: int
#     secret: str
#     start_time:int
#     end_time:int


# class TransferHistoryBody(BaseModel):
#     tel_id: int
#     secret: str
#     start_time:int
#     end_time:int
