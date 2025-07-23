from fastapi import Depends,HTTPException,APIRouter,status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from core import auth,databases,utils
from sqlalchemy import select
from app import models,schemas

router=APIRouter(prefix="/auth",
                 tags=["Authentication"])

#Registering User
@router.post("/register",response_model=schemas.Send_user)
async def register_user(user_info:schemas.User,db: AsyncSession=Depends(databases.get_db)):
    hashed_password=utils.hashing(user_info.password_hash)
    user_info.password_hash=hashed_password

    result= await db.execute(select(models.User).where(models.User.email==user_info.email))
    data=result.scalars().first()
    if data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User With this email already exists ")
    user = models.User(**user_info.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

#Login User
@router.post("/login",response_model=schemas.Token)
async def login_user(user_info: OAuth2PasswordRequestForm = Depends(),db: AsyncSession=Depends(databases.get_db)):
    result=await db.execute(select(models.User).where(models.User.email == user_info.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    
    if not utils.verify(user_info.password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")
    access_token=auth.Create_Access_Token(data={"id":user.id})
    
    return {"access_token":access_token,"token_type":"bearer"}