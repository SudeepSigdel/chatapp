from fastapi import APIRouter, HTTPException, status
from .. import models, database, utils
from sqlmodel import select

router = APIRouter(
    tags = ["user"],
    prefix="/users"
)

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