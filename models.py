from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Double
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
    phone_number = Column(String(225))
    address_id = Column(Integer, ForeignKey('address.id'), nullable=True)

    todos = relationship('Todos', back_populates='owner')
    address = relationship('Address', back_populates='user_address')


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(225))
    amount = Column(Double)
    description = Column(String(225))
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('Users', back_populates='todos')


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, index=True)
    apt_num = Column(Integer)  # alembic
    address1 = Column(String(255))
    address2 = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))
    postalcode = Column(String(255))

    user_address = relationship('Users', back_populates='address')
