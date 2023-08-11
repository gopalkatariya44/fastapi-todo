from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./todos1.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:12345678@localhost/Todos"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3306/todos"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL#, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
