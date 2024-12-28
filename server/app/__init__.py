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

from .routes import example_router


app = FastAPI()

app.include_router(example_router)
