from fastapi import FastAPI
from pydantic import BaseModel

from src.core.load import load


app = FastAPI()


class MessagePayload(BaseModel):
    id: int
    user: str
    message: str


@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/send")
async def send_message(payload: MessagePayload):
    await load(payload.model_dump_json())

    return {
        "status": "envoyé"
    }
