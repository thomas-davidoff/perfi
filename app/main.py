from config.initializers import initialize_all

initialize_all()

from fastapi import FastAPI
from app.api.v1 import router as V1Router
from app.api.exception_handlers import register_exception_handlers


app = FastAPI(title="Perfi")

app.include_router(router=V1Router)


register_exception_handlers(app)
