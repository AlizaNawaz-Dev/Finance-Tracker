from fastapi import APIRouter,Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import  select
from app import schemas,models,enums
from core import databases,auth
from sqlalchemy.ext.asyncio import AsyncSession
from . import jwt_auth
from datetime import datetime
from typing import Optional


router=APIRouter(prefix='/user',
    tags=["Users"])


# GET /me/history?type=&page=&limit= –
# list own CapitalHistory and/or WithdrawalRequests with basic filtering/pagination.

#Deposit Money
@router.post('/deposit',response_model=schemas.Send_Capital)
async def deposit(capital:schemas.Capital,db: AsyncSession=Depends(databases.get_db),current_user: int= Depends(auth.Get_Current_User)):
    if capital.action.value=='DEPOSIT':
       result = models.CapitalHistory(**capital.model_dump(),user=current_user.id)
       db.add(result)
       await db.commit()
       await db.refresh(result)
       user_query= await db.execute(select(models.User).where(models.User.id==current_user.id))
       return schemas.Send_Capital(
            amount=result.amount,
            created_at=datetime.fromtimestamp(result.created_at_ms / 1000).isoformat(),
            user=result.owner
        )

#Withdrawing Amount
@router.post('/withdraw',response_model=schemas.Send_Withdrawal_Info)
async def withdraw(data:schemas.Withdraw,db: AsyncSession=Depends(databases.get_db),current_user: int= Depends(auth.Get_Current_User)):
       result = models.WithdrawalRequest(**data.model_dump(),user_id=current_user.id,status=enums.WithdrawalStatus.PENDING.value)
       db.add(result)
       await db.commit()
       await db.refresh(result)
       user_query= await db.execute(select(models.User).where(models.User.id==current_user.id))
       return schemas.Send_Withdrawal_Info(
            amount=result.amount,
            status=result.status,
            created_at=datetime.fromtimestamp(result.created_at_ms / 1000).isoformat(),
            user=result.owner
       )
#To get user based on their action performed
@router.get('/history')
async def get_history(db: AsyncSession=Depends(databases.get_db),current_user: int= Depends(auth.Get_Current_User),type: Optional[str] = None, limit: int = 10,page: int = Query(1, ge=1),):
     offset = (page - 1) * limit
     if type=='DEPOSIT':
        user_query= await db.execute(select(models.CapitalHistory).where(models.CapitalHistory.user==current_user.id).offset(offset).limit(limit))
        user=user_query.scalars().all()
        return user
     if type=='WITHDRAW':
        user_query= await db.execute(select(models.WithdrawalRequest).where(models.WithdrawalRequest.user_id==current_user.id).offset(offset).limit(limit))
        user=user_query.scalars().all()
        return user
     
     else:
        return "Invalid Type"
     