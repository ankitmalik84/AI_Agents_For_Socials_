from fastapi import APIRouter, HTTPException, Query
from typing import Optional, AsyncGenerator
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.rag import process_query, process_query_stream
from uuid import uuid4
import json
from typing import Dict, Any

router = APIRouter()

class QueryInput(BaseModel):
    content: str
    thread_id: Optional[str] = None

router = APIRouter()

@router.post("/invoke")
def invoke(request: QueryInput) -> Dict[str, Any]:
    """
    Process a query and return a simple response
    """
    try:
        print(f"Processing query: {request.content}")
        response = process_query(request.content, request.thread_id)

        return {
            "answer": response["messages"][-1].content,
            "success": True
        }
    
    except Exception as e:
        return {
            "error": f"Error processing query: {str(e)}",
            "success": False
        }

@router.get("/stream/{message}")
async def stream_response(
    message: str, 
    thread_id: Optional[str] = Query(None)
) -> StreamingResponse:
    """Streaming endpoint for RAG responses"""
    return StreamingResponse(
        process_query_stream(message, thread_id),
        media_type="text/event-stream"
    )

async def format_stream_response(content: str, type: str = "content") -> str:
    """Helper function to format SSE messages"""
    data = {
        "type": type,
        "content": content.replace('"', '\\"').replace("\n", "\\n")
    }
    return f"data: {json.dumps(data)}\n\n"