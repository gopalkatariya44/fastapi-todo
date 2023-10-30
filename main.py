from fastapi import FastAPI
import uvicorn

import models
from database import engine
from routers import auth, todos, users, address
from starlette.staticfiles import StaticFiles

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount('/static', StaticFiles(directory='static'), name='static')


app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(address.router)
app.include_router(users.router)

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
