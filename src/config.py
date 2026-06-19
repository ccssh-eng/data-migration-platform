from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    SERVICEBUS_CONNECTION_STRING = os.getenv(
        "SERVICEBUS_CONNECTION_STRING"
    )

    SERVICEBUS_NAMESPACE = os.getenv(
        "SERVICEBUS_NAMESPACE",
        "sb-data-migration-tgt1.servicebus.windows.net"
    )

    MI_CLIENT_ID = os.getenv(
        "MI_CLIENT_ID"
    )

    TOPIC_NAME = os.getenv(
        "TOPIC_NAME",
        "etl-topic"
    )

    SUBSCRIPTION_NAME = os.getenv(
        "SUBSCRIPTION_NAME",
        "etl-sub"
    )

    SQL_SERVER = os.getenv("SQL_SERVER")
    SQL_DATABASE = os.getenv("SQL_DATABASE")

    MAX_RETRY = int(
        os.getenv("MAX_RETRY", "5")
    )


settings = Settings()
