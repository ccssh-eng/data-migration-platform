import os


def get_source_db_url():
    return os.getenv("SOURCE_DB_URL")


def get_target_db_url():
    return os.getenv("TARGET_DB_URL")


print("ENV TEST:", os.getenv("SOURCE_DB_URL"))
