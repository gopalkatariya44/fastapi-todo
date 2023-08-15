import sys

from fastapi import Depends, HTTPException, APIRouter, Request, Response
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

import models
from database import engine, SessionLocal
from models import Users
from jose import JWTError, jwt
from datetime import datetime, timedelta
import time

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

sys.path.append('..')

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    phone_number: Optional[str]


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='templates')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'user': 'Not authorized'
        }
    }
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get('email')
        self.password = form.get('password')


class RegisterForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.email: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.password2: Optional[str] = None
        self.firstname: Optional[str] = None
        self.lastname: Optional[str] = None

    async def create_register_form(self):
        form = await self.request.form()
        self.email = form.get('email')
        self.username = form.get('username')
        self.password = form.get('password')
        self.password2 = form.get('password2')
        self.firstname = form.get('firstname')
        self.lastname = form.get('lastname')


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return bcrypt_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request):
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            print("us")
            raise get_user_exception()
        return {'username': username, 'id': user_id}
    except JWTError:
        raise get_user_exception()


def authenticate_user(db, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post('/token')
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        return False  # token_exception()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, 'id': user.id},
        expires_delta=access_token_expires)

    response.set_cookie(key='access_token', value=access_token, httponly=True)

    return True  # {"access_token": access_token, "token_type": "bearer"}


@router.get('/', response_class=HTMLResponse)
async def auth_page(request: Request):
    user = await get_current_user(request)
    if user is not None:
        return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('user/login.html', {'request': request})


@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = 'Incorrect Username or Password'
            return templates.TemplateResponse('user/login.html', {'request': request, 'msg': msg})
        return response
    except HTTPException:
        msg = 'Unknown Error'
        return templates.TemplateResponse('user/login.html', {'request': request, 'msg': msg})


@router.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    msg = 'Logout Successful'
    response = templates.TemplateResponse('user/login.html', {'request': request, 'msg': msg})
    response.delete_cookie(key='access_token')
    return response


@router.get('/register', response_class=HTMLResponse)
async def register_page(request: Request):
    user = await get_current_user(request)
    if user is not None:
        return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('user/register.html', {'request': request})


@router.post('/register')
async def create_new_user(request: Request, db: Session = Depends(get_db)):
    form = RegisterForm(request)
    await form.create_register_form()
    user = Users()
    user.email = form.email
    user.username = form.username
    user.first_name = form.firstname
    user.last_name = form.lastname
    user.hashed_password = get_password_hash(form.password)
    # user.phone_number = form.phonenumber
    user.is_active = True

    db.add(user)
    db.commit()

    msg = 'User successfully created'
    response = templates.TemplateResponse('user/login.html', {'request': request, 'msg': msg})
    return response


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
