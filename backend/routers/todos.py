from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from ..config import templates
from ..database import SessionLocal
from .. import models
from .auth import get_current_user

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
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

    print(f"todos is : {todos}")

    context = {"request": request, "todos": todos}
    return templates.TemplateResponse("todos-list.html", context=context)


@router.get("/add-todo/", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "add-todo.html", {"request": request, "user": user}
    )


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
    todo_model.completed = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}/", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    context = {"request": request, "todo": todo, "user": user}
    return templates.TemplateResponse("edit-todo.html", context=context)


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

    todo_model = (
        db.query(models.Todos)
        .filter(models.Todos.id == todo_id)
        .filter(models.Todos.owner_id == user.get("id"))
        .first()
    )

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

    todo.completed = not todo.completed

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos/", status_code=status.HTTP_302_FOUND)
