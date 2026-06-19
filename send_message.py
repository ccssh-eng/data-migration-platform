import os
import json
from azure.servicebus import (
    ServiceBusClient,
    ServiceBusMessage
)

from azure.identity import AzureCliCredential

credential = AzureCliCredential()

client = ServiceBusClient(
    fully_qualified_namespace=
        "sb-data-migration-tgt1.servicebus.windows.net",
    credential=credential
)

with client:

    sender = client.get_topic_sender(
        topic_name="etl-topic"
    )

    with sender:
        sender.send_messages(
            ServiceBusMessage(
                '{"test":"dlq"}'
            )
        )

print("Message envoyé !")
