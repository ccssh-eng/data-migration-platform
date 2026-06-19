import os
import struct

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL

from src.auth import credential


def get_engine():

    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")

    connection_url = URL.create(
        "mssql+pyodbc",
        host=server,
        database=database,
        query={
            "driver": "ODBC Driver 18 for SQL Server",
            "Encrypt": "yes",
            "TrustServerCertificate": "no",
        },
    )

    engine = create_engine(connection_url)

    @event.listens_for(engine, "do_connect")
    def provide_token(
        dialect,
        conn_rec,
        cargs,
        cparams,
    ):
        token = credential.get_token(
            "https://database.windows.net/.default"
        ).token

        token_bytes = token.encode("utf-16-le")

        token_struct = struct.pack(
            f"<I{len(token_bytes)}s",
            len(token_bytes),
            token_bytes
        )

        cargs[0] = cargs[0].replace(
            ";Trusted_Connection=Yes",
            ""
        )

        cparams["attrs_before"] = {
            1256: token_struct
        }

    return engine

