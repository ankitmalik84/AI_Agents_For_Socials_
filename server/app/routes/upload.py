import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_processor import process_pdf

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save PDF temporarily
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the PDF
        result = process_pdf(file_path)
        
        # Clean up the uploaded file
        os.remove(file_path)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 