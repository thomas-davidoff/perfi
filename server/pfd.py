from initializers import load_env, load_configuration, get_logger
import os

init_logger = get_logger("init")

environment = os.environ["FLASK_ENV"]
load_env(".env")  # load default env
load_env(f".env.{environment}")

configuration = load_configuration(environment, init_logger)

from app import create_app

app = create_app(configuration, init_logger)
