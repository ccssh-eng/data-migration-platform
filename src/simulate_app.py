import asyncio
import json
import random

from src.core.load import load


async def simulate():
    for i in range(10):
        payload = {
            "test": "dlq"
        }

        await load(json.dumps(payload))

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(simulate())
