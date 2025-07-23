from core.databases import Base
from sqlalchemy import Integer,String,Boolean,Column,BigInteger,text,ForeignKey,Numeric,Enum
from sqlalchemy.orm import relationship
from . import enums



class User(Base):
    __tablename__='users'

    id=Column(Integer,primary_key=True)
    email=Column(String,nullable=False,unique=True)
    password_hash=Column(String,nullable=False)
    is_admin=Column(Boolean,server_default="False" )
    created_at_ms=Column(BigInteger,server_default=text("(EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT"))

class CapitalHistory(Base):
    __tablename__='capital_history'

   
    id=Column(Integer,primary_key=True)
    action=Column(Enum(enums.CapitalAction, name="capital_action_enum"),nullable=False)
    amount=Column(Numeric(precision=10, scale=5),nullable=False)
    created_at_ms=Column(BigInteger,server_default=text("(EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT"))
    user=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)

    owner=relationship("User")

class WithdrawalRequest(Base):
    __tablename__="withdrawal_request"

    id=Column(Integer,primary_key=True)
    amount=Column(Numeric(precision=10, scale=5),nullable=False)
    status=Column(Enum(enums.WithdrawalStatus, name="withdrawal_status_enum"),nullable=False)
    created_at_ms=Column(BigInteger,server_default=text("(EXTRACT(EPOCH FROM NOW()) * 1000)::BIGINT"))
    decided_at_ms=Column(BigInteger,nullable=True)
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)

    owner=relationship("User")