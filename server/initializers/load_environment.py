import os
from dotenv import load_dotenv
import warnings
from config import DevelopmentConfig, TestingConfig, DefaultConfig


ENVIRONMENTS = {"development": DevelopmentConfig, "testing": TestingConfig}


def load_env(env_filename, override=False):
    # Get path of env file for environment
    env_dir = os.path.dirname(os.path.dirname(__file__))
    env_file = os.path.abspath(os.path.join(env_dir, env_filename))

    # Load environment file
    if not os.path.exists(env_file):
        raise RuntimeError(f"Dot file {env_file} does not exist.")

    load_dotenv(env_file, override=override)


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
        return DefaultConfig()
