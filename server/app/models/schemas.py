from typing import Dict, List, Optional, TypedDict, Literal
from pydantic import BaseModel, Field

# Request models
class QueryRequest(BaseModel):
    content: str = Field(..., description="The question to ask")
    thread_id: Optional[str] = Field(None, description="Optional thread ID for conversation continuity")

# Response models
class StepResult(TypedDict):
    name: str
    result: Dict[str, str]

class QueryResponse(BaseModel):
    question: str
    steps: List[StepResult] = []
    result: Dict[str, str] = {}

# Agent state models
class AgentState(TypedDict):
    messages: List
    documents: List
    on_topic: str
    rephrased_question: str
    proceed_to_generate: bool
    rephrase_count: int
    question: dict
    workflow_type: str

class GradeQuestion(BaseModel):
    score: str = Field(
        description="Question is about the specified topics? If yes -> 'Yes' if not -> 'No'"
    )

# Add this class near the top with other schema definitions
class WorkflowType(BaseModel):
    type: Literal["system_design", "casual", "off_topic"]

class GradeDocument(BaseModel):
    score: str = Field(
        description="Document is relevant to the question? If yes -> 'Yes' if not -> 'No'"
    )

# Add these classes to schemas.py
class ConversationResponse(BaseModel):
    response: str = Field(description="The conversation response")

class OffTopicResponse(BaseModel):
    response: str = Field(description="The off-topic response message")