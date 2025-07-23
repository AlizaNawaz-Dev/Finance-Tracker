from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from routers import jwt_auth,users,admins
from core import databases,utils
from sqlalchemy import select
from . import models
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    db=None
    try:
        db: AsyncSession = databases.SessionLocal()
        async with databases.engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        admin_exists = await db.scalar(select(models.User).filter(models.User.email == "admin@example.com"))
        if not admin_exists:

            password = utils.hashing("adminpassword")
            admin_user = models.User(
                email="admin@example.com",
                is_admin=True,
                password_hash=password
            )
            db.add(admin_user)
            await db.commit()
        else:    
            print ("Admin Already Exists")
        user_exists = await db.scalar(select(models.User).filter(models.User.email == "user@example.com"))
        if not user_exists:
            normal_password_hash = utils.hashing("userpassword")
            normal_user = models.User(
                email="user@example.com",
                password_hash=normal_password_hash,
            )
            db.add(normal_user)
            await db.commit()
        else:    
            print ("User Already Exists")
        yield
    except Exception as e:
        if db:
            await db.rollback()
        raise 
    finally:
        if db:
            await db.close()
            print("DB session closed.")
     

app = FastAPI(title="Finance Tracker",lifespan=lifespan)
app.include_router(jwt_auth.router)
app.include_router(users.router)
app.include_router(admins.router)















