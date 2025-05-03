from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import PyPDF2
import io
import docx

from app.services.vector_store import add_documents

router = APIRouter()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file"""
    pdf_file = io.BytesIO(file_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX file"""
    doc = docx.Document(io.BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload documents to be added to the knowledge base
    Supports PDF and DOCX files
    """
    try:
        all_texts = []
        all_metadata = []
        
        for file in files:
            content = await file.read()
            
            if file.filename.endswith('.pdf'):
                text = extract_text_from_pdf(content)
            elif file.filename.endswith('.docx'):
                text = extract_text_from_docx(content)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Only PDF and DOCX files are supported."
                )
            
            # Split text into chunks of roughly 1000 characters
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            
            all_texts.extend(chunks)
            all_metadata.extend([{"source": file.filename} for _ in chunks])
        
        # Add documents to vector store
        add_documents(all_texts, all_metadata)
        
        return {"message": f"Successfully processed {len(files)} files"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 