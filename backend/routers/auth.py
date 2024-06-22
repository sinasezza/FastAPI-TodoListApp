from fastapi import APIRouter
from passlib.context import CryptContext
from .. import models, schemas


router = APIRouter()


bcrypt_context = CryptContext(schemes=['bcrypt',], deprecated='auto')


@router.post("/auth/")
async def create_user(user: schemas.CreateUserRequest):
    user_model = models.Users(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        hashed_password=bcrypt_context.hash(user.password),
        is_active=True
    )
    return user_model