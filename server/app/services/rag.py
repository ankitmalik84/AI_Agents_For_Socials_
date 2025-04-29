from langchain_core.messages import HumanMessage
from app.services.graph import create_graph
from app.services.vector_store import get_vector_store
from typing import AsyncGenerator
from uuid import uuid4
import json

# Cache for the RAG pipeline
_rag_pipeline = None

def get_rag_pipeline():
    """
    Get or create the RAG pipeline
    """
    global _rag_pipeline
    
    # Return cached pipeline if available
    if _rag_pipeline is not None:
        return _rag_pipeline
    
    # Create a new pipeline
    _rag_pipeline = create_graph()
    
    return _rag_pipeline

def process_query(content: str, thread_id: str = None):
    """
    Process a query through the RAG pipeline
    """
    # Get the RAG pipeline
    rag_pipeline = get_rag_pipeline()
    
    # Create input data for the graph
    input_data = {"question": HumanMessage(content=content)}
    
    # Invoke the graph with the input data
    config = {"configurable": {"thread_id": thread_id or "default"}}
    result = rag_pipeline.invoke(input_data, config=config)
    
    return result

async def process_query_stream(content: str, thread_id: str = None) -> AsyncGenerator[str, None]:
    """
    Process a query through the RAG pipeline with streaming response
    """
    # Generate new thread_id if not provided
    if not thread_id:
        thread_id = str(uuid4())
        yield f"data: {{\"type\": \"thread_id\", \"thread_id\": \"{thread_id}\"}}\n\n"

    try:
        # Get the RAG pipeline
        rag_pipeline = get_rag_pipeline()
        
        # Create input data
        input_data = {"question": HumanMessage(content=content)}
        config = {"configurable": {"thread_id": thread_id}}

        # Stream the response
        async for event in rag_pipeline.astream_events(
            input_data,
            config=config,
            version="v2"
        ):
            event_type = event["event"]
            
            if event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content"):
                    yield f"data: {{\"type\": \"content\", \"content\": \"{chunk.content}\"}}\n\n"
            
            elif event_type == "on_tool_end" and event.get("name") == "tavily_search":
                # Handle search results
                results = event["data"]["output"]
                yield f"data: {{\"type\": \"search_results\", \"results\": {json.dumps(results)}}}\n\n"

        # Send end event
        yield f"data: {{\"type\": \"end\"}}\n\n"
        
    except Exception as e:
        error_msg = str(e).replace('"', '\\"').replace("\n", "\\n")
        yield f"data: {{\"type\": \"error\", \"content\": \"{error_msg}\"}}\n\n"