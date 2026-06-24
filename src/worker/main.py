import os
import json
import logging
import hashlib

from azure.servicebus import ServiceBusClient
from src.db import get_engine
from src.config import settings
from src.core.extract import extract
from src.core.transform import transform
from src.core.load import load_to_sql

from src.auth import credential

from src.core.idempotency import (
    build_file_id,
    already_processed
)

logging.basicConfig(level=logging.INFO)
logging.info(
    f"MI_CLIENT_ID={os.getenv('MANAGED_IDENTITY_CLIENT_ID')}"
)
logging.warning("WORKER STARTED")

namespace = os.environ["SERVICEBUS_NAMESPACE"]

logging.error("WORKER VERSION DLQ TEST 2026-06-22")

def process_message(msg):

    body = json.loads(
        b"".join(bytes(part) for part in msg.body).decode("utf-8")
    )

    logging.warning(f"BODY={body}")

    blob_url = body.get("data", {}).get("url")

    if not blob_url:
        raise ValidationError("Il manque blob_url")

    file_id = build_file_id(blob_url)
    engine = get_engine()

    if already_processed(engine, file_id):
        logging.warning("DEJA TRAITE")
        return

    df = extract(blob_url)
    df = transform(df)

    load_to_sql(engine, df, blob_url, file_id)

    logging.info(f"SUCCES: {len(df)} lignes traitées")

def main():

    client = ServiceBusClient(
        fully_qualified_namespace=namespace,
        credential=credential
    )

    with client:
        receiver = client.get_subscription_receiver(
            topic_name=settings.TOPIC_NAME,
            subscription_name=settings.SUBSCRIPTION_NAME
        )

        with receiver:
            logging.warning("RECEPTEUR OUVERT")

            for message in receiver:
                logging.warning("MESSAGE RECU")

                logging.error("INSIDE LOOP")

                try:
                    # TESTER DLQ DIRECT
                    logging.error("INSIDE NEW LOOP")

                    receiver.dead_letter_message(
                        message,
                        reason="test",
                        error_description="forcer DLQ"
                    )


                except ValidationError as e:
                    logging.warning("MESSAGE POISON")

                    receiver.dead_letter_message(
                        message,
                        reason="test",
                        error_description="forcer DLQ"
                    )

                except Exception as e:
                    logging.exception("Le traitement a échoué")

                    if message.delivery_count >= 10:
                        receiver.dead_letter_message(
                            message,
                            reason="MaxRetriesExceeded",
                            error_description=str(e)
                        )
                else:
                    receiver.abandon_message(message)

if __name__ == "__main__":
    main()

