from fastapi import APIRouter, HTTPException, status, Depends
from .. import models, database, utils, oauth2
from sqlmodel import select
from .websocket import manager
from typing import List

router = APIRouter(
    tags = ["user"],
    prefix="/users"
)

@router.get("/active", response_model=List[models.ActiveUsers])
async def get_active_users(current_user= Depends(oauth2.get_current_user)):
    active_users: List[models.ActiveUsers] = []
    for conn in list(manager.active_connections.values()):
        con = next(iter(conn))
        active_users.append(models.ActiveUsers(user_id=con.user_id ,username = con.username))
    return active_users

@router.post("/", response_model=models.UserResponse)
def register_user(db: database.SessionLocal, user_data : models.UserCreate):
    user = db.exec(select(models.User).where(models.User.email == user_data.email)).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User already exists with that email: {user.email}.")
    
    user_data.password = utils.hash(user_data.password)
    user = models.User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user