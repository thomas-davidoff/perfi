from config.initializers import initialize_all
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v0 import router as v0Router
from app.api.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_all()
    yield

def create_app():
    app = FastAPI(title="Perfi", lifespan=lifespan)
    app.include_router(router=v0Router)
    register_exception_handlers(app)

    return app


app = create_app()
