from fastapi import APIRouter, HTTPException, status, Depends
from .. import models, database, utils, oauth2
from sqlmodel import select
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags = ["Authentication", "user"]
)

@router.post("/login", response_model=models.TokenResponse)
def login(db: database.SessionLocal, user_data: OAuth2PasswordRequestForm = Depends()):
    user = db.exec(select(models.User).where(models.User.email == user_data.username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    if not utils.verify(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    token = oauth2.create_access_token({"user_id": user.id}) #type: ignore
    return {"access_token":token, "token_type": "bearer"}