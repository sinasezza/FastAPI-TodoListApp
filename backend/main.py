import models
from fastapi import FastAPI, HTTPException, Path, Query, Depends
from starlette import status
from sqlalchemy.orm import Session
from typing import Optional, Annotated
from database import engine, SessionLocal
from models import Todos
from schemas import TodosRequest


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get(
    "/todo/{todo_id}/", response_model=TodosRequest, status_code=status.HTTP_200_OK
)
async def read_todo(
    db: db_dependency, todo_id: int = Path(gt=0, title="The ID of the todo to read")
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@app.post("/todo/", response_model=TodosRequest, status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo: TodosRequest):
    todo_model = Todos(**todo.model_dump())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@app.put("/todo/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency,
    todo: TodosRequest,
    todo_id: int = Path(gt=0, title="The ID of the todo to update"),
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
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


@app.delete("/todo/{todo_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    db: db_dependency, todo_id: int = Path(gt=0, title="The ID of the todo to delete")
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
        return
    raise HTTPException(status_code=404, detail="Todo not found")
