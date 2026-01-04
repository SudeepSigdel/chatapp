from jose import jwt, JWTError
from fastapi.security.oauth2 import OAuth2PasswordBearer
from .config import settings
from . import database, models
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRATION_TIME = settings.access_token_expiration_time

def create_access_token(payload: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
    payload.update({"exp":expire})
    token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
    return token

def verify_token(token: str, credential_error):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        user_id : int = payload["user_id"]
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed")
        
    except JWTError:
        raise credential_error
    
    return user_id

def get_current_user(db: database.SessionLocal, token: str =Depends(oauth2_scheme)):
    credential_error = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Couldn't Validate Token", headers={"WWW_Authenticate": "Bearer"})

    user_id = verify_token(token, credential_error)
    
    user = db.get(models.User, user_id)

    return user