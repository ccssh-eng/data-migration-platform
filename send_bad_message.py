import json
from azure.identity import AzureCliCredential
from src.config import settings
from azure.servicebus import (
    ServiceBusClient,
    ServiceBusMessage
)

credential = AzureCliCredential()

payload = {
    "data": {
        "url": "TEST_DLQ"
    }
}

message = ServiceBusMessage(
    json.dumps(payload)
)


token = credential.get_token(
    "https://servicebus.azure.net/.default"
)

print("TOKEN OK")
print(token.expires_on)

print(type(credential))
print(credential)

client = ServiceBusClient(
    fully_qualified_namespace=
    settings.SERVICEBUS_NAMESPACE,
    credential=credential
)

with client:

    sender = client.get_topic_sender(
        topic_name=settings.TOPIC_NAME
    )

    with sender:
        sender.send_messages(message)

print("MAUVAIS MESSAGE ENVOYÉ")

