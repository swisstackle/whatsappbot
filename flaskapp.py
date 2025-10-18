from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
import os
TWILIO_AUTH_TOKEN = os.environ.get('twilio_auth_token')  # Keep this secret!
ACCOUNT_SID = os.environ.get('accountsid') 


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    # Extract the sender's WhatsApp number
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    signature = request.headers.get('X-Twilio-Signature', '')
    url = request.url
    post_vars = request.form.to_dict()
    if not validator.validate(url, post_vars, signature):
        return 'bad'  # Forbidden

  #  client = Client(ACCOUNT_SID, TWILIO_AUTH_TOKEN)
   # client.messages.create({
    #    messagingServiceSid: 'MGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    #    to='whatsapp:+17164286677',
    #    content_sid: 'HXb5b62575e6e4ff6129ad7c8efe1f983e', // your template SID
    #    content_variables: JSON.stringify({1: 'I have to pick up my son'}),
    #    schedule_type: 'fixed',
    #    send_at: '2025-10-05T16:00:00Z'
    #});
    sender = request.form.get('From')  # e.g., 'whatsapp:+1234567890'

    # Extract the message body
    message_body = request.form.get('Body')

    resp = MessagingResponse()
    resp.message(f"Received from {sender}: {message_body}")

    # Return the TwiML (as XML) response
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
