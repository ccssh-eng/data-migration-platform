import logging
import time

from azure.servicebus import ServiceBusClient
from prometheus_client import start_http_server, Counter
from src.auth import credential

NAMESPACE = "sb-data-migration-tgt1.servicebus.windows.net"
TOPIC = "etl-topic"
SUBSCRIPTION = "etl-sub"

logging.basicConfig(level=logging.INFO)

# Métriques
dlq_messages_total = Counter(
    "dlq_messages_total",
    "Total des messages DLQ traités"
)

def monitor_dlq():

    start_http_server(8001)

    client = ServiceBusClient(
        fully_qualified_namespace=NAMESPACE,
        credential=credential
    )

    with client:

        receiver = client.get_subscription_receiver(
            topic_name=TOPIC,
            subscription_name=SUBSCRIPTION,
            sub_queue="deadletter"
        )

        with receiver:

            logging.warning("LE MONITEUR DLQ A DEMARRE")

            while True:

                messages = receiver.receive_messages(
                    max_message_count=10,
                    max_wait_time=5
                )

                if not messages:
                    logging.info("DLQ est vide")
                    continue

                for msg in messages:

                    body = b"".join(bytes(part) for part in msg.body).decode()

                    logging.error(
                        f"DLQ | reason={msg.dead_letter_reason} "
                        f"| error={msg.dead_letter_error_description} "
                        f"| body={body}"
                    )

                    dlq_messages_total.inc()

                    receiver.complete_message(msg)

                time.sleep(2)


if __name__ == "__main__":
    monitor_dlq()
