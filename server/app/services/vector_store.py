import time
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from typing import List, Optional
from fastapi import HTTPException

from app.config import settings

# Cache for the vector store
_vector_store = None

def get_vector_store():
    """
    Get or create the vector store
    """
    global _vector_store
    
    # Return cached vector store if available
    if _vector_store is not None:
        return _vector_store
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
    
    # Check if index exists, create if it doesn't
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    
    if settings.PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=1536,  # Dimension for text-embedding-3-small
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.PINECONE_CLOUD, 
                region=settings.PINECONE_REGION
            ),
        )
        # Wait for index to be ready
        while not pc.describe_index(settings.PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(1)
    
    # Get the index
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    
    # Create the vector store
    _vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    
    return _vector_store

def add_documents(texts: List[str], metadatas: Optional[List[dict]] = None):
    """
    Add documents to the vector store with error handling
    """
    try:
        vector_store = get_vector_store()
        
        # Validate inputs
        if not texts:
            raise ValueError("No texts provided for embedding")
        
        if metadatas and len(metadatas) != len(texts):
            raise ValueError("Number of metadata items must match number of texts")
        
        # Add texts to vector store
        vector_store.add_texts(
            texts=texts,
            metadatas=metadatas or [{} for _ in texts]
        )
        print(f"Successfully added {len(texts)} documents to vector store")
        
    except Exception as e:
        print(f"Error adding documents to vector store: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add documents to vector store: {str(e)}"
        )