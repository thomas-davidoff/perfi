from config.environments import configuration
from app import create_app

app = create_app(configuration)
