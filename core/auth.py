from jose import JWTError,jwt
from datetime import datetime, timedelta
from app import schemas 
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTE = settings.access_token_expiry_minutes

def Create_Access_Token(data: dict):
    Data = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTE)
    Data.update({"exp":expire})

    encode_jwt = jwt.encode(Data, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt

def Verify_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms = [ALGORITHM])
        id:str = payload.get("id")

        if id is None:
          raise credentials_exception
        token_data=schemas.TokenData(id=id)
       
    except JWTError:
        raise credentials_exception
    return token_data

def Get_Current_User(Token:str=Depends(oauth2_scheme)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail='Credentials are not authorized')
    return Verify_token(Token,credentials_exception)