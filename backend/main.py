from typing import Annotated
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

from .database import SessionLocal, engine
from .models import Base
from .routers import admin, auth, todos, users
from .config import BASE_DIR, templates


app: FastAPI = FastAPI()

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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
