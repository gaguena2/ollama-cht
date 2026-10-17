from contextlib import asynccontextmanager

from fastapi import FastAPI

from .dependencies import engine
from .infrastructure.persistence.models import Base
from .interfaces.api.routers import health, webhook


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="ollama-cht", lifespan=lifespan)
app.include_router(health.router)
app.include_router(webhook.router)
