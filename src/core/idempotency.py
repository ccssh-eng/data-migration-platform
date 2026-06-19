import hashlib
import logging
from sqlalchemy import text


def build_file_id(blob_url):

    return hashlib.sha256(
        blob_url.encode()
    ).hexdigest()


def already_processed(engine, file_id):

    query = text(
        """
        SELECT COUNT(*)
        FROM processed_files
        WHERE file_id = :file_id
        """
    )

    logging.warning("OUVERTURE DE LA CONNEXION SQL")


    with engine.connect() as conn:

        logging.warning("CONNEXION SQL OUVERTE")

        result = conn.execute(
            query,
            {"file_id": file_id}
        )

        logging.warning("REQUETE EXECUTEE")

        value = result.scalar()

        logging.warning("COUNT=%s", value)

        return value > 0


def mark_processed(engine, file_id, blob_url):

    query = text(
        """
        INSERT INTO processed_files
        (
            file_id,
            blob_url
        )
        VALUES
        (
            :file_id,
            :blob_url
        )
        """
    )

    with engine.begin() as conn:

        conn.execute(
            query,
            {
                "file_id": file_id,
                "blob_url": blob_url
            }
        )

