import os
import logging

from azure.identity import (
    DefaultAzureCredential
)

logging.warning(
    "MANAGED_IDENTITY_CLIENT_ID=%s",
    os.getenv("MANAGED_IDENTITY_CLIENT_ID")
)

credential = DefaultAzureCredential(
    managed_identity_client_id=
    os.getenv("MANAGED_IDENTITY_CLIENT_ID")
)

