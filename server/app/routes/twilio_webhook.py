from fastapi import APIRouter, Request, HTTPException
from twilio.rest import Client
from twilio.request_validator import RequestValidator
import tempfile
import os
from typing import Optional

from app.config import settings
from app.services.rag import process_query
from app.services.vector_store import add_documents
from app.utils.document_processor import extract_text_from_pdf, extract_text_from_docx

router = APIRouter()

# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# Store pending document confirmations
pending_confirmations = {}

async def handle_document_upload(conversation_sid: str, message_sid: str, media_url: str, filename: str) -> None:
    """Handle document upload from WhatsApp"""
    try:
        # Download the file
        response = await twilio_client.conversations.v1.conversations(conversation_sid) \
                                                    .messages(message_sid) \
                                                    .media.download()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name

        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(temp_path)
        elif filename.lower().endswith(('.docx', '.doc')):
            text = extract_text_from_docx(temp_path)
        else:
            raise ValueError("Unsupported file type")

        # Store for confirmation
        pending_confirmations[conversation_sid] = {
            'text': text,
            'filename': filename
        }

        # Ask for confirmation
        await send_whatsapp_message(
            conversation_sid,
            "I received your document. Would you like to add it to the knowledge base? (Reply 'yes' to confirm)"
        )

    finally:
        # Cleanup temp file
        if 'temp_path' in locals():
            os.unlink(temp_path)

async def send_whatsapp_message(to_number: str, message: str):
    """Send a message through WhatsApp"""
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
            to=f"whatsapp:{to_number}"
        )
        return message.sid
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    """Handle incoming WhatsApp messages through Twilio"""
    # Validate Twilio signature
    form_data = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    if not validator.validate(url, form_data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    
    # Get message details
    from_number = form_data.get('From', '').replace('whatsapp:', '')
    message_body = form_data.get('Body', '').lower()
    media_url = form_data.get('MediaUrl0')
    filename = form_data.get('MediaFilename0')

    try:
        # Handle document upload
        if media_url and filename:
            await handle_document_upload(from_number, form_data.get('MessageSid'), media_url, filename)
            return {"success": True}

        # Handle confirmation response
        if message_body == 'yes' and from_number in pending_confirmations:
            doc_info = pending_confirmations[from_number]
            
            # Add to vector store
            add_documents(
                texts=[doc_info['text']], 
                metadatas=[{"source": doc_info['filename']}]
            )
            
            # Confirm and cleanup
            await send_whatsapp_message(from_number, f"Document '{doc_info['filename']}' has been added to the knowledge base!")
            del pending_confirmations[from_number]
            return {"success": True}

        # Handle regular query
        if from_number not in pending_confirmations:
            result = process_query(message_body)
            response = result["messages"][-1].content if result.get("messages") else "I couldn't process your query."
            
            await send_whatsapp_message(from_number, response)
            return {"success": True}

    except Exception as e:
        await send_whatsapp_message(from_number, "Sorry, I encountered an error. Please try again.")
        raise HTTPException(status_code=500, detail=str(e))

    return {"success": True} 