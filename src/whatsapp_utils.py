import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
print(f"💥 Using access token: {WHATSAPP_ACCESS_TOKEN}")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")

logger = logging.getLogger(__name__)


def is_valid_whatsapp_message(body: dict) -> bool:
    try:
        return bool(    
            body.get("entry", [{}])[0]
                .get("changes", [{}])[0]
                .get("value", {})
                .get("messages")
        )
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False


def process_whatsapp_message(body: dict, agent):
    try:
        value = body["entry"][0]["changes"][0]["value"]
        message = value["messages"][0]
        from_id = message["from"]
        text = message["text"]["body"]

        logger.info(f"Processing message from {from_id}: {text}")

        response = agent.run(text)
        text_response = getattr(response, "content", str(response)).strip()

        send_whatsapp_message(to=from_id, message=text_response)
    except Exception as e:
        logger.exception("Error while processing WhatsApp message")


def send_whatsapp_message(to: str, message: str):
    max_length = 4096
    url = f"https://graph.facebook.com/{VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    print("API Token :", WHATSAPP_ACCESS_TOKEN)
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    chunks = [message[i:i + max_length] for i in range(0, len(message), max_length)]

    for i, chunk in enumerate(chunks):
        logger.info(f"Sending chunk {i + 1}/{len(chunks)} - length: {len(chunk)}")
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": chunk}
        }

        response = requests.post(url, json=data, headers=headers)
        logger.info(f"WhatsApp API response [{response.status_code}]: {response.text}")