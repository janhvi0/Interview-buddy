from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
import os
import logging
from dotenv import load_dotenv

from agent_service import get_agent
from whatsapp_utils import is_valid_whatsapp_message, process_whatsapp_message

load_dotenv(dotenv_path=".env", override=True)

logging.basicConfig(level=logging.INFO)   
logger = logging.getLogger(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


app = FastAPI()
agent = get_agent()


@app.get("/")
def read_root():
    return {"message": "Welcome to the WhatsApp Agent Portal."}


@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("WEBHOOK_VERIFIED")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            logger.warning("VERIFICATION_FAILED")
            return JSONResponse(status_code=403, content={"error": "Verification failed"})
    else:
        logger.error("MISSING_PARAMETER")
        return JSONResponse(status_code=400, content={"error": "Missing parameters"})


@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        body = await request.json()
        logger.info(f"Incoming webhook payload: {body}")


        if body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("statuses"):
            logger.info("Received a WhatsApp status update.")
            return {"status": "ok"}


        if is_valid_whatsapp_message(body):
            process_whatsapp_message(body, agent)
            return {"status": "ok"}

        logger.warning("Not a WhatsApp API event")
        return JSONResponse(status_code=404, content={"error": "Not a WhatsApp API event"})

    except Exception as e:
        logger.exception("Error processing webhook")
        return JSONResponse(status_code=400, content={"error": "Invalid payload", "details": str(e)})
