from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from .database import engine, SessionLocal
from . import models
from .routers import auth, todos, admin, users


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

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
