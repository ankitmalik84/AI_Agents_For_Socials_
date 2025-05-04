from langchain_core.messages import HumanMessage, AIMessage
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
                # Handle normal chat model responses
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content"):
                    content = chunk.content
                    if (not any(skip in content for skip in [
                        "WARNING:", "INFO:", "ERROR:",
                        "Entering", "research_node",
                        "StatReload"
                    ]) and content.strip() and 
                        not content.strip().startswith('{"score":') and
                        not content.strip() in ['{"', '"', '"}', '":"', 'score', 'Yes', 'No', '}']):
                        
                        content = content.replace('"', '\\"').replace("\n", "\\n")
                        yield f"data: {{\"type\": \"content\", \"content\": \"{content}\"}}\n\n"
            
            elif event_type == "on_chat_model_end":
                # Check for tool calls related to search
                if "output" in event["data"] and hasattr(event["data"]["output"], "tool_calls"):
                    tool_calls = event["data"]["output"].tool_calls
                    search_calls = [call for call in tool_calls if call.get("name") == "tavily_search_results_json"]
                    
                    if search_calls:
                        # Signal search is starting
                        search_query = search_calls[0]["args"].get("query", "")
                        safe_query = search_query.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
                        yield f"data: {{\"type\": \"search_start\", \"query\": \"{safe_query}\"}}\n\n"
            
            elif event_type == "on_tool_end" and event.get("name") == "tavily_search_results_json":
                try:
                    # Extract search results from the ToolMessage
                    tool_message = event["data"]["output"]
                    if hasattr(tool_message, "content"):
                        # Parse the JSON string content
                        results = json.loads(tool_message.content)
                        
                        # Process each result
                        processed_results = []
                        for result in results:
                            processed_result = {
                                "title": result.get("title", "").replace('"', '\\"').replace("\n", "\\n"),
                                "url": result.get("url", ""),
                                "content": result.get("content", "").replace('"', '\\"').replace("\n", "\\n"),
                                "score": result.get("score", 0)
                            }
                            processed_results.append(processed_result)
                        
                        # Send a single search_results event with both results and urls
                        results_json = json.dumps({
                            "type": "search_results",
                            "results": processed_results,
                            "urls": [result["url"] for result in processed_results]
                        })
                        yield f"data: {results_json}\n\n"
                except Exception as e:
                    print(f"Error processing search results: {str(e)}")
                    error_msg = str(e).replace('"', '\\"').replace("\n", "\\n")
                    yield f"data: {{\"type\": \"search_error\", \"error\": \"{error_msg}\"}}\n\n"

        # Send end event
        yield f"data: {{\"type\": \"end\"}}\n\n"
        
    except Exception as e:
        error_msg = str(e).replace('"', '\\"').replace("\n", "\\n")
        yield f"data: {{\"type\": \"error\", \"error\": \"{error_msg}\"}}\n\n"