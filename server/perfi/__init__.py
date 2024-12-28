# logging needs to be configured first
import logging
import logging.config
import logging.handlers
from pathlib import Path
import yaml

# requires relative logging config file
logging_config = Path("config/logging/logging.yml")
with open(logging_config, "r") as f:
    dict_config = yaml.safe_load(f)

logging.config.dictConfig(dict_config)


logger = logging.getLogger(__name__)


from .cli import cli
from fastapi import FastAPI
from .core.database.models import *  # important: registers models with base.metadata


app = FastAPI(title="Perfi", description="Manage yo finances", openapi_url="/spec")


from .routes import routers

for router in routers:
    app.include_router(router=router)

from .core.middleware import app_exception_handler, log_request
from .core.exc import CustomException

app.middleware("http")(log_request)
app.add_exception_handler(
    handler=app_exception_handler, exc_class_or_status_code=CustomException
)


logger.debug("App initialized successfully.")
