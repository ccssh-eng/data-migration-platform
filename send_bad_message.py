import json
import sys
import time
from azure.identity import AzureCliCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage, TransportType
from src.config import settings

credential = AzureCliCredential(process_timeout=30)

scenario = sys.argv[1] if len(sys.argv) > 1 else "bad"

if scenario == "good":
    payload = {
        "data": {
            "url": "https://stdatamigration0cue2d.blob.core.windows.net/raw/customers_legacy.csv"
        }
    }
elif scenario == "empty":
    payload = {}
else:
    payload = {
        "data": {
            "url": "TEST_DLQ"
        }
    }

print(f"Scénario : {scenario}")
print(f"Payload  : {json.dumps(payload, indent=2)}")

token = credential.get_token("https://servicebus.azure.net/.default")
print(f"TOKEN OK — expire à : {token.expires_on}")

message = ServiceBusMessage(json.dumps(payload))

# Essaie jusqu'à 3 fois
for attempt in range(1, 4):
    try:
        print(f"Tentative {attempt}...")

        client = ServiceBusClient(
            fully_qualified_namespace=settings.SERVICEBUS_NAMESPACE,
            credential=credential,
            retry_total=3,          # essaies internes SDK
            retry_backoff_factor=1,  # attente entre essaies
            transport_type=TransportType.AmqpOverWebsocket  # port 443 au lieu de 5671

        )

        with client:
            sender = client.get_topic_sender(topic_name=settings.TOPIC_NAME)
            with sender:
                sender.send_messages(message)
                print(f"Message envoyé avec succès (tentative {attempt})")
                break  # sortir si succès

    except Exception as e:
        print(f"Tentative {attempt} échouée : {e}")
        if attempt < 3:
            time.sleep(3)
        else:
            print("Abandon après 3 tentatives")
            raise
