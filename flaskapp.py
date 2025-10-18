import os
import logging
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator

# Use conventional, uppercase env var names and safe defaults
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
ACCOUNT_SID = os.getenv("ACCOUNT_SID", "")

app = Flask(__name__)

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print("listening on", port)
    app.run(host="0.0.0.0", port=port)
