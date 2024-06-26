from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse

from .. import config, models, schemas
from ..database import SessionLocal

router = APIRouter(tags=["auth_api"])


SECRET_KEY = config.JWT_SECRET_KEY
ALGORITHM = config.JWT_ALGORITHM


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(
    schemes=[
        "bcrypt",
    ],
    deprecated="auto",
)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


async def authenticate_user(
    username: str, password: str, db: Session
) -> models.Users | bool:
    user: models.Users = (
        db.query(models.Users).filter(models.Users.username == username).first()
    )

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    expires = datetime.now(UTC) + expires_delta
    encode = {
        "sub": username,
        "id": user_id,
        "role": role,
        "expires_delta": expires.isoformat(),
    }
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user.",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: schemas.CreateUserRequest):
    user_model = models.Users(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        hashed_password=bcrypt_context.hash(user.password),
        is_active=True,
        phone_number=user.phone_number,
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return user_model


@router.post("/token/", response_model=schemas.Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user: models.Users | None = await authenticate_user(
        form_data.username, form_data.password, db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    return {"access_token": token, "token_type": "bearer"}
