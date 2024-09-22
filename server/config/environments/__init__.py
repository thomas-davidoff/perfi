import os
from dotenv import load_dotenv
from .development import DevelopmentConfig
from .default import Config
import warnings


ENVIRONMENTS = {"development": DevelopmentConfig}


def load_env(environment):
    # Get path of env file for environment
    env_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    env_file = os.path.abspath(os.path.join(env_dir, f".env.{environment}"))

    # Load environment file
    if not os.path.exists(env_file):
        raise RuntimeError(f"Dot file for environment {environment} does not exist.")
    else:
        load_dotenv(env_file)


# get the configuration
def load_configuration(environment):
    if environment in ENVIRONMENTS:
        return ENVIRONMENTS[environment]()
    else:
        msg = f"""
The provided environment does not have a corresponding configuration: {environment}.

Falling back to default configuration at config/environments/default.py

Available environments are:
    - {", ".join([env for env in ENVIRONMENTS.keys()])}

To create a new configuration:
    - Create a configuration at config/environments/{environment}.py
    - Import the configuration in this file @ {os.path.abspath(__file__)}
    - Add the configuration to `load_configuration()` for the specified env.
        """
        warnings.warn(msg, UserWarning)
        return Config()


# Get the flask environment
environment = os.environ["FlASK_ENV"]
load_env(environment)
configuration = load_configuration(environment)
