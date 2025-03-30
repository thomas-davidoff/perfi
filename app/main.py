from fastapi import Depends, FastAPI
from app.api.v1.auth import router

from config.initializers import initialize_all

initialize_all()

app = FastAPI()

app.include_router(router=router)
