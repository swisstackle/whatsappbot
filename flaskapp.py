import os
import logging
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Use conventional, uppercase env var names and safe defaults
TWILIO_AUTH_TOKEN = os.getenv("twilio_auth_token", "")
ACCOUNT_SID = os.getenv("accountsid", "")
client = Client(ACCOUNT_SID, TWILIO_AUTH_TOKEN)
conversation = client.conversations.v1.conversations.create(
    friendly_name="My WhatsApp Group",
    timers_inactive="PT0S",
    timers_closed="PT0S" 
)
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not TWILIO_AUTH_TOKEN:
    logger.warning("TWILIO_AUTH_TOKEN not set. Twilio request validation will be skipped. "
                   "Set TWILIO_AUTH_TOKEN in environment for production.")

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/", methods=["GET", "POST"])
def hello_world():
    # Only validate Twilio signature for POST (webhooks). Skip if token missing.
    if request.method == "POST" and TWILIO_AUTH_TOKEN:
        signature = request.headers.get("X-Twilio-Signature", "")
        validator = RequestValidator(TWILIO_AUTH_TOKEN)
        url = request.url
        post_vars = request.form.to_dict()
        if not validator.validate(url, post_vars, signature):
            logger.warning("Twilio signature validation failed for %s", url)
            return "Forbidden", 403
    
    sender = request.form.get("From")  # e.g., 'whatsapp:+1234567890'
    message_body = request.form.get("Body", "")

    resp = MessagingResponse()
    resp.message(f"Received from {sender}: {message_body}")

    return Response(str(resp), mimetype="text/xml")

@app.route("/add_to_group", methods=["POST"])
def add_to_group():
    data = request.form  # Changed from request.json to request.form
    conversation_sid = conversation.sid
    user_whatsapp = data.get("user_whatsapp")
    print(f"Adding {user_whatsapp} to conversation {conversation_sid}")
    twilio_whatsapp = "whatsapp:+15558375988"
    user_whatsapp_whole = user_whatsapp if user_whatsapp.startswith("whatsapp:") else f"whatsapp:{user_whatsapp}"
    participant = client.conversations.v1.conversations(conversation_sid).participants.create(
        messaging_binding_address=user_whatsapp_whole,
        messaging_binding_proxy_address=twilio_whatsapp
    )
    return {"participant_sid": participant.sid}, 201

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("listening on", port)
    app.run(host="0.0.0.0", port=port)
