from pydantic import BaseModel,EmailStr
from .enums import CapitalAction
from typing import Union, Optional
from decimal import Decimal


#Schema for storing token data
class TokenData(BaseModel):
     id: Optional[int]=None

#Schema for user registration
class User(BaseModel):
     email:EmailStr
     password_hash:str
     is_admin:Optional[bool]=False

#Schema for amount deposit
class Capital(BaseModel):
     action:CapitalAction
     amount:Union[int,Decimal]

#Schema for withdrawal request
class Withdraw(BaseModel):
     amount:Union[int,Decimal]

#Schema for Withdrawal Approval
class Decide(BaseModel):
     status:str
#Schema for sending back token
class Token(BaseModel):
    access_token : str
    token_type : str
    
    class Config:
         from_attributes = True

#schema for sending user registeration data
class Send_user(BaseModel):
     id:int
     email:EmailStr
     class Config:
         from_attributes = True
     
#Schema for sending capital History
class Send_Capital(BaseModel):
     amount:Union[int,Decimal]
     created_at:str
     user:Send_user
     class Config:
         from_attributes = True
#Schema for withdrawal response
class Send_Withdrawal_Info(BaseModel):
     amount:Union[int,Decimal]
     status:str
     created_at:str
     user:Send_user
     class Config:
         from_attributes = True
#Schema for sending updated withdrawal status
class updated_withdrawal(BaseModel):
     amount:float
     status:str
     decided_at_ms:int
     class Config:
         from_attributes = True