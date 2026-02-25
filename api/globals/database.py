from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .constants import DB_URL, SQL_ECHO

engine = create_engine(DB_URL, echo=SQL_ECHO)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
