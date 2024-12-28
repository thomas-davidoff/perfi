import logging
import logging.config
from pathlib import Path
import yaml


logging_config = Path("config/logging/logging.yml")
with open(logging_config, "r") as f:
    dict_config = yaml.safe_load(f)

logging.config.dictConfig(dict_config)

import os
from .init_extensions import init_extensions
from .load_environment import load_configuration, load_env


logger = logging.getLogger(__name__)

environment = os.environ["FLASK_ENV"]
logger.debug(f"Configurating the application for the '{environment}' environment")

load_env(".env")
load_env(f".env.{environment}", override=True)

configuration = load_configuration(environment)
