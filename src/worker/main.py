import os
import json
import time
import signal
import logging

from azure.servicebus import ServiceBusClient, TransportType, ServiceBusReceiveMode
from src.db import get_engine
from src.config import settings
from src.core.extract import extract
from src.core.transform import transform
from src.core.load import load_to_sql
from src.auth import credential
from src.core.idempotency import build_file_id, already_processed
from src.core.exceptions import ValidationError

logging.basicConfig(level=logging.INFO)
logging.info(f"MI_CLIENT_ID={os.getenv('MANAGED_IDENTITY_CLIENT_ID')}")
logging.warning("WORKER STARTED")

namespace = os.environ["SERVICEBUS_NAMESPACE"]


# Timeout helper
class SettlementTimeoutError(Exception):
    pass

def _timeout_handler(signum, frame):
    raise SettlementTimeoutError("Settlement timeout")

def safe_dead_letter(receiver, message, reason, description, timeout=10):
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout)
    try:
        logging.warning(f"AVANT DLQ — delivery_count={message.delivery_count} locked_until={message.locked_until_utc}")
        receiver.dead_letter_message(
            message,
            reason=reason,
            error_description=description
        )

        logging.warning(f"DLQ OK: {reason}")
    except SettlementTimeoutError:
        logging.error("dead_letter_message timeout — abandon")
        receiver.abandon_message(message)
    except Exception as e:
        logging.error(f"DLQ ERREUR: {e}")
        raise
    finally:
        signal.alarm(0)

def safe_complete(receiver, message, timeout=10):
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout)
    try:
        receiver.complete_message(message)
        logging.warning("COMPLETE OK")
    except SettlementTimeoutError:
        logging.error("complete_message timeout — abandon")
        receiver.abandon_message(message)
    finally:
        signal.alarm(0)


def process_message(msg):

    body = json.loads(
        b"".join(bytes(part) for part in msg.body).decode("utf-8")
    )

    logging.warning(f"BODY={body}")

    blob_url = body.get("data", {}).get("url")

    if not blob_url:
        raise ValidationError("Il manque blob_url")

    if not blob_url.startswith("https://") or ".blob.core.windows.net" not in blob_url:
        raise ValidationError(f"blob_url invalide: {blob_url}")

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
    while True:
        try:
            client = ServiceBusClient(
                fully_qualified_namespace=namespace,
                credential=credential,
                transport_type=TransportType.AmqpOverWebsocket,
                keep_alive=30
            )
            with client:
                receiver = client.get_subscription_receiver(
                    topic_name=settings.TOPIC_NAME,
                    subscription_name=settings.SUBSCRIPTION_NAME,
                    max_wait_time=30,
                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK
                )
                with receiver:
                    logging.warning("RECEPTEUR OUVERT")

                    for message in receiver:
                        logging.warning("MESSAGE RECU")

                        try:
                            process_message(msg=message)

                        except ValidationError as e:
                            logging.warning(f"MESSAGE POISON: {e}")
                            safe_dead_letter(
                                receiver, message,
                                reason="ValidationError",
                                description=str(e)
                            )

                        except Exception as e:
                            logging.exception("Le traitement a échoué")
                            logging.warning(f"delivery_count={message.delivery_count}")
                            if message.delivery_count >= 10:
                                safe_dead_letter(
                                    receiver, message,
                                    reason="MaxRetriesExceeded",
                                    description=str(e)
                                )
                            else:
                                receiver.abandon_message(message)

                        else:
                            safe_complete(receiver, message)

        except Exception as e:
            logging.exception(f"CONNEXION PERDUE — reconnexion dans 5s : {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

