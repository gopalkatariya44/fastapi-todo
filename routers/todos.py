import sys

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, status
from pydantic import BaseModel, Field

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from routers.auth import get_current_user, get_user_exception

sys.path.append('..')

router = APIRouter(
    prefix='/todos',
    tags=['Todos'],
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Not found'
        }
    }
)

models.Base.metadata.create_all(bind=engine)


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


@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get('/user')
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()


@router.get('/{todo_id}')
async def read_todo(todo_id: int,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = (db.query(models.Todos)
                  .filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id'))
                  .first())
    if todo_model is not None:
        return todo_model
    raise http_exception()


@router.post('/')
async def create_todo(todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get('id')
    print(todo_model.__dict__)
    db.add(todo_model)
    db.commit()

    return {
        'status': 201,
        'transaction': 'Successfully added.'
    }


@router.put('/{todo_id}')
async def update_todo(todo_id: int,
                      todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = (db.query(models.Todos)
                  .filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id'))
                  .first())
    print(todo_model.__dict__)
    if todo_model is None:
        raise http_exception()

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    print(todo_model.__dict__)
    db.add(todo_model)
    db.commit()

    return {
        'status': 200,
        'transaction': 'Successfully updated.'
    }


@router.delete('/{todo_id}')
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = (db.query(models.Todos)
                  .filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id'))
                  .first())
    if todo_model is None:
        raise http_exception()
    (db.query(models.Todos)
     .filter(models.Todos.id == todo_id)
     .filter(models.Todos.owner_id == user.get('id'))
     .delete())
    db.commit()
    return {
        'status': 201,
        'transaction': 'Successfully deleted.'
    }


def http_exception():
    return HTTPException(status_code=404, detail='Todo not Found')
