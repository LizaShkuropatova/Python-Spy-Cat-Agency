from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from db import engine
from endpoints import cats, missions

@asynccontextmanager
async def lifespan(_app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Spy Cat Agency", lifespan=lifespan)

app.include_router(cats.router)
app.include_router(missions.router)
