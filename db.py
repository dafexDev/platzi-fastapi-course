from typing import Annotated

from fastapi import FastAPI, Depends
from sqlmodel import Session, create_engine, SQLModel


SQLITE_NAME = "db.sqlite3"
SQLITE_URL = f"sqlite:///{SQLITE_NAME}"


engine = create_engine(SQLITE_URL)


def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
