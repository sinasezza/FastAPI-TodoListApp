from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.responses import HTMLResponse, RedirectResponse

from .. import config, models
from ..config import templates
from ..database import SessionLocal

router = APIRouter(prefix="/auth", tags=["auth"])


SECRET_KEY = config.JWT_SECRET_KEY
ALGORITHM = config.JWT_ALGORITHM

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(SimpleUser):
    def __init__(self, username: str, user_id: int):
        super().__init__(username)
        self.id = user_id

    @property
    def is_authenticated(self) -> bool:
        return True


class JWTAuthenticationBackend(AuthenticationBackend):
    async def authenticate(self, request):
        user = await get_current_user(request)
        if user:
            return AuthCredentials(["authenticated"]), User(
                user["username"], user["id"]
            )
        return None


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, expires_delta: Optional[timedelta] = None
):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/token/")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos/", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(
            response=response, form_data=form, db=db
        )

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse(
                "login.html", {"request": request, "msg": msg}
            )
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse(
            "login.html", {"request": request, "msg": msg}
        )


@router.get("/logout/")
async def logout(request: Request):
    response: Response = RedirectResponse(
        url="/auth/", status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie(key="access_token")
    return response


@router.get("/register/", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    validation1 = (
        db.query(models.Users).filter(models.Users.username == username).first()
    )

    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse(
            "register.html", {"request": request, "msg": msg}
        )

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname

    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/change-password/", response_class=HTMLResponse)
async def change_password_page(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("change-password.html", {"request": request})


@router.get("/profile/", response_class=HTMLResponse)
async def get_user_profile(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    profile = db.query(models.Users).filter(models.Users.id == user["id"]).first()

    if profile is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    context = {"request": request, "user": user, "profile": profile}

    return templates.TemplateResponse("profile.html", context=context)


@router.get("/edit-profile/", response_class=HTMLResponse)
async def edit_profile_page(request: Request, db: Session = Depends(get_db)):
    user_data = await get_current_user(request)
    if user_data is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    # Fetch full user details from the database
    user = db.query(models.Users).filter(models.Users.id == user_data["id"]).first()

    return templates.TemplateResponse(
        "edit-profile.html", {"request": request, "user": user}
    )


@router.post("/edit-profile/", response_class=HTMLResponse)
async def edit_profile(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    db: Session = Depends(get_db),
):
    user_data = await get_current_user(request)
    if user_data is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    user = db.query(models.Users).filter(models.Users.id == user_data["id"]).first()

    # validating username and email for uniqueness
    if username != user.username:
        validation = (
            db.query(models.Users).filter(models.Users.username == username).first()
        )
        if validation is not None:
            return templates.TemplateResponse(
                "edit-profile.html",
                {
                    "request": request,
                    "user": user,
                    "error": "Username already exists",
                    "form_data": {
                        "email": email,
                        "username": username,
                        "firstname": firstname,
                        "lastname": lastname,
                    },
                },
            )

    if email != user.email:
        validation = db.query(models.Users).filter(models.Users.email == email).first()
        if validation is not None:
            return templates.TemplateResponse(
                "edit-profile.html",
                {
                    "request": request,
                    "user": user,
                    "error": "Email already exists",
                    "form_data": {
                        "email": email,
                        "username": username,
                        "firstname": firstname,
                        "lastname": lastname,
                    },
                },
            )

    user.email = email
    user.username = username
    user.first_name = firstname
    user.last_name = lastname

    db.commit()

    return templates.TemplateResponse(
        "edit-profile.html",
        {"request": request, "user": user, "success": "Profile updated"},
    )


@router.post("/change-password/", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    if new_password != confirm_password:
        return templates.TemplateResponse(
            "change-password.html",
            {"request": request, "error": "New passwords do not match"},
        )

    user_model = db.query(models.Users).filter(models.Users.id == user["id"]).first()
    if not verify_password(current_password, user_model.hashed_password):
        return templates.TemplateResponse(
            "change-password.html",
            {"request": request, "error": "Current password is incorrect"},
        )

    user_model.hashed_password = get_password_hash(new_password)
    db.commit()

    return templates.TemplateResponse(
        "change-password.html",
        {"request": request, "success": "Password changed successfully"},
    )
