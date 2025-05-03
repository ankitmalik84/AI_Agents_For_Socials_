from fastapi import HTTPException
from twilio.rest import Client
from app.config import settings

# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

async def send_whatsapp_message(to_number: str, message: str):
    """Send a message through WhatsApp"""
    try:
        # Remove any existing 'whatsapp:' prefix and format numbers
        to_number = to_number.replace('whatsapp:', '')
        from_number = settings.TWILIO_PHONE_NUMBER.replace('whatsapp:', '')
        
        # Create message with proper WhatsApp formatting
        message = twilio_client.messages.create(
            body=message,
            from_=f'whatsapp:{from_number}',
            to=f'whatsapp:{to_number}'
        )
        print(f"Message sent successfully to {to_number} with SID: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        print(f"Attempted to send from: whatsapp:{from_number} to: whatsapp:{to_number}")
        raise HTTPException(status_code=500, detail=str(e)) 