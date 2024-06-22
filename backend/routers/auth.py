from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from typing import Annotated
from ..database import SessionLocal
from .. import models, schemas


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt',], deprecated='auto')


def authenticate_user(username: str, password: str, db: Session):
    user: models.Users = db.query(models.Users).filter(models.Users.username == username).first()
    
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/auth/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: schemas.CreateUserRequest):
    user_model = models.Users(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        hashed_password=bcrypt_context.hash(user.password),
        is_active=True
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model



@router.post("/token/")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "failed authentication"
    return "successful authentication"
