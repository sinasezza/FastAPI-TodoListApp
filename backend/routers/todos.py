from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Form,
)
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from .. import models, schemas
from ..database import SessionLocal
from .auth import get_current_user
from ..config import templates

router = APIRouter(
    prefix="/todos", tags=["todos"], responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todos).filter(models.Todos.owner_id == 2).all()

    context = {"request": request, "todos": todos}
    return templates.TemplateResponse(name="todos-list.html", context=context)


@router.get("/add-todo/", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.post("/add-todo/", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}/", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int):
    todo = models.Todos(
        id=1,
        title="test1",
        description="test1 description",
        priority=2,
        completed=False,
        owner_id=1,
    )
    return templates.TemplateResponse(
        "edit-todo.html",
        {
            "request": request,
            "todo": todo,
        },
    )


@router.post("/edit-todo/{todo_id}/", response_class=HTMLResponse)
async def edit_todo_commit(
    request: Request,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)



@router.get("/delete/{todo_id}/")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        return RedirectResponse(url="/todos/", status_code=status.HTTP_302_FOUND)

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()

    return RedirectResponse(url="/todos/", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}/", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos/", status_code=status.HTTP_302_FOUND)

