from fastapi import APIRouter, HTTPException, Path, Query, Depends
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext
from ..database import SessionLocal
from .. import schemas
from .. import models
from .auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(
    schemes=[
        "bcrypt",
    ],
    deprecated="auto",
)


@router.get("/info/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed."
        )

    return db.query(models.Users).filter(models.Users.id == user.get("id")).first()


@router.post("/change-pass/", status_code=status.HTTP_202_ACCEPTED)
async def change_password(
    user: user_dependency, db: db_dependency, userPass: schemas.UserVerificationPassword
):
    if user is None:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed."
        )

    user_model = (
        db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    )

    if not bcrypt_context.verify(userPass.password, user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password Change."
        )

    user_model.hashed_password = bcrypt_context.hash(userPass.new_password)
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return