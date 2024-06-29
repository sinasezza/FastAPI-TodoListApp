from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.staticfiles import StaticFiles

from .apis import admin as admin_api
from .apis import auth as auth_api
from .apis import todos as todos_api
from .apis import users as users_api
from .config import BASE_DIR, templates
from .database import SessionLocal, engine
from .models import Base
from .routers import admin, auth, todos, users

app: FastAPI = FastAPI()

app.add_middleware(AuthenticationMiddleware, backend=auth.JWTAuthenticationBackend())

Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/healthy/")
async def health_check():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

app.include_router(admin_api.router, prefix="/api/admin")
app.include_router(users_api.router, prefix="/api/users")
app.include_router(auth_api.router, prefix="/api/auth")
app.include_router(todos_api.router, prefix="/api/todos")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
