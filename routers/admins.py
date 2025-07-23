from fastapi import APIRouter,Depends,status,HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import TIMESTAMP, and_, cast, func, literal, select
from core import databases,auth
from sqlalchemy.ext.asyncio import AsyncSession
from app import models,enums,schemas
from datetime import datetime, timezone
from sqlalchemy import extract
router=APIRouter(prefix='/admin',
                 tags=["Admins"])

#To get stats of current month
@router.get('/stats/currentmonth')
async def get_stats(db: AsyncSession=Depends(databases.get_db),current_user: int= Depends(auth.Get_Current_User)):
      stmt=await db.execute(select(models.User.is_admin).where(models.User.id==current_user.id))
      result=stmt.scalar()
      if result:
        current_month = datetime.now(timezone.utc).month
        
        withdrawal_sum_query = select(func.sum(models.WithdrawalRequest.amount)).where(and_(
                func.extract('month', func.to_timestamp(models.WithdrawalRequest.decided_at_ms / 1000)) == current_month,))
        withdrawal_query = await db.execute(withdrawal_sum_query)
        total_withdraw = withdrawal_query.scalar_one_or_none()

        Deposit_sum_query = select(func.sum(models.CapitalHistory.amount)).where(and_(
                func.extract('month', func.to_timestamp(models.CapitalHistory.created_at_ms / 1000)) == current_month,))
        deposit_query = await db.execute(Deposit_sum_query)
        total_deposit = deposit_query.scalar_one_or_none()

        net_amount=total_deposit-total_withdraw
        return{"total_deposit": total_deposit, "total_withdraw": total_withdraw, "net_flow": net_amount}

      else:
       raise HTTPException(status_code=403,detail="Admin Access Needed")

#To get Withdrawals of pending status
@router.get('/withdrawals')
async def get_withdrawal(db: AsyncSession=Depends(databases.get_db),current_user: int= Depends(auth.Get_Current_User),status:str=" "):
   stmt=await db.execute(select(models.User.is_admin).where(models.User.id==current_user.id))
   result=stmt.scalar()
   if result:
       if status not in enums.WithdrawalStatus:
          return JSONResponse(content="Invalid Status",status_code=406)
       withdraw_query=await db.execute(select(models.WithdrawalRequest).where(models.WithdrawalRequest.status==status))  
       user=withdraw_query.scalars().all()
       if user:
        return user
       else:
        raise HTTPException(status_code=404,detail=f"No Data Found ")
   else:
      raise HTTPException(status_code=403,detail="Admin Access Needed")
   
#To update status and data of user
@router.patch('/withdrawals/{id}',response_model=schemas.updated_withdrawal)
async def updating_withdraw_status(decision:schemas.Decide,id:int,db: AsyncSession=Depends(databases.get_db),current_user: int= Depends(auth.Get_Current_User)):
   stmt=await db.execute(select(models.User.is_admin).where(models.User.id==current_user.id))
   result=stmt.scalar()
   if result:
      withdraw_query=await db.execute(select(models.WithdrawalRequest).where(models.WithdrawalRequest.id==id))  
      user=withdraw_query.scalar_one_or_none()
      if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No request with this id")
    
      if decision.status == enums.WithdrawalStatus.APPROVED.value:
        user.status = enums.WithdrawalStatus.APPROVED.value
        timed=user.decided_at_ms=int(datetime.utcnow().timestamp() * 1000)
       
        db.add(user) 
        await db.commit() 
        await db.refresh(user)
        return schemas.updated_withdrawal(
            amount=user.amount,
            status=decision.status,
            decided_at_ms=timed,
        )
      if not user.status=="APPROVED":
        if decision.status == enums.WithdrawalStatus.REJECTED.value:
        
            timed=user.decided_at_ms=int(datetime.utcnow().timestamp() * 1000)
            user.status="REJECTED"
            db.add(user) 
            await db.commit() 
            await db.refresh(user)
            return schemas.updated_withdrawal(
            amount=user.amount,
            status=decision.status,
            decided_at_ms=timed,
            )
        else:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or unhandled withdrawal status decision: {decision.status}"
         )
      else:
         raise HTTPException(status_code=403,detail="Request Already Approved")
        
    
      
   else:
       raise HTTPException(status_code=403,detail="Admin Access Needed")

      


    