from fastapi import APIRouter, HTTPException, Path, Query, Depends
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated
from ..database import SessionLocal
from .. import schemas
from .. import models


router = APIRouter(prefix="/todos", tags=["todos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(models.Todos).all()


@router.get(
    "/todo/{todo_id}/",
    response_model=schemas.TodosRequest,
    status_code=status.HTTP_200_OK,
)
async def read_todo(
    db: db_dependency, todo_id: int = Path(gt=0, title="The ID of the todo to read")
):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post(
    "/todo/", response_model=schemas.TodosRequest, status_code=status.HTTP_201_CREATED
)
async def create_todo(db: db_dependency, todo: schemas.TodosRequest):
    todo_model = models.Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.put("/todo/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency,
    todo: schemas.TodosRequest,
    todo_id: int = Path(gt=0, title="The ID of the todo to update"),
):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        todo_model.title = todo.title
        todo_model.description = todo.description
        todo_model.priority = todo.priority
        todo_model.completed = todo.completed
        db.add(todo_model)
        db.commit()
        db.refresh(todo_model)
        return
    raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/todo/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    db: db_dependency, todo_id: int = Path(gt=0, title="The ID of the todo to delete")
):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
        return
    raise HTTPException(status_code=404, detail="Todo not found")
