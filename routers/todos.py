import sys

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, status, Request, Form
from pydantic import BaseModel, Field

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from routers.auth import get_current_user, get_user_exception

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

sys.path.append('..')

router = APIRouter(
    tags=['Todos'],
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Not found'
        }
    }
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='templates')


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description='The priority must be between 1-5')
    complete: bool


@router.get('/', response_class=HTMLResponse)
async def read_all_by_user(request: Request,
                           db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todos = (db.query(models.Todos)
             .filter(models.Todos.owner_id == user.get('id'))
             .order_by(models.Todos.id).all())
    return templates.TemplateResponse('todo/home.html', {'request': request, 'todos': todos, 'user': user})


@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse('todo/add_todo.html', {'request': request, 'user': user})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo_commit(request: Request,
                             title: str = Form(...),
                             description: str = Form(...),
                             priority: int = Form(...),
                             db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get('id')
    # print(todo_model.__dict__)
    # for i in range(1, 40):
    #     tm = models.Todos()
    #     tm.title = f"Todo {i}"
    #     tm.description = f"Todo description {i}"
    #     tm.priority = 1 if i % 2 == 0 else 4
    #     tm.complete = False if i % 2 == 0 else True
    #     tm.owner_id = user.get('id')
    #     db.add(tm)
    #     db.commit()
    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(todo_id: int,
                    request: Request,
                    db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = (db.query(models.Todos).filter(models.Todos.id == todo_id)
            .filter(models.Todos.owner_id == user.get('id')).first())
    return templates.TemplateResponse('todo/edit_todo.html', {'request': request, 'todo': todo, 'user': user})


@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo_commit(request: Request,
                           todo_id: int,
                           title: str = Form(...),
                           description: str = Form(...),
                           complete: bool = Form(False),
                           priority: int = Form(...),
                           db: Session = Depends(get_db)
                           ):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = (db.query(models.Todos).filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id')).first())
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    print(complete)
    todo_model.complete = complete
    print(todo_model.__dict__)

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/delete/{todo_id}', response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = (db.query(models.Todos).filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id')).first())
    if todo_model is None:
        return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)
    (db.query(models.Todos).filter(models.Todos.id == todo_id)
     .filter(models.Todos.owner_id == 1).delete())
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/complete/{todo_id}', response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = (db.query(models.Todos).filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id')).first())
    todo_model.complete = not todo_model.complete

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
