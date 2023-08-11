from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True)
    username = Column(String(200), unique=True, index=True)
    first_name = Column(String(200))
    last_name = Column(String(225))
    hashed_password = Column(String(225))
    is_active = Column(Boolean, default=True)

    todos = relationship('Todos', back_populates='owner')


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(225))
    description = Column(String(225))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('Users', back_populates='todos')
