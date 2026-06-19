import pandas as pd
from azure.storage.blob import BlobClient
from src.auth import credential
from io import BytesIO


def extract(blob_url):

    blob_client = BlobClient.from_blob_url(
        blob_url,
        credential=credential
    )

    print(
        f"CREDENTIAL_TYPE={type(credential).__name__}",
        flush=True
    )

    print(
        f"BLOB_URL={blob_url}",
        flush=True
    )

    data = blob_client.download_blob().readall()

    return pd.read_csv(
        BytesIO(data)
    )
