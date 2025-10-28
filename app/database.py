from sqlalchemy.orm import sessionmaker, Session 
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from .config import settings




DATABASE_URL=f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine= create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()