from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from .. import models, schemas
from ..database import SessionLocal
from .auth import get_current_user
from ..config import templates

router = APIRouter(prefix="/todos", tags=["todos"], responses={404: {"description": "Not found"}})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

    

@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request):
    return templates.TemplateResponse("todos-list.html", {"request": request})


@router.get("/add-todo/", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})



@router.get("/edit-todo/{todo_id}/", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int):
    todo = models.Todos(id=1, title="test1", description="test1 description", priority=2, completed=False, owner_id=1)
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo,})