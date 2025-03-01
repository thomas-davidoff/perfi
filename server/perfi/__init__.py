# load settings first
from config import get_settings

settings = get_settings()

# logging needs to be configured first
import logging
from logging.config import dictConfig
from pathlib import Path
import yaml

# requires relative logging config file
logging_config_rel_path = "config/logging/logging.yml"
server_directory = Path(__file__).parents[1].resolve()
logging_config_fp = server_directory.joinpath(logging_config_rel_path).resolve()

with open(logging_config_fp, "r") as f:
    dict_config = yaml.safe_load(f)

dictConfig(dict_config)


logger = logging.getLogger(__name__)


from fastapi import FastAPI
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# from .core.database.models import *  # Note: registers models with base.metadata
from .routes import routers
from .core.middleware import (
    log_request,
)
from .core.exc import CustomException


app = FastAPI(
    title="Perfi", description="Personal finance manager", openapi_url="/spec"
)

for router in routers:
    app.include_router(router=router)


app.middleware("http")(log_request)


def make_error(code: int, msg: str):
    return JSONResponse(
        status_code=code,
        content=jsonable_encoder({"error": msg}),
    )


@app.exception_handler(Exception)
async def catch_all_exception_handler(request: Request, exc: Exception):
    return make_error(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "An unhandled internal error occurred"
    )


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logger.error(exc.msg, exc_info=exc)
    return make_error(exc.code, exc.msg)


logger.debug("App initialized successfully.")
