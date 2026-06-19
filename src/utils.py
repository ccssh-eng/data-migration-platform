import os
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(name):
    value = os.getenv(name)
    if not value:
        raise Exception(f"Variable env manquante: {name}")
    return value


