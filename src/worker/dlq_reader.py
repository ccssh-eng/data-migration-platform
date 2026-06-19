import json
import logging
import inspect

from azure.servicebus import (
    ServiceBusClient,
    ServiceBusSubQueue
)

from azure.identity import ManagedIdentityCredential
from src.config import settings
from azure.servicebus.management import ServiceBusAdministrationClient

logging.basicConfig(level=logging.INFO)

logging.getLogger("azure").setLevel(logging.ERROR)
logging.getLogger("azure.identity").setLevel(logging.ERROR)
logging.getLogger("azure.core").setLevel(logging.ERROR)
logging.getLogger("azure.servicebus").setLevel(logging.ERROR)


def read_dlq():

    credential = ManagedIdentityCredential(
        client_id=settings.MI_CLIENT_ID
    )

    token = credential.get_token(
        "https://servicebus.azure.net/.default"
    )

    admin = ServiceBusAdministrationClient(
        fully_qualified_namespace=settings.SERVICEBUS_NAMESPACE,
        credential=credential
    )

    runtime = admin.get_subscription_runtime_properties(
        settings.TOPIC_NAME,
        settings.SUBSCRIPTION_NAME
    )

    logging.warning("ACTIVE=%s", runtime.active_message_count)

    logging.warning(
        "DLQ COUNT=%s", 
        runtime.dead_letter_message_count)

    if runtime.dead_letter_message_count > 0:

        logging.error(
            "ALERTE: DLQ contient %s messages",
            runtime.dead_letter_message_count
        )

    else:

        logging.info(
            "DLQ sain: 0 message"
        )

    client = ServiceBusClient(
        fully_qualified_namespace=
        settings.SERVICEBUS_NAMESPACE,
        credential=credential
    )

    with client:

        receiver = client.get_subscription_receiver(
            topic_name=settings.TOPIC_NAME,
            subscription_name=settings.SUBSCRIPTION_NAME,
            sub_queue=ServiceBusSubQueue.DEAD_LETTER
        )

        with receiver:

            messages = receiver.receive_messages(
                max_message_count=10,
                max_wait_time=10
            )

            if not messages:

                logging.info("DLQ est vide")
                return

            for msg in messages:

                logging.info(
                    "------ DLQ MESSAGE ------"
                )

                body = b"".join(
                    bytes(part)
                    for part in msg.body
                ).decode("utf-8")

                logging.info("Body: %s", body)

                logging.info(
                    "DeadLetter Reason: %s",
                    msg.dead_letter_reason
                )

                logging.info(
                    "DeadLetter Error: %s",
                    msg.dead_letter_error_description
                )

                logging.info("Message ID: %s", msg.message_id)
                logging.info("Sequence #: %s", msg.sequence_number)
                logging.info("Enqueued: %s", msg.enqueued_time_utc)
                logging.info("Reason: %s", msg.dead_letter_reason)

                logging.info(
                    "Description: %s",
                    msg.dead_letter_error_description
                )
                logging.info("Body: %s", body)

#                receiver.complete_message(msg)


if __name__ == "__main__":

    read_dlq()

