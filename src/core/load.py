import os
import struct
import traceback
import logging

from sqlalchemy import event, text

from src.db import get_engine
from src.auth import credential
from src.core.idempotency import build_file_id


def load_to_sql(engine, df, blob_url, file_id):

    @event.listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):

        print("DO_CONNECT ENTER", flush=True)

        cargs[0] = cargs[0].replace(";Trusted_Connection=Yes", "")

        print("DEMANDE DE JETON SQL", flush=True)

        token = credential.get_token(
            "https://database.windows.net/.default"
        ).token

        print("JETON ACQUIS", flush=True)

        token_bytes = token.encode("utf-16-le")
        token_struct = struct.pack(
            f"<I{len(token_bytes)}s",
            len(token_bytes),
            token_bytes
        )

        cparams["attrs_before"] = {1256: token_struct}

        print("JETON ATTACHE", flush=True)

    try:
        print("avant engine.connect", flush=True)

        with engine.connect() as conn:
            print("SUCCES DE LA CONNEXION SQL", flush=True)

        print("avant df.to_sql", flush=True)

        df.to_sql(
            "customers",
            engine,
            if_exists="append",
            index=False
        )

        print("TO_SQL REUSSI", flush=True)

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO processed_files (file_id, blob_url)
                    VALUES (:file_id, :blob_url)
                """),
                {"file_id": file_id, "blob_url": blob_url}
            )

        logging.warning(f"{len(df)} lignes insérées")

    except Exception as e:
        print(f"TO_SQL AVAIT ECHOUE: {e}", flush=True)
        traceback.print_exc()
        raise
