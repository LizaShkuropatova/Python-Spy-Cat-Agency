from typing import Generator
from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///./spycat.db"
engine = create_engine(DATABASE_URL, echo=False)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
