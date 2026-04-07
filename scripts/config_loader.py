import os
from urllib.parse import quote_plus


def get_source_db_url():
    password = quote_plus(os.getenv("SOURCE_DB_PASSWORD", ""))

    return (
        f"{os.getenv('SOURCE_DB_TYPE')}+{os.getenv('SOURCE_DB_DRIVER')}://"
        f"{os.getenv('SOURCE_DB_USER')}:{password}@"
        f"{os.getenv('SOURCE_DB_HOST')}:{os.getenv('SOURCE_DB_PORT')}/"
        f"{os.getenv('SOURCE_DB_NAME')}"
    )


def get_target_db_url():
    password = quote_plus(os.getenv("TARGET_DB_PASSWORD", ""))
    driver = quote_plus(os.getenv("TARGET_DB_ODBC_DRIVER", ""))

    return (
        f"{os.getenv('TARGET_DB_TYPE')}+{os.getenv('TARGET_DB_DRIVER')}://"
        f"{os.getenv('TARGET_DB_USER')}:{password}@"
        f"{os.getenv('TARGET_DB_HOST')}:{os.getenv('TARGET_DB_PORT')}/"
        f"{os.getenv('TARGET_DB_NAME')}?"
        f"driver={driver}"
    )
