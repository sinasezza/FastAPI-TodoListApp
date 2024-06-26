from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Base
from .routers import admin, auth, todos, users

app: FastAPI = FastAPI()

Base.metadata.create_all(bind=engine)


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
