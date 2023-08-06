from enum import Enum
from typing import Optional

from fastapi import FastAPI

app = FastAPI(host="0.0.0.0")

BOOKS = {
    'book_1': {'title': 'Title One', 'author': 'Author One'},
    'book_2': {'title': 'Title Two', 'author': 'Author Two'},
    'book_3': {'title': 'Title Three', 'author': 'Author Three'},
    'book_4': {'title': 'Title Four', 'author': 'Author Four'},
    'book_5': {'title': 'Title Five', 'author': 'Author Five'},
    'book_6': {'title': 'Title Six', 'author': 'Author Six'},
}


class DirectionName(str, Enum):
    north = 'North'
    south = 'South'
    east = 'East'
    west = 'West'


@app.get("/")
async def read_all_books(skip_book: Optional[str] = None):
    if skip_book:
        books_copy = BOOKS.copy()
        del books_copy[skip_book]
        return books_copy
    return BOOKS


@app.get('/directions/{direction_name}')
async def get_direction(direction_name: DirectionName):
    if direction_name == DirectionName.north:
        return {'Direction': direction_name, 'Sub': 'Up'}
    if direction_name == DirectionName.south:
        return {'Direction': direction_name, 'Sub': 'Down'}
    if direction_name == DirectionName.west:
        return {'Direction': direction_name, 'Sub': 'Left'}
    if direction_name == DirectionName.east:
        return {'Direction': direction_name, 'Sub': 'Right'}


@app.get("/book/{book_title}")
async def read_book(book_title):
    return BOOKS[book_title]


@app.post('/')
async def create_book(book_title, book_author):
    current_book_id = 0
    if len(BOOKS) > 0:
        for book in BOOKS:
            x = int(book.split('_')[-1])
            if x > current_book_id:
                current_book_id = x
    current_book_id += 1
    BOOKS[f'book_{current_book_id}'] = {'title': book_title, 'author': book_author}
    return BOOKS[f'book_{current_book_id}']


@app.put('/{book_name}')
async def update_book(book_name: str, book_title: str, book_author: str):
    book_info = {'title': book_title, 'author': book_author}
    BOOKS[book_name] = book_info
    return book_info


@app.delete('/{book_name}')
async def delete_book(book_name):
    del BOOKS[book_name]
    return f'{book_name} deleted.'


@app.get('/assignment/')
async def read_book_by_name(book_name: str):
    return BOOKS[book_name]


@app.delete('/assignment/')
async def read_book_by_name(book_name: str):
    del BOOKS[book_name]
    return f'{book_name} deleted.'
