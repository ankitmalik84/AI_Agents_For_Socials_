from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.config import settings
from app.services.vector_store import get_vector_store

def process_pdf(file_path: str) -> dict:
    """
    Process a PDF file and store it in the vector store
    """
    try:
        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        
        # Add metadata
        for split in splits:
            split.metadata.update({
                "source": "uploaded_pdf",
                "file_name": file_path.split("/")[-1]
            })
        
        # Store in vector store
        retriever = get_vector_store()
        retriever.vectorstore.add_documents(splits)
        
        return {
            "status": "success",
            "message": f"Successfully processed {len(splits)} chunks from PDF",
            "chunks": len(splits)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing PDF: {str(e)}"
        } 