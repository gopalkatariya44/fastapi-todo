from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Form, Header
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import JSONResponse

app = FastAPI(host="0.0.0.0")


class NegativeNumberException(Exception):
    def __init__(self, return_books):
        self.return_books = return_books


class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(title='Description of the book', min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)

    class Config:
        schema_extra = {
            'example': {
                'id': '3fa87f64-5717-4562-b3fc-2c963f66afa6',
                'title': 'AI & ML',
                'author': 'Gopal',
                'description': 'this is my first book',
                'rating': 90
            }
        }


class BookNoRating(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str
    description: Optional[str] = Field(title='Description of the book', min_length=1, max_length=100)


BOOKS = []


@app.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request,
                                            exception: NegativeNumberException):
    return JSONResponse(
        status_code=418,
        content={
            'message': f'Hey, why do you want {exception.return_books} '
                       f'books? You need to read more!'
        }
    )


@app.post('/books/login')
async def books_login(username: str = Form(...), password: str = Form(...)):
    return {'username': username, 'password': password}


@app.get('/header')
async def read_header(random_header: Optional[str] = Header(None)):
    return {'Random-Header': random_header}


@app.get("/")
async def read_all_books(return_books: Optional[int] = None):
    if return_books:
        if return_books < 0:
            raise NegativeNumberException(return_books=return_books)
    create_book_no_api()
    if return_books and len(BOOKS) >= return_books > 0:
        i = 1
        new_books = []
        while i <= return_books:
            new_books.append(BOOKS[i - 1])
            i += 1
        return new_books
    return BOOKS


@app.get('/book/{book_id}')
async def read_book(book_id: UUID):
    for b in BOOKS:
        if b.id == book_id:
            return b
    raise raise_book_not_found()


@app.get('/book/rating/{book_id}', response_model=BookNoRating)
async def read_book_no_rating(book_id: UUID):
    for b in BOOKS:
        if b.id == book_id:
            return b
    raise raise_book_not_found()


@app.put('/{book_id}')
async def update_book(book_id: UUID, book: Book):
    c = 0
    for b in BOOKS:
        if b.id == book_id:
            BOOKS[c] = book
            return book
        else:
            c += 1
    raise raise_book_not_found()


@app.delete('/{book_id}')
async def update_book(book_id: UUID):
    c = 0
    for b in BOOKS:
        if b.id == book_id:
            del BOOKS[c]
            return f'{book_id} deleted.'
        else:
            c += 1
    raise raise_book_not_found()


@app.post('/', status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    BOOKS.append(book)
    print(BOOKS)
    return book


def create_book_no_api():
    if len(BOOKS) < 1:
        for i in range(1, 5):
            BOOKS.append(
                Book(id=f'3fa8{i}f64-5717-4562-b3fc-2c963f66afa6',
                     title=f'Title {i}',
                     author=f'Author {i}',
                     description=f"Description {i}",
                     rating=f'{i}0')
            )


def raise_book_not_found():
    return HTTPException(status_code=404, detail='Book not found.',
                         headers={'X-Header-Error': 'Nothing to be seen at the UUID'})
