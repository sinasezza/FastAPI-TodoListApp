from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from .. import models
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(tags=["admin_api"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role").casefold() not in ("admin", "superuser"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed."
        )

    return db.query(models.Todos).all()


@router.delete("/todo/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0, title="todo id should be greater than 0"),
):
    if user is None or user.get("user_role").casefold() not in ("admin", "superuser"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed."
        )

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is not None:
        db.delete(todo)
        db.commit()
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found.")
